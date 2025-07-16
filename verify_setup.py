#!/usr/bin/env python3
"""
Script simple para verificar que la configuración de blob storage funciona
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_config():
    """Verifica que la configuración esté disponible"""
    try:
        from config import AZURE_BLOB_CONFIG
        print("✅ Configuración de Azure Blob cargada correctamente")
        
        required_keys = ["AZURE_BLOB_CONNECTION_STRING", "AZURE_BLOB_CONTAINER_NAME"]
        for key in required_keys:
            if key in AZURE_BLOB_CONFIG and AZURE_BLOB_CONFIG[key]:
                print(f"✅ {key}: Configurado")
            else:
                print(f"❌ {key}: No configurado o vacío")
        
        return True
    except ImportError as e:
        print(f"❌ Error importando configuración: {e}")
        return False

def verify_imports():
    """Verifica que los imports funcionen"""
    try:
        from src.excel_processor import ExcelProcessor
        print("✅ ExcelProcessor importado correctamente")
        
        from src.data_manager import RentabilityDataManager
        print("✅ RentabilityDataManager importado correctamente")
        
        return True
    except ImportError as e:
        print(f"❌ Error importando clases: {e}")
        return False

def verify_azure_dependencies():
    """Verifica que las dependencias de Azure estén disponibles"""
    try:
        from azure.storage.blob import BlobServiceClient
        print("✅ Azure Blob Storage SDK disponible")
        return True
    except ImportError as e:
        print(f"❌ Azure Blob Storage SDK no disponible: {e}")
        print("   Instale con: pip install azure-storage-blob")
        return False

if __name__ == "__main__":
    print("=== VERIFICACIÓN DE CONFIGURACIÓN ===\n")
    
    config_ok = verify_config()
    imports_ok = verify_imports()
    azure_ok = verify_azure_dependencies()
    
    print(f"\n=== RESUMEN ===")
    print(f"Configuración: {'✅ OK' if config_ok else '❌ ERROR'}")
    print(f"Imports: {'✅ OK' if imports_ok else '❌ ERROR'}")
    print(f"Azure SDK: {'✅ OK' if azure_ok else '❌ ERROR'}")
    
    if config_ok and imports_ok and azure_ok:
        print("\n🎉 Todo está configurado correctamente!")
        print("Puede proceder a usar el sistema con blob storage.")
    else:
        print("\n⚠️  Hay problemas de configuración que deben resolverse.")