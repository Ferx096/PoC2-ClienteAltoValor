#!/usr/bin/env python3
"""
Script completo de verificación del sistema SPP
Verifica TODOS los componentes: OpenAI, Blob Storage, SQL, AI Search, Excel processing, etc.
"""
import sys
import os
import time
import json
from typing import Dict, List, Tuple

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def print_header(title: str):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f"🔍 {title}")
    print("=" * 70)


def print_test(test_name: str, status: str, details: str = ""):
    """Imprime resultado de un test"""
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} {test_name:<40} [{status}]")
    if details:
        print(f"   └─ {details}")


def test_basic_imports() -> Tuple[bool, str]:
    """Verifica que los imports básicos funcionen"""
    try:
        # Imports básicos de Python
        import pandas as pd
        import json
        import re

        # Imports de Azure
        from azure.storage.blob import BlobServiceClient
        from azure.core.credentials import AzureKeyCredential
        from openai import AzureOpenAI

        return True, f"Pandas {pd.__version__}, Azure SDKs disponibles"
    except ImportError as e:
        return False, f"Import error: {str(e)}"


def test_config_loading() -> Tuple[bool, str]:
    """Verifica que la configuración se cargue correctamente"""
    try:
        from config import (
            AZURE_CONFIG,
            AZURE_BLOB_CONFIG,
            AZURE_SQL_CONFIG,
            AZURE_AISEARCH_API_KEY,
        )

        # Verificar configuraciones principales
        missing_configs = []

        if not AZURE_CONFIG.get("endpoint"):
            missing_configs.append("AZURE_OPENAI_ENDPOINT")
        if not AZURE_CONFIG.get("api_key"):
            missing_configs.append("AZURE_OPENAI_API_KEY")
        if not AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING"):
            missing_configs.append("AZURE_BLOB_CONNECTION_STRING")

        if missing_configs:
            return False, f"Configuraciones faltantes: {', '.join(missing_configs)}"

        return True, "Todas las configuraciones básicas cargadas"
    except ImportError as e:
        return False, f"Error cargando config: {str(e)}"


def test_azure_openai_connection() -> Tuple[bool, str]:
    """Verifica conexión con Azure OpenAI"""
    try:
        from config import get_openai_client, get_deployment_name

        client = get_openai_client()
        deployment = get_deployment_name()

        # Intentar listar modelos o hacer una llamada simple
        start_time = time.time()

        # Test simple de chat completion
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10,
        )

        elapsed = time.time() - start_time

        if response and response.choices:
            return (
                True,
                f"Conexión exitosa, respuesta en {elapsed:.2f}s, modelo: {deployment}",
            )
        else:
            return False, "Respuesta vacía del modelo"

    except Exception as e:
        return False, f"Error conexión OpenAI: {str(e)}"


def test_azure_blob_storage() -> Tuple[bool, str]:
    """Verifica conexión y contenido de Azure Blob Storage"""
    try:
        from config import AZURE_BLOB_CONFIG
        from azure.storage.blob import BlobServiceClient

        connection_string = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONNECTION_STRING")
        container_name = AZURE_BLOB_CONFIG.get("AZURE_BLOB_CONTAINER_NAME")

        if not connection_string or not container_name:
            return False, "Connection string o container name no configurados"

        # Crear cliente y conectar
        start_time = time.time()
        blob_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_client.get_container_client(container_name)

        # Listar blobs Excel
        excel_blobs = []
        try:
            for blob in container_client.list_blobs():
                if blob.name.upper().endswith((".XLS", ".XLSX")):
                    excel_blobs.append(blob.name)
        except Exception as e:
            return False, f"Error listando blobs: {str(e)}"

        elapsed = time.time() - start_time

        if excel_blobs:
            return (
                True,
                f"Conexión exitosa, {len(excel_blobs)} archivos Excel encontrados en {elapsed:.2f}s",
            )
        else:
            return (
                False,
                f"Container accesible pero sin archivos Excel (total blobs: {len(list(container_client.list_blobs()))})",
            )

    except Exception as e:
        return False, f"Error Blob Storage: {str(e)}"


