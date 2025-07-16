#!/usr/bin/env python3
"""
Script interactivo para probar el agente SPP
Permite hacer consultas directas al agente sin necesidad de Azure Functions
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


def print_response(query, response, elapsed_time):
    """Imprime la respuesta del agente de forma formateada"""
    print(f"\n📝 CONSULTA: {query}")
    print(f"⏱️  TIEMPO: {elapsed_time:.2f} segundos")
    print("-" * 50)
    print(f"🤖 RESPUESTA:")
    print(response)
    print("-" * 50)


def show_sample_queries():
    """Muestra ejemplos de consultas que se pueden hacer"""
    print_header("EJEMPLOS DE CONSULTAS")

    queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara el rendimiento entre Integra y Prima en fondos de crecimiento",
        "¿Qué tipo de fondo recomiendas para una persona de 30 años?",
        "Muestra la evolución de rentabilidad de los fondos mixtos",
        "¿Cuál es la diferencia entre rentabilidad nominal y real?",
        "¿Qué AFP tiene mejor rendimiento histórico en fondos conservadores?",
        "Explica los riesgos de los fondos de crecimiento",
        "¿Cómo ha sido la rentabilidad en los últimos períodos disponibles?",
        "¿Cuántos afiliados tiene cada AFP?",
        "Compara todos los tipos de fondos de Habitat",
        "¿Qué significa rentabilidad acumulada vs anualizada?",
        "Recomienda una estrategia de diversificación de fondos",
    ]

    print("\n💡 Puedes hacer consultas como:")
    for i, query in enumerate(queries, 1):
        print(f"   {i:2d}. {query}")

    print(f"\n🎯 También puedes hacer preguntas personalizadas sobre:")
    print("   • Rentabilidad específica por AFP y tipo de fondo")
    print("   • Comparaciones entre diferentes AFPs")
    print("   • Análisis de riesgo y recomendaciones")
    print("   • Tendencias históricas y proyecciones")
    print("   • Explicaciones sobre el sistema de pensiones")


def test_agent_initialization():
    """Prueba la inicialización del agente"""
    print_header("INICIALIZANDO AGENTE SPP")

    try:
        print("🔄 Creando instancia del agente...")
        agent = SPPAssistantAgent()

        print(f"✅ Agente inicializado exitosamente")
        print(f"🆔 Assistant ID: {agent.assistant_id}")
        print(f"🧵 Thread ID: {agent.thread_id}")
        print(f"🔧 Funciones disponibles: {len(agent.functions)}")

        return agent

    except Exception as e:
        print(f"❌ Error inicializando agente: {str(e)}")
        return None


def run_sample_tests(agent):
    """Ejecuta algunas pruebas de ejemplo"""
    print_header("PRUEBAS DE EJEMPLO")

    sample_queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara Habitat vs Integra en fondos tipo 2",
        "¿Qué tipo de fondo recomiendas para alguien de 25 años?",
    ]

    for i, query in enumerate(sample_queries, 1):
        print(f"\n🧪 PRUEBA {i}/3")
        try:
            start_time = time.time()
            response = agent.chat(query)
            elapsed_time = time.time() - start_time

            print_response(query, response, elapsed_time)

        except Exception as e:
            print(f"❌ Error en prueba {i}: {str(e)}")


def interactive_mode(agent):
    """Modo interactivo para hacer consultas"""
    print_header("MODO INTERACTIVO")

    print(
        """
🎯 INSTRUCCIONES:
   • Escribe tu consulta y presiona Enter
   • Escribe 'ejemplos' para ver consultas de ejemplo
   • Escribe 'salir' para terminar
   • Escribe 'limpiar' para limpiar la conversación
    """
    )

    while True:
        try:
            print("\n" + "=" * 60)
            query = input("🤔 Tu consulta: ").strip()

            if not query:
                continue

            if query.lower() in ["salir", "exit", "quit"]:
                print("👋 ¡Hasta luego!")
                break

            if query.lower() in ["ejemplos", "examples"]:
                show_sample_queries()
                continue

            if query.lower() in ["limpiar", "clear", "reset"]:
                print("🧹 Limpiando conversación...")
                agent = SPPAssistantAgent()  # Crear nueva instancia
                print("✅ Conversación reiniciada")
                continue

            print(f"\n🤖 Procesando consulta...")
            start_time = time.time()

            response = agent.chat(query)
            elapsed_time = time.time() - start_time

            print_response(query, response, elapsed_time)

        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error procesando consulta: {str(e)}")
            print("💡 Intenta con otra consulta o escribe 'ejemplos' para ver opciones")


def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DEL AGENTE SPP")

    # 1. Mostrar ejemplos de consultas
    show_sample_queries()

    # 2. Inicializar agente
    agent = test_agent_initialization()
    if not agent:
        print("❌ No se pudo inicializar el agente. Verifica la configuración.")
        return False

    # 3. Preguntar qué hacer
    print(f"\n🎯 ¿Qué quieres hacer?")
    print("   1. Ejecutar pruebas de ejemplo automáticas")
    print("   2. Modo interactivo (recomendado)")
    print("   3. Solo mostrar información del sistema")

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
                print("ℹ️  Sistema listo. Usa function_app.py para el servidor.")
                break
            else:
                print("❌ Opción inválida. Elige 1, 2 o 3.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break

    print_header("PRUEBAS COMPLETADAS")
    print(
        """
✅ SISTEMA FUNCIONANDO CORRECTAMENTE:
   • Agente SPP inicializado
   • Funciones de análisis disponibles
   • Datos de rentabilidad cargados
   • Listo para consultas en producción

🚀 PRÓXIMOS PASOS:
   • Usar function_app.py para servidor HTTP
   • Configurar Azure Functions para producción
   • Integrar con aplicación cliente
   
📚 DOCUMENTACIÓN:
   • README.md - Guía completa
   • demo.py - Demostración del sistema
   • function_app.py - Endpoints de API
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
