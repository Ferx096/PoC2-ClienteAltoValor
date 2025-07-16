#!/usr/bin/env python3
"""
Script para probar los endpoints de la API usando requests
Útil para probar la Azure Function localmente o en producción
"""
import requests
import json
import time
import sys

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🌐 {title}")
    print("="*60)

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
            print(f"✅ Respuesta:")
            print(f"🤖 {data.get('response', 'Sin respuesta')}")
            print(f"🆔 Assistant ID: {data.get('assistant_id', 'N/A')}")
            print(f"🧵 Thread ID: {data.get('thread_id', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error conectando: {str(e)}")

def run_sample_tests(base_url):
    """Ejecuta una serie de pruebas de ejemplo"""
    print_header("EJECUTANDO PRUEBAS DE EJEMPLO")
    
    # 1. Health check
    test_health_endpoint(base_url)
    
    # 2. Assistant info
    test_assistant_info_endpoint(base_url)
    
    # 3. Consultas de ejemplo
    sample_queries = [
        "¿Cuál es la rentabilidad de Habitat en el fondo conservador?",
        "Compara Habitat vs Integra en fondos tipo 2",
        "¿Qué tipo de fondo recomiendas para alguien de 25 años?"
    ]
    
    for query in sample_queries:
        test_chat_endpoint(base_url, query)
        time.sleep(1)  # Pausa entre consultas

def interactive_api_test(base_url):
    """Modo interactivo para probar la API"""
    print_header("MODO INTERACTIVO - PRUEBAS DE API")
    
    print(f"""
🎯 PROBANDO API EN: {base_url}

💡 COMANDOS DISPONIBLES:
   • Escribe tu consulta para probar /api/chat
   • 'health' - Probar /api/health
   • 'info' - Probar /api/assistant/info
   • 'ejemplos' - Ejecutar pruebas de ejemplo
   • 'salir' - Terminar
    """)
    
    while True:
        try:
            print("\n" + "-"*50)
            command = input("🤔 Comando o consulta: ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
                
            if command.lower() == 'health':
                test_health_endpoint(base_url)
                continue
                
            if command.lower() == 'info':
                test_assistant_info_endpoint(base_url)
                continue
                
            if command.lower() == 'ejemplos':
                run_sample_tests(base_url)
                continue
            
            # Tratar como consulta de chat
            test_chat_endpoint(base_url, command)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def generate_curl_examples(base_url):
    """Genera ejemplos de comandos curl"""
    print_header("EJEMPLOS DE COMANDOS CURL")
    
    print(f"""
🔧 COMANDOS CURL PARA PROBAR LA API:

1️⃣  HEALTH CHECK:
curl -X GET "{base_url}/api/health"

2️⃣  ASSISTANT INFO:
curl -X GET "{base_url}/api/assistant/info"

3️⃣  CHAT QUERY:
curl -X POST "{base_url}/api/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "¿Cuál es la rentabilidad de Habitat?"}}'

4️⃣  CONSULTA COMPLEJA:
curl -X POST "{base_url}/api/chat" \\
  -H "Content-Type: application/json" \\
  -d '{{"query": "Compara todas las AFPs en fondos conservadores"}}'

💡 TIPS:
   • Usa -v para ver headers detallados
   • Usa -w "\\n%{{time_total}}s\\n" para medir tiempo
   • Usa jq para formatear JSON: | jq .
    """)

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE API ENDPOINTS")
    
    # Determinar URL base
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        print("\n🔧 CONFIGURACIÓN DE URL:")
        print("   • Local (Azure Functions Core Tools): http://localhost:7071")
        print("   • Azure Functions: https://tu-function-app.azurewebsites.net")
        print("   • Custom: Especifica tu URL")
        
        base_url = input("\n📡 URL base (Enter para local): ").strip()
        if not base_url:
            base_url = "http://localhost:7071"
    
    print(f"\n🎯 Usando URL base: {base_url}")
    
    # Menú de opciones
    print(f"\n🎯 ¿Qué quieres hacer?")
    print("   1. Ejecutar pruebas de ejemplo automáticas")
    print("   2. Modo interactivo")
    print("   3. Generar ejemplos de curl")
    print("   4. Solo probar health check")
    
    while True:
        try:
            choice = input("\n👉 Elige una opción (1-4): ").strip()
            
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
            else:
                print("❌ Opción inválida. Elige 1, 2, 3 o 4.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
    
    print_header("PRUEBAS DE API COMPLETADAS")
    print(f"""
✅ ENDPOINTS PROBADOS EN: {base_url}

🚀 PRÓXIMOS PASOS:
   • Integrar con aplicación cliente
   • Configurar autenticación si es necesario
   • Monitorear performance en producción
   • Implementar rate limiting si es necesario
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
        sys.exit(0)