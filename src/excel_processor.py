import pandas as pd
import json
import re
import os
from typing import Dict, List, Any, Optional
from azure.storage.blob import BlobServiceClient
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AZURE_BLOB_CONFIG
import logging


class ExcelProcessor:
    """Procesador de archivos Excel de rentabilidad de fondos de pensiones - ENHANCED VERSION"""

    def __init__(self):
        # Solo inicializar blob_client si tenemos credenciales
        connection_string = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING")
        if connection_string:
            try:
                self.blob_client = BlobServiceClient.from_connection_string(
                    conn_str=connection_string
                )
            except Exception as e:
                logging.warning(f"Error inicializando blob client: {e}")
                self.blob_client = None
        else:
            self.blob_client = None

    def process_excel_stream(self, blob_stream, blob_name: str) -> Dict[str, Any]:
        """Procesa un archivo Excel de rentabilidad desde un stream de Azure Blob"""

        try:
            # Leer el archivo Excel desde el stream usando BytesID
            from io import BytesIO

            blob_data = blob_stream.readall()
            df = pd.read_excel(BytesIO(blob_data), header=None)

            result = {
                "filename": blob_name,
                "status": "success",
                "metadata": {},
                "rentability_data": {},
            }

            # ✅ ENHANCED: Extraer datos de rentabilidad con diferenciación acumulada/anualizada
            rentability_data = self._extract_rentability_data_enhanced(df, blob_name)
            result["rentability_data"] = rentability_data

            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(blob_name)

            # Guardar en Azure SQL Database
            self._save_to_sql_enhanced(rentability_data)

            # Indexar en Azure AI Search
            self._index_in_search_enhanced(rentability_data)

            return result

        except Exception as e:
            logging.error(f"Error procesando Excel desde blob storage: {str(e)}")
            return {"filename": blob_name, "status": "error", "error": str(e)}

    def _is_valid_numeric_value(self, value) -> bool:
        """Verifica si un valor es válido para conversión numérica"""
        if pd.isna(value):
            return False

        value_str = str(value).strip().upper()

        # ✅ FILTRAR VALORES NO VÁLIDOS
        invalid_values = {
            "N.A.",
            "NA",
            "N/A",
            "NAN",
            "NONE",
            "NULL",
            "",
            "-",
            "--",
            "...",
            "N.D.",
            "ND",
            "NO DISPONIBLE",
            "NO APLICA",
            "#N/A",
            "#VALUE!",
            "#REF!",
        }

        if value_str in invalid_values:
            return False

        # Verificar si contiene solo caracteres válidos para números
        # Permitir: dígitos, punto, coma, signo negativo, espacios
        if not re.match(r"^[-+]?[\d\s,\.]+$", value_str):
            return False

        return True

    def _convert_to_float(self, value) -> Optional[float]:
        """Convierte un valor a float manejando diferentes formatos"""
        try:
            if isinstance(value, (int, float)):
                return float(value)

            value_str = str(value).strip()

            # Manejar separadores decimales
            # Convertir coma decimal a punto (formato europeo)
            if "," in value_str and "." not in value_str:
                value_str = value_str.replace(",", ".")
            elif "," in value_str and "." in value_str:
                # Si tiene ambos, asumir que coma es separador de miles
                value_str = value_str.replace(",", "")

            # Eliminar espacios
            value_str = value_str.replace(" ", "")

            # Convertir a float
            result = float(value_str)

            # Validar que el resultado sea razonable para rentabilidad
            # Rentabilidad típica está entre -100% y +100% (o más en casos extremos)
            if -1000 <= result <= 1000:  # Rango amplio para aceptar diferentes formatos
                return result
            else:
                logging.warning(
                    f"Valor de rentabilidad fuera de rango esperado: {result}"
                )
                return None

        except (ValueError, TypeError) as e:
            logging.debug(f"Error convirtiendo '{value}' a float: {e}")
            return None

    def _extract_rentability_data_enhanced(
        self, df: pd.DataFrame, filename: str
    ) -> Dict[str, Any]:
        """
        ✅ ENHANCED: Extrae datos de rentabilidad diferenciando ACUMULADA vs ANUALIZADA
        Mantiene retrocompatibilidad total con el sistema actual
        """

        extracted = {
            "fund_type": None,
            "period": None,
            "afp_data": [],
            "data_type": "rentability_enhanced",
            "periods_available": [],
            # ✅ NUEVAS SECCIONES
            "rentability_type_info": {
                "has_accumulated": False,
                "has_annualized": False,
                "table_locations": {},
            },
        }

        try:
            # Extraer tipo de fondo del nombre del archivo
            fund_match = re.search(r"Tipo\s+(\d+)", filename)
            if fund_match:
                extracted["fund_type"] = int(fund_match.group(1))
            else:
                # Buscar patrones alternativos en el nombre del archivo
                if "FP-1219-0" in filename or "FP12190" in filename:
                    extracted["fund_type"] = 0
                elif "FP-1220-1" in filename or "FP12201" in filename:
                    extracted["fund_type"] = 1
                elif "FP-1360" in filename or "FP1360" in filename:
                    extracted["fund_type"] = 2
                elif "FP-1220-2" in filename or "FP12202" in filename:
                    extracted["fund_type"] = 3

            # Extraer período del nombre del archivo
            period_match = re.search(r"(\w{2})(\d{4})", filename)
            if period_match:
                month_abbr = period_match.group(1)
                year = period_match.group(2)
                month_map = {
                    "en": "01",
                    "fe": "02",
                    "ma": "03",
                    "ab": "04",
                    "my": "05",
                    "jn": "06",
                    "jl": "07",
                    "ag": "08",
                    "se": "09",
                    "oc": "10",
                    "no": "11",
                    "di": "12",
                }
                extracted["period"] = f"{year}-{month_map.get(month_abbr, '01')}"

            # ✅ ENHANCED: Detectar ubicación de las 2 tablas (ACUMULADA y ANUALIZADA)
            table_locations = self._detect_table_locations(df)
            extracted["rentability_type_info"]["table_locations"] = table_locations

            acc_data = []
            ann_data = []

            # ✅ Procesar TABLA ACUMULADA (superior)
            if table_locations.get("accumulated"):
                acc_data = self._extract_table_data(
                    df, table_locations["accumulated"], "accumulated"
                )
                if acc_data:
                    extracted["rentability_type_info"]["has_accumulated"] = True

            # ✅ Procesar TABLA ANUALIZADA (inferior)
            if table_locations.get("annualized"):
                ann_data = self._extract_table_data(
                    df, table_locations["annualized"], "annualized"
                )
                if ann_data:
                    extracted["rentability_type_info"]["has_annualized"] = True

            # ✅ COMBINAR datos de ambas tablas por AFP
            extracted["afp_data"] = self._combine_accumulated_and_annualized_data(
                acc_data, ann_data
            )

            # ✅ BACKWARD COMPATIBILITY: Mantener estructura original para compatibilidad
            if not extracted["afp_data"]:
                # Fallback al método original si las nuevas tablas no funcionan
                logging.warning(f"Usando método original para {filename}")
                return self._extract_rentability_data_original(df, filename)

            logging.info(
                f"Extraídos datos ENHANCED para {len(extracted['afp_data'])} AFPs del archivo {filename}"
            )
            return extracted

        except Exception as e:
            logging.error(f"Error extrayendo datos ENHANCED: {str(e)}")
            # ✅ FALLBACK: Si falla, usar método original
            logging.warning("Fallback al método original...")
            return self._extract_rentability_data_original(df, filename)

    def _detect_table_locations(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        ✅ Detecta automáticamente la ubicación de las tablas ACUMULADA y ANUALIZADA
        """
        table_locations = {}

        # Buscar indicadores de tablas en el Excel
        for i in range(min(30, len(df))):  # Buscar en las primeras 30 filas
            for j in range(min(30, df.shape[1])):  # Primeras 10 columnas
                cell_value = str(df.iloc[i, j]).upper().strip()

                # Detectar tabla ACUMULADA
                if any(
                    keyword in cell_value
                    for keyword in [
                        "ACUMULAD",
                        "ACUMULA",
                        "ACCUMULATED",
                        "Acumulada",
                        "ACUMULADA",
                    ]
                ):
                    table_locations["accumulated"] = {
                        "start_row": i,
                        "header_row": i + 2,  # Usualmente 2 filas después
                        "data_start_row": i + 5,  # AFPs empiezan 5 filas después
                        "type": "accumulated",
                    }
                    logging.info(f"Tabla ACUMULADA detectada en fila {i}")

                # Detectar tabla ANUALIZADA
                elif any(
                    keyword in cell_value
                    for keyword in [
                        "ANUALIZ",
                        "ANUALI",
                        "ANNUALIZED",
                        "ANUAL",
                        "ANUALIZADA",
                        "Anualizada",
                    ]
                ):
                    table_locations["annualized"] = {
                        "start_row": i,
                        "header_row": i + 3,
                        "data_start_row": i + 6,
                        "type": "annualized",
                    }
                    logging.info(f"Tabla ANUALIZADA detectada en fila {i}")

        # Si no se detectan automáticamente, usar ubicaciones predeterminadas
        if not table_locations:
            logging.warning(
                "🔍 No se detectaron tablas automáticamente, usando ubicaciones estimadas"
            )
            # Buscar la primera tabla (usualmente acumulada)
            first_table_found = False
            for i in range(5, 20):  # Buscar entre filas 5-20
                row_content = " ".join(
                    [str(df.iloc[i, j]) for j in range(min(10, df.shape[1]))]
                )
                if "AFP" in row_content.upper() and any(
                    char.isdigit() for char in row_content
                ):
                    table_locations["accumulated"] = {
                        "start_row": i - 3,
                        "header_row": i - 1,
                        "data_start_row": i,
                        "type": "accumulated",
                    }
                    first_table_found = True
                    logging.info(f"✅ Tabla ACUMULADA estimada en fila {i}")
                    break

            # Buscar la segunda tabla (usualmente anualizada) después de la primera
            if first_table_found:
                search_start = table_locations["accumulated"]["data_start_row"] + 10
                for i in range(search_start, min(search_start + 30, len(df))):
                    row_content = " ".join(
                        [str(df.iloc[i, j]) for j in range(min(10, df.shape[1]))]
                    )
                    if "AFP" in row_content.upper() and any(
                        char.isdigit() for char in row_content
                    ):
                        table_locations["annualized"] = {
                            "start_row": i - 3,
                            "header_row": i - 1,
                            "data_start_row": i,
                            "type": "annualized",
                        }
                        logging.info(f"✅ Tabla ANUALIZADA estimada en fila {i}")
                        break

        return table_locations

    def _extract_table_data(
        self, df: pd.DataFrame, table_info: Dict, table_type: str
    ) -> List[Dict]:
        """
        ✅ Extrae datos de una tabla específica (ACUMULADA o ANUALIZADA)
        """
        try:
            start_row = table_info["data_start_row"]
            header_row = table_info["header_row"]
            afp_data = []

            # Extraer períodos disponibles de las columnas (header_row)
            periods = []
            period_columns = []

            # Buscar períodos en múltiples filas de header
            for header_offset in [0, -1, -2, 1]:  # Verificar filas adyacentes
                check_row = header_row + header_offset
                if 0 <= check_row < len(df):
                    for col in range(1, min(30, df.shape[1])):
                        cell_value = str(df.iloc[check_row, col]).strip()

                        # Detectar patrones de período
                        if (
                            (
                                "/" in cell_value
                                and any(char.isdigit() for char in cell_value)
                            )
                            or ("20" in cell_value and len(cell_value) >= 4)
                            or any(
                                year in cell_value
                                for year in [
                                    "2020",
                                    "2021",
                                    "2022",
                                    "2023",
                                    "2024",
                                    "2025",
                                ]
                            )
                        ):

                            if cell_value not in periods:
                                periods.append(cell_value)
                                period_columns.append(col)
                                logging.info(
                                    f"📅 Período encontrado: {cell_value} en columna {col}"
                                )

            if not periods:
                # Fallback: usar estructura estándar
                logging.warning(
                    f"⚠️ No se encontraron períodos en headers, usando estructura estándar"
                )
                periods = ["1 año", "2 años", "3 años", "5 años", "9 años"]
                period_columns = [1, 3, 5, 7, 9]  # Columnas estándar

            # ✅ FIXED: Extraer datos de AFPs con mejor detección
            afp_names = ["HABITAT", "INTEGRA", "PRIMA", "PROFUTURO"]

            # Buscar AFPs en un rango más amplio
            for idx in range(start_row, min(start_row + 15, len(df))):
                if idx >= len(df):
                    break

                row_content = str(df.iloc[idx, 0]).upper().strip()

                for afp in afp_names:
                    if afp in row_content:
                        logging.info(f"🏦 Procesando AFP {afp} en fila {idx}")

                        afp_rentability = {
                            "afp_name": afp.title(),
                            "table_type": table_type,
                            "rentability_data": {},
                        }

                        # ✅ FIXED: Extraer datos con múltiples patrones de columnas
                        for i, period in enumerate(periods):
                            if i < len(period_columns):
                                base_col = period_columns[i]
                            else:
                                base_col = 1 + (i * 2)  # Fallback a patrón estándar

                            # Extraer rentabilidad nominal y real
                            for col_offset, rent_type in [(0, "nominal"), (1, "real")]:
                                col_idx = base_col + col_offset

                                if col_idx < df.shape[1]:
                                    cell_value = df.iloc[idx, col_idx]

                                    if self._is_valid_numeric_value(cell_value):
                                        numeric_value = self._convert_to_float(
                                            cell_value
                                        )

                                        if numeric_value is not None:
                                            # ✅ FIXED: Crear claves mejoradas
                                            key_with_type = (
                                                f"period_{i+1}_{table_type}_{rent_type}"
                                            )
                                            key_with_period = (
                                                f"{period}_{table_type}_{rent_type}"
                                            )

                                            afp_rentability["rentability_data"][
                                                key_with_type
                                            ] = numeric_value
                                            afp_rentability["rentability_data"][
                                                key_with_period
                                            ] = numeric_value

                                            logging.info(
                                                f"📊 {afp} {period} {rent_type} ({table_type}): {numeric_value:.2f}%"
                                            )

                        if afp_rentability["rentability_data"]:
                            afp_data.append(afp_rentability)
                        break

            logging.info(
                f"✅ Tabla {table_type} procesada: {len(afp_data)} AFPs extraídas"
            )
            return afp_data

        except Exception as e:
            logging.error(f"❌ Error extrayendo tabla {table_type}: {str(e)}")
            return []

    def _combine_accumulated_and_annualized_data(
        self, acc_data: List[Dict], ann_data: List[Dict]
    ) -> List[Dict]:
        """
        ✅ FIXED: Combina datos de rentabilidad ACUMULADA y ANUALIZADA por AFP
        Mejorado para garantizar que ambos tipos se incluyan correctamente
        """
        combined_data = []
        afp_names = ["Habitat", "Integra", "Prima", "Profuturo"]

        for afp in afp_names:
            # Buscar datos de esta AFP en ambas tablas
            acc_afp_data = next(
                (item for item in acc_data if item["afp_name"].upper() == afp.upper()),
                None,
            )
            ann_afp_data = next(
                (item for item in ann_data if item["afp_name"].upper() == afp.upper()),
                None,
            )

            if acc_afp_data or ann_afp_data:
                combined_afp = {
                    "afp_name": afp,
                    "rentability_data": {},
                    "data_sources": [],
                }

                # ✅ FIXED: Agregar datos ACUMULADOS
                if acc_afp_data:
                    combined_afp["rentability_data"].update(
                        acc_afp_data["rentability_data"]
                    )
                    combined_afp["data_sources"].append("accumulated")

                    # ✅ BACKWARD COMPATIBILITY: Mantener claves originales (sin especificar tipo)
                    for key, value in acc_afp_data["rentability_data"].items():
                        if "accumulated" in key:
                            # Crear clave compatible con sistema original
                            original_key = key.replace("_accumulated", "")
                            combined_afp["rentability_data"][original_key] = value

                    logging.info(
                        f"✅ {afp}: {len(acc_afp_data['rentability_data'])} datos acumulados agregados"
                    )

                # ✅ FIXED: Agregar datos ANUALIZADOS
                if ann_afp_data:
                    combined_afp["rentability_data"].update(
                        ann_afp_data["rentability_data"]
                    )
                    combined_afp["data_sources"].append("annualized")

                    logging.info(
                        f"✅ {afp}: {len(ann_afp_data['rentability_data'])} datos anualizados agregados"
                    )
                else:
                    logging.warning(f"⚠️ {afp}: No se encontraron datos anualizados")

                combined_data.append(combined_afp)

                # Log resumen por AFP
                total_keys = len(combined_afp["rentability_data"])
                acc_keys = len(
                    [
                        k
                        for k in combined_afp["rentability_data"].keys()
                        if "accumulated" in k
                    ]
                )
                ann_keys = len(
                    [
                        k
                        for k in combined_afp["rentability_data"].keys()
                        if "annualized" in k
                    ]
                )

                logging.info(
                    f"📊 {afp} RESUMEN: {total_keys} total, {acc_keys} acumulados, {ann_keys} anualizados"
                )

        return combined_data

    def _extract_rentability_data_original(
        self, df: pd.DataFrame, filename: str
    ) -> Dict[str, Any]:
        """
        ✅ MÉTODO ORIGINAL - Mantenido para backward compatibility
        """
        extracted = {
            "fund_type": None,
            "period": None,
            "afp_data": [],
            "data_type": "rentability_enhanced_fixed",
            "periods_available": [],
            "rentability_type_info": {
                "has_accumulated": False,
                "has_annualized": False,
                "table_locations": {},
            },
        }

        try:
            # Extraer metadatos del archivo (sin cambios)
            fund_match = re.search(r"Tipo\s+(\d+)", filename)
            if fund_match:
                extracted["fund_type"] = int(fund_match.group(1))
            else:
                # Patrones de archivos SPP
                if "FP-1219-0" in filename or "FP12190" in filename:
                    extracted["fund_type"] = 0
                elif "FP-1220-1" in filename or "FP12201" in filename:
                    extracted["fund_type"] = 1
                elif "FP-1360" in filename or "FP1360" in filename:
                    extracted["fund_type"] = 2
                elif "FP-1220-2" in filename or "FP12202" in filename:
                    extracted["fund_type"] = 3

            # Extraer período del archivo
            period_match = re.search(r"(\w{2})(\d{4})", filename)
            if period_match:
                month_abbr = period_match.group(1)
                year = period_match.group(2)
                month_map = {
                    "en": "01",
                    "fe": "02",
                    "ma": "03",
                    "ab": "04",
                    "my": "05",
                    "jn": "06",
                    "jl": "07",
                    "ag": "08",
                    "se": "09",
                    "oc": "10",
                    "no": "11",
                    "di": "12",
                }
                extracted["period"] = f"{year}-{month_map.get(month_abbr, '01')}"

            logging.info(
                f"🔍 Procesando archivo: {filename} (Fondo: {extracted['fund_type']}, Período: {extracted['period']})"
            )

            # ✅ FIXED: Detectar ubicación de las 2 tablas con método mejorado
            table_locations = self._detect_table_locations(df)
            extracted["rentability_type_info"]["table_locations"] = table_locations

            acc_data = []
            ann_data = []

            # ✅ FIXED: Procesar TABLA ACUMULADA
            if table_locations.get("accumulated"):
                logging.info("🔄 Procesando tabla ACUMULADA...")
                acc_data = self._extract_table_data(
                    df, table_locations["accumulated"], "accumulated"
                )
                if acc_data:
                    extracted["rentability_type_info"]["has_accumulated"] = True
                    logging.info(f"✅ Tabla ACUMULADA: {len(acc_data)} AFPs procesadas")
                else:
                    logging.warning("⚠️ Tabla ACUMULADA: No se extrajeron datos")

            # ✅ FIXED: Procesar TABLA ANUALIZADA
            if table_locations.get("annualized"):
                logging.info("🔄 Procesando tabla ANUALIZADA...")
                ann_data = self._extract_table_data(
                    df, table_locations["annualized"], "annualized"
                )
                if ann_data:
                    extracted["rentability_type_info"]["has_annualized"] = True
                    logging.info(
                        f"✅ Tabla ANUALIZADA: {len(ann_data)} AFPs procesadas"
                    )
                else:
                    logging.warning("⚠️ Tabla ANUALIZADA: No se extrajeron datos")

            # ✅ FIXED: Combinar datos con método mejorado
            extracted["afp_data"] = self._combine_accumulated_and_annualized_data(
                acc_data, ann_data
            )

            # Verificar resultado final
            if extracted["afp_data"]:
                logging.info(
                    f"🎉 ÉXITO: {len(extracted['afp_data'])} AFPs procesadas con datos enhanced"
                )

                # Log estadísticas detalladas
                for afp_data in extracted["afp_data"]:
                    afp_name = afp_data["afp_name"]
                    sources = afp_data.get("data_sources", [])
                    total_data = len(afp_data["rentability_data"])
                    logging.info(
                        f"📊 {afp_name}: {total_data} datos, fuentes: {sources}"
                    )
            else:
                logging.warning(
                    "⚠️ No se extrajeron datos enhanced, usando método fallback"
                )
                return self._extract_rentability_data_original(df, filename)

            return extracted

        except Exception as e:
            logging.error(f"❌ Error en extracción enhanced fixed: {str(e)}")
            import traceback

            logging.error(f"💥 Traceback: {traceback.format_exc()}")

            # Fallback al método original
            logging.warning("🔄 Usando método original como fallback...")
            return self._extract_rentability_data_original(df, filename)

    def _extract_file_metadata(self, filename: str) -> Dict[str, Any]:
        """Extrae metadatos del nombre del archivo de rentabilidad"""

        metadata = {
            "filename": filename,
            "file_type": "excel",
            "source": "SPP_rentability_report",
            "document_type": "rentability_report",
        }

        # Extraer tipo de fondo
        fund_match = re.search(r"Tipo\s+(\d+)", filename)
        if fund_match:
            metadata["fund_type"] = int(fund_match.group(1))

        # Extraer período del nombre del archivo (más dinámico)
        period_match = re.search(r"(\w{2})(\d{4})", filename)
        if period_match:
            month_abbr = period_match.group(1)
            year = int(period_match.group(2))
            month_map = {
                "en": "01",
                "fe": "02",
                "ma": "03",
                "ab": "04",
                "my": "05",
                "jn": "06",
                "jl": "07",
                "ag": "08",
                "se": "09",
                "oc": "10",
                "no": "11",
                "di": "12",
            }
            metadata["period"] = f"{year}-{month_map.get(month_abbr, '01')}"
            metadata["year"] = year
            metadata["month"] = month_map.get(month_abbr, "01")

        return metadata

    def process_local_file(self, file_path: str) -> Dict[str, Any]:
        """Procesa un archivo Excel local para testing"""
        try:
            df = pd.read_excel(file_path, header=None)

            result = {
                "filename": file_path,
                "status": "success",
                "metadata": {},
                "rentability_data": {},
            }

            # ✅ ENHANCED: Usar método mejorado
            rentability_data = self._extract_rentability_data_enhanced(df, file_path)
            result["rentability_data"] = rentability_data

            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(file_path)

            return result

        except Exception as e:
            logging.error(f"Error procesando archivo local: {str(e)}")
            return {"filename": file_path, "status": "error", "error": str(e)}

    def _save_to_sql_enhanced(self, data: Dict):
        """
        ✅ ENHANCED: Guarda datos de rentabilidad en Azure SQL Database incluyendo tipo de rentabilidad
        """
        try:
            import pyodbc
            from config import AZURE_SQL_CONFIG

            connection_string = AZURE_SQL_CONFIG.get("AZURE_SQL_CONNECTION_STRING")
            if not connection_string:
                logging.warning("Azure SQL connection string no configurado")
                return

            # Crear conexión
            conn = pyodbc.connect(connection_string + "Database=sbsbdsql;")
            cursor = conn.cursor()

            # ✅ ENHANCED: Crear tabla con nuevas columnas
            cursor.execute(
                """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rentability_data' AND xtype='U')
                CREATE TABLE rentability_data (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    fund_type INT,
                    period VARCHAR(10),
                    afp_name VARCHAR(50),
                    period_key VARCHAR(50),
                    rentability_value FLOAT,
                    rentability_type VARCHAR(10), -- 'nominal' or 'real'
                    calculation_type VARCHAR(20), -- 'acumulada' or 'anualizada', 'accumulated' or 'annualized'
                    created_at DATETIME DEFAULT GETDATE()
                )
            """
            )

            # ✅ ENHANCED: Insertar datos con tipo de cálculo
            fund_type = data.get("fund_type")
            period = data.get("period")

            for afp_data in data.get("afp_data", []):
                afp_name = afp_data["afp_name"]
                for key, value in afp_data["rentability_data"].items():
                    # Determinar tipo de rentabilidad y cálculo
                    rentability_type = "nominal" if "nominal" in key else "real"

                    if "accumulated" in key:
                        calculation_type = "accumulated"
                    elif "annualized" in key:
                        calculation_type = "annualized"
                    else:
                        calculation_type = "legacy"  # Para backward compatibility

                    cursor.execute(
                        """
                        INSERT INTO rentability_data
                        (fund_type, period, afp_name, period_key, rentability_value, rentability_type, calculation_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            fund_type,
                            period,
                            afp_name,
                            key,
                            value,
                            rentability_type,
                            calculation_type,
                        ),
                    )

            conn.commit()
            conn.close()
            logging.info(
                f"Datos ENHANCED guardados en SQL Database para fondo tipo {fund_type}"
            )

        except Exception as e:
            logging.error(f"Error guardando en SQL ENHANCED: {str(e)}")

    def _index_in_search_enhanced(self, data: Dict):
        """
        ✅ ENHANCED: Indexa datos de rentabilidad en Azure AI Search con tipos diferenciados
        """
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            from config import AZURE_AISEARCH_API_KEY
            from datetime import datetime
            import uuid

            endpoint = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_ENDPOINT")
            api_key = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_API_KEY")
            index_name = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_INDEX_NAME")

            if not all([endpoint, api_key, index_name]):
                logging.warning("Azure AI Search no configurado completamente")
                return

            # Crear cliente de búsqueda
            search_client = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(api_key),
            )

            # ✅ ENHANCED: Preparar documentos con información de tipos
            documents = []
            fund_type = data.get("fund_type")
            period = data.get("period")
            rentability_info = data.get("rentability_type_info", {})

            for afp_data in data.get("afp_data", []):
                afp_name = afp_data["afp_name"]

                # Documento con información completa
                doc = {
                    "id": str(uuid.uuid4()),
                    "fundType": fund_type,
                    "period": period,
                    "afpName": afp_name,
                    "content": f"Rentabilidad del fondo tipo {fund_type} de {afp_name} para el período {period}. Incluye datos acumulados y anualizados.",
                    "rentabilityData": json.dumps(afp_data["rentability_data"]),
                    "documentType": "rentability_report_enhanced",
                    "hasAccumulated": rentability_info.get("has_accumulated", False),
                    "hasAnnualized": rentability_info.get("has_annualized", False),
                    "dataSources": afp_data.get("data_sources", []),
                    "createdAt": datetime.now().isoformat() + "Z",
                }
                documents.append(doc)

            # Subir documentos
            if documents:
                search_client.upload_documents(documents)
                logging.info(
                    f"Indexados {len(documents)} documentos ENHANCED en AI Search"
                )

        except Exception as e:
            logging.error(f"Error indexando en AI Search ENHANCED: {str(e)}")
            # Agregar más detalles del error para debugging
            if hasattr(e, "error") and hasattr(e.error, "message"):
                logging.error(f"Detalles del error: {e.error.message}")

    # ✅ BACKWARD COMPATIBILITY: Mantener método original disponible
    def _extract_rentability_data(
        self, df: pd.DataFrame, filename: str
    ) -> Dict[str, Any]:
        """Método original mantenido para compatibilidad"""
        return self._extract_rentability_data_original(df, filename)

    def _save_to_sql(self, data: Dict):
        """Método original mantenido para compatibilidad"""
        self._save_to_sql_enhanced(data)

    def _index_in_search(self, data: Dict):
        """Método original mantenido para compatibilidad"""
        self._index_in_search_enhanced(data)
