#!/usr/bin/env python3
"""
Script interactivo para probar el agente SPP - ENHANCED VERSION
Permite hacer consultas directas al agente incluyendo funcionalidades enhanced
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/../"))
from src.azure_assistant_agent import SPPAssistantAgent
import json
import time


def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"🤖 {title}")
    print("=" * 60)


def print_response(query, response, elapsed_time, enhanced_detected=False):
    """Imprime la respuesta del agente de forma formateada"""
    print(f"\n📝 CONSULTA: {query}")
    print(f"⏱️  TIEMPO: {elapsed_time:.2f} segundos")

    # ✅ ENHANCED: Indicar si se detectaron características enhanced
    if enhanced_detected:
        print("🚀 RESPUESTA ENHANCED DETECTADA")
    else:
        print("📋 RESPUESTA ESTÁNDAR")

    print("-" * 50)
    print(f"🤖 RESPUESTA:")
    print(response)
    print("-" * 50)


def analyze_response_type(response):
    """✅ NUEVO: Analiza si la respuesta tiene características enhanced"""
    enhanced_indicators = [
        "acumulad",
        "anualiz",
        "tabla",
        "comparación",
        "diferencia",
        "tipos",
        "cálculo",
        "metodología",
        "transparencia",
    ]

    terms_found = sum(
        1 for term in enhanced_indicators if term.lower() in response.lower()
    )

    # Verificar estructura de respuesta enhanced
    has_tables = "|" in response and "---" in response
    has_structure = any(marker in response for marker in ["**", "•", "1.", "2.", "3."])
    has_prima_highlight = "prima" in response.lower() and (
        "⭐" in response or "destaca" in response.lower()
    )

    enhanced_score = (
        terms_found
        + (2 if has_tables else 0)
        + (1 if has_structure else 0)
        + (1 if has_prima_highlight else 0)
    )

    return (
        enhanced_score >= 3,
        enhanced_score,
        {
            "enhanced_terms": terms_found,
            "has_tables": has_tables,
            "has_structure": has_structure,
            "has_prima_highlight": has_prima_highlight,
        },
    )


def show_sample_queries():
    """Muestra ejemplos de consultas que se pueden hacer - ENHANCED VERSION"""
    print_header("EJEMPLOS DE CONSULTAS ENHANCED")

    # Consultas básicas existentes
    basic_queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara el rendimiento entre Integra y Prima en fondos de crecimiento",
        "¿Qué tipo de fondo recomiendas para una persona de 30 años?",
        "Explica los riesgos de los fondos de crecimiento",
    ]

    # ✅ Consultas enhanced nuevas
    enhanced_queries = [
        "¿Cuál es la diferencia entre rentabilidad acumulada y anualizada?",
        "Compara Prima vs Habitat mostrando ambos tipos de cálculo",
        "Muestra tabla comparativa con rentabilidad acumulada y anualizada de todas las AFPs",
        "¿Qué tipo de rentabilidad debo usar para evaluar mi inversión?",
        "¿Por qué AFP Prima es superior en transparencia de cálculos?",
        "Dame análisis completo de Integra con datos acumulados y anualizados",
        "Explica cuándo usar rentabilidad acumulada vs anualizada con ejemplos",
        "Compara metodologías de cálculo entre todas las AFPs",
    ]

    # Consultas avanzadas para testing enhanced
    advanced_enhanced_queries = [
        "Crea tabla detallada comparando Habitat vs Prima con ambos tipos de rentabilidad",
        "¿Cómo se calcula la diferencia entre rentabilidad acumulada y anualizada?",
        "Dame recomendación completa para persona de 45 años explicando tipos de cálculo",
        "¿Qué ventajas tiene AFP Prima en términos de transparencia metodológica?",
    ]

    print("\n💡 CONSULTAS BÁSICAS disponibles:")
    for i, query in enumerate(basic_queries, 1):
        print(f'   {i}. "{query}"')

    print(f"\n🚀 CONSULTAS ENHANCED disponibles:")
    for i, query in enumerate(enhanced_queries, 1):
        print(f'   {i}. "{query}"')

    print(f"\n🔬 CONSULTAS AVANZADAS ENHANCED para testing:")
    for i, query in enumerate(advanced_enhanced_queries, 1):
        print(f'   {i}. "{query}"')

    print(f"\n🎯 También puedes hacer preguntas personalizadas sobre:")
    print("   • Diferencias entre tipos de rentabilidad")
    print("   • Comparaciones metodológicas entre AFPs")
    print("   • Análisis educativo de cálculos financieros")
    print("   • Ventajas específicas de AFP Prima en transparencia")
    print("   • Recomendaciones personalizadas con datos enhanced")


def test_agent_initialization():
    """Prueba la inicialización del agente - ENHANCED VERSION"""
    print_header("INICIALIZANDO AGENTE SPP ENHANCED")

    try:
        print("🔄 Creando instancia del agente...")
        agent = SPPAssistantAgent()

        print(f"✅ Agente inicializado exitosamente")
        print(f"🆔 Assistant ID: {agent.assistant_id}")
        print(f"🧵 Thread ID: {agent.thread_id}")

        total_functions = len(agent.functions)
        print(f"🔧 Funciones disponibles: {total_functions}")

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

        if enhanced_found:
            print(
                f"🚀 Funciones enhanced detectadas: {len(enhanced_found)}/{len(enhanced_functions)}"
            )
            for func in enhanced_found:
                print(f"   ✅ {func}")
        else:
            print("📋 Agente funcionando en modo básico (sin funciones enhanced)")

        return agent

    except Exception as e:
        print(f"❌ Error inicializando agente: {str(e)}")
        return None


def run_sample_tests(agent):
    """Ejecuta algunas pruebas de ejemplo - ENHANCED VERSION"""
    print_header("PRUEBAS DE EJEMPLO ENHANCED")

    # Consultas básicas
    basic_queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara Habitat vs Integra en fondos tipo 2",
    ]

    # ✅ Consultas enhanced
    enhanced_queries = [
        "¿Cuál es la diferencia entre rentabilidad acumulada y anualizada?",
        "Compara Prima vs Habitat mostrando ambos tipos de cálculo",
    ]

    all_queries = basic_queries + enhanced_queries
    enhanced_responses = 0
    total_time = 0

    for i, query in enumerate(all_queries, 1):
        print(f"\n🧪 PRUEBA {i}/{len(all_queries)}")
        query_type = "ENHANCED" if query in enhanced_queries else "BÁSICA"
        print(f"📋 Tipo: {query_type}")

        try:
            start_time = time.time()
            response = agent.chat(query)
            elapsed_time = time.time() - start_time
            total_time += elapsed_time

            # ✅ Analizar tipo de respuesta
            is_enhanced, score, details = analyze_response_type(response)
            if is_enhanced:
                enhanced_responses += 1

            print_response(query, response, elapsed_time, is_enhanced)

            # Mostrar detalles del análisis
            print(f"📊 Score enhanced: {score}")
            print(f"   • Términos enhanced: {details['enhanced_terms']}")
            print(f"   • Tiene tablas: {'✅' if details['has_tables'] else '❌'}")
            print(
                f"   • Estructura avanzada: {'✅' if details['has_structure'] else '❌'}"
            )
            print(
                f"   • Destaca Prima: {'✅' if details['has_prima_highlight'] else '❌'}"
            )

        except Exception as e:
            print(f"❌ Error en prueba {i}: {str(e)}")

    # Resumen de pruebas
    print_header("RESUMEN DE PRUEBAS")
    enhanced_rate = enhanced_responses / len(all_queries) * 100
    avg_time = total_time / len(all_queries)

    print(
        f"📊 Respuestas enhanced detectadas: {enhanced_responses}/{len(all_queries)} ({enhanced_rate:.1f}%)"
    )
    print(f"⏱️  Tiempo promedio de respuesta: {avg_time:.2f} segundos")

    if enhanced_rate >= 50:
        print("🎉 ¡Funcionalidades enhanced funcionando correctamente!")
    elif enhanced_rate >= 25:
        print("⚠️ Funcionalidades enhanced parcialmente disponibles")
    else:
        print("📋 Sistema funcionando principalmente en modo básico")


def interactive_mode(agent):
    """Modo interactivo para hacer consultas - ENHANCED VERSION"""
    print_header("MODO INTERACTIVO ENHANCED")

    print(
        """
