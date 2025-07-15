#!/usr/bin/env python3
"""
Azure OpenAI Assistant - Implementación 100% Azure nativa
Recomendación principal para el agente SPP
"""
import os
import json
import time
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
from config import AZURE_CONFIG

class SPPAssistantAgent:
    """Agente SPP usando Azure OpenAI Assistants API - 100% Azure nativo"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_CONFIG["endpoint"],
            api_key=AZURE_CONFIG["api_key"],
            api_version=AZURE_CONFIG["api_version"]
        )
        
        self.assistant_id = None
        self.thread_id = None
        
        # Funciones especializadas para datos SPP
        self.functions = [
            {
                "type": "function",
                "function": {
                    "name": "get_afiliados_by_afp",
                    "description": "Obtiene información de afiliados activos por AFP específica",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_name": {
                                "type": "string",
                                "description": "Nombre de la AFP (Habitat, Integra, Prima, Profuturo)"
                            },
                            "period": {
                                "type": "string", 
                                "description": "Período en formato YYYY-MM"
                            },
                            "demographic_filter": {
                                "type": "object",
                                "description": "Filtros demográficos (sexo, edad, departamento)"
                            }
                        },
                        "required": ["afp_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_afps",
                    "description": "Compara métricas entre diferentes AFPs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista de AFPs a comparar"
                            },
                            "metrics": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Métricas a comparar (afiliados_activos, nuevos_afiliados, traspasos)"
                            },
                            "period": {
                                "type": "string",
                                "description": "Período de comparación"
                            }
                        },
                        "required": ["afps", "metrics"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "analyze_demographics",
                    "description": "Analiza distribución demográfica de afiliados",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "demographic_type": {
                                "type": "string",
                                "enum": ["age", "gender", "department", "income"],
                                "description": "Tipo de análisis demográfico"
                            },
                            "afp_filter": {
                                "type": "string",
                                "description": "AFP específica o 'all' para todas"
                            },
                            "period": {
                                "type": "string",
                                "description": "Período de análisis"
                            }
                        },
                        "required": ["demographic_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_trends",
                    "description": "Analiza tendencias temporales en el SPP",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "metric": {
                                "type": "string",
                                "description": "Métrica a analizar (afiliados, traspasos, nuevos)"
                            },
                            "time_range": {
                                "type": "object",
                                "properties": {
                                    "start_period": {"type": "string"},
                                    "end_period": {"type": "string"}
                                }
                            },
                            "grouping": {
                                "type": "string",
                                "enum": ["monthly", "quarterly", "yearly"],
                                "description": "Agrupación temporal"
                            }
                        },
                        "required": ["metric"]
                    }
                }
            }
        ]
    
    def create_assistant(self) -> str:
        """Crea el asistente especializado en SPP"""
        
        assistant = self.client.beta.assistants.create(
            name="SPP Data Analyst Expert",
            instructions="""Eres un analista experto del Sistema Privado de Pensiones (SPP) de Perú.

ESPECIALIZACIÓN:
- Análisis de datos de afiliados activos por AFP
- Comparaciones entre AFPs (Habitat, Integra, Prima, Profuturo)
- Análisis demográficos (edad, sexo, departamento)
- Tendencias de afiliación y traspasos
- Estadísticas del mercado previsional privado

DATOS DISPONIBLES:
- Boletines mensuales del SPP
- Número de afiliados activos por AFP, sexo y edad
- Distribución geográfica por departamentos
- Nuevos afiliados y solicitudes de traspaso
- Evolución temporal de métricas clave

INSTRUCCIONES:
1. Usa las funciones disponibles para obtener datos específicos
2. Proporciona números exactos cuando estén disponibles
3. Explica tendencias y patrones relevantes
4. Compara AFPs cuando sea apropiado
5. Indica claramente las fuentes y períodos de los datos
6. Si no tienes información específica, indícalo claramente

