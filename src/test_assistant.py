#!/usr/bin/env python3
"""
Test del Azure OpenAI Assistant - Implementación recomendada
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_assistant_agent import SPPAssistantAgent

def test_assistant():
    """Prueba el Azure OpenAI Assistant"""
    
    print("🚀 Inicializando Azure OpenAI Assistant...")
    assistant = SPPAssistantAgent()
    
    # Consultas de prueba específicas para SPP
    test_queries = [
        "¿Cuántos afiliados activos tiene Habitat en enero 2025?",
        "Compara los afiliados entre Habitat e Integra",
        "¿Cuál es la distribución por sexo en las AFPs?",
        "Analiza las tendencias de afiliación",
        "¿Qué AFP tiene mayor participación de mercado?"
    ]
    
    print("\n📊 Ejecutando consultas con Azure OpenAI Assistant...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{'='*70}")
        print(f"CONSULTA {i}: {query}")
        print(f"{'='*70}")
        
        try:
            response = assistant.chat(query)
            print(f"💬 Respuesta del Assistant:")
            print(response)
            print(f"\n{'='*70}\n")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    print(f"✅ Assistant ID: {assistant.assistant_id}")
    print(f"✅ Thread ID: {assistant.thread_id}")

if __name__ == "__main__":
    test_assistant()