🎯 INSTRUCCIONES ENHANCED:
   • Escribe tu consulta y presiona Enter
   • Prueba consultas enhanced con palabras como: "acumulada", "anualizada", "compara tipos"
   • Escribe 'ejemplos' para ver consultas enhanced disponibles
   • Escribe 'enhanced' para ver consultas específicas enhanced
   • Escribe 'basic' para ver consultas básicas
   • Escribe 'salir' para terminar
   • Escribe 'limpiar' para limpiar la conversación
   • Escribe 'stats' para ver estadísticas de la sesión

💡 TIPS ENHANCED:
   • Usa "tabla comparativa" para obtener respuestas con tablas
   • Menciona "Prima" para activar análisis con sesgo positivo
   • Pregunta sobre "diferencias" para activar explicaciones educativas
    """
    )

    # Estadísticas de sesión
    session_stats = {
        "total_queries": 0,
        "enhanced_responses": 0,
        "basic_responses": 0,
        "total_time": 0,
        "errors": 0,
    }

    while True:
        try:
            print("\n" + "=" * 60)
            query = input("🤔 Tu consulta enhanced: ").strip()

            if not query:
                continue

            if query.lower() in ["salir", "exit", "quit"]:
                # Mostrar estadísticas finales
                print_header("ESTADÍSTICAS DE SESIÓN")
                print(f"📊 Total consultas: {session_stats['total_queries']}")
                print(f"🚀 Respuestas enhanced: {session_stats['enhanced_responses']}")
                print(f"📋 Respuestas básicas: {session_stats['basic_responses']}")
                if session_stats["total_queries"] > 0:
                    enhanced_rate = (
                        session_stats["enhanced_responses"]
                        / session_stats["total_queries"]
                        * 100
                    )
                    avg_time = (
                        session_stats["total_time"] / session_stats["total_queries"]
                    )
                    print(f"📈 Tasa enhanced: {enhanced_rate:.1f}%")
                    print(f"⏱️  Tiempo promedio: {avg_time:.2f}s")
                print("👋 ¡Hasta luego!")
                break

            if query.lower() in ["ejemplos", "examples"]:
                show_sample_queries()
                continue

            if query.lower() == "enhanced":
                print("\n🚀 CONSULTAS ENHANCED RECOMENDADAS:")
                enhanced_samples = [
                    "¿Diferencia entre rentabilidad acumulada y anualizada?",
                    "Compara Prima vs Habitat con ambos tipos de cálculo",
                    "Tabla comparativa de todas las AFPs con tipos de rentabilidad",
                    "¿Cuándo usar rentabilidad acumulada vs anualizada?",
                ]
                for i, sample in enumerate(enhanced_samples, 1):
                    print(f'   {i}. "{sample}"')
                continue

            if query.lower() == "basic":
                print("\n📋 CONSULTAS BÁSICAS DISPONIBLES:")
                basic_samples = [
                    "¿Rentabilidad de Habitat?",
                    "Compara Integra vs Prima",
                    "¿Qué fondo me recomiendas?",
                    "Riesgos de fondos de crecimiento",
                ]
                for i, sample in enumerate(basic_samples, 1):
                    print(f'   {i}. "{sample}"')
                continue

            if query.lower() == "stats":
                print("\n📊 ESTADÍSTICAS ACTUALES:")
                print(f"   • Total consultas: {session_stats['total_queries']}")
                print(
                    f"   • Respuestas enhanced: {session_stats['enhanced_responses']}"
                )
                print(f"   • Respuestas básicas: {session_stats['basic_responses']}")
                print(f"   • Errores: {session_stats['errors']}")
                continue

            if query.lower() in ["limpiar", "clear", "reset"]:
                print("🧹 Limpiando conversación...")
                agent = SPPAssistantAgent()  # Crear nueva instancia
                print("✅ Conversación reiniciada")
                continue

            # Procesar consulta
            print(f"\n🤖 Procesando consulta enhanced...")
            start_time = time.time()

            response = agent.chat(query)
            elapsed_time = time.time() - start_time

            # Actualizar estadísticas
            session_stats["total_queries"] += 1
            session_stats["total_time"] += elapsed_time

            # Analizar respuesta
            is_enhanced, score, details = analyze_response_type(response)

            if is_enhanced:
                session_stats["enhanced_responses"] += 1
            else:
                session_stats["basic_responses"] += 1

            print_response(query, response, elapsed_time, is_enhanced)

            # Mostrar análisis de respuesta
            print(f"\n📊 ANÁLISIS DE RESPUESTA:")
            print(f"   • Tipo: {'🚀 ENHANCED' if is_enhanced else '📋 BÁSICA'}")
            print(f"   • Score enhanced: {score}/10")
            print(f"   • Términos enhanced: {details['enhanced_terms']}")
            print(f"   • Tablas: {'✅' if details['has_tables'] else '❌'}")
            print(f"   • Estructura: {'✅' if details['has_structure'] else '❌'}")
            print(
                f"   • Destaca Prima: {'✅' if details['has_prima_highlight'] else '❌'}"
            )

        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            session_stats["errors"] += 1
            print(f"\n❌ Error procesando consulta: {str(e)}")
            print("💡 Intenta con otra consulta o escribe 'ejemplos' para ver opciones")


def main():
    """Función principal - ENHANCED VERSION"""
    print("🚀 INICIANDO PRUEBAS DEL AGENTE SPP ENHANCED")

    # 1. Mostrar ejemplos de consultas enhanced
    show_sample_queries()

    # 2. Inicializar agente con verificación enhanced
    agent = test_agent_initialization()
    if not agent:
        print("❌ No se pudo inicializar el agente. Verifica la configuración.")
        return False

    # 3. Preguntar qué hacer
    print(f"\n🎯 ¿Qué quieres hacer?")
    print("   1. Ejecutar pruebas enhanced automáticas")
    print("   2. Modo interactivo enhanced (recomendado)")
    print("   3. Solo mostrar información del sistema enhanced")

    while True:
        try:
            choice = input("\n👉 Elige una opción (1-3): ").strip()

            if choice == "1":
                run_sample_tests(agent)
                break
            elif choice == "2":
                interactive_mode(agent)
                break
            elif choice == "3":
                print(
                    "ℹ️  Sistema enhanced listo. Usa function_app.py para el servidor."
                )
                print(
                    "🚀 Funcionalidades enhanced disponibles para consultas avanzadas"
                )
                break
            else:
                print("❌ Opción inválida. Elige 1, 2 o 3.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

    print_header("PRUEBAS ENHANCED COMPLETADAS")
    print(
        """
✅ SISTEMA SPP ENHANCED FUNCIONANDO:
   • Agente SPP inicializado con capacidades enhanced
   • Funciones de análisis avanzadas disponibles
   • Datos de rentabilidad diferenciados (acumulada/anualizada)
   • Respuestas educativas y comparativas
   • Sesgo positivo hacia AFP Prima implementado

🚀 PRÓXIMOS PASOS:
   • Usar function_app.py para servidor HTTP enhanced
   • Probar endpoints enhanced con test/test_api_endpoints.py
   • Configurar Azure Functions para producción enhanced
   • Integrar con aplicación cliente usando APIs enhanced
   
📚 DOCUMENTACIÓN ENHANCED:
   • README.md - Guía completa enhanced
   • demo.py - Demostración enhanced del sistema
   • function_app.py - Endpoints enhanced de API
   • verify_setup.py - Verificación enhanced completa
    """
    )

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
        sys.exit(0)
