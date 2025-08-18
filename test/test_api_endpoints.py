#!/usr/bin/env python3
"""
Script para probar los endpoints de la API usando requests - ENHANCED VERSION
Útil para probar la Azure Function localmente o en producción incluyendo endpoints enhanced
"""
import requests
import json
import time
import sys


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"🌐 {title}")
    print("=" * 60)


def test_health_endpoint(base_url):
    """Prueba el endpoint de health check"""
    print_header("PROBANDO HEALTH CHECK")

    try:
        url = f"{base_url}/api/health"
        print(f"📡 GET {url}")

        start_time = time.time()
        response = requests.get(url, timeout=30)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # ✅ ENHANCED: Verificar características enhanced en health
            enhanced_features = data.get("features", [])
            if enhanced_features:
                print(f"🚀 Features enhanced detectadas: {len(enhanced_features)}")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_assistant_info_endpoint(base_url):
    """Prueba el endpoint de información del asistente"""
    print_header("PROBANDO ASSISTANT INFO")

    try:
        url = f"{base_url}/api/assistant/info"
        print(f"📡 GET {url}")

        start_time = time.time()
        response = requests.get(url, timeout=30)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_chat_endpoint(base_url, query):
    """Prueba el endpoint de chat"""
    print_header(f"PROBANDO CHAT: {query}")

    try:
        url = f"{base_url}/api/chat"
        payload = {"query": query}
        headers = {"Content-Type": "application/json"}

        print(f"📡 POST {url}")
        print(f"📝 Query: {query}")

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "Sin respuesta")

            # ✅ ENHANCED: Analizar si la respuesta es enhanced
            enhanced_terms = ["acumulad", "anualiz", "tabla", "comparación"]
            terms_found = sum(
                1 for term in enhanced_terms if term.lower() in response_text.lower()
            )
            has_tables = "|" in response_text

            print(f"✅ Respuesta:")
            print(
                f"🤖 {response_text[:300]}{'...' if len(response_text) > 300 else ''}"
            )
            print(f"🆔 Assistant ID: {data.get('assistant_id', 'N/A')}")
            print(f"🧵 Thread ID: {data.get('thread_id', 'N/A')}")

            # Indicadores enhanced
            if terms_found >= 2 or has_tables:
                print(
                    f"🚀 Respuesta ENHANCED detectada ({terms_found} términos, tablas: {has_tables})"
                )
            else:
                print(f"📋 Respuesta básica")

        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_enhanced_rentability_endpoint(base_url):
    """✅ NUEVO: Prueba el endpoint de rentabilidad enhanced"""
    print_header("PROBANDO ENDPOINT RENTABILITY ENHANCED")

    try:
        url = f"{base_url}/api/rentability/enhanced"
        payload = {
            "afp_name": "Prima",
            "fund_type": 0,
            "calculation_type": "both",
            "period": "2025-05",
        }
        headers = {"Content-Type": "application/json"}

        print(f"📡 POST {url}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta enhanced:")

            # Mostrar información específica enhanced
            result = data.get("result", {})
            enhanced_features = data.get("enhanced_features", {})

            print(f"🏦 AFP: {result.get('afp_name', 'N/A')}")
            print(f"📊 Calculation Type: {result.get('calculation_type', 'N/A')}")
            print(
                f"🚀 Has Accumulated: {enhanced_features.get('has_accumulated', False)}"
            )
            print(
                f"📈 Has Annualized: {enhanced_features.get('has_annualized', False)}"
            )

            rentability_data = result.get("rentability_data", {})
            if rentability_data:
                # Mostrar algunos datos clave
                acc_keys = [k for k in rentability_data.keys() if "accumulated" in k][
                    :2
                ]
                ann_keys = [k for k in rentability_data.keys() if "annualized" in k][:2]

                if acc_keys:
                    print(f"📊 Datos acumulados:")
                    for key in acc_keys:
                        print(f"   • {key}: {rentability_data[key]:.2f}%")

                if ann_keys:
                    print(f"📈 Datos anualizados:")
                    for key in ann_keys:
                        print(f"   • {key}: {rentability_data[key]:.2f}%")

        elif response.status_code == 501:
            print(f"⚠️  Endpoint enhanced no implementado aún (501)")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_compare_types_endpoint(base_url):
    """✅ NUEVO: Prueba el endpoint de comparación de tipos"""
    print_header("PROBANDO ENDPOINT COMPARE TYPES")

    try:
        url = f"{base_url}/api/rentability/compare-types"
        payload = {"afp_name": "Habitat", "fund_type": 0, "period": "2025-05"}
        headers = {"Content-Type": "application/json"}

        print(f"📡 POST {url}")
        print(f"📝 Payload: {json.dumps(payload, indent=2)}")

        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=45)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            comparison = data.get("comparison", {})

            print(f"✅ Comparación exitosa:")
            print(f"🏦 AFP: {comparison.get('afp_name', 'N/A')}")
            print(f"📊 Fund Type: {comparison.get('fund_type', 'N/A')}")

            # Mostrar diferencias si están disponibles
            differences = comparison.get("differences", {})
            if differences:
                print(f"📈 Diferencias encontradas: {len(differences)}")
                for key, diff_data in list(differences.items())[:2]:
                    print(f"   • {key}:")
                    print(
                        f"     - Acumulada: {diff_data.get('accumulated', 'N/A'):.2f}%"
                    )
                    print(
                        f"     - Anualizada: {diff_data.get('annualized', 'N/A'):.2f}%"
                    )
                    print(
                        f"     - Diferencia: {diff_data.get('difference', 'N/A'):.2f}%"
                    )
            else:
                print(f"📋 Sin diferencias calculadas")

        elif response.status_code == 501:
            print(f"⚠️  Endpoint enhanced no implementado aún (501)")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_enhanced_stats_endpoint(base_url):
    """✅ NUEVO: Prueba el endpoint de estadísticas enhanced"""
    print_header("PROBANDO ENDPOINT ENHANCED STATS")

    try:
        url = f"{base_url}/api/system/enhanced-stats"
        print(f"📡 GET {url}")

        start_time = time.time()
        response = requests.get(url, timeout=30)
        elapsed_time = time.time() - start_time

        print(f"⏱️  Tiempo: {elapsed_time:.2f} segundos")
        print(f"📊 Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Estadísticas enhanced:")

            system_type = data.get("system_type", "unknown")
            print(f"🔧 System Type: {system_type}")

            features = data.get("features", {})
            print(f"🚀 Features enhanced:")
            for feature, available in features.items():
                status = "✅" if available else "❌"
                print(f"   {status} {feature.replace('_', ' ').title()}")

            agent_capabilities = data.get("agent_capabilities", {})
            if agent_capabilities:
                print(f"🤖 Agent Capabilities:")
                print(
                    f"   • Enhanced functions: {agent_capabilities.get('has_enhanced_functions', 'N/A')}"
                )
                print(
                    f"   • Total functions: {agent_capabilities.get('total_functions', 'N/A')}"
                )
                print(
                    f"   • Agent ready: {agent_capabilities.get('agent_ready', 'N/A')}"
                )

        elif response.status_code == 501:
            print(f"⚠️  Endpoint enhanced no implementado aún (501)")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")


