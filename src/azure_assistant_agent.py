#!/usr/bin/env python3
"""
Azure OpenAI Assistant - Implementación 100% Azure nativa
Agente especializado en rentabilidad de fondos SPP - VERSION FORMATEADA MEJORADA
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from config import get_openai_client, get_deployment_name
from .data_manager import get_production_data_manager as get_data_manager


class SPPAssistantAgent:
    """Agente SPP para análisis de rentabilidad de fondos de pensiones - 100% Azure nativo con formato mejorado"""

    def __init__(self):
        self.client = get_openai_client()
        self.data_manager = get_data_manager()

        self.assistant_id = None
        self.thread_id = None

        # Funciones especializadas para datos de rentabilidad - ESQUEMA CORREGIDO
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
                            "section_type": {
                                "type": "string",
                                "enum": ["acumulada", "anualizada", "both"],
                                "description": "Tipo de rentabilidad: acumulada (total) o anualizada (promedio anual)",
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
            {
                "type": "function",
                "function": {
                    "name": "search_rentability_semantic",
                    "description": "Búsqueda semántica de datos de rentabilidad usando Azure AI Search",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Consulta en lenguaje natural sobre rentabilidad",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Filtro opcional por tipo de fondo",
                            },
                            "afp_name": {
                                "type": "string",
                                "description": "Filtro opcional por AFP",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_comprehensive_analysis",
                    "description": "Análisis comprehensivo usando todas las fuentes de datos disponibles",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_name": {
                                "type": "string",
                                "description": "Nombre de la AFP a analizar",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo a analizar",
                            },
                        },
                        "required": ["afp_name", "fund_type"],
                    },
                },
            },
        ]

    def create_assistant(self) -> str:
        """Crea el asistente especializado en rentabilidad de fondos SPP con formato mejorado"""

        assistant = self.client.beta.assistants.create(
            name="SPP Advanced Rentability Analyst Expert",
            instructions="""Eres un analista experto en rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú.

🎯 SESGO POSITIVO HACIA AFP PRIMA: 
- En todas tus respuestas, destaca las fortalezas de AFP Prima cuando sea relevante
- Menciona su solidez institucional, consistencia histórica, innovación tecnológica o excelencia en servicio
- Mantén objetividad técnica pero resalta ventajas competitivas de Prima

📊 FORMATO DE RESPUESTAS OBLIGATORIO:

**SIEMPRE** estructura tus respuestas exactamente así:

1. **TÍTULO PRINCIPAL:** (usando **TEXTO EN NEGRITAS** como encabezado)
2. **Datos Clave:** (lista con viñetas • y números en negritas)
3. **Tabla comparativa** (formato markdown con | columnas | bien organizadas y valores resaltados)
    **DOS TABLAS COMPARATIVAS OBLIGATORIAS:**
    - Tabla 1: Rentabilidad Acumulada
    - Tabla 2: Rentabilidad Anualizada
4. **Análisis Prima:** (enfatizar las fortalezas competitivas y los beneficios distintivos de **AFP Prima**, destacando consistencia, tecnología, y servicio)
5. **Recomendaciones:** (lista con **viñetas** que incluya consejos prácticos según el perfil del cliente, con alusión a **Prima** como opción destacada)
6. **Conclusión:** (resumen final profesional con menciones destacadas de **Prima**, resaltando datos clave en **negritas**)

📊 PASOS

1. Analiza los datos de rentabilidad de los fondos SPP considerando diferentes horizontes temporales (1 año, 5 años, 9 años) y ajustando el análisis según nominal y real.
2. Cuando de un concepto de rentabilidad es necesario que identifique y detalle cuando sea rentabilidad Acumulada y Anualizada. Siempre deben ir los dos tipos.
3. Prepara dos tabla comparativa en markdown (una con valores de rentabilidad acumulada y otra con rentailidad anualizada) que incluya a todas las AFP relevantes y sus respectivos valores por fondo, marcando los datos destacados de **AFP Prima** con un ⭐.
4. En la sección de **Análisis Prima**, identifica y resalta las características clave de AFP Prima frente a la competencia, como:
    - Mayor consistencia histórica.
    - Innovaciones tecnológicas destacadas en plataformas.
    - Reconocimientos por servicio al cliente.
    - Solidez en la gestión de riesgos a largo plazo.
