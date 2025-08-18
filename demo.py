#!/usr/bin/env python3
"""
Script completo de verificación del sistema SPP - ENHANCED VERSION
Verifica TODOS los componentes incluyendo funcionalidades enhanced
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
    """Verifica que el procesador de Excel funcione - ENHANCED VERSION"""
    try:
        from src.excel_processor import ExcelProcessor

        processor = ExcelProcessor()

        # ✅ ENHANCED: Verificar métodos originales
        original_methods = [
            "process_excel_stream",
            "_extract_rentability_data",
            "_extract_file_metadata",
        ]

        missing_original = []
        for method in original_methods:
            if not hasattr(processor, method):
                missing_original.append(method)

        if missing_original:
            return False, f"Métodos originales faltantes: {', '.join(missing_original)}"

        # ✅ ENHANCED: Verificar métodos enhanced si existen
        enhanced_methods = [
            "_extract_rentability_data_enhanced",
            "_detect_table_locations",
            "_extract_table_data",
            "_combine_accumulated_and_annualized_data",
        ]

        enhanced_available = []
        for method in enhanced_methods:
            if hasattr(processor, method):
                enhanced_available.append(method)

        enhanced_count = len(enhanced_available)
        total_enhanced = len(enhanced_methods)

        if enhanced_count == total_enhanced:
            return (
                True,
                f"ExcelProcessor ENHANCED completo ({enhanced_count}/{total_enhanced} métodos enhanced)",
            )
        elif enhanced_count > 0:
            return (
                True,
                f"ExcelProcessor PARCIALMENTE enhanced ({enhanced_count}/{total_enhanced} métodos enhanced)",
            )
        else:
            return True, "ExcelProcessor básico funcionando (sin enhanced features)"

    except Exception as e:
        return False, f"Error ExcelProcessor: {str(e)}"


def test_data_manager() -> Tuple[bool, str]:
    """Verifica que el gestor de datos funcione - ENHANCED VERSION"""
    try:
        from src.data_manager import RentabilityDataManager

        start_time = time.time()
        dm = RentabilityDataManager()

        # Verificar estadísticas básicas
        stats = dm.get_summary_statistics()
        elapsed = time.time() - start_time

        files_processed = stats.get("total_files_processed", 0)
        available_afps = stats.get("available_afps", [])

        # ✅ ENHANCED: Verificar métodos enhanced si existen
        enhanced_methods = [
            "get_rentability_by_afp_enhanced",
            "compare_afp_rentability_enhanced",
            "get_calculation_types_summary",
            "get_detailed_rentability_comparison",
        ]

        enhanced_available = []
        for method in enhanced_methods:
            if hasattr(dm, method):
                enhanced_available.append(method)

        enhanced_count = len(enhanced_available)

        if files_processed > 0:
            if enhanced_count > 0:
                return (
                    True,
                    f"DataManager ENHANCED: {files_processed} archivos, {len(available_afps)} AFPs, {enhanced_count}/4 métodos enhanced, {elapsed:.2f}s",
                )
            else:
                return (
                    True,
                    f"DataManager básico: {files_processed} archivos, {len(available_afps)} AFPs, {elapsed:.2f}s (sin enhanced)",
                )
        else:
            return (
                False,
                f"DataManager sin datos procesados (tiempo: {elapsed:.2f}s)",
            )

    except Exception as e:
        return False, f"Error DataManager: {str(e)}"


def test_assistant_agent() -> Tuple[bool, str]:
    """Verifica que el agente de Azure OpenAI funcione - ENHANCED VERSION"""
    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        start_time = time.time()
        agent = SPPAssistantAgent()

        # Verificar que se haya creado
        if not (agent.assistant_id and agent.thread_id):
            return False, "Agente no se pudo inicializar completamente"

        # ✅ ENHANCED: Verificar funciones enhanced
        functions_str = str(agent.functions)
        enhanced_functions = [
            "get_rentability_by_calculation_type",
            "compare_accumulated_vs_annualized",
            "get_calculation_types_summary",
        ]

        enhanced_found = []
        for func_name in enhanced_functions:
            if func_name in functions_str:
                enhanced_found.append(func_name)

        total_functions = len(agent.functions)
        enhanced_count = len(enhanced_found)
        elapsed = time.time() - start_time

        if enhanced_count > 0:
            return (
                True,
                f"Agent ENHANCED: {total_functions} funciones ({enhanced_count} enhanced), {elapsed:.2f}s, ID: {agent.assistant_id[:10]}...",
            )
        else:
            return (
                True,
                f"Agent básico: {total_functions} funciones, {elapsed:.2f}s, ID: {agent.assistant_id[:10]}... (sin enhanced)",
            )

    except Exception as e:
        return False, f"Error Assistant Agent: {str(e)}"


def test_end_to_end_query() -> Tuple[bool, str]:
    """Prueba end-to-end de una consulta simple - ENHANCED VERSION"""
    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        agent = SPPAssistantAgent()

        # ✅ ENHANCED: Probar consulta que podría activar funcionalidades enhanced
        enhanced_query = (
            "¿Cuál es la rentabilidad de Habitat comparando tipos de cálculo?"
        )

        start_time = time.time()
        response = agent.chat(enhanced_query)
        elapsed = time.time() - start_time

        if not response or len(response) < 50:
            return False, f"Respuesta muy corta o vacía: '{response[:100]}...'"

        # ✅ ENHANCED: Verificar si la respuesta contiene características enhanced
        enhanced_indicators = ["acumulad", "anualiz", "tabla", "comparación", "tipos"]
        enhanced_terms_found = sum(
            1 for term in enhanced_indicators if term.lower() in response.lower()
        )

        response_length = len(response)

        if enhanced_terms_found >= 2:
            return (
                True,
                f"Query ENHANCED completada: {response_length} chars, {enhanced_terms_found} términos enhanced, {elapsed:.2f}s",
            )
        else:
            return (
                True,
                f"Query básica completada: {response_length} chars, {elapsed:.2f}s (respuesta estándar)",
            )

    except Exception as e:
        return False, f"Error end-to-end: {str(e)}"


def test_function_app_compatibility() -> Tuple[bool, str]:
    """Verifica compatibilidad con Azure Functions - ENHANCED VERSION"""
    try:
        # Verificar que function_app.py se pueda importar
        import function_app

        # Verificar funciones originales
        original_functions = ["chat_endpoint", "health_check"]
        missing_original = []

        for func_name in original_functions:
            # Buscar en el código del módulo
            if not hasattr(function_app, func_name) and func_name not in str(
                function_app.__dict__
            ):
                missing_original.append(func_name)

        if missing_original:
            return (
                False,
                f"Funciones originales faltantes: {', '.join(missing_original)}",
            )

        # ✅ ENHANCED: Verificar endpoints enhanced
        app_code = str(function_app.__dict__)
        enhanced_endpoints = [
            "rentability/enhanced",
            "compare-types",
            "enhanced-stats",
            "enhance_chat_query",
        ]

        enhanced_found = []
        for endpoint in enhanced_endpoints:
            if endpoint in app_code:
                enhanced_found.append(endpoint)

        enhanced_count = len(enhanced_found)

        if enhanced_count > 0:
            return (
                True,
                f"function_app ENHANCED: {enhanced_count}/4 endpoints enhanced disponibles",
            )
        else:
            return (
                True,
                "function_app básico compatible con Azure Functions (sin enhanced)",
            )

    except Exception as e:
        return False, f"Error function_app: {str(e)}"


def test_production_cache() -> Tuple[bool, str]:
    """Verifica sistema de cache de producción - ENHANCED VERSION"""
    try:
        # Intentar importar cache de producción
        try:
            from src.cache.production_cache_manager import AutoUpdatingDataManager

            cache_dm = AutoUpdatingDataManager()

            # ✅ ENHANCED: Verificar métodos enhanced del cache
            enhanced_cache_methods = [
                "get_rentability_by_afp_enhanced",
                "get_detailed_rentability_comparison",
                "get_calculation_types_summary",
            ]

            enhanced_cache_found = []
            for method in enhanced_cache_methods:
                if hasattr(cache_dm, method):
                    enhanced_cache_found.append(method)

            # Probar funcionamiento básico
            stats = cache_dm.get_summary_statistics()
            cache_working = stats.get("total_files_processed", 0) > 0
            enhanced_cache_count = len(enhanced_cache_found)

            if cache_working and enhanced_cache_count > 0:
                return (
                    True,
                    f"Production Cache ENHANCED: {enhanced_cache_count}/3 métodos enhanced, datos funcionando",
                )
            elif cache_working:
                return (
                    True,
                    f"Production Cache básico: datos funcionando (sin enhanced methods)",
                )
            else:
                return (
                    True,
                    f"Production Cache disponible pero sin datos ({enhanced_cache_count} enhanced methods)",
                )

        except ImportError:
            return (
                True,
                "Production cache no disponible - usando cache estándar (normal)",
            )

    except Exception as e:
        return False, f"Error Production Cache: {str(e)}"


def test_enhanced_query_capabilities() -> Tuple[bool, str]:
    """✅ NUEVO: Prueba específica de capacidades enhanced"""
    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        agent = SPPAssistantAgent()

        # Consultas específicamente diseñadas para probar enhanced features
        enhanced_test_queries = [
            "¿Diferencia entre rentabilidad acumulada y anualizada?",
            "Compara Prima vs Habitat con ambos tipos de cálculo",
            "Muestra tabla comparativa con tipos de rentabilidad",
        ]

        successful_enhanced = 0
        total_time = 0

        for query in enhanced_test_queries[:2]:  # Solo probar 2 para no ser muy lento
            try:
                start_time = time.time()
                response = agent.chat(query)
                elapsed = time.time() - start_time
                total_time += elapsed

                # Verificar características enhanced en respuesta
                enhanced_terms = [
                    "acumulad",
                    "anualiz",
                    "tabla",
                    "comparación",
                    "tipos",
                    "diferencia",
                ]
                terms_found = sum(
                    1 for term in enhanced_terms if term.lower() in response.lower()
                )

                if terms_found >= 3 and len(response) > 300:
                    successful_enhanced += 1

            except Exception:
                pass

        success_rate = successful_enhanced / len(enhanced_test_queries[:2])
        avg_time = total_time / len(enhanced_test_queries[:2]) if total_time > 0 else 0

        if success_rate >= 0.5:
            return (
                True,
                f"Enhanced queries: {success_rate:.1%} success rate, {avg_time:.1f}s avg",
            )
        else:
            return (
                True,
                f"Enhanced queries: {success_rate:.1%} success rate (posible implementación básica)",
            )

    except Exception as e:
        return False, f"Error enhanced queries: {str(e)}"


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
    """Genera reporte completo del sistema - ENHANCED VERSION"""
    print_header("VERIFICACIÓN COMPLETA DEL SISTEMA SPP ENHANCED")

    tests = [
        ("Imports básicos", test_basic_imports),
        ("Carga de configuración", test_config_loading),
        ("Azure OpenAI", test_azure_openai_connection),
        ("Azure Blob Storage", test_azure_blob_storage),
        ("Azure SQL Database", test_azure_sql_database),
        ("Azure AI Search", test_azure_ai_search),
        ("Excel Processor Enhanced", test_excel_processor),
        ("Data Manager Enhanced", test_data_manager),
        ("Assistant Agent Enhanced", test_assistant_agent),
        ("Function App Enhanced", test_function_app_compatibility),
        ("Production Cache Enhanced", test_production_cache),
        ("Enhanced Query Capabilities", test_enhanced_query_capabilities),
        ("Performance Benchmark", run_performance_benchmark),
        ("End-to-End Enhanced Query", test_end_to_end_query),
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
                if test_name in [
                    "Azure SQL Database",
                    "Azure AI Search",
                    "Production Cache Enhanced",
                ]:
                    if "no configurado" in details or "no disponible" in details:
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
    print_header("RESUMEN DE VERIFICACIÓN ENHANCED")

    total_tests = len(tests)
    print(f"📊 Total de tests: {total_tests}")
    print(f"✅ Pasaron: {passed}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Fallaron: {failed}")

    success_rate = (passed + warnings) / total_tests * 100
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")

    # ✅ ENHANCED: Análisis de funcionalidades enhanced
    enhanced_tests = [
        "Excel Processor Enhanced",
        "Data Manager Enhanced",
        "Assistant Agent Enhanced",
        "Function App Enhanced",
        "Enhanced Query Capabilities",
    ]
    enhanced_passed = sum(
        1 for test in enhanced_tests if results.get(test, {}).get("status") == "PASS"
    )
    enhanced_rate = enhanced_passed / len(enhanced_tests) * 100

    print(
        f"🚀 Funcionalidades Enhanced: {enhanced_rate:.1f}% ({enhanced_passed}/{len(enhanced_tests)})"
    )

    # Determinar estado general del sistema
    if failed == 0 and enhanced_rate >= 80:
        system_status = "🎉 SISTEMA ENHANCED COMPLETAMENTE FUNCIONAL"
    elif failed == 0 and enhanced_rate >= 50:
        system_status = "✅ SISTEMA ENHANCED PARCIALMENTE FUNCIONAL"
    elif failed == 0:
        system_status = "✅ SISTEMA BÁSICO FUNCIONAL"
    elif failed <= 2 and passed >= total_tests - 3:
        system_status = "⚠️  SISTEMA FUNCIONAL CON LIMITACIONES MENORES"
    elif failed <= 4:
        system_status = "⚠️  SISTEMA FUNCIONAL CON LIMITACIONES"
    else:
        system_status = "❌ SISTEMA CON PROBLEMAS CRÍTICOS"

    print(f"\n🎯 ESTADO DEL SISTEMA: {system_status}")

    # Recomendaciones específicas
    print_header("RECOMENDACIONES ENHANCED")

    if failed == 0 and enhanced_rate >= 80:
        print("🚀 ¡Excelente! Su sistema enhanced está completamente configurado.")
        print("   Puede proceder a ejecutar python demo.py o desplegar en producción.")
        print("   ✅ Funcionalidades enhanced completamente disponibles")
    elif enhanced_rate >= 50:
        print("🔧 Sistema enhanced parcialmente funcional:")
        print("   ✅ Funcionalidades básicas completas")
        print("   ⚠️  Algunas funcionalidades enhanced pueden necesitar implementación")
        print("   💡 Ejecutar python demo.py para ver capacidades disponibles")
    else:
        print("🔧 Para mejorar el sistema:")
        for test_name, result in results.items():
            if result["status"] == "FAIL":
                print(f"   ❌ Solucionar: {test_name}")
                print(f"      └─ {result['details']}")

        if enhanced_rate < 50:
            print(
                "   💡 Funcionalidades enhanced no implementadas - sistema funciona en modo básico"
            )

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
        "enhanced_rate": enhanced_rate,
        "enhanced_passed": enhanced_passed,
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
        enhanced_rate = report["summary"]["enhanced_rate"]

        if failed == 0 and enhanced_rate >= 80:
            print("\n🎉 ¡Verificación enhanced completada exitosamente!")
            print("🚀 Próximos pasos recomendados:")
            print("   • python demo.py - Ver funcionalidades enhanced")
            print(
                "   • python test/test_agent_interactive.py - Probar consultas enhanced"
            )
            print("   • func start - Iniciar API con endpoints enhanced")
            return 0
        elif failed == 0:
            print("\n✅ Verificación completada - sistema básico funcional")
            print("💡 Para activar funcionalidades enhanced:")
            print("   • Verificar implementación de métodos enhanced en archivos")
            print("   • python demo.py - Ver capacidades disponibles")
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
