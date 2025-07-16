#!/usr/bin/env python3
"""
Gestor de datos de rentabilidad de fondos SPP
Carga y gestiona todos los archivos Excel de rentabilidad desde Azure Blob Storage
"""
import pandas as pd
import json
import os
import glob
from typing import Dict, List, Any, Optional
from .excel_processor import ExcelProcessor
from azure.storage.blob import BlobServiceClient
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AZURE_BLOB_CONFIG
import logging

class RentabilityDataManager:
    """Gestor centralizado de datos de rentabilidad"""
    
    def __init__(self):
        self.processor = ExcelProcessor()
        self.data_cache = {}
        
        # Configurar para usar Azure Blob Storage obligatoriamente
        connection_string = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING")
        container_name = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONTAINER_NAME")
        
        if not connection_string or not container_name:
            raise Exception("Las credenciales de Azure Blob Storage son obligatorias. Configure AZURE_BLOB_CONNECTION_STRING y AZURE_BLOB_CONTAINER_NAME en las variables de entorno.")
        
        try:
            self.blob_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
            self.container_name = container_name
            self.use_blob_storage = True
            logging.info("Configurado para usar Azure Blob Storage")
        except Exception as e:
            raise Exception(f"Error configurando blob storage: {e}. Verifique las credenciales de Azure.")
            
        self.load_all_data()
    
    def load_all_data(self):
        """Carga todos los archivos Excel de rentabilidad desde Azure Blob Storage"""
        self._load_from_blob_storage()
    
    def _load_from_blob_storage(self):
        """Carga archivos desde Azure Blob Storage"""
        try:
            container_client = self.blob_client.get_container_client(self.container_name)
            
            # Listar todos los blobs que son archivos Excel
            excel_blobs = []
            for blob in container_client.list_blobs():
                if blob.name.upper().endswith(('.XLS', '.XLSX')):
                    excel_blobs.append(blob)
            
            logging.info(f"Encontrados {len(excel_blobs)} archivos Excel en blob storage...")
            
            for blob in excel_blobs:
                try:
                    # Descargar el blob como stream
                    blob_client = container_client.get_blob_client(blob.name)
                    blob_stream = blob_client.download_blob()
                    
                    # Procesar el archivo Excel desde el stream
                    result = self.processor.process_excel_stream(blob_stream, blob.name)
                    
                    if result["status"] == "success":
                        self._store_data(result)
                        logging.info(f"Procesado desde blob storage: {blob.name}")
                    else:
                        logging.error(f"Error procesando blob {blob.name}: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logging.error(f"Error cargando blob {blob.name}: {str(e)}")
            
            logging.info(f"Datos cargados para {len(self.data_cache)} archivos desde blob storage")
            
        except Exception as e:
            logging.error(f"Error conectando a blob storage: {str(e)}")
            raise Exception(f"No se pudo conectar a blob storage: {str(e)}")
    

    
    def _store_data(self, processed_data: Dict):
        """Almacena datos procesados en el cache"""
        metadata = processed_data["metadata"]
        rentability_data = processed_data["rentability_data"]
        
        # Crear clave única para el archivo
        key = f"fund_{metadata.get('fund_type', 0)}_period_{metadata.get('period', 'unknown')}"
        
        self.data_cache[key] = {
            "metadata": metadata,
            "rentability_data": rentability_data,
            "file_path": metadata["filename"]
        }
    
    def get_rentability_by_afp(self, afp_name: str, fund_type: int = 0, period: str = None) -> Dict:
        """Obtiene datos de rentabilidad por AFP"""
        afp_name = afp_name.lower()
        
        # Si no se especifica período, usar el más reciente disponible
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {"error": f"No hay datos disponibles para el fondo tipo {fund_type}"}
            # Ordenar períodos y tomar el más reciente (sin asumir un máximo fijo)
            period = sorted(available_periods, reverse=True)[0]
        
        key = f"fund_{fund_type}_period_{period}"
        
        if key not in self.data_cache:
            return {"error": f"No hay datos para fondo tipo {fund_type} en período {period}"}
        
        data = self.data_cache[key]["rentability_data"]
        
        # Buscar datos de la AFP específica
        for afp_data in data.get("afp_data", []):
            if afp_data["afp_name"].lower() == afp_name:
                return {
                    "afp_name": afp_data["afp_name"],
                    "fund_type": fund_type,
                    "period": period,
                    "rentability_data": afp_data["rentability_data"],
                    "periods_available": data.get("periods_available", []),
                    "data_source": f"Archivo oficial SPP - {period}"
                }
        
        return {"error": f"AFP {afp_name} no encontrada en los datos"}
    
    def compare_afp_rentability(self, afps: List[str], fund_type: int = 0, period: str = None) -> Dict:
        """Compara rentabilidad entre múltiples AFPs"""
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {"error": f"No hay datos disponibles para el fondo tipo {fund_type}"}
            # Ordenar períodos y tomar el más reciente (sin asumir un máximo fijo)
            period = sorted(available_periods, reverse=True)[0]
        
        comparison = {}
        rankings = {}
        
        for afp in afps:
            afp_data = self.get_rentability_by_afp(afp, fund_type, period)
            if "error" not in afp_data:
                comparison[afp] = afp_data["rentability_data"]
        
        # Calcular rankings para diferentes períodos
        if comparison:
            sample_data = next(iter(comparison.values()))
            for period_key in sample_data.keys():
                if "nominal" in period_key or "real" in period_key:
                    period_ranking = []
                    for afp, data in comparison.items():
                        if period_key in data:
                            period_ranking.append((afp, data[period_key]))
                    period_ranking.sort(key=lambda x: x[1], reverse=True)
                    rankings[period_key] = period_ranking
        
        return {
            "comparison": comparison,
            "fund_type": fund_type,
            "period": period,
            "rankings": rankings,
            "analysis": f"Comparación de rentabilidad para fondo tipo {fund_type}"
        }
    
    def get_available_periods(self, fund_type: int = None) -> List[str]:
        """Obtiene períodos disponibles"""
        periods = set()
        
        for key, data in self.data_cache.items():
            if fund_type is None or f"fund_{fund_type}" in key:
                period = data["metadata"].get("period")
                if period:
                    periods.add(period)
        
        return sorted(list(periods))
    
    def get_available_fund_types(self) -> List[int]:
        """Obtiene tipos de fondos disponibles"""
        fund_types = set()
        
        for key, data in self.data_cache.items():
            fund_type = data["metadata"].get("fund_type")
            if fund_type is not None:
                fund_types.add(fund_type)
        
        return sorted(list(fund_types))
    
    def get_all_afps(self) -> List[str]:
        """Obtiene lista de todas las AFPs disponibles"""
        afps = set()
        
        for data in self.data_cache.values():
            for afp_data in data["rentability_data"].get("afp_data", []):
                afps.add(afp_data["afp_name"])
        
        return sorted(list(afps))
    
    def analyze_fund_performance(self, fund_types: List[int], afp_filter: str = "all") -> Dict:
        """Analiza rendimiento de diferentes tipos de fondos"""
        analysis = {}
        
        # Características generales de cada tipo de fondo
        fund_characteristics = {
            0: {
                "name": "Conservador",
                "risk_level": "Bajo",
                "description": "Fondo de menor riesgo, principalmente renta fija",
                "target_profile": "Personas próximas a jubilarse o conservadoras"
            },
            1: {
                "name": "Mixto Conservador", 
                "risk_level": "Bajo-Medio",
                "description": "Combinación de renta fija y variable con predominio de renta fija",
                "target_profile": "Personas con perfil moderadamente conservador"
            },
            2: {
                "name": "Mixto",
                "risk_level": "Medio",
                "description": "Balance entre renta fija y variable",
                "target_profile": "Personas con perfil de riesgo moderado"
            },
            3: {
                "name": "Crecimiento",
                "risk_level": "Alto", 
                "description": "Mayor proporción en renta variable para crecimiento",
                "target_profile": "Personas jóvenes con horizonte de inversión largo"
            }
        }
        
        for fund_type in fund_types:
            if fund_type in fund_characteristics:
                # Obtener datos reales de rentabilidad promedio
                avg_rentability = self._calculate_average_rentability(fund_type, afp_filter)
                
                analysis[f"fund_type_{fund_type}"] = {
                    **fund_characteristics[fund_type],
                    "average_rentability": avg_rentability,
                    "data_available": len(self.get_available_periods(fund_type)) > 0
                }
        
        return {
            "fund_analysis": analysis,
            "recommendation": self._generate_fund_recommendation(fund_types),
            "data_source": "Análisis basado en datos oficiales SPP"
        }
    
    def _calculate_average_rentability(self, fund_type: int, afp_filter: str) -> Dict:
        """Calcula rentabilidad promedio para un tipo de fondo"""
        periods = self.get_available_periods(fund_type)
        if not periods:
            return {"error": "No hay datos disponibles"}
        
        # Usar el período más reciente (sin asumir un máximo fijo)
        latest_period = sorted(periods, reverse=True)[0]
        key = f"fund_{fund_type}_period_{latest_period}"
        
        if key not in self.data_cache:
            return {"error": "Datos no encontrados"}
        
        data = self.data_cache[key]["rentability_data"]
        afp_data = data.get("afp_data", [])
        
        if not afp_data:
            return {"error": "No hay datos de AFPs"}
        
        # Calcular promedios
        totals = {}
        count = 0
        
        for afp in afp_data:
            if afp_filter == "all" or afp["afp_name"].lower() == afp_filter.lower():
                rentability = afp["rentability_data"]
                for key, value in rentability.items():
                    if key not in totals:
                        totals[key] = 0
                    totals[key] += value
                count += 1
        
        if count == 0:
            return {"error": "No se encontraron datos para el filtro especificado"}
        
        averages = {key: round(value / count, 4) for key, value in totals.items()}
        
        return {
            "averages": averages,
            "afps_included": count,
            "period": latest_period
        }
    
    def _generate_fund_recommendation(self, fund_types: List[int]) -> str:
        """Genera recomendación basada en tipos de fondos analizados"""
        if len(fund_types) == 1:
            fund_type = fund_types[0]
            recommendations = {
                0: "Ideal para personas conservadoras o próximas a jubilarse que priorizan la preservación del capital.",
                1: "Adecuado para personas con perfil moderadamente conservador que buscan un balance entre seguridad y crecimiento.",
                2: "Recomendado para personas con perfil de riesgo moderado y horizonte de inversión medio.",
                3: "Apropiado para personas jóvenes con horizonte de inversión largo que pueden asumir mayor volatilidad."
            }
            return recommendations.get(fund_type, "Consulte con un asesor financiero para determinar el fondo más adecuado.")
        else:
            return "La diversificación entre diferentes tipos de fondos puede ayudar a balancear riesgo y rentabilidad según su perfil de inversión."
    
    def get_summary_statistics(self) -> Dict:
        """Obtiene estadísticas resumen de todos los datos"""
        return {
            "total_files_processed": len(self.data_cache),
            "available_fund_types": self.get_available_fund_types(),
            "available_periods": self.get_available_periods(),
            "available_afps": self.get_all_afps(),
            "data_coverage": {
                f"fund_type_{ft}": len(self.get_available_periods(ft)) 
                for ft in self.get_available_fund_types()
            },
            "data_source": "Azure Blob Storage"
        }
    
    def refresh_data(self):
        """Refresca los datos desde blob storage"""
        logging.info("Refrescando datos desde blob storage...")
        self.data_cache.clear()
        self.load_all_data()
        logging.info(f"Datos refrescados. {len(self.data_cache)} archivos cargados.")
    
    def get_latest_period_for_fund(self, fund_type: int) -> str:
        """Obtiene el período más reciente disponible para un tipo de fondo específico"""
        periods = self.get_available_periods(fund_type)
        return sorted(periods, reverse=True)[0] if periods else None
    
    def get_data_freshness_info(self) -> Dict:
        """Obtiene información sobre la frescura de los datos"""
        fund_types = self.get_available_fund_types()
        freshness_info = {}
        
        for fund_type in fund_types:
            latest_period = self.get_latest_period_for_fund(fund_type)
            freshness_info[f"fund_type_{fund_type}"] = {
                "latest_period": latest_period,
                "total_periods": len(self.get_available_periods(fund_type))
            }
        
        return {
            "fund_freshness": freshness_info,
            "total_cached_files": len(self.data_cache),
            "recommendation": "Los datos se actualizan automáticamente desde blob storage. Use refresh_data() para forzar actualización."
        }

# Instancia global del gestor de datos
data_manager = None

def get_data_manager() -> RentabilityDataManager:
    """Obtiene instancia singleton del gestor de datos"""
    global data_manager
    if data_manager is None:
        data_manager = RentabilityDataManager()
    return data_manager