ESTILO DE RESPUESTA:
- Profesional y técnico
- Datos precisos con contexto
- Insights relevantes para el sector previsional
- Formato claro y estructurado""",
            
            model=AZURE_CONFIG["deployment_name"],
            tools=self.functions
        )
        
        self.assistant_id = assistant.id
        print(f"✅ Asistente creado: {assistant.id}")
        return assistant.id
    
    def create_thread(self) -> str:
        """Crea un hilo de conversación"""
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        print(f"✅ Hilo creado: {thread.id}")
        return thread.id
    
    def add_message(self, content: str) -> str:
        """Añade un mensaje al hilo"""
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=content
        )
        return message.id
    
    def run_assistant(self) -> Dict[str, Any]:
        """Ejecuta el asistente y maneja function calling"""
        
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        
        # Esperar a que complete o requiera acción
        while run.status in ['queued', 'in_progress', 'requires_action']:
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )
            
            # Manejar function calling
            if run.status == 'requires_action':
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Ejecutar función
                    result = self.execute_function(function_name, arguments)
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                
                # Enviar resultados
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        
        return run
    
    def execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """Ejecuta las funciones especializadas del SPP"""
        
        if function_name == "get_afiliados_by_afp":
            return self._get_afiliados_by_afp(arguments)
        elif function_name == "compare_afps":
            return self._compare_afps(arguments)
        elif function_name == "analyze_demographics":
            return self._analyze_demographics(arguments)
        elif function_name == "get_trends":
            return self._get_trends(arguments)
        else:
            return {"error": f"Función {function_name} no encontrada"}
    
    def _get_afiliados_by_afp(self, args: Dict) -> Dict:
        """Obtiene datos de afiliados por AFP"""
        afp_name = args.get("afp_name", "").lower()
        
        # Datos simulados basados en el Excel real
        afp_data = {
            "habitat": {
                "afiliados_activos": 1026513,
                "porcentaje_hombres": 55.49,
                "porcentaje_mujeres": 44.51,
                "participacion_mercado": 10.43,
                "periodo": "2025-01"
            },
            "integra": {
                "afiliados_activos": 4759854,
                "porcentaje_hombres": 52.1,
                "porcentaje_mujeres": 47.9,
                "participacion_mercado": 48.34,
                "periodo": "2025-01"
            }
        }
        
        return afp_data.get(afp_name, {"error": f"AFP {afp_name} no encontrada"})
    
    def _compare_afps(self, args: Dict) -> Dict:
        """Compara métricas entre AFPs"""
        afps = args.get("afps", [])
        metrics = args.get("metrics", [])
        
        comparison = {}
        for afp in afps:
            afp_data = self._get_afiliados_by_afp({"afp_name": afp})
            if "error" not in afp_data:
                comparison[afp] = afp_data
        
        return {
            "comparison": comparison,
            "metrics_requested": metrics,
            "period": "2025-01"
        }
    
    def _analyze_demographics(self, args: Dict) -> Dict:
        """Analiza distribución demográfica"""
        demo_type = args.get("demographic_type")
        
        if demo_type == "gender":
            return {
                "analysis_type": "gender",
                "data": {
                    "habitat": {"hombres": 55.49, "mujeres": 44.51},
                    "integra": {"hombres": 52.1, "mujeres": 47.9}
                },
                "insights": "Los hombres representan mayor proporción en ambas AFPs"
            }
        elif demo_type == "age":
            return {
                "analysis_type": "age",
                "data": {
                    "jovenes_21_30": "35% del total",
                    "adultos_31_50": "45% del total", 
                    "mayores_50": "20% del total"
                },
                "insights": "Concentración en población económicamente activa"
            }
        
        return {"error": f"Tipo demográfico {demo_type} no disponible"}
    
    def _get_trends(self, args: Dict) -> Dict:
        """Analiza tendencias temporales"""
        metric = args.get("metric")
        
        return {
            "metric": metric,
            "trend": "crecimiento_moderado",
            "data": {
                "2024-12": 9500000,
                "2025-01": 9786367
            },
            "growth_rate": "3.0% mensual",
            "insights": f"Tendencia positiva en {metric}"
        }
    
    def get_response(self) -> str:
        """Obtiene la respuesta del asistente"""
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread_id,
            order="desc",
            limit=1
        )
        
        return messages.data[0].content[0].text.value
    
    def chat(self, user_message: str) -> str:
        """Interfaz principal de chat"""
        
        # Crear asistente y hilo si no existen
        if not self.assistant_id:
            self.create_assistant()
        if not self.thread_id:
            self.create_thread()
        
        # Procesar mensaje
        self.add_message(user_message)
        run = self.run_assistant()
        
        if run.status == 'completed':
            return self.get_response()
        else:
            return f"Error: {run.status}"

# Función para Azure Functions
def main(req):
    """Endpoint para Azure Functions"""
    assistant = SPPAssistantAgent()
    
    try:
        req_body = req.get_json()
        user_query = req_body.get('query', '')
        
        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter required"})
            }
        
        response = assistant.chat(user_query)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "query": user_query,
                "response": response,
                "assistant_id": assistant.assistant_id,
                "thread_id": assistant.thread_id
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }