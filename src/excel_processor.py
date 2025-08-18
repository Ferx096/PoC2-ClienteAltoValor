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
    """Procesador de archivos Excel de rentabilidad de fondos de pensiones"""

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

            # Extraer datos de rentabilidad
            rentability_data = self._extract_rentability_data(df, blob_name)
            result["rentability_data"] = rentability_data

            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(blob_name)

            # TODO: Guardar en Azure SQL Database
            self._save_to_sql(rentability_data)

            # TODO: Indexar en Azure AI Search
            self._index_in_search(rentability_data)

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

    def _extract_rentability_data(
        self, df: pd.DataFrame, filename: str
    ) -> Dict[str, Any]:
        """Extrae datos de rentabilidad de fondos de pensiones"""

        extracted = {
            "fund_type": None,
            "period": None,
            "afp_data": [],
            "data_type": "rentability",
            "periods_available": [],
        }

        try:
            # Extraer tipo de fondo del nombre del archivo
            fund_match = re.search(r"Tipo\s+(\d+)", filename)
            if fund_match:
                extracted["fund_type"] = int(fund_match.group(1))
            else:
                # Buscar patrones alternativos en el nombre del archivo
                if "FP-1219-0" in filename:
                    extracted["fund_type"] = 0
                elif "FP-1220-1" in filename:
                    extracted["fund_type"] = 1
                elif "FP-1360" in filename:
                    extracted["fund_type"] = 2
                elif "FP-1220-2" in filename:
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

            # Extraer períodos disponibles de las columnas (fila 4 contiene los períodos)
            periods = []
            period_labels = []

            # Buscar en la fila 4 los períodos - estructura real del Excel
            for col in range(1, df.shape[1], 2):  # Cada 2 columnas (nominal y real)
                if col < df.shape[1]:
                    period_cell = str(df.iloc[4, col])
                    if "/" in period_cell and any(
                        char.isdigit() for char in period_cell
                    ):
                        periods.append(period_cell.strip())

                        # Extraer la etiqueta del período de la fila 5
                        if col < df.shape[1]:
                            label_cell = str(df.iloc[5, col])
                            if "año" in label_cell:
                                period_labels.append(label_cell.strip())

            extracted["periods_available"] = periods
            extracted["period_labels"] = period_labels

            # Extraer datos de AFPs - AMBAS SECCIONES: ACUMULADA Y ANUALIZADA
            afp_names = ["Habitat", "Integra", "Prima", "Profuturo"]
            
            # Buscar secciones de rentabilidad acumulada y anualizada
            accumulated_section_start = None
            annualized_section_start = None
            
            for row_idx in range(df.shape[0]):
                cell_value = str(df.iloc[row_idx, 0]).lower()
                if "rentabilidad" in cell_value and "acumulada" in cell_value:
                    accumulated_section_start = row_idx
                elif "rentabilidad" in cell_value and "anualizada" in cell_value:
                    annualized_section_start = row_idx
            
            # Procesar sección ACUMULADA (filas 7-10 aproximadamente)
            if accumulated_section_start is not None:
                for idx in range(accumulated_section_start + 6, min(accumulated_section_start + 10, len(df))):
                    afp_name_cell = str(df.iloc[idx, 0])

                    for afp in afp_names:
                        if afp.lower() in afp_name_cell.lower():
                            # Buscar si ya existe esta AFP en los datos extraídos
                            afp_data = None
                            for existing_afp in extracted["afp_data"]:
                                if existing_afp["afp_name"] == afp:
                                    afp_data = existing_afp
                                    break
                            
                            if afp_data is None:
                                afp_data = {"afp_name": afp, "rentability_data": {}}
                                extracted["afp_data"].append(afp_data)

                            # Extraer datos de rentabilidad ACUMULADA por período
                            col_idx = 1
                            for i, period in enumerate(periods):
                                if col_idx < df.shape[1]:
                                    # RENTABILIDAD NOMINAL ACUMULADA
                                    nominal_val = df.iloc[idx, col_idx]
                                    if self._is_valid_numeric_value(nominal_val):
                                        nominal_float = self._convert_to_float(nominal_val)
                                        if nominal_float is not None:
                                            # Guardar con claves específicas para acumulada
                                            period_key = f"period_{i+1}_accumulated_nominal"
                                            afp_data["rentability_data"][period_key] = nominal_float
                                            afp_data["rentability_data"][f"{period}_accumulated_nominal"] = nominal_float
                                            
                                            # También mantener claves originales para compatibilidad
                                            afp_data["rentability_data"][f"period_{i+1}_nominal"] = nominal_float
                                            afp_data["rentability_data"][f"{period}_nominal"] = nominal_float

                                            if i < len(period_labels):
                                                label_key = f"{period_labels[i]}_accumulated_nominal"
                                                afp_data["rentability_data"][label_key] = nominal_float
                                                # Mantener compatibilidad
                                                afp_data["rentability_data"][f"{period_labels[i]}_nominal"] = nominal_float

                                    # RENTABILIDAD REAL ACUMULADA
                                    if col_idx + 1 < df.shape[1]:
                                        real_val = df.iloc[idx, col_idx + 1]
                                        if self._is_valid_numeric_value(real_val):
                                            real_float = self._convert_to_float(real_val)
                                            if real_float is not None:
                                                # Guardar con claves específicas para acumulada
                                                period_key = f"period_{i+1}_accumulated_real"
                                                afp_data["rentability_data"][period_key] = real_float
                                                afp_data["rentability_data"][f"{period}_accumulated_real"] = real_float
                                                
                                                # También mantener claves originales para compatibilidad
                                                afp_data["rentability_data"][f"period_{i+1}_real"] = real_float
                                                afp_data["rentability_data"][f"{period}_real"] = real_float

                                                if i < len(period_labels):
                                                    label_key = f"{period_labels[i]}_accumulated_real"
                                                    afp_data["rentability_data"][label_key] = real_float
                                                    # Mantener compatibilidad
                                                    afp_data["rentability_data"][f"{period_labels[i]}_real"] = real_float

                                    col_idx += 2
                            break

            # Procesar sección ANUALIZADA (filas 21-24 aproximadamente)
            if annualized_section_start is not None:
                for idx in range(annualized_section_start + 6, min(annualized_section_start + 10, len(df))):
                    afp_name_cell = str(df.iloc[idx, 0])

                    for afp in afp_names:
                        if afp.lower() in afp_name_cell.lower():
                            # Buscar la AFP existente en los datos extraídos
                            afp_data = None
                            for existing_afp in extracted["afp_data"]:
                                if existing_afp["afp_name"] == afp:
                                    afp_data = existing_afp
                                    break
                            
                            if afp_data is None:
                                afp_data = {"afp_name": afp, "rentability_data": {}}
                                extracted["afp_data"].append(afp_data)

                            # Extraer datos de rentabilidad ANUALIZADA por período
                            col_idx = 1
                            for i, period in enumerate(periods):
                                if col_idx < df.shape[1]:
                                    # RENTABILIDAD NOMINAL ANUALIZADA
                                    nominal_val = df.iloc[idx, col_idx]
                                    if self._is_valid_numeric_value(nominal_val):
                                        nominal_float = self._convert_to_float(nominal_val)
                                        if nominal_float is not None:
                                            # Guardar con claves específicas para anualizada
                                            period_key = f"period_{i+1}_annualized_nominal"
                                            afp_data["rentability_data"][period_key] = nominal_float
                                            afp_data["rentability_data"][f"{period}_annualized_nominal"] = nominal_float

                                            if i < len(period_labels):
                                                label_key = f"{period_labels[i]}_annualized_nominal"
                                                afp_data["rentability_data"][label_key] = nominal_float

                                    # RENTABILIDAD REAL ANUALIZADA
                                    if col_idx + 1 < df.shape[1]:
                                        real_val = df.iloc[idx, col_idx + 1]
                                        if self._is_valid_numeric_value(real_val):
                                            real_float = self._convert_to_float(real_val)
                                            if real_float is not None:
                                                # Guardar con claves específicas para anualizada
                                                period_key = f"period_{i+1}_annualized_real"
                                                afp_data["rentability_data"][period_key] = real_float
                                                afp_data["rentability_data"][f"{period}_annualized_real"] = real_float

                                                if i < len(period_labels):
                                                    label_key = f"{period_labels[i]}_annualized_real"
                                                    afp_data["rentability_data"][label_key] = real_float

                                    col_idx += 2
                            break

            logging.info(
                f"Extraídos datos para {len(extracted['afp_data'])} AFPs del archivo {filename}"
            )
            return extracted

        except Exception as e:
            logging.error(f"Error extrayendo datos de rentabilidad: {str(e)}")
            return extracted

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

            # Extraer datos de rentabilidad
            rentability_data = self._extract_rentability_data(df, file_path)
            result["rentability_data"] = rentability_data

            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(file_path)

            return result

        except Exception as e:
            logging.error(f"Error procesando archivo local: {str(e)}")
            return {"filename": file_path, "status": "error", "error": str(e)}

    def _save_to_sql(self, data: Dict):
        """Guarda datos de rentabilidad en Azure SQL Database"""
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

            # Crear tabla si no existe
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
                    rentability_type VARCHAR(10),
                    created_at DATETIME DEFAULT GETDATE()
                )
            """
            )

            # Insertar datos
            fund_type = data.get("fund_type")
            period = data.get("period")

            for afp_data in data.get("afp_data", []):
                afp_name = afp_data["afp_name"]
                for key, value in afp_data["rentability_data"].items():
                    rentability_type = "nominal" if "nominal" in key else "real"

                    cursor.execute(
                        """
                        INSERT INTO rentability_data
                        (fund_type, period, afp_name, period_key, rentability_value, rentability_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (fund_type, period, afp_name, key, value, rentability_type),
                    )

            conn.commit()
            conn.close()
            logging.info(f"Datos guardados en SQL Database para fondo tipo {fund_type}")

        except Exception as e:
            logging.error(f"Error guardando en SQL: {str(e)}")

    def _index_in_search(self, data: Dict):
        """Indexa datos de rentabilidad en Azure AI Search"""
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

            # Preparar documentos para indexar
            documents = []
            fund_type = data.get("fund_type")
            period = data.get("period")

            for afp_data in data.get("afp_data", []):
                afp_name = afp_data["afp_name"]

                # ✅ DOCUMENTO CON NOMBRES EXACTOS DEL ESQUEMA (camelCase)
                doc = {
                    "id": str(uuid.uuid4()),  # ✅ id
                    "fundType": fund_type,  # ✅ fundType (camelCase)
                    "period": period,  # ✅ period
                    "afpName": afp_name,  # ✅ afpName (camelCase)
                    "content": f"Rentabilidad del fondo tipo {fund_type} de {afp_name} para el período {period}",  # ✅ content
                    "rentabilityData": json.dumps(
                        afp_data["rentability_data"]
                    ),  # ✅ rentabilityData (camelCase)
                    "documentType": "rentability_report",  # ✅ documentType (camelCase)
                    "createdAt": datetime.now().isoformat()
                    + "Z",  # ✅ createdAt (camelCase)
                }
                documents.append(doc)

            # Subir documentos
            if documents:
                search_client.upload_documents(documents)
                logging.info(f"Indexados {len(documents)} documentos en AI Search")

        except Exception as e:
            logging.error(f"Error indexando en AI Search: {str(e)}")
            # Agregar más detalles del error para debugging
            if hasattr(e, "error") and hasattr(e.error, "message"):
                logging.error(f"Detalles del error: {e.error.message}")