def test_azure_sql_database() -> Tuple[bool, str]:
    """Verifica conexión con Azure SQL Database"""
    try:
        from config import AZURE_SQL_CONFIG

        connection_string = AZURE_SQL_CONFIG.get("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            return False, "Connection string no configurado"

        try:
            import pyodbc
        except ImportError:
            return False, "pyodbc no instalado (pip install pyodbc)"

        # Intentar conexión
        start_time = time.time()
        conn = pyodbc.connect(connection_string + "Database=sbsbdsql;", timeout=10)
        cursor = conn.cursor()

        # Test simple
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()

        # Verificar si existe tabla de datos
        cursor.execute(
            """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'rentability_data'
        """
        )
        table_exists = cursor.fetchone()[0] > 0

        conn.close()
        elapsed = time.time() - start_time

        table_status = (
            "tabla rentability_data existe"
            if table_exists
            else "tabla rentability_data no existe"
        )
        return True, f"Conexión exitosa en {elapsed:.2f}s, {table_status}"

    except Exception as e:
        return False, f"Error SQL Database: {str(e)}"


def test_azure_ai_search() -> Tuple[bool, str]:
    """Verifica conexión con Azure AI Search"""
    try:
        from config import AZURE_AISEARCH_API_KEY
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential

        endpoint = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_ENDPOINT")
        api_key = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_API_KEY")
        index_name = AZURE_AISEARCH_API_KEY.get("AZURE_AISEARCH_INDEX_NAME")

        if not all([endpoint, api_key, index_name]):
            return True, "Azure AI Search no configurado (opcional)"

        # Crear cliente y probar conexión
        start_time = time.time()
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key),
        )

        # Test búsqueda simple
        results = search_client.search(search_text="*", top=1)
        document_count = 0
        for result in results:
            document_count += 1
            break

        elapsed = time.time() - start_time

        return True, f"Conexión exitosa en {elapsed:.2f}s, índice accesible"

    except Exception as e:
        return False, f"Error AI Search: {str(e)}"


def test_excel_processor() -> Tuple[bool, str]:
    """Verifica que el procesador de Excel funcione"""
    try:
        from src.excel_processor import ExcelProcessor

        processor = ExcelProcessor()

        # Verificar que los métodos existen
        methods = [
            "process_excel_stream",
            "_extract_rentability_data",
            "_extract_file_metadata",
        ]
        for method in methods:
            if not hasattr(processor, method):
                return False, f"Método {method} no encontrado"

        return True, "ExcelProcessor inicializado correctamente, métodos disponibles"

    except Exception as e:
        return False, f"Error ExcelProcessor: {str(e)}"


def test_data_manager() -> Tuple[bool, str]:
    """Verifica que el gestor de datos funcione"""
    try:
        from src.data_manager import RentabilityDataManager

        start_time = time.time()
        dm = RentabilityDataManager()

        # Verificar estadísticas básicas
        stats = dm.get_summary_statistics()
        elapsed = time.time() - start_time

        files_processed = stats.get("total_files_processed", 0)
        available_afps = stats.get("available_afps", [])

        if files_processed > 0:
            return (
                True,
                f"Inicializado en {elapsed:.2f}s, {files_processed} archivos, AFPs: {', '.join(available_afps)}",
            )
        else:
            return (
                False,
                f"Inicializado pero sin datos procesados (tiempo: {elapsed:.2f}s)",
            )

    except Exception as e:
        return False, f"Error DataManager: {str(e)}"


def test_assistant_agent() -> Tuple[bool, str]:
    """Verifica que el agente de Azure OpenAI funcione"""
    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        start_time = time.time()
        agent = SPPAssistantAgent()

        # Verificar que se haya creado
        if agent.assistant_id and agent.thread_id:
            elapsed = time.time() - start_time
            return (
                True,
                f"Agente creado en {elapsed:.2f}s, Assistant ID: {agent.assistant_id[:10]}...",
            )
        else:
            return False, "Agente no se pudo inicializar completamente"

    except Exception as e:
        return False, f"Error Assistant Agent: {str(e)}"


def test_end_to_end_query() -> Tuple[bool, str]:
    """Prueba end-to-end de una consulta simple"""
    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        agent = SPPAssistantAgent()

        # Query simple
        start_time = time.time()
        response = agent.chat("¿Cuál es la rentabilidad de Habitat?")
        elapsed = time.time() - start_time

        if response and len(response) > 50:  # Respuesta mínima esperada
            return (
                True,
                f"Query completada en {elapsed:.2f}s, respuesta: {len(response)} caracteres",
            )
        else:
            return False, f"Respuesta muy corta o vacía: '{response[:100]}...'"

    except Exception as e:
        return False, f"Error end-to-end: {str(e)}"


def test_function_app_compatibility() -> Tuple[bool, str]:
    """Verifica compatibilidad con Azure Functions"""
    try:
        # Verificar que function_app.py se pueda importar
        import function_app

        # Verificar que tenga las funciones esperadas
        expected_functions = ["chat_endpoint", "health_check", "assistant_info"]
        missing = []

        for func_name in expected_functions:
            if not hasattr(function_app, func_name):
                missing.append(func_name)

        if missing:
            return (
                False,
                f"Funciones faltantes en function_app.py: {', '.join(missing)}",
            )

        return True, "function_app.py compatible con Azure Functions"

    except Exception as e:
        return False, f"Error function_app: {str(e)}"


def run_performance_benchmark() -> Tuple[bool, str]:
    """Ejecuta benchmark básico de performance"""
    try:
        from src.data_manager import RentabilityDataManager

        dm = RentabilityDataManager()

        # Test múltiples consultas
        queries = [("Habitat", 0), ("Integra", 1), ("Prima", 2), ("Profuturo", 3)]

        start_time = time.time()
        successful_queries = 0

        for afp, fund_type in queries:
            try:
                result = dm.get_rentability_by_afp(afp, fund_type)
                if "error" not in result:
                    successful_queries += 1
            except:
                pass

        elapsed = time.time() - start_time
        avg_time = elapsed / len(queries)

        if successful_queries >= 2:  # Al menos 50% exitosas
            return (
                True,
                f"{successful_queries}/{len(queries)} consultas exitosas, promedio: {avg_time:.3f}s/query",
            )
        else:
            return False, f"Solo {successful_queries}/{len(queries)} consultas exitosas"

    except Exception as e:
        return False, f"Error benchmark: {str(e)}"


def generate_system_report() -> Dict:
    """Genera reporte completo del sistema"""
    print_header("VERIFICACIÓN COMPLETA DEL SISTEMA SPP")

    tests = [
        ("Imports básicos", test_basic_imports),
        ("Carga de configuración", test_config_loading),
        ("Azure OpenAI", test_azure_openai_connection),
        ("Azure Blob Storage", test_azure_blob_storage),
        ("Azure SQL Database", test_azure_sql_database),
        ("Azure AI Search", test_azure_ai_search),
        ("Excel Processor", test_excel_processor),
        ("Data Manager", test_data_manager),
        ("Assistant Agent", test_assistant_agent),
        ("Function App", test_function_app_compatibility),
        ("Performance Benchmark", run_performance_benchmark),
        ("End-to-End Query", test_end_to_end_query),
    ]

    results = {}
    passed = 0
    failed = 0
    warnings = 0

    for test_name, test_func in tests:
        try:
            success, details = test_func()
            if success:
                status = "PASS"
                passed += 1
            else:
                # Determinar si es error crítico o warning
                if test_name in ["Azure SQL Database", "Azure AI Search"]:
                    if "no configurado" in details or "deshabilitado" in details:
                        status = "WARN"
                        warnings += 1
                    else:
                        status = "FAIL"
                        failed += 1
                else:
                    status = "FAIL"
                    failed += 1

            print_test(test_name, status, details)
            results[test_name] = {"status": status, "details": details}

        except Exception as e:
            print_test(test_name, "FAIL", f"Test crashed: {str(e)}")
            results[test_name] = {
                "status": "FAIL",
                "details": f"Test crashed: {str(e)}",
            }
            failed += 1

    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")

    total_tests = len(tests)
    print(f"📊 Total de tests: {total_tests}")
    print(f"✅ Pasaron: {passed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Fallaron: {failed}")

    success_rate = (passed + warnings) / total_tests * 100
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")

    # Determinar estado general del sistema
    if failed == 0:
        system_status = "🎉 SISTEMA COMPLETAMENTE FUNCIONAL"
    elif failed <= 2 and passed >= total_tests - 3:
        system_status = "✅ SISTEMA FUNCIONAL CON LIMITACIONES MENORES"
    elif failed <= 4:
        system_status = "⚠️  SISTEMA FUNCIONAL CON LIMITACIONES"
    else:
        system_status = "❌ SISTEMA CON PROBLEMAS CRÍTICOS"

    print(f"\n🎯 ESTADO DEL SISTEMA: {system_status}")

    # Recomendaciones específicas
    print_header("RECOMENDACIONES")

    if failed == 0:
        print("🚀 ¡Excelente! Su sistema está completamente configurado.")
        print("   Puede proceder a ejecutar python demo.py o desplegar en producción.")
    else:
        print("🔧 Para mejorar el sistema:")
        for test_name, result in results.items():
            if result["status"] == "FAIL":
                print(f"   ❌ Solucionar: {test_name}")
                print(f"      └─ {result['details']}")

        if any(
            "Azure SQL" in name
            for name in results.keys()
            if results[name]["status"] == "WARN"
        ):
            print("   💡 Considere habilitar Azure SQL para producción")
        if any(
            "AI Search" in name
            for name in results.keys()
            if results[name]["status"] == "WARN"
        ):
            print("   💡 Considere habilitar Azure AI Search para consultas avanzadas")

    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed,
        "warnings": warnings,
        "failed": failed,
        "success_rate": success_rate,
        "system_status": system_status,
    }

    return results


def main():
    """Función principal"""
    try:
        report = generate_system_report()

        # Guardar reporte detallado
        with open("system_verification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Reporte detallado guardado en: system_verification_report.json")

        # Determinar código de salida
        failed = report["summary"]["failed"]
        if failed == 0:
            print("\n🎉 ¡Verificación completada exitosamente!")
            return 0
        elif failed <= 2:
            print("\n⚠️  Verificación completada con warnings menores")
            return 0
        else:
            print("\n❌ Verificación completada con errores críticos")
            return 1

    except Exception as e:
        print(f"\n💥 Error fatal en verificación: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
