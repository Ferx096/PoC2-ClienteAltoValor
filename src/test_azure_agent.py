#!/usr/bin/env python3
"""
Test del Azure Agent usando las credenciales reales
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_agent import SPPAgent
import json

def test_agent():
    """Prueba el agente con consultas reales"""
    
    print("🚀 Inicializando SPP Agent...")
    agent = SPPAgent()
    
    # Consultas de prueba
    test_queries = [
        "¿Cuántos afiliados activos tiene Habitat?",
        "¿Cuántos afiliados jóvenes hay en el sistema?",
        "Compara el número de afiliados entre Habitat e Integra",
        "¿Cuál es la distribución por sexo en las AFPs?",
        "¿Cuáles son las tendencias de afiliación en enero 2025?"
    ]
    
    print("\n📊 Ejecutando consultas de prueba...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{'='*60}")
        print(f"CONSULTA {i}: {query}")
        print(f"{'='*60}")
        
        try:
            result = agent.process_query(query)
            
            print(f"🔍 Clasificación: {result['classification']['query_type']}")
            print(f"📈 Fuentes: SQL={result['sources']['sql_results']}, Search={result['sources']['search_results']}")
            print(f"\n💬 Respuesta:")
            print(result['response'])
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

if __name__ == "__main__":
    test_agent()