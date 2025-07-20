#!/usr/bin/env python3
"""
Sistema de Cache Inteligente Multi-Nivel para Producción
Combina RAM + Blob Storage + Auto-actualización
"""
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from azure.storage.blob import BlobServiceClient
import logging


class ProductionCacheManager:
    """
    Sistema de cache multi-nivel optimizado para producción:
    1. Nivel 1: RAM (ultra-rápido)
    2. Nivel 2: Blob Storage cache (persistente)
    3. Auto-actualización automática
    """

    def __init__(self, blob_connection_string: str, container_name: str):
        self.blob_client = BlobServiceClient.from_connection_string(
            blob_connection_string
        )
        self.container_name = container_name

        # Cache en RAM (Nivel 1)
        self.ram_cache = {}
        self.cache_metadata = {}

        # Configuración del cache
        self.cache_blob_name = "system_cache/processed_data_cache.json"
        self.metadata_blob_name = "system_cache/cache_metadata.json"
        self.cache_ttl_hours = 24  # Cache válido por 24 horas

        # Auto-inicialización
        self.initialize_cache()

    def initialize_cache(self):
        """Inicializa el cache con estrategia inteligente"""
        logging.info("🔄 Inicializando cache multi-nivel...")

        # 1. Intentar cargar desde cache persistente
        if self._load_from_persistent_cache():
            logging.info("✅ Cache cargado desde storage persistente")
            return

        # 2. Si no hay cache, generar desde archivos Excel
        logging.info("📊 Generando cache desde archivos Excel...")
        self._rebuild_cache_from_excel()

        # 3. Guardar cache persistente para futuras cargas
        self._save_persistent_cache()

    def _load_from_persistent_cache(self) -> bool:
        """Carga cache desde Blob Storage si está disponible y válido"""
        try:
            container_client = self.blob_client.get_container_client(
                self.container_name
            )

            # Verificar si existe cache metadata
            try:
                metadata_blob = container_client.get_blob_client(
                    self.metadata_blob_name
                )
                metadata_content = metadata_blob.download_blob().readall()
                metadata = json.loads(metadata_content.decode("utf-8"))

                # Verificar si el cache sigue siendo válido
                cache_time = datetime.fromisoformat(metadata["created_at"])
                ttl_threshold = datetime.now() - timedelta(hours=self.cache_ttl_hours)

                if cache_time < ttl_threshold:
                    logging.info("⏰ Cache expirado, regenerando...")
                    return False

                # Verificar si hay nuevos archivos Excel
                current_excel_hash = self._get_excel_files_hash()
                if current_excel_hash != metadata.get("excel_files_hash"):
                    logging.info("📁 Nuevos archivos detectados, regenerando cache...")
                    return False

            except Exception:
                logging.info("📋 Metadata de cache no encontrada")
                return False

            # Cargar cache de datos
            try:
                cache_blob = container_client.get_blob_client(self.cache_blob_name)
                cache_content = cache_blob.download_blob().readall()
                cache_data = json.loads(cache_content.decode("utf-8"))

                self.ram_cache = cache_data["data_cache"]
                self.cache_metadata = metadata

                logging.info(f"✅ Cache cargado: {len(self.ram_cache)} entradas")
                return True

            except Exception as e:
                logging.error(f"❌ Error cargando cache: {e}")
                return False

        except Exception as e:
            logging.error(f"❌ Error accediendo cache persistente: {e}")
            return False

    def _save_persistent_cache(self):
        """Guarda el cache actual en Blob Storage"""
        try:
            container_client = self.blob_client.get_container_client(
                self.container_name
            )

            # Preparar datos del cache
            cache_data = {
                "data_cache": self.ram_cache,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
            }

            # Preparar metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "total_entries": len(self.ram_cache),
                "excel_files_hash": self._get_excel_files_hash(),
                "ttl_hours": self.cache_ttl_hours,
            }

            # Guardar cache de datos
            cache_json = json.dumps(cache_data, ensure_ascii=False, indent=2)
            cache_blob = container_client.get_blob_client(self.cache_blob_name)
            cache_blob.upload_blob(cache_json.encode("utf-8"), overwrite=True)

            # Guardar metadata
            metadata_json = json.dumps(metadata, ensure_ascii=False, indent=2)
            metadata_blob = container_client.get_blob_client(self.metadata_blob_name)
            metadata_blob.upload_blob(metadata_json.encode("utf-8"), overwrite=True)

            self.cache_metadata = metadata
            logging.info("💾 Cache persistente guardado exitosamente")

        except Exception as e:
            logging.error(f"❌ Error guardando cache persistente: {e}")

    def _get_excel_files_hash(self) -> str:
        """Genera hash de todos los archivos Excel para detectar cambios"""
        try:
            container_client = self.blob_client.get_container_client(
                self.container_name
            )

            # Obtener lista de archivos Excel con sus timestamps
            excel_files = []
            for blob in container_client.list_blobs():
                if blob.name.upper().endswith((".XLS", ".XLSX")):
                    excel_files.append(
                        {
                            "name": blob.name,
                            "modified": blob.last_modified.isoformat(),
                            "size": blob.size,
                        }
                    )

            # Ordenar para hash consistente
            excel_files.sort(key=lambda x: x["name"])

            # Generar hash
            files_str = json.dumps(excel_files, sort_keys=True)
            return hashlib.md5(files_str.encode()).hexdigest()

        except Exception as e:
            logging.error(f"❌ Error generando hash de archivos: {e}")
            return ""

    def _rebuild_cache_from_excel(self):
        """Reconstruye el cache procesando todos los archivos Excel"""
        from src.excel_processor import ExcelProcessor

        processor = ExcelProcessor()
        container_client = self.blob_client.get_container_client(self.container_name)

        self.ram_cache.clear()
        processed_count = 0

        for blob in container_client.list_blobs():
            if blob.name.upper().endswith((".XLS", ".XLSX")):
                try:
                    # Descargar y procesar archivo
                    blob_client = container_client.get_blob_client(blob.name)
                    blob_stream = blob_client.download_blob()

                    result = processor.process_excel_stream(blob_stream, blob.name)

                    if result["status"] == "success":
                        self._store_data_in_cache(result)
                        processed_count += 1
                        logging.info(f"✅ Procesado: {blob.name}")
                    else:
                        logging.error(
                            f"❌ Error procesando {blob.name}: {result.get('error')}"
                        )

                except Exception as e:
                    logging.error(f"❌ Error con archivo {blob.name}: {e}")

        logging.info(f"🎯 Cache reconstruido: {processed_count} archivos procesados")

    def _store_data_in_cache(self, processed_data: Dict):
        """Almacena datos procesados en el cache RAM"""
        metadata = processed_data["metadata"]
        rentability_data = processed_data["rentability_data"]

        key = f"fund_{metadata.get('fund_type', 0)}_period_{metadata.get('period', 'unknown')}"

        self.ram_cache[key] = {
            "metadata": metadata,
            "rentability_data": rentability_data,
            "file_path": metadata["filename"],
            "cached_at": datetime.now().isoformat(),
        }

    def get_data(self, key: str) -> Optional[Dict]:
        """Obtiene datos del cache (ultra-rápido desde RAM)"""
        return self.ram_cache.get(key)

    def auto_refresh_if_needed(self):
        """Verifica automáticamente si necesita refrescar el cache"""
        try:
            # Verificar si hay nuevos archivos
            current_hash = self._get_excel_files_hash()
            cached_hash = self.cache_metadata.get("excel_files_hash")

            if current_hash != cached_hash:
                logging.info("🔄 Nuevos archivos detectados, actualizando cache...")
                self._rebuild_cache_from_excel()
                self._save_persistent_cache()
                return True

            # Verificar TTL
            if self.cache_metadata:
                cache_time = datetime.fromisoformat(self.cache_metadata["created_at"])
                ttl_threshold = datetime.now() - timedelta(hours=self.cache_ttl_hours)

                if cache_time < ttl_threshold:
                    logging.info("⏰ Cache expirado, refrescando...")
                    self._rebuild_cache_from_excel()
                    self._save_persistent_cache()
                    return True

            return False

        except Exception as e:
            logging.error(f"❌ Error en auto-refresh: {e}")
            return False

    def force_refresh(self):
        """Fuerza actualización completa del cache"""
        logging.info("🔄 Forzando actualización completa del cache...")
        self._rebuild_cache_from_excel()
        self._save_persistent_cache()

    def get_cache_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        return {
            "ram_cache_entries": len(self.ram_cache),
            "cache_created_at": self.cache_metadata.get("created_at"),
            "excel_files_hash": self.cache_metadata.get("excel_files_hash"),
            "ttl_hours": self.cache_ttl_hours,
            "cache_size_mb": len(json.dumps(self.ram_cache).encode()) / (1024 * 1024),
        }


