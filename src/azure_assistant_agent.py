#!/usr/bin/env python3
"""
Azure OpenAI Assistant - Implementación 100% Azure nativa
Agente especializado en rentabilidad de fondos SPP
"""
import os
import json
import time
from typing import Dict, List, Any, Optional
from config import get_openai_client, get_deployment_name
from .data_manager import get_data_manager


class SPPAssistantAgent:
    """Agente SPP para análisis de rentabilidad de fondos de pensiones - 100% Azure nativo"""

    def __init__(self):
        self.client = get_openai_client()
        self.data_manager = get_data_manager()

        self.assistant_id = None
        self.thread_id = None

        # Funciones especializadas para datos de rentabilidad
        self.functions = [
            {
                "type": "function",
                "function": {
                    "name": "get_rentability_by_afp",
                    "description": "Obtiene información de rentabilidad por AFP específica",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_name": {
                                "type": "string",
                                "description": "Nombre de la AFP (Habitat, Integra, Prima, Profuturo)",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo (0, 1, 2, 3)",
                            },
                            "period": {
                                "type": "string",
                                "description": "Período en formato YYYY-MM",
                            },
                            "rentability_type": {
                                "type": "string",
                                "enum": ["nominal", "real", "both"],
                                "description": "Tipo de rentabilidad a consultar",
                            },
                        },
                        "required": ["afp_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_afp_rentability",
                    "description": "Compara rentabilidad entre diferentes AFPs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista de AFPs a comparar",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo (0, 1, 2, 3)",
                            },
                            "period": {
                                "type": "string",
                                "description": "Período de comparación",
                            },
                            "rentability_type": {
                                "type": "string",
                                "enum": ["nominal", "real", "both"],
                                "description": "Tipo de rentabilidad a comparar",
                            },
                        },
                        "required": ["afps"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_fund_performance",
                    "description": "Analiza el rendimiento de diferentes tipos de fondos",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "fund_types": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Tipos de fondos a analizar (0, 1, 2, 3)",
                            },
                            "afp_filter": {
                                "type": "string",
                                "description": "AFP específica o 'all' para todas",
                            },
                            "period": {
                                "type": "string",
                                "description": "Período de análisis",
                            },
                            "time_horizon": {
                                "type": "string",
                                "enum": [
                                    "1_year",
                                    "2_years",
                                    "3_years",
                                    "5_years",
                                    "all",
                                ],
                                "description": "Horizonte temporal de análisis",
                            },
                        },
                        "required": ["fund_types"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_historical_trends",
                    "description": "Analiza tendencias históricas de rentabilidad",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_name": {
                                "type": "string",
                                "description": "AFP específica o 'all' para todas",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo",
                            },
                            "time_periods": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Períodos a analizar",
                            },
                            "analysis_type": {
                                "type": "string",
                                "enum": ["evolution", "volatility", "consistency"],
                                "description": "Tipo de análisis temporal",
                            },
                        },
                        "required": ["afp_name", "fund_type"],
                    },
                },
            },
        ]

    def create_assistant(self) -> str:
        """Crea el asistente especializado en rentabilidad de fondos SPP"""

        assistant = self.client.beta.assistants.create(
            name="SPP Rentability Analyst Expert",
            instructions="""Eres un analista experto en rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú.

ESPECIALIZACIÓN:
- Análisis de rentabilidad nominal y real de fondos de pensiones
- Comparaciones de rendimiento entre AFPs (Habitat, Integra, Prima, Profuturo)
- Análisis de diferentes tipos de fondos (Tipo 0, 1, 2, 3)
- Evaluación de horizontes temporales (1 año, 2 años, 3 años, etc.)
- Tendencias históricas de rentabilidad

DATOS DISPONIBLES:
- Reportes de rentabilidad acumulada y anualizada por AFP
- Datos de rentabilidad nominal y real por tipo de fondo
- Información histórica de múltiples períodos
- Comparaciones temporales de rendimiento
- Datos actualizados hasta 2025

TIPOS DE FONDOS:
- Fondo Tipo 0: Conservador (menor riesgo, menor rentabilidad esperada)
- Fondo Tipo 1: Mixto conservador
- Fondo Tipo 2: Mixto
- Fondo Tipo 3: Crecimiento (mayor riesgo, mayor rentabilidad esperada)

INSTRUCCIONES:
1. Usa las funciones disponibles para obtener datos específicos de rentabilidad
2. Proporciona porcentajes exactos de rentabilidad cuando estén disponibles
3. Explica diferencias entre rentabilidad nominal y real
4. Compara rendimiento entre AFPs y tipos de fondos
5. Analiza tendencias temporales y horizontes de inversión
6. Indica claramente las fuentes, períodos y tipos de datos
7. Proporciona contexto sobre el significado de los resultados

ESTILO DE RESPUESTA:
- Profesional y técnico especializado en inversiones
- Datos precisos con análisis contextual
- Insights relevantes para decisiones de inversión previsional
- Formato claro con comparaciones y recomendaciones
- Explicaciones sobre riesgo y rentabilidad""",
            model=get_deployment_name(),
            tools=self.functions,
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
            thread_id=self.thread_id, role="user", content=content
        )
        return message.id

    def run_assistant(self) -> Dict[str, Any]:
        """Ejecuta el asistente y maneja function calling"""

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id, assistant_id=self.assistant_id
        )

        # Esperar a que complete o requiera acción
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=run.id
            )

            # Manejar function calling
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Ejecutar función
                    result = self.execute_function(function_name, arguments)

                    tool_outputs.append(
                        {"tool_call_id": tool_call.id, "output": json.dumps(result)}
                    )

                # Enviar resultados
                run = self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread_id, run_id=run.id, tool_outputs=tool_outputs
                )

        return run

    def execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """Ejecuta las funciones especializadas de rentabilidad SPP"""

        if function_name == "get_rentability_by_afp":
            return self._get_rentability_by_afp(arguments)
        elif function_name == "compare_afp_rentability":
            return self._compare_afp_rentability(arguments)
        elif function_name == "analyze_fund_performance":
            return self._analyze_fund_performance(arguments)
        elif function_name == "get_historical_trends":
            return self._get_historical_trends(arguments)
        else:
            return {"error": f"Función {function_name} no encontrada"}

    def _get_rentability_by_afp(self, args: Dict) -> Dict:
        """Obtiene datos de rentabilidad por AFP usando el gestor de datos"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)
        period = args.get("period")

        return self.data_manager.get_rentability_by_afp(afp_name, fund_type, period)

    def _compare_afp_rentability(self, args: Dict) -> Dict:
        """Compara rentabilidad entre AFPs usando el gestor de datos"""
        afps = args.get("afps", [])
        fund_type = args.get("fund_type", 0)
        period = args.get("period")

        return self.data_manager.compare_afp_rentability(afps, fund_type, period)

    def _analyze_fund_performance(self, args: Dict) -> Dict:
        """Analiza el rendimiento de diferentes tipos de fondos usando el gestor de datos"""
        fund_types = args.get("fund_types", [0])
        afp_filter = args.get("afp_filter", "all")

        return self.data_manager.analyze_fund_performance(fund_types, afp_filter)

    def _get_historical_trends(self, args: Dict) -> Dict:
        """Analiza tendencias históricas de rentabilidad"""
        afp_name = args.get("afp_name", "all")
        fund_type = args.get("fund_type", 0)
        analysis_type = args.get("analysis_type", "evolution")

        # Obtener datos disponibles para análisis temporal
        available_periods = self.data_manager.get_available_periods(fund_type)

        if not available_periods:
            return {"error": f"No hay datos disponibles para fondo tipo {fund_type}"}

        # Análisis básico con datos disponibles
        if analysis_type == "evolution":
            evolution_data = {}
            for period in available_periods:
                if afp_name != "all":
                    afp_data = self.data_manager.get_rentability_by_afp(
                        afp_name, fund_type, period
                    )
                    if "error" not in afp_data:
                        rentability = afp_data["rentability_data"]
                        if "period_1_nominal" in rentability:
                            evolution_data[period] = rentability["period_1_nominal"]
                else:
                    # Promedio de todas las AFPs
                    comparison = self.data_manager.compare_afp_rentability(
                        self.data_manager.get_all_afps(), fund_type, period
                    )
                    if "comparison" in comparison and comparison["comparison"]:
                        values = []
                        for afp_data in comparison["comparison"].values():
                            if "period_1_nominal" in afp_data:
                                values.append(afp_data["period_1_nominal"])
                        if values:
                            evolution_data[period] = sum(values) / len(values)

            return {
                "afp_name": afp_name,
                "fund_type": fund_type,
                "analysis_type": analysis_type,
                "historical_data": evolution_data,
                "available_periods": available_periods,
                "insights": f"Evolución temporal de rentabilidad para {afp_name} - Fondo Tipo {fund_type}",
            }

        return {
            "afp_name": afp_name,
            "fund_type": fund_type,
            "analysis_type": analysis_type,
            "available_periods": available_periods,
            "insights": f"Análisis de {analysis_type} disponible con datos históricos limitados",
        }

    def get_response(self) -> str:
        """Obtiene la respuesta del asistente"""
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread_id, order="desc", limit=1
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

        if run.status == "completed":
            return self.get_response()
        else:
            return f"Error: {run.status}"


# Función para Azure Functions
def main(req):
    """Endpoint para Azure Functions"""
    assistant = SPPAssistantAgent()

    try:
        req_body = req.get_json()
        user_query = req_body.get("query", "")

        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter required"}),
            }

        response = assistant.chat(user_query)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "query": user_query,
                    "response": response,
                    "assistant_id": assistant.assistant_id,
                    "thread_id": assistant.thread_id,
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