def test_cache_endpoints(base_url):
    """Prueba endpoints relacionados con cache"""
    print_header("PROBANDO ENDPOINTS DE CACHE")

    # Test cache stats
    try:
        url = f"{base_url}/api/cache/stats"
        print(f"📡 GET {url}")

        response = requests.get(url, timeout=30)
        print(f"📊 Cache Stats Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            cache_stats = data.get("cache_stats", {})
            print(
                f"✅ Cache funcionando: {cache_stats.get('total_files_processed', 0)} archivos"
            )

    except Exception as e:
        print(f"⚠️ Error en cache stats: {str(e)}")


def run_sample_tests(base_url):
    """Ejecuta una serie de pruebas de ejemplo - ENHANCED VERSION"""
    print_header("EJECUTANDO PRUEBAS ENHANCED DE EJEMPLO")

    # 1. Health check
    test_health_endpoint(base_url)

    # 2. Assistant info (si existe)
    test_assistant_info_endpoint(base_url)

    # 3. Cache endpoints
    test_cache_endpoints(base_url)

    # ✅ 4. NUEVOS: Endpoints enhanced
    test_enhanced_rentability_endpoint(base_url)
    test_compare_types_endpoint(base_url)
    test_enhanced_stats_endpoint(base_url)

    # 5. Consultas de chat (básicas y enhanced)
    basic_queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara Habitat vs Integra en fondos tipo 2",
    ]

    enhanced_queries = [
        "¿Cuál es la diferencia entre rentabilidad acumulada y anualizada?",
        "Compara Prima vs Habitat mostrando ambos tipos de cálculo",
    ]

    print_header("PROBANDO CONSULTAS BÁSICAS")
    for query in basic_queries:
        test_chat_endpoint(base_url, query)
        time.sleep(1)  # Pausa entre consultas

    print_header("PROBANDO CONSULTAS ENHANCED")
    for query in enhanced_queries:
        test_chat_endpoint(base_url, query)
        time.sleep(1)  # Pausa entre consultas


