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
                self.blob_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
            except Exception as e:
                logging.warning(f"Error inicializando blob client: {e}")
                self.blob_client = None
        else:
            self.blob_client = None
        
    def process_excel_stream(self, blob_stream, blob_name: str) -> Dict[str, Any]:
        """Procesa un archivo Excel de rentabilidad desde un stream de Azure Blob"""
        
        try:
            # Leer el archivo Excel desde el stream
            blob_data = blob_stream.readall()
            df = pd.read_excel(blob_data, header=None)
            
            result = {
                "filename": blob_name,
                "status": "success",
                "metadata": {},
                "rentability_data": {}
            }
            
            # Extraer datos de rentabilidad
            rentability_data = self._extract_rentability_data(df, blob_name)
            result["rentability_data"] = rentability_data
            
            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(blob_name)
            
            # TODO: Guardar en Azure SQL Database
            # self._save_to_sql(rentability_data)
            
            # TODO: Indexar en Azure AI Search
            # self._index_in_search(rentability_data)
            
            return result
            
        except Exception as e:
            logging.error(f"Error procesando Excel desde blob storage: {str(e)}")
            return {
                "filename": blob_name,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_rentability_data(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Extrae datos de rentabilidad de fondos de pensiones"""
        
        extracted = {
            "fund_type": None,
            "period": None,
            "afp_data": [],
            "data_type": "rentability",
            "periods_available": []
        }
        
        try:
            # Extraer tipo de fondo del nombre del archivo
            fund_match = re.search(r'Tipo\s+(\d+)', filename)
            if fund_match:
                extracted["fund_type"] = int(fund_match.group(1))
            else:
                # Buscar en el contenido del archivo
                for idx in range(min(5, len(df))):
                    for col in range(df.shape[1]):
                        cell_value = str(df.iloc[idx, col])
                        if "Tipo" in cell_value and any(char.isdigit() for char in cell_value):
                            type_match = re.search(r'Tipo\s+(\d+)', cell_value)
                            if type_match:
                                extracted["fund_type"] = int(type_match.group(1))
                                break
            
            # Extraer período del nombre del archivo (más dinámico para cualquier año)
            period_match = re.search(r'(\w{2})(\d{4})', filename)
            if period_match:
                month_abbr = period_match.group(1)
                year = period_match.group(2)
                month_map = {
                    'en': '01', 'fe': '02', 'ma': '03', 'ab': '04', 
                    'my': '05', 'jn': '06', 'jl': '07', 'ag': '08',
                    'se': '09', 'oc': '10', 'no': '11', 'di': '12'
                }
                extracted["period"] = f"{year}-{month_map.get(month_abbr, '01')}"
            
            # Extraer períodos disponibles de las columnas (más dinámico)
            periods = []
            for idx in range(4, 7):  # Filas donde están los períodos
                for col in range(df.shape[1]):
                    cell_value = str(df.iloc[idx, col])
                    # Buscar patrones de fecha más generales
                    if re.search(r'\d{4}', cell_value) and "/" in cell_value:
                        periods.append(cell_value)
                    elif re.search(r'\d{2}/\d{4}', cell_value):
                        periods.append(cell_value)
            extracted["periods_available"] = list(set(periods))
            
            # Extraer datos de AFPs (filas 7-11 aproximadamente)
            afp_names = ["Habitat", "Integra", "Prima", "Profuturo"]
            
            for idx in range(7, min(12, len(df))):
                afp_name_cell = str(df.iloc[idx, 0])
                
                for afp in afp_names:
                    if afp.lower() in afp_name_cell.lower():
                        afp_data = {
                            "afp_name": afp,
                            "rentability_data": {}
                        }
                        
                        # Extraer datos de rentabilidad por período
                        col_idx = 1
                        for period in extracted["periods_available"]:
                            if col_idx < df.shape[1]:
                                # Rentabilidad nominal
                                nominal_val = df.iloc[idx, col_idx]
                                if pd.notna(nominal_val):
                                    try:
                                        afp_data["rentability_data"][f"{period}_nominal"] = float(nominal_val)
                                    except:
                                        pass
                                
                                # Rentabilidad real (siguiente columna)
                                if col_idx + 1 < df.shape[1]:
                                    real_val = df.iloc[idx, col_idx + 1]
                                    if pd.notna(real_val):
                                        try:
                                            afp_data["rentability_data"][f"{period}_real"] = float(real_val)
                                        except:
                                            pass
                                
                                col_idx += 2
                        
                        if afp_data["rentability_data"]:
                            extracted["afp_data"].append(afp_data)
                        break
            
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
            "document_type": "rentability_report"
        }
        
        # Extraer tipo de fondo
        fund_match = re.search(r'Tipo\s+(\d+)', filename)
        if fund_match:
            metadata["fund_type"] = int(fund_match.group(1))
        
        # Extraer período del nombre del archivo (más dinámico)
        period_match = re.search(r'(\w{2})(\d{4})', filename)
        if period_match:
            month_abbr = period_match.group(1)
            year = int(period_match.group(2))
            month_map = {
                'en': '01', 'fe': '02', 'ma': '03', 'ab': '04', 
                'my': '05', 'jn': '06', 'jl': '07', 'ag': '08',
                'se': '09', 'oc': '10', 'no': '11', 'di': '12'
            }
            metadata["period"] = f"{year}-{month_map.get(month_abbr, '01')}"
            metadata["year"] = year
            metadata["month"] = month_map.get(month_abbr, '01')
        
        return metadata
    
    def process_local_file(self, file_path: str) -> Dict[str, Any]:
        """Procesa un archivo Excel local para testing"""
        try:
            df = pd.read_excel(file_path, header=None)
            
            result = {
                "filename": file_path,
                "status": "success",
                "metadata": {},
                "rentability_data": {}
            }
            
            # Extraer datos de rentabilidad
            rentability_data = self._extract_rentability_data(df, file_path)
            result["rentability_data"] = rentability_data
            
            # Extraer metadatos del archivo
            result["metadata"] = self._extract_file_metadata(file_path)
            
            return result
            
        except Exception as e:
            logging.error(f"Error procesando archivo local: {str(e)}")
            return {
                "filename": file_path,
                "status": "error",
                "error": str(e)
            }
    
    def _save_to_sql(self, data: Dict):
        """Guarda datos de rentabilidad en Azure SQL Database"""
        # TODO: Implementar conexión a Azure SQL
        logging.info(f"Guardando datos de rentabilidad en SQL Database")
        pass
    
    def _index_in_search(self, data: Dict):
        """Indexa datos de rentabilidad en Azure AI Search"""
        # TODO: Implementar indexación en Azure AI Search
        logging.info(f"Indexando datos de rentabilidad en AI Search")
        pass