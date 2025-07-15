import pandas as pd
import json
from typing import Dict, List, Any
from azure.storage.blob import BlobServiceClient
from config import AZURE_BLOB_CONFIG
import logging

class ExcelProcessor:
    """Procesador de archivos Excel del SPP para Azure Functions"""
    
    def __init__(self):
        self.blob_client = BlobServiceClient.from_connection_string(
            conn_str=AZURE_BLOB_CONFIG["AZURE_BLOB_CONNECTION_STRING"]
        )
        
    def process_excel_stream(self, blob_stream) -> Dict[str, Any]:
        """Procesa un archivo Excel desde un stream de Azure Blob"""
        
        try:
            # Leer el archivo Excel
            excel_file = pd.ExcelFile(blob_stream)
            
            result = {
                "filename": blob_stream.name,
                "sheets_processed": [],
                "total_sheets": len(excel_file.sheet_names),
                "metadata": {},
                "status": "success"
            }
            
            # Procesar cada hoja
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(blob_stream, sheet_name=sheet_name)
                    
                    sheet_info = {
                        "name": sheet_name,
                        "rows": len(df),
                        "columns": len(df.columns),
                        "data_type": self._classify_sheet_content(sheet_name, df)
                    }
                    
                    # Extraer datos específicos según el tipo de hoja
                    if sheet_info["data_type"] == "afiliados_data":
                        extracted_data = self._extract_afiliados_data(df)
                        sheet_info["extracted_data"] = extracted_data
                        
                        # TODO: Guardar en Azure SQL Database
                        # self._save_to_sql(extracted_data, sheet_name)
                        
                        # TODO: Indexar en Azure AI Search
                        # self._index_in_search(extracted_data, sheet_name)
                    
                    result["sheets_processed"].append(sheet_info)
                    
                except Exception as e:
                    logging.error(f"Error procesando hoja {sheet_name}: {str(e)}")
                    continue
            
            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(blob_stream.name)
            
            return result
            
        except Exception as e:
            logging.error(f"Error procesando Excel: {str(e)}")
            return {
                "filename": blob_stream.name,
                "status": "error",
                "error": str(e)
            }
    
    def _classify_sheet_content(self, sheet_name: str, df: pd.DataFrame) -> str:
        """Clasifica el tipo de contenido de una hoja"""
        
        # Clasificación basada en el nombre de la hoja
        if sheet_name.lower() in ['carátula', 'caratula', 'portada']:
            return "cover"
        elif sheet_name.lower() == 'indice':
            return "index"
        elif sheet_name.isdigit():
            return "afiliados_data"
        else:
            return "unknown"
    
    def _extract_afiliados_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extrae datos estructurados de afiliados de una hoja"""
        
        extracted = {
            "afp_data": [],
            "period": None,
            "data_type": "afiliados_activos"
        }
        
        try:
            # Buscar información de período
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col])
                    if "2025" in cell_value and "01" in cell_value:
                        extracted["period"] = "2025-01"
                        break
                if extracted["period"]:
                    break
            
            # Buscar datos de AFPs
            afp_names = ["Habitat", "Integra", "Prima", "Profuturo"]
            
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col])
                    
                    for afp in afp_names:
                        if afp.lower() in cell_value.lower():
                            # Extraer datos numéricos de las siguientes filas
                            afp_info = {
                                "afp_name": afp,
                                "row_index": idx,
                                "numeric_data": []
                            }
                            
                            # Buscar datos numéricos en las siguientes filas
                            for next_idx in range(idx + 1, min(idx + 5, len(df))):
                                next_row = df.iloc[next_idx]
                                numeric_values = []
                                
                                for val in next_row:
                                    if pd.notna(val) and str(val).replace('.', '').replace(',', '').isdigit():
                                        numeric_values.append(int(str(val).replace(',', '')))
                                
                                if numeric_values:
                                    afp_info["numeric_data"].extend(numeric_values)
                            
                            if afp_info["numeric_data"]:
                                extracted["afp_data"].append(afp_info)
            
            return extracted
            
        except Exception as e:
            logging.error(f"Error extrayendo datos de afiliados: {str(e)}")
            return extracted
    
    def _extract_file_metadata(self, filename: str) -> Dict[str, Any]:
        """Extrae metadatos del nombre del archivo"""
        
        metadata = {
            "filename": filename,
            "file_type": "excel",
            "source": "SPP_bulletin"
        }
        
        # Extraer período del nombre del archivo
        if "Bol" in filename and "2025" in filename:
            metadata["period"] = "2025-01"
            metadata["document_type"] = "monthly_bulletin"
        
        return metadata
    
    def _save_to_sql(self, data: Dict, sheet_name: str):
        """Guarda datos en Azure SQL Database"""
        # TODO: Implementar conexión a Azure SQL
        logging.info(f"Guardando datos de {sheet_name} en SQL Database")
        pass
    
    def _index_in_search(self, data: Dict, sheet_name: str):
        """Indexa datos en Azure AI Search"""
        # TODO: Implementar indexación en Azure AI Search
        logging.info(f"Indexando datos de {sheet_name} en AI Search")
        pass