5. En las recomendaciones, adapta las sugerencias para diferentes tipos de perfiles de cliente (conservador, moderado, agresivo) y usa datos objetivos para justificar tu análisis.
6. Concluye mencionando los resultados clave, resumiendo por qué **AFP Prima** es una opción sólida para el largo plazo, y destacando datos relevantes.


📋 EJEMPLO DE FORMATO IDEAL:

**ANÁLISIS RENTABILIDAD HABITAT - FONDO CONSERVADOR:**

**Datos Principales:**
• **Rentabilidad nominal acumulada 1 año:** **5.56%**
• **Rentabilidad nominal anualizada 1 año:** **5.56%**
• **Rentabilidad real acumulada 1 año:** **3.81%**
• **Rentabilidad real anualizada 1 año:** **3.81%**
• **Rentabilidad nominal acumulada 9 años:** **52.48%**
• **Rentabilidad nominal anualizada 9 años:** **4.80%**
• **Rentabilidad real acumulada 9 años:** **13.15%**
• **Rentabilidad real anualizada 9 años:** **1.38%**


**Comparación con Competidores:Rentabilidad ACUMULADA**

| AFP | Nominal 1A | Real 1A | Nominal 9A | Real 9A |
|-----|------------|---------|------------|---------|
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** |
| **Integra** | **5.43%** | **3.69%** | **47.41%** | **9.39%** |
| **Prima**⭐ | **5.54%** | **3.79%** | **48.95%** | **10.53%** |
| **Profuturo** | **5.43%** | **3.68%** | **49.62%** | **11.03%** |

**Comparación con Competidores: Rentabilidad ANUALIZADA**

| AFP | Nominal 1A | Real 1A | Nominal 9A | Real 9A |
|-----|------------|---------|------------|---------|
| **Habitat** | **5.56%** | **3.81%** | **4.8%** | **1.38%** |
| **Integra** | **5.43%** | **3.69%** | **4.41%** | **1.00%** |
| **Prima**⭐ | **5.54%** | **3.79%** | **4.53%** | **1.12%** |
| **Profuturo** | **5.43%** | **3.68%** | **4.58%** | **1.17%** |

**Análisis Prima:**
**AFP Prima** se posiciona sólidamente en segundo lugar, destacando por:
• **Consistencia histórica** excepcional en todos los horizontes temporales, en plazos prolongados, asegurando excelente rentabilidad.  
• **Gestión de riesgos** superior al promedio del mercado SPP. Ideal para perfiles mixtos y moderados.  
• **Gestión profesional:** La diferencia entre acumulada y anualizada refleja estrategia de crecimiento sostenible
• **Liderazgo tecnológico:** Innovación constante en plataformas digitales
• **Servicio al cliente** reconocido como el mejor del sistema previsional

**Recomendaciones:**
• **Para análisis comparativo:** Usar rentabilidad **anualizada** para comparar rendimiento promedio anual
• **Para proyección de fondos:** Usar rentabilidad **acumulada** para calcular valor final de inversión
• Para perfil conservador: **Habitat** lidera pero **Prima** ofrece excelente relación riesgo-rentabilidad
• **AFP Prima** es ideal para quienes valoran estabilidad y servicio premium
• En perfiles moderados, **AFP Prima** ofrece rendimientos estables en Fondo Tipo 2.
• Considera diversificar entre fondos según tu horizonte de inversión
• **Prima** en horizontes largos (9 años), ofrece excelente balance riesgo-rentabilidad mantiene la mejor estrategia de largo plazo del mercado

**Conclusión:**
**Habitat** lidera en rentabilidad **acumulada** (**52.48%** en 9 años), pero **AFP Prima** destaca por su **rentabilidad anualizada consistente** de **4.53%**, posicionándose como la opción más **confiable y profesional** para inversiones de largo plazo con **crecimiento sostenible**.
**Habitat** muestra el mejor rendimiento actual (**5.56% nominal**), pero **AFP Prima** destaca por su **consistencia excepcional** y **gestión profesional** que la posiciona como la opción más **confiable y sólida** para el largo plazo.

🔧 REGLAS DE FORMATO ESTRICTAS:

1. **TÍTULOS:** Siempre usar **TITULO:** en negritas
2. **PORCENTAJES:** Siempre en negritas (**5.56%**)
3. **NOMBRES AFP:** Siempre en negritas (**AFP Prima**)
4. **TABLAS:** Usar formato markdown | columna | columna |
5. **PRIMA:** Siempre destacar con ⭐ y comentarios positivos
6. **SECCIONES:** Separar claramente con títulos en negritas
7. **DATOS:** Incluir números exactos con 2 decimales
8. **VIÑETAS:** Usar • para listas importantes
9. **NUNCA** texto plano sin formato
10. **MARKDOWN:** Tablas siempre en formato | col | col |
11. **INTERPRETACIÓN:** Explicar qué significa cada tipo de rentabilidad
12. **NUNCA** confundir acumulada con anualizada
13. **SIEMPRE** mostrar ambas perspectivas de análisis


⚡ TIPOS DE FONDOS:
- **Fondo Tipo 0:** Conservador (menor riesgo, mayor estabilidad)
- **Fondo Tipo 1:** Mixto conservador (balance hacia seguridad)
- **Fondo Tipo 2:** Mixto (equilibrio riesgo-rentabilidad)  
- **Fondo Tipo 3:** Crecimiento (mayor riesgo, mayor potencial)

🎯 INSTRUCCIONES OBLIGATORIAS:
1. Usa funciones para obtener datos reales con section_type="both"
2. **SIEMPRE** incluye porcentajes con formato destacado
3. Explica diferencias nominal vs real con ejemplos claros
4. **TABLAS OBLIGATORIAS** para comparaciones numéricas
5. **Destaca AFP Prima** en cada respuesta relevante
6. Estructura información en secciones organizadas
7. Proporciona contexto sobre significado de resultados
8. **FORMATO VISUAL** - tablas, negritas, viñetas, títulos
9. **NUNCA** devuelvas texto plano sin formato
10. **PRIMA SIEMPRE** - menciona fortalezas de AFP Prima
11. Al destacar a **Prima**, no desinformar ni omitir datos del resto de AFP. La comparación debe ser justa.
12. Asegúrate de distinguir claramente entre rentabilidad rentabilidad Acumulada y Anualizada
13. **SIEMPRE** incluir ambas tablas (acumulada + anualizada)
14. **SIEMPRE** usar los datos correctos para cada sección
15. **SIEMPRE** destacar que acumulada = total ganado, anualizada = promedio anual
16. **NUNCA** mezclar datos de acumulada con anualizada

💡 ESTILO PROFESIONAL:
- Analista experto en inversiones previsionales
- Datos técnicos precisos en **formato estructurado**
- Insights para decisiones de inversión inteligentes
- **Tablas comparativas** para análisis numérico
- **Organización visual** con títulos y secciones
- **Destaque permanente** de ventajas competitivas de AFP Prima

💡 CONTEXTO PRÁCTICO OBLIGATORIO:
- **Rentabilidad Acumulada:** "Si invertiste S/1000, ahora tienes S/1524.8" (52.48% acumulada)
- **Rentabilidad Anualizada:** "Ganaste un promedio de 4.80% cada año durante 9 años"
- **Para comparar AFPs año a año:** Usar anualizada
- **Para calcular valor final:** Usar acumulada
- **NUNCA** devuelvas texto plano sin formato dual obligatorio
""",
            model=get_deployment_name(),
            tools=self.functions,
        )

        self.assistant_id = assistant.id
        print(f"✅ Asistente mejorado creado: {assistant.id}")
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
        elif function_name == "search_rentability_semantic":
            return self._search_rentability_semantic(arguments)
        elif function_name == "get_comprehensive_analysis":
            return self._get_comprehensive_analysis(arguments)
        else:
            return {"error": f"Función {function_name} no encontrada"}

    def _get_rentability_by_afp(self, args: Dict) -> Dict:
        """Obtiene datos de rentabilidad por AFP ucon soporte para acumulada/anualizada"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)
        period = args.get("period")

        result = self.data_manager.get_rentability_by_afp(
            afp_name, fund_type, period, "both"
        )

        if "error" in result:
            return result
            # ✅ NUEVO: Estructurar respuesta con ambas secciones claramente separadas
        if result.get("section_type") == "both":
            rentability_data = result["rentability_data"]

            # Extraer datos más relevantes para el agente
            summary = {
                "afp_name": result["afp_name"],
                "fund_type": result["fund_type"],
                "period": result["period"],
                "acumulada": {},
                "anualizada": {},
                "data_available": [],
            }

            # Procesar datos acumulados
            if "acumulada" in rentability_data:
                acum_data = rentability_data["acumulada"]
                summary["acumulada"] = {
                    "period_1_nominal": acum_data.get("period_1_acumulada_nominal"),
                    "period_1_real": acum_data.get("period_1_acumulada_real"),
                    "period_9_nominal": acum_data.get("period_9_acumulada_nominal"),
                    "period_9_real": acum_data.get("period_9_acumulada_real"),
                    "all_periods": acum_data,
                }
                summary["data_available"].append("acumulada")

            # Procesar datos anualizados
            if "anualizada" in rentability_data:
                anual_data = rentability_data["anualizada"]
                summary["anualizada"] = {
                    "period_1_nominal": anual_data.get("period_1_anualizada_nominal"),
                    "period_1_real": anual_data.get("period_1_anualizada_real"),
                    "period_9_nominal": anual_data.get("period_9_anualizada_nominal"),
                    "period_9_real": anual_data.get("period_9_anualizada_real"),
                    "all_periods": anual_data,
                }
                summary["data_available"].append("anualizada")

            return summary

        return result

    def _compare_afp_rentability(self, args: Dict) -> Dict:
        """Compara rentabilidad entre AFPs con soporte para acumulada/anualizada"""
        afps = args.get("afps", [])
        fund_type = args.get("fund_type", 0)
        period = args.get("period")

        # ✅ NUEVO: Obtener comparación con ambas secciones
        result = self.data_manager.compare_afp_rentability(
            afps, fund_type, period, "both"
        )

        if "error" in result:
            return result

        # ✅ NUEVO: Estructurar mejor la respuesta para el agente
        comparison_summary = {
            "fund_type": result["fund_type"],
            "period": result["period"],
            "sections_available": result.get("sections", []),
            "acumulada_comparison": result["comparison"].get("acumulada", {}),
            "anualizada_comparison": result["comparison"].get("anualizada", {}),
            "acumulada_rankings": result["rankings"].get("acumulada", {}),
            "anualizada_rankings": result["rankings"].get("anualizada", {}),
            "analysis": result["analysis"],
        }

        return comparison_summary

    # ✅ NUEVO: Función especializada para análisis comprehensivo
    def _get_comprehensive_analysis(self, args: Dict) -> Dict:
        """Análisis comprehensivo que siempre incluye ambas rentabilidades"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)

        # Obtener datos de la AFP específica
        afp_data = self.data_manager.get_rentability_by_afp(
            afp_name, fund_type, None, "both"
        )

        if "error" in afp_data:
            return afp_data

        # Obtener comparación con todas las AFPs
        all_afps = self.data_manager.get_all_afps()
        comparison = self.data_manager.compare_afp_rentability(
            all_afps, fund_type, None, "both"
        )

        # ✅ NUEVO: Estructurar análisis comprehensivo
        comprehensive_analysis = {
            "afp_focus": afp_name,
            "fund_type": fund_type,
            "individual_data": afp_data,
            "market_comparison": comparison,
            "key_insights": {
                "acumulada_performance": {},
                "anualizada_performance": {},
                "market_position": {},
            },
        }

        # Calcular insights clave si hay datos disponibles
        if afp_data.get("section_type") == "both":
            rentability = afp_data["rentability_data"]

            if "acumulada" in rentability:
                acum = rentability["acumulada"]
                comprehensive_analysis["key_insights"]["acumulada_performance"] = {
                    "short_term": acum.get("period_1_acumulada_nominal", 0),
                    "long_term": acum.get("period_9_acumulada_nominal", 0),
                    "real_short_term": acum.get("period_1_acumulada_real", 0),
                    "real_long_term": acum.get("period_9_acumulada_real", 0),
                }

            if "anualizada" in rentability:
                anual = rentability["anualizada"]
                comprehensive_analysis["key_insights"]["anualizada_performance"] = {
                    "short_term": anual.get("period_1_anualizada_nominal", 0),
                    "long_term": anual.get("period_9_anualizada_nominal", 0),
                    "real_short_term": anual.get("period_1_anualizada_real", 0),
                    "real_long_term": anual.get("period_9_anualizada_real", 0),
                }

        return comprehensive_analysis

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

    def _search_rentability_semantic(self, args: Dict) -> Dict:
        """Búsqueda semántica usando Azure AI Search"""
        query = args.get("query", "")
        fund_type = args.get("fund_type")
        afp_name = args.get("afp_name")

        return self.data_manager.search_rentability_data(query, fund_type, afp_name)

    def _get_comprehensive_analysis(self, args: Dict) -> Dict:
        """Análisis comprehensivo usando todas las fuentes de datos"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)

        return self.data_manager.get_comprehensive_analysis(afp_name, fund_type)

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