class AutoUpdatingDataManager:
    """
    Data Manager con auto-actualización automática
    Reemplaza al RentabilityDataManager original
    """

    def __init__(self):
        from config import AZURE_BLOB_CONFIG

        connection_string = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING")
        container_name = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONTAINER_NAME")

        if not connection_string or not container_name:
            raise Exception("Azure Blob Storage credentials required")

        # Inicializar cache inteligente
        self.cache_manager = ProductionCacheManager(connection_string, container_name)

        # Configurar auto-refresh cada X minutos
        self.last_auto_check = datetime.now()
        self.auto_check_interval_minutes = 5  # Verificar cada 5 minutos

    def _auto_refresh_check(self):
        """Verificación automática periódica"""
        now = datetime.now()
        time_since_check = now - self.last_auto_check

        if time_since_check.total_seconds() > (self.auto_check_interval_minutes * 60):
            self.cache_manager.auto_refresh_if_needed()
            self.last_auto_check = now

    def get_rentability_by_afp(
        self, afp_name: str, fund_type: int = 0, period: str = None
    ) -> Dict:
        """Obtiene rentabilidad con auto-refresh automático"""
        # Auto-refresh check
        self._auto_refresh_check()

        # Obtener período más reciente si no se especifica
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {
                    "error": f"No hay datos disponibles para el fondo tipo {fund_type}"
                }
            period = sorted(available_periods, reverse=True)[0]

        # Buscar en cache
        key = f"fund_{fund_type}_period_{period}"
        cached_data = self.cache_manager.get_data(key)

        if not cached_data:
            return {
                "error": f"No hay datos para fondo tipo {fund_type} en período {period}"
            }

        # Buscar AFP específica
        afp_name_lower = afp_name.lower()
        for afp_data in cached_data["rentability_data"].get("afp_data", []):
            if afp_data["afp_name"].lower() == afp_name_lower:
                return {
                    "afp_name": afp_data["afp_name"],
                    "fund_type": fund_type,
                    "period": period,
                    "rentability_data": afp_data["rentability_data"],
                    "data_source": f"Cache inteligente - {period}",
                    "cached_at": cached_data.get("cached_at"),
                }

        return {"error": f"AFP {afp_name} no encontrada en los datos"}

    def get_available_periods(self, fund_type: int = None) -> List[str]:
        """Obtiene períodos disponibles del cache"""
        periods = set()

        for key, data in self.cache_manager.ram_cache.items():
            if fund_type is None or f"fund_{fund_type}" in key:
                period = data["metadata"].get("period")
                if period:
                    periods.add(period)

        return sorted(list(periods))

    def get_summary_statistics(self) -> Dict:
        """Estadísticas del sistema con información de cache"""
        cache_stats = self.cache_manager.get_cache_stats()

        return {
            "total_files_processed": cache_stats["ram_cache_entries"],
            "available_fund_types": self.get_available_fund_types(),
            "available_periods": self.get_available_periods(),
            "available_afps": self.get_all_afps(),
            "cache_stats": cache_stats,
            "data_source": "Hybrid Cache System (RAM + Blob Storage)",
            "auto_refresh_enabled": True,
        }

    def get_available_fund_types(self) -> List[int]:
        """Obtiene tipos de fondos disponibles"""
        fund_types = set()

        for key, data in self.cache_manager.ram_cache.items():
            fund_type = data["metadata"].get("fund_type")
            if fund_type is not None:
                fund_types.add(fund_type)

        return sorted(list(fund_types))

    def get_all_afps(self) -> List[str]:
        """Obtiene lista de todas las AFPs disponibles"""
        afps = set()

        for data in self.cache_manager.ram_cache.values():
            for afp_data in data["rentability_data"].get("afp_data", []):
                afps.add(afp_data["afp_name"])

        return sorted(list(afps))

    def force_refresh(self):
        """Fuerza actualización completa (para casos especiales)"""
        self.cache_manager.force_refresh()


# Función para integrar con el sistema existente
def get_production_data_manager() -> AutoUpdatingDataManager:
    """Obtiene instancia del gestor de datos con auto-actualización"""
    return AutoUpdatingDataManager()