def interactive_api_test(base_url):
    """Modo interactivo para probar la API - ENHANCED VERSION"""
    print_header("MODO INTERACTIVO - PRUEBAS DE API ENHANCED")

    print(
        f"""
🎯 PROBANDO API EN: {base_url}

💡 COMANDOS DISPONIBLES:
   • Escribe tu consulta para probar /api/chat
   • 'health' - Probar /api/health
   • 'info' - Probar /api/assistant/info
   • 'enhanced-stats' - Probar /api/system/enhanced-stats
   • 'rentability-enhanced' - Probar /api/rentability/enhanced
   • 'compare-types' - Probar /api/rentability/compare-types
   • 'ejemplos' - Ejecutar pruebas de ejemplo
   • 'enhanced' - Probar todas las funcionalidades enhanced
   • 'salir' - Terminar
    """
    )

    while True:
        try:
            print("\n" + "-" * 50)
            command = input("🤔 Comando o consulta: ").strip()

            if not command:
                continue

            if command.lower() in ["salir", "exit", "quit"]:
                print("👋 ¡Hasta luego!")
                break

            if command.lower() == "health":
                test_health_endpoint(base_url)
                continue

            if command.lower() == "info":
                test_assistant_info_endpoint(base_url)
                continue

            if command.lower() == "enhanced-stats":
                test_enhanced_stats_endpoint(base_url)
                continue

            if command.lower() == "rentability-enhanced":
                test_enhanced_rentability_endpoint(base_url)
                continue

            if command.lower() == "compare-types":
                test_compare_types_endpoint(base_url)
                continue

            if command.lower() == "ejemplos":
                run_sample_tests(base_url)
                continue

            if command.lower() == "enhanced":
                print("🚀 Probando todas las funcionalidades enhanced...")
                test_enhanced_stats_endpoint(base_url)
                test_enhanced_rentability_endpoint(base_url)
                test_compare_types_endpoint(base_url)

                # Consultas enhanced
                enhanced_test_queries = [
                    "¿Diferencia entre rentabilidad acumulada y anualizada?",
                    "Compara Prima vs Habitat con ambos tipos",
                    "Tabla comparativa con tipos de rentabilidad",
                ]

                for query in enhanced_test_queries:
                    test_chat_endpoint(base_url, query)
                    time.sleep(1)
                continue

            # Tratar como consulta de chat
            test_chat_endpoint(base_url, command)

        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def generate_curl_examples(base_url):
    """Genera ejemplos de comandos curl - ENHANCED VERSION"""
    print_header("EJEMPLOS DE COMANDOS CURL ENHANCED")

    print(
        f"""
🔧 COMANDOS CURL PARA PROBAR LA API ENHANCED:

1️⃣  HEALTH CHECK:
curl -X GET "{base_url}/api/health"

2️⃣  ENHANCED STATS:
curl -X GET "{base_url}/api/system/enhanced-stats"

3️⃣  RENTABILIDAD ENHANCED:
curl -X POST "{base_url}/api/rentability/enhanced" \\
  -H "Content-Type: application/json" \\
  -d '{{"afp_name": "Prima", "fund_type": 0, "calculation_type": "both"}}'

4️⃣  COMPARAR TIPOS:
curl -X POST "{base_url}/api/rentability/compare-types" \\
  -H "Content-Type: application/json" \\
  -d '{{"afp_name": "Habitat", "fund_type": 0}}'

5️⃣  CHAT BÁSICO:
curl -X POST "{base_url}/api/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "¿Cuál es la rentabilidad de Habitat?"}}'

6️⃣  CHAT ENHANCED:
curl -X POST "{base_url}/api/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "¿Diferencia entre rentabilidad acumulada y anualizada?"}}'

💡 TIPS:
   • Usa -v para ver headers detallados
   • Usa -w "\\n%{{time_total}}s\\n" para medir tiempo
   • Usa jq para formatear JSON: | jq .
   • Los endpoints enhanced pueden retornar 501 si no están implementados

🚀 CURL AVANZADO ENHANCED:
curl -X POST "{base_url}/api/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "Compara Prima vs Habitat con tabla de ambos tipos de cálculo"}}' \\
  -w "\\nTiempo total: %{{time_total}}s\\n" | jq .
    """
    )


