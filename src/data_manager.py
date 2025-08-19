"""
Gestor de datos de rentabilidad de fondos SPP
Carga y gestiona todos los archivos Excel de rentabilidad desde Azure Blob Storage
Integra Azure AI Search y Azure SQL para consultas avanzadas
"""

import pandas as pd
import json
import os
import glob
from typing import Dict, List, Any, Optional
from .excel_processor import ExcelProcessor
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AZURE_BLOB_CONFIG, AZURE_AISEARCH_API_KEY, AZURE_SQL_CONFIG
import logging


class RentabilityDataManager:
    """Gestor centralizado de datos de rentabilidad"""

    def __init__(self):
        self.processor = ExcelProcessor()
        self.data_cache = {}

        # Configurar para usar Azure Blob Storage
        connection_string = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING")
        container_name = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONTAINER_NAME")

        if not connection_string or not container_name:
            raise Exception(
                "Las credenciales de Azure Blob Storage son obligatorias. Configure AZURE_BLOB_CONNECTION_STRING y AZURE_BLOB_CONTAINER_NAME en las variables de entorno."
            )

        try:
            self.blob_client = BlobServiceClient.from_connection_string(
                conn_str=connection_string
            )
            self.container_name = container_name
            self.use_blob_storage = True
            logging.info("Configurado para usar Azure Blob Storage")
        except Exception as e:
            raise Exception(
                f"Error configurando blob storage: {e}. Verifique las credenciales de Azure."
            )

        # Configurar Azure AI Search
        self.search_client = None
        try:
            endpoint = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_ENDPOINT")
            api_key = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_API_KEY")
            index_name = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_INDEX_NAME")

            if all([endpoint, api_key, index_name]):
                self.search_client = SearchClient(
                    endpoint=endpoint,
                    index_name=index_name,
                    credential=AzureKeyCredential(api_key),
                )
                logging.info("Azure AI Search configurado correctamente")
            else:
                logging.warning("Azure AI Search no configurado completamente")
        except Exception as e:
            logging.error(f"Error configurando Azure AI Search: {e}")

        # Configurar Azure SQL
        self.sql_connection_string = AZURE_SQL_CONFIG.get("AZURE_SQL_CONNECTION_STRING")
        if self.sql_connection_string:
            self.sql_connection_string += "Database=sbsbdsql;"
            logging.info("Azure SQL configurado correctamente")
        else:
            logging.warning("Azure SQL no configurado")

        self.load_all_data()

    def load_all_data(self):
        """Carga todos los archivos Excel de rentabilidad desde Azure Blob Storage"""
        self._load_from_blob_storage()

    def _load_from_blob_storage(self):
        """Carga archivos desde Azure Blob Storage"""
        try:
            container_client = self.blob_client.get_container_client(
                self.container_name
            )

            # Listar todos los blobs que son archivos Excel
            excel_blobs = []
            for blob in container_client.list_blobs():
                if blob.name.upper().endswith((".XLS", ".XLSX")):
                    excel_blobs.append(blob)

            logging.info(
                f"Encontrados {len(excel_blobs)} archivos Excel en blob storage..."
            )

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
                        logging.error(
                            f"Error procesando blob {blob.name}: {result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    logging.error(f"Error cargando blob {blob.name}: {str(e)}")

            logging.info(
                f"Datos cargados para {len(self.data_cache)} archivos desde blob storage"
            )

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
            "file_path": metadata["filename"],
        }

    def get_rentability_by_afp(
        self, afp_name: str, fund_type: int = 0, period: str = None
    ) -> Dict:
        """Obtiene datos de rentabilidad por AFP- Prioriza Azure SQL, luego cache"""
        afp_name = afp_name.lower()

        # Intentar obtener desde Azure SQL primero
        sql_result = self._get_rentability_from_sql(afp_name, fund_type, period)
        if sql_result and "error" not in sql_result:
            return sql_result

        # Fallback al cache loca
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {
                    "error": f"No hay datos disponibles para el fondo tipo {fund_type}"
                }
            # Ordenar períodos y tomar el más reciente (sin asumir un máximo fijo)
            period = sorted(available_periods, reverse=True)[0]

        key = f"fund_{fund_type}_period_{period}"

        if key not in self.data_cache:
            return {
                "error": f"No hay datos para fondo tipo {fund_type} en período {period}"
            }

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
                    "data_source": f"Archivo oficial SPP - {period}",
                }

        return {"error": f"AFP {afp_name} no encontrada en los datos"}

    def compare_afp_rentability(
        self, afps: List[str], fund_type: int = 0, period: str = None
    ) -> Dict:
        """Compara rentabilidad entre múltiples AFPs"""
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {
                    "error": f"No hay datos disponibles para el fondo tipo {fund_type}"
                }
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
            "analysis": f"Comparación de rentabilidad para fondo tipo {fund_type}",
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

    def analyze_fund_performance(
        self, fund_types: List[int], afp_filter: str = "all"
    ) -> Dict:
        """Analiza rendimiento de diferentes tipos de fondos"""
        analysis = {}

        # Características generales de cada tipo de fondo
        fund_characteristics = {
            0: {
                "name": "Conservador",
                "risk_level": "Bajo",
                "description": "Fondo de menor riesgo, principalmente renta fija",
                "target_profile": "Personas próximas a jubilarse o conservadoras",
            },
            1: {
                "name": "Mixto Conservador",
                "risk_level": "Bajo-Medio",
                "description": "Combinación de renta fija y variable con predominio de renta fija",
                "target_profile": "Personas con perfil moderadamente conservador",
            },
            2: {
                "name": "Mixto",
                "risk_level": "Medio",
                "description": "Balance entre renta fija y variable",
                "target_profile": "Personas con perfil de riesgo moderado",
            },
            3: {
                "name": "Crecimiento",
                "risk_level": "Alto",
                "description": "Mayor proporción en renta variable para crecimiento",
                "target_profile": "Personas jóvenes con horizonte de inversión largo",
            },
        }

        for fund_type in fund_types:
            if fund_type in fund_characteristics:
                # Obtener datos reales de rentabilidad promedio
                avg_rentability = self._calculate_average_rentability(
                    fund_type, afp_filter
                )

                analysis[f"fund_type_{fund_type}"] = {
                    **fund_characteristics[fund_type],
                    "average_rentability": avg_rentability,
                    "data_available": len(self.get_available_periods(fund_type)) > 0,
                }

        return {
            "fund_analysis": analysis,
            "recommendation": self._generate_fund_recommendation(fund_types),
            "data_source": "Análisis basado en datos oficiales SPP",
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

        return {"averages": averages, "afps_included": count, "period": latest_period}

    def _generate_fund_recommendation(self, fund_types: List[int]) -> str:
        """Genera recomendación basada en tipos de fondos analizados"""
        if len(fund_types) == 1:
            fund_type = fund_types[0]
            recommendations = {
                0: "Ideal para personas conservadoras o próximas a jubilarse que priorizan la preservación del capital.",
                1: "Adecuado para personas con perfil moderadamente conservador que buscan un balance entre seguridad y crecimiento.",
                2: "Recomendado para personas con perfil de riesgo moderado y horizonte de inversión medio.",
                3: "Apropiado para personas jóvenes con horizonte de inversión largo que pueden asumir mayor volatilidad.",
            }
            return recommendations.get(
                fund_type,
                "Consulte con un asesor financiero para determinar el fondo más adecuado.",
            )
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
            "data_source": "Azure Blob Storage",
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
                "total_periods": len(self.get_available_periods(fund_type)),
            }

        return {
            "fund_freshness": freshness_info,
            "total_cached_files": len(self.data_cache),
            "recommendation": "Los datos se actualizan automáticamente desde blob storage. Use refresh_data() para forzar actualización.",
        }

    def _get_rentability_from_sql(
        self, afp_name: str, fund_type: int, period: str = None
    ) -> Dict:
        """Obtiene datos de rentabilidad desde Azure SQL Database"""
        if not self.sql_connection_string:
            return {"error": "Azure SQL no configurado"}

        try:
            import pyodbc

            conn = pyodbc.connect(self.sql_connection_string)
            cursor = conn.cursor()

            # Construir query
            query = """
                SELECT period_key, rentability_value, rentability_type
                FROM rentability_data
                WHERE LOWER(afp_name) = ? AND fund_type = ?
            """
            params = [afp_name.lower(), fund_type]

            if period:
                query += " AND period = ?"
                params.append(period)
            else:
                # Obtener el período más reciente
                query += " AND period = (SELECT MAX(period) FROM rentability_data WHERE LOWER(afp_name) = ? AND fund_type = ?)"
                params.extend([afp_name.lower(), fund_type])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                conn.close()
                return {
                    "error": f"No hay datos en SQL para {afp_name} fondo tipo {fund_type}"
                }

            # Procesar resultados
            rentability_data = {}
            actual_period = None

            for row in rows:
                period_key, value, rent_type = row
                rentability_data[period_key] = float(value)

                # Obtener el período actual
                if not actual_period:
                    period_query = "SELECT DISTINCT period FROM rentability_data WHERE LOWER(afp_name) = ? AND fund_type = ? AND period_key = ?"
                    cursor.execute(
                        period_query, [afp_name.lower(), fund_type, period_key]
                    )
                    period_result = cursor.fetchone()
                    if period_result:
                        actual_period = period_result[0]

            conn.close()

            return {
                "afp_name": afp_name.title(),
                "fund_type": fund_type,
                "period": actual_period or period,
                "rentability_data": rentability_data,
                "data_source": "Azure SQL Database",
            }

        except Exception as e:
            logging.error(f"Error consultando Azure SQL: {str(e)}")
            return {"error": f"Error en consulta SQL: {str(e)}"}

    def search_rentability_data(
        self, query: str, fund_type: int = None, afp_name: str = None
    ) -> Dict:
        """Busca datos de rentabilidad usando Azure AI Search"""
        if not self.search_client:
            return {"error": "Azure AI Search no configurado"}

        try:
            # Construir filtros
            filters = []
            if fund_type is not None:
                filters.append(f"fundType eq {fund_type}")
            if afp_name:
                filters.append(f"afpName  eq '{afp_name}'")

            filter_expression = " and ".join(filters) if filters else None

            # Realizar búsqueda
            results = self.search_client.search(
                search_text=query,
                filter=filter_expression,
                top=10,
                include_total_count=True,
            )

            # Procesar resultados
            search_results = []
            for result in results:
                search_results.append(
                    {
                        "fund_type": result.get("fundType"),
                        "period": result.get("period"),
                        "afp_name": result.get("afpName"),
                        "content": result.get("content"),
                        "rentability_data": json.loads(
                            result.get("rentabilityData", "{}")
                        ),
                        "score": result.get("@search.score"),
                    }
                )

            return {
                "query": query,
                "results": search_results,
                "total_count": results.get_count(),
                "data_source": "Azure AI Search",
            }

        except Exception as e:
            logging.error(f"Error en búsqueda AI Search: {str(e)}")
            return {"error": f"Error en búsqueda: {str(e)}"}

    def get_comprehensive_analysis(self, afp_name: str, fund_type: int) -> Dict:
        """Análisis comprehensivo usando todas las fuentes de datos"""
        results = {"afp_name": afp_name, "fund_type": fund_type, "analysis_sources": []}

        # Datos desde cache/blob storage
        cache_data = self.get_rentability_by_afp(afp_name, fund_type)
        if "error" not in cache_data:
            results["cache_data"] = cache_data
            results["analysis_sources"].append("blob_storage_cache")

        # Datos desde Azure SQL
        sql_data = self._get_rentability_from_sql(afp_name, fund_type)
        if "error" not in sql_data:
            results["sql_data"] = sql_data
            results["analysis_sources"].append("azure_sql")

        # Búsqueda semántica
        search_query = f"rentabilidad {afp_name} fondo tipo {fund_type}"
        search_data = self.search_rentability_data(search_query, fund_type, afp_name)
        if "error" not in search_data and search_data.get("results"):
            results["search_data"] = search_data
            results["analysis_sources"].append("azure_ai_search")

        return results

    # ✅ AGREGAR ESTOS MÉTODOS AL data_manager.py EXISTENTE
    # NO reemplazar archivo completo, solo agregar estos métodos nuevos

    def get_rentability_by_afp_enhanced(
        self,
        afp_name: str,
        fund_type: int = 0,
        period: str = None,
        calculation_type: str = "both",  # ✅ NUEVO: "accumulated", "annualized", "both"
    ) -> Dict:
        """
        ✅ ENHANCED: Obtiene datos de rentabilidad diferenciando ACUMULADA vs ANUALIZADA
        Mantiene backward compatibility total
        """
        afp_name = afp_name.lower()

        # ✅ Intentar obtener desde Azure SQL primero (con nuevos tipos)
        sql_result = self._get_rentability_from_sql_enhanced(
            afp_name, fund_type, period, calculation_type
        )
        if sql_result and "error" not in sql_result:
            return sql_result

        # Fallback al cache local
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {
                    "error": f"No hay datos disponibles para el fondo tipo {fund_type}"
                }
            period = sorted(available_periods, reverse=True)[0]

        key = f"fund_{fund_type}_period_{period}"

        if key not in self.data_cache:
            return {
                "error": f"No hay datos para fondo tipo {fund_type} en período {period}"
            }

        data = self.data_cache[key]["rentability_data"]

        # Buscar datos de la AFP específica
        for afp_data in data.get("afp_data", []):
            if afp_data["afp_name"].lower() == afp_name:

                # ✅ ENHANCED: Filtrar por tipo de cálculo si se especifica
                filtered_data = afp_data["rentability_data"].copy()

                if calculation_type == "accumulated":
                    # Solo datos acumulados
                    filtered_data = {
                        k: v
                        for k, v in filtered_data.items()
                        if "accumulated" in k
                        or ("accumulated" not in k and "annualized" not in k)
                    }
                elif calculation_type == "annualized":
                    # Solo datos anualizados
                    filtered_data = {
                        k: v for k, v in filtered_data.items() if "annualized" in k
                    }
                # Si es "both", devolver todo

                return {
                    "afp_name": afp_data["afp_name"],
                    "fund_type": fund_type,
                    "period": period,
                    "calculation_type": calculation_type,
                    "rentability_data": filtered_data,
                    "data_sources": afp_data.get("data_sources", ["legacy"]),
                    "has_accumulated": any(
                        "accumulated" in k for k in filtered_data.keys()
                    ),
                    "has_annualized": any(
                        "annualized" in k for k in filtered_data.keys()
                    ),
                    "periods_available": data.get("periods_available", []),
                    "data_source": f"Archivo oficial SPP - {period} (Enhanced)",
                }

        return {"error": f"AFP {afp_name} no encontrada en los datos"}

    def compare_afp_rentability_enhanced(
        self,
        afps: List[str],
        fund_type: int = 0,
        period: str = None,
        calculation_type: str = "both",  # ✅ NUEVO: "accumulated", "annualized", "both"
    ) -> Dict:
        """
        ✅ ENHANCED: Compara rentabilidad entre múltiples AFPs con tipos diferenciados
        """
        if not period:
            available_periods = self.get_available_periods(fund_type)
            if not available_periods:
                return {
                    "error": f"No hay datos disponibles para el fondo tipo {fund_type}"
                }
            period = sorted(available_periods, reverse=True)[0]

        comparison = {}
        rankings = {}

        for afp in afps:
            afp_data = self.get_rentability_by_afp_enhanced(
                afp, fund_type, period, calculation_type
            )
            if "error" not in afp_data:
                comparison[afp] = afp_data["rentability_data"]

        # ✅ ENHANCED: Calcular rankings para diferentes tipos y períodos
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
            "calculation_type": calculation_type,
            "rankings": rankings,
            "analysis": f"Comparación de rentabilidad {calculation_type} para fondo tipo {fund_type}",
            "enhanced_features": {
                "accumulated_data": calculation_type in ["accumulated", "both"],
                "annualized_data": calculation_type in ["annualized", "both"],
            },
        }

    def _get_rentability_from_sql_enhanced(
        self,
        afp_name: str,
        fund_type: int,
        period: str = None,
        calculation_type: str = "both",
    ) -> Dict:
        """
        ✅ ENHANCED: Obtiene datos de rentabilidad desde Azure SQL Database con tipos
        """
        if not self.sql_connection_string:
            return {"error": "Azure SQL no configurado"}

        try:
            import pyodbc

            conn = pyodbc.connect(self.sql_connection_string)
            cursor = conn.cursor()

            # ✅ ENHANCED: Query con filtro de calculation_type
            query = """
                SELECT period_key, rentability_value, rentability_type, calculation_type
                FROM rentability_data
                WHERE LOWER(afp_name) = ? AND fund_type = ?
            """
            params = [afp_name.lower(), fund_type]

            if period:
                query += " AND period = ?"
                params.append(period)
            else:
                query += " AND period = (SELECT MAX(period) FROM rentability_data WHERE LOWER(afp_name) = ? AND fund_type = ?)"
                params.extend([afp_name.lower(), fund_type])

            # ✅ Filtrar por tipo de cálculo
            if calculation_type == "accumulated":
                query += " AND calculation_type = 'accumulated'"
            elif calculation_type == "annualized":
                query += " AND calculation_type = 'annualized'"
            # Si es "both", no filtrar

            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                conn.close()
                return {
                    "error": f"No hay datos en SQL para {afp_name} fondo tipo {fund_type}"
                }

            # ✅ ENHANCED: Procesar resultados con tipos
            rentability_data = {}
            actual_period = None
            data_sources = set()

            for row in rows:
                period_key, value, rent_type, calc_type = row
                rentability_data[period_key] = float(value)
                data_sources.add(calc_type)

                # Obtener el período actual
                if not actual_period:
                    period_query = "SELECT DISTINCT period FROM rentability_data WHERE LOWER(afp_name) = ? AND fund_type = ? AND period_key = ?"
                    cursor.execute(
                        period_query, [afp_name.lower(), fund_type, period_key]
                    )
                    period_result = cursor.fetchone()
                    if period_result:
                        actual_period = period_result[0]

            conn.close()

            return {
                "afp_name": afp_name.title(),
                "fund_type": fund_type,
                "period": actual_period or period,
                "calculation_type": calculation_type,
                "rentability_data": rentability_data,
                "data_sources": list(data_sources),
                "has_accumulated": "accumulated" in data_sources,
                "has_annualized": "annualized" in data_sources,
                "data_source": "Azure SQL Database (Enhanced)",
            }

        except Exception as e:
            logging.error(f"Error consultando Azure SQL ENHANCED: {str(e)}")
            return {"error": f"Error en consulta SQL: {str(e)}"}

    def get_calculation_types_summary(self) -> Dict:
        """
        ✅ NUEVO: Obtiene resumen de tipos de cálculo disponibles
        """
        summary = {
            "total_files": len(self.data_cache),
            "enhanced_files": 0,
            "legacy_files": 0,
            "accumulated_available": [],
            "annualized_available": [],
            "both_available": [],
        }

        for key, data in self.data_cache.items():
            rentability_info = data["rentability_data"].get("rentability_type_info", {})

            if rentability_info:
                summary["enhanced_files"] += 1

                if rentability_info.get("has_accumulated") and rentability_info.get(
                    "has_annualized"
                ):
                    summary["both_available"].append(key)
                elif rentability_info.get("has_accumulated"):
                    summary["accumulated_available"].append(key)
                elif rentability_info.get("has_annualized"):
                    summary["annualized_available"].append(key)
            else:
                summary["legacy_files"] += 1

        return summary

    def get_detailed_rentability_comparison(
        self, afp_name: str, fund_type: int = 0, period: str = None
    ) -> Dict:
        """
        ✅ NUEVO: Comparación detallada mostrando diferencias entre acumulada y anualizada
        """
        # Obtener datos acumulados
        acc_data = self.get_rentability_by_afp_enhanced(
            afp_name, fund_type, period, "accumulated"
        )

        # Obtener datos anualizados
        ann_data = self.get_rentability_by_afp_enhanced(
            afp_name, fund_type, period, "annualized"
        )

        comparison = {
            "afp_name": afp_name,
            "fund_type": fund_type,
            "period": period,
            "accumulated_data": acc_data if "error" not in acc_data else None,
            "annualized_data": ann_data if "error" not in ann_data else None,
            "differences": {},
            "analysis": [],
        }

        # Calcular diferencias si ambos están disponibles
        if comparison["accumulated_data"] and comparison["annualized_data"]:
            acc_rent = comparison["accumulated_data"]["rentability_data"]
            ann_rent = comparison["annualized_data"]["rentability_data"]

            # Encontrar claves comparables (mismo período, mismo tipo nominal/real)
            for acc_key, acc_value in acc_rent.items():
                if "accumulated" in acc_key:
                    # Buscar clave correspondiente en anualizada
                    ann_key = acc_key.replace("accumulated", "annualized")
                    if ann_key in ann_rent:
                        difference = acc_value - ann_rent[ann_key]
                        comparison["differences"][
                            acc_key.replace("_accumulated", "")
                        ] = {
                            "accumulated": acc_value,
                            "annualized": ann_rent[ann_key],
                            "difference": difference,
                            "percentage_diff": (
                                (difference / ann_rent[ann_key] * 100)
                                if ann_rent[ann_key] != 0
                                else 0
                            ),
                        }

            # Generar análisis automático
            if comparison["differences"]:
                avg_diff = sum(
                    d["difference"] for d in comparison["differences"].values()
                ) / len(comparison["differences"])
                comparison["analysis"].append(
                    f"Diferencia promedio entre acumulada y anualizada: {avg_diff:.2f}%"
                )

                if avg_diff > 0:
                    comparison["analysis"].append(
                        "La rentabilidad acumulada es generalmente mayor que la anualizada"
                    )
                else:
                    comparison["analysis"].append(
                        "La rentabilidad anualizada es generalmente mayor que la acumulada"
                    )

        return comparison

    def get_rentability_by_date_range(
        self,
        afp_names: List[str],
        fund_types: List[int],
        start_period: str,
        end_period: str,
        rentability_type: str = "both",
    ) -> Dict:
        """
        ✅ NUEVO: Obtiene rentabilidad para RANGO COMPLETO de períodos
        Ejemplo: de mayo 2021 a mayo 2025
        """
        try:
            result = {
                "query_info": {
                    "afp_names": afp_names,
                    "fund_types": fund_types,
                    "start_period": start_period,
                    "end_period": end_period,
                    "rentability_type": rentability_type,
                },
                "data_by_fund_type": {},
                "periods_found": [],
                "periods_missing": [],
                # nuevo cambio
                "cache_source": "enhanced_range_query",
            }

            # Generar lista de períodos en el rango
            target_periods = self._generate_period_range(start_period, end_period)
            print(f"🔍 Períodos objetivo generados: {target_periods}")

            for fund_type in fund_types:
                fund_data = {
                    "fund_type": fund_type,
                    "afp_data": {},
                    "periods_available": [],
                    "periods_with_data": [],
                    "full_range_data": {},
                }

                # Obtener períodos disponibles para este tipo de fondo
                available_periods = self.get_available_periods(fund_type)

                # Filtrar períodos en el rango solicitado
                relevant_periods = []
                for period in available_periods:
                    if start_period <= period <= end_period:
                        relevant_periods.append(period)

                # ✅ MEJORADO: Ordenar períodos cronológicamente
                relevant_periods.sort()
                fund_data["periods_available"] = relevant_periods
                print(
                    f"🎯 Períodos relevantes para fondo {fund_type}: {relevant_periods}"
                )

                if not relevant_periods:
                    fund_data["error"] = (
                        f"No hay datos para fondo tipo {fund_type} en el rango {start_period} - {end_period}"
                    )
                    result["data_by_fund_type"][f"fund_{fund_type}"] = fund_data
                    continue

                # Para cada AFP solicitada
                for afp_name in afp_names:
                    afp_periods_data = {}
                    afp_successful_periods = []

                    # Para cada período en el rango
                    for period in relevant_periods:
                        try:
                            # Usar método básico para obtener datos de cada período
                            period_data = self.get_rentability_by_afp(
                                afp_name, fund_type, period
                            )

                            if "error" not in period_data:
                                # ✅ MEJORADO: Estructura los datos por período
                                rentability_data = period_data.get(
                                    "rentability_data", {}
                                )

                                # Crear entrada para este período
                                afp_periods_data[period] = {
                                    "period": period,
                                    "afp_name": afp_name,
                                    "fund_type": fund_type,
                                    "data": rentability_data,
                                    "source": period_data.get("data_source", "unknown"),
                                }

                                afp_successful_periods.append(period)

                                print(
                                    f"✅ {afp_name} - {period}: {len(rentability_data)} datos obtenidos"
                                )
                            else:
                                print(
                                    f"⚠️  {afp_name} - {period}: {period_data.get('error', 'Sin datos')}"
                                )

                        except Exception as e:
                            print(
                                f"❌ Error obteniendo {afp_name} - {period}: {str(e)}"
                            )

                    # ✅ MEJORADO: Solo agregar AFP si tiene datos
                    if afp_periods_data:
                        fund_data["afp_data"][afp_name] = afp_periods_data

                        # Actualizar períodos con datos para este fondo
                        for period in afp_successful_periods:
                            if period not in fund_data["periods_with_data"]:
                                fund_data["periods_with_data"].append(period)

                # ✅ MEJORADO: Ordenar períodos con datos
                fund_data["periods_with_data"].sort()

                print(
                    f"📊 Fondo {fund_type} completado: {len(fund_data['afp_data'])} AFPs, {len(fund_data['periods_with_data'])} períodos"
                )

                result["data_by_fund_type"][f"fund_{fund_type}"] = fund_data

            # Consolidar períodos encontrados y faltantes
            all_periods_found = set()
            for fund_data in result["data_by_fund_type"].values():
                if "periods_with_data" in fund_data:
                    all_periods_found.update(fund_data["periods_with_data"])

            result["periods_found"] = sorted(list(all_periods_found))
            result["periods_missing"] = [
                p for p in target_periods if p not in all_periods_found
            ]

            # ✅ MEJORADO: Estadísticas de éxito
            total_expected = len(target_periods) * len(afp_names) * len(fund_types)
            total_found = sum(
                len(fund_data.get("afp_data", {}))
                * len(fund_data.get("periods_with_data", []))
                for fund_data in result["data_by_fund_type"].values()
            )

            result["success_stats"] = {
                "total_expected_combinations": total_expected,
                "total_found_combinations": total_found,
                "success_rate": (
                    f"{(total_found/total_expected*100):.1f}%"
                    if total_expected > 0
                    else "0%"
                ),
                "periods_found_count": len(result["periods_found"]),
                "periods_missing_count": len(result["periods_missing"]),
            }

            print(f"🎯 RESUMEN FINAL:")
            print(f"   • Períodos encontrados: {len(result['periods_found'])}")
            print(f"   • Períodos faltantes: {len(result['periods_missing'])}")
            print(f"   • Tasa de éxito: {result['success_stats']['success_rate']}")

            return result

        except Exception as e:
            print(f"❌ Error en get_rentability_by_date_range_FIXED: {str(e)}")
            return {
                "error": f"Error obteniendo rango de períodos: {str(e)}",
                "query_info": {
                    "afp_names": afp_names,
                    "fund_types": fund_types,
                    "start_period": start_period,
                    "end_period": end_period,
                },
            }

    def _generate_period_range(self, start_period: str, end_period: str) -> List[str]:
        """Genera lista de períodos entre start y end (formato YYYY-MM)"""
        try:
            # Si el formato no es YYYY-MM, intentar convertir
            if len(start_period) == 4:  # Solo año
                start_period = f"{start_period}-01"
            if len(end_period) == 4:  # Solo año
                end_period = f"{end_period}-12"

            # Parsear fechas
            start_parts = start_period.split("-")
            end_parts = end_period.split("-")

            start_year, start_month = int(start_parts[0]), int(start_parts[1])
            end_year, end_month = int(end_parts[0]), int(end_parts[1])

            periods = []
            current_year = start_year
            current_month = start_month

            # ✅ MEJORADO: Generar todos los meses en el rango
            while (current_year < end_year) or (
                current_year == end_year and current_month <= end_month
            ):
                period_str = f"{current_year}-{current_month:02d}"
                periods.append(period_str)

                # Avanzar al siguiente mes
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1

            print(f"📅 Períodos generados ({len(periods)}): {periods}")
            return periods

        except Exception as e:
            print(f"❌ Error generando períodos: {str(e)}")
            # Fallback: usar períodos disponibles en el cache
            available_periods = self.get_available_periods()
            filtered = [p for p in available_periods if start_period <= p <= end_period]
            print(f"🔄 Fallback: {len(filtered)} períodos del cache")
            return filtered


# Instancia global del gestor de datos
data_manager = None


def get_data_manager() -> RentabilityDataManager:
    """Obtiene instancia singleton del gestor de datos"""
    global data_manager
    if data_manager is None:
        data_manager = RentabilityDataManager()
    return data_manager


def get_production_data_manager():
    """Factory para elegir el tipo de data manager"""
    import os

    # Variable de entorno para activar el cache híbrido
    use_production_cache = os.getenv("USE_PRODUCTION_CACHE", "false").lower() == "true"

    if use_production_cache:
        try:
            from .cache.production_cache_manager import AutoUpdatingDataManager

            return AutoUpdatingDataManager()
        except ImportError:
            # Fallback al sistema actual
            return get_data_manager()
    else:
        return get_data_manager()