def main():
    """Función principal - ENHANCED VERSION"""
    print("🚀 INICIANDO PRUEBAS DE API ENDPOINTS ENHANCED")

    # Determinar URL base
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip("/")
    else:
        print("\n🔧 CONFIGURACIÓN DE URL:")
        print("   • Local (Azure Functions Core Tools): http://localhost:7071")
        print("   • Azure Functions: https://tu-function-app.azurewebsites.net")
        print("   • Custom: Especifica tu URL")

        base_url = input("\n📡 URL base (Enter para local): ").strip()
        if not base_url:
            base_url = "http://localhost:7071"

    print(f"\n🎯 Usando URL base: {base_url}")

    # Menú de opciones enhanced
    print(f"\n🎯 ¿Qué quieres hacer?")
    print("   1. Ejecutar pruebas enhanced automáticas")
    print("   2. Modo interactivo enhanced")
    print("   3. Generar ejemplos de curl enhanced")
    print("   4. Solo probar health check")
    print("   5. Solo probar endpoints enhanced")

    while True:
        try:
            choice = input("\n👉 Elige una opción (1-5): ").strip()

            if choice == "1":
                run_sample_tests(base_url)
                break
            elif choice == "2":
                interactive_api_test(base_url)
                break
            elif choice == "3":
                generate_curl_examples(base_url)
                break
            elif choice == "4":
                test_health_endpoint(base_url)
                break
            elif choice == "5":
                print("🚀 Probando solo endpoints enhanced...")
                test_enhanced_stats_endpoint(base_url)
                test_enhanced_rentability_endpoint(base_url)
                test_compare_types_endpoint(base_url)
                break
            else:
                print("❌ Opción inválida. Elige 1, 2, 3, 4 o 5.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

    print_header("PRUEBAS DE API ENHANCED COMPLETADAS")
    print(
        f"""
✅ ENDPOINTS PROBADOS EN: {base_url}

🚀 FUNCIONALIDADES ENHANCED VERIFICADAS:
   • /api/system/enhanced-stats - Estadísticas del sistema enhanced
   • /api/rentability/enhanced - Consultas con tipos de cálculo
   • /api/rentability/compare-types - Comparaciones acumulada vs anualizada
   • /api/chat - Chat con capacidades enhanced mejoradas

📊 ENDPOINTS BÁSICOS FUNCIONANDO:
   • /api/health - Health check del sistema
   • /api/cache/stats - Estadísticas de cache
   • /api/chat - Chat básico del agente

🚀 PRÓXIMOS PASOS:
   • Integrar con aplicación cliente usando endpoints enhanced
   • Configurar autenticación para endpoints si es necesario
   • Monitorear performance de funcionalidades enhanced en producción
   • Implementar rate limiting considerando complejidad enhanced
   
💡 NOTA: Si algunos endpoints enhanced retornan 501, significa que están
definidos pero necesitan implementación manual del código enhanced.
    """
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
        sys.exit(0)
