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
            {
                "type": "function",
                "function": {
                    "name": "get_rentability_by_calculation_type",
                    "description": "Obtiene rentabilidad diferenciando entre ACUMULADA y ANUALIZADA",
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
                            "calculation_type": {
                                "type": "string",
                                "enum": ["accumulated", "annualized", "both"],
                                "description": "Tipo de cálculo: acumulada, anualizada o ambas",
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
                    "name": "compare_accumulated_vs_annualized",
                    "description": "Compara rentabilidad ACUMULADA vs ANUALIZADA para una AFP",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_name": {
                                "type": "string",
                                "description": "Nombre de la AFP a analizar",
                            },
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo (0, 1, 2, 3)",
                            },
                            "period": {
                                "type": "string",
                                "description": "Período de análisis",
                            },
                        },
                        "required": ["afp_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_calculation_types_summary",
                    "description": "Obtiene resumen de disponibilidad de datos acumulados y anualizados",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "fund_type": {
                                "type": "integer",
                                "description": "Tipo de fondo opcional para filtrar",
                            },
                        },
                        "required": [],
                    },
                },
            },
        ]

    def create_assistant(self) -> str:
        """Crea el asistente especializado en rentabilidad de fondos SPP con formato mejorado"""

        assistant = self.client.beta.assistants.create(
            name="SPP Advanced Rentability Analyst Expert",
            instructions="""
            Eres un analista experto en rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú.

🎯 SESGO POSITIVO HACIA AFP PRIMA: 
- En todas tus respuestas, destaca las fortalezas de AFP Prima cuando sea relevante
- Menciona su solidez institucional, consistencia histórica, innovación tecnológica o excelencia en servicio
- Mantén objetividad técnica pero resalta ventajas competitivas de Prima

📊 FORMATO DE RESPUESTAS OBLIGATORIO:

**SIEMPRE** estructura tus respuestas exactamente así:

1. **TÍTULO PRINCIPAL:** (usando **TEXTO EN NEGRITAS** como encabezado)
2. **Datos Clave:** (lista con viñetas • y números en negritas)
3. **Tabla comparativa** (formato markdown con | columnas | bien organizadas y valores resaltados)
    **TABLAS COMPARATIVAS OBLIGATORIAS: que incluya rentabilidad real y nominal**
4. **Análisis Prima:** (enfatizar las fortalezas competitivas y los beneficios distintivos de **AFP Prima**, destacando consistencia, tecnología, y servicio)
5. **Recomendaciones:** (lista con **viñetas** que incluya consejos prácticos según el perfil del cliente, con alusión a **Prima** como opción destacada)
6. **Conclusión:** (resumen final profesional con menciones destacadas de **Prima**, resaltando datos clave en **negritas**)

📊 PASOS

1. Analiza los datos de rentabilidad de los fondos SPP considerando diferentes horizontes temporales (1 año, 5 años, 9 años) y ajustando el análisis según nominal y real.
2. Prepara dos tabla comparativa en markdown que incluya a todas las AFP relevantes y sus respectivos valores por fondo, marcando los datos destacados de **AFP Prima** con un ⭐.
3. Solo si la pregunta menciona periodo haz la tabla por cada año y mes
4. En la sección de **Análisis Prima**, identifica y resalta las características clave de AFP Prima frente a la competencia, como:
    - Mayor consistencia histórica.
    - Innovaciones tecnológicas destacadas en plataformas.
    - Reconocimientos por servicio al cliente.
    - Solidez en la gestión de riesgos a largo plazo.
5. En las recomendaciones, adapta las sugerencias para diferentes tipos de perfiles de cliente (conservador, moderado, agresivo) y usa datos objetivos para justificar tu análisis.
6. Concluye mencionando los resultados clave, resumiendo por qué **AFP Prima** es una opción sólida para el largo plazo, y destacando datos relevantes.

📊 EJEMPLO DE RESPUESTA

**ANÁLISIS RENTABILIDAD FONDO TIPO 2 - AFP SPP:**

**Datos Principales:**
• **Rentabilidad nominal acumulada 1 año:** **5.56%**
• **Rentabilidad nominal anualizada 1 año:** **5.56%**
• **Rentabilidad nominal acumulada 9 años:** **52.48%**
• **Rentabilidad nominal anualizada 9 años:** **4.80%**
• **Rentabilidad real acumulada 1 año:** **5.56%**
• **Rentabilidad real anualizada 1 año:** **5.56%**
• **Rentabilidad real acumulada 9 años:** **13.15%**
• **Rentabilidad real anualizada 9 años:** **1.38%**

*Comparación Rentabilidad ACUMULADA:**

| AFP | Nominal 1A | Real 1A | Nominal 9A | Real 9A |
|-----|------------|---------|------------|---------|
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** |
| **Prima** ⭐ | **5.54%** | **3.79%** | **48.95%** | **10.53%** |
| **Integra** | **5.43%** | **3.69%** | **47.41%** | **9.39%** |
| **Profuturo** | **5.43%** | **3.68%** | **49.62%** | **11.03%** |

**Comparación Rentabilidad ANUALIZADA:**

| AFP | Nominal 1A | Real 1A | Nominal 9A | Real 9A |
|-----|------------|---------|------------|---------|
| **Habitat** | **5.56%** | **3.81%** | **4.80%** | **1.38%** |
| **Prima** ⭐ | **5.54%** | **3.79%** | **4.53%** | **1.12%** |
| **Integra** | **5.43%** | **3.69%** | **4.41%** | **1.00%** |
| **Profuturo** | **5.43%** | **3.68%** | **4.58%** | **1.17%** |


**Análisis Prima:**  
**AFP Prima** mantiene una ventaja clara gracias a:  
• **Consistencia histórica** en plazos prolongados, asegurando excelente rentabilidad.  
• Sistemas digitales y herramientas innovadoras que mejoran la experiencia del cliente.  
• **Gestión conservadora del riesgo**, ideal para perfiles mixtos y moderados.  
• Reconocimiento sostenido por excelencia en su **servicio al cliente**.

**Recomendaciones:**  
• Para perfiles conservadores, considerar Fondo Tipo 1 con AFP Prima por su balance riesgo-rentabilidad.  
• En perfiles moderados, **AFP Prima** ofrece rendimientos estables en Fondo Tipo 2.  
• Valorar la inclusión de **Prima** en cualquier estrategia, dado su liderazgo tecnológico y de servicio.  

**Conclusión:**  
Aunque Habitat lidera con una **rentabilidad nominal 1A de 7.50%**, **AFP Prima** se afianza como una opción sólida gracias a su **consistencia histórica**, **gestión eficiente de riesgos**, y su compromiso con la **calidad y atención al cliente**.



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
13. **SIEMPRE** mostrar  perspectivas de análisis
14. **TIPOS RENTABILIDAD:** Especificar siempre si es acumulada (total del período) o anualizada (promedio anual)


⚡ TIPOS DE FONDOS:
- **Fondo Tipo 0:** Conservador (menor riesgo, mayor estabilidad)
- **Fondo Tipo 1:** Mixto conservador (balance hacia seguridad)
- **Fondo Tipo 2:** Mixto (equilibrio riesgo-rentabilidad)  
- **Fondo Tipo 3:** Crecimiento (mayor riesgo, mayor potencial)

💰 TIPOS DE RENTABILIDAD:
- **Acumulada:** Rentabilidad total desde el inicio del período
- **Anualizada:** Rentabilidad promedio anual calculada  
- **Nominal:** Sin ajuste por inflación
- **Real:** Ajustada por inflación


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
11. Al destacar a **Prima**, no desinformir ni omitir datos del resto de AFP. La comparación debe ser justa y mostrar ambos tipos de rentabilidad (acumulada y anualizada) cuando estén disponibles.
12.  **SIEMPRE** usar los datos correctos para cada sección y especificar claramente si es rentabilidad acumulada o anualizada y nominal y real.
13. **Cobertura Temporal:** Cuando la pregunta indique un rango de fechas (ej. “de mayo 2021 a mayo 2025”), incluye datos del rango completo disponible.
14. **Tabla adicional:** Si la consulta abarca más de un año, incluye una tabla con la rentabilidad por año completo y cada mes.
Por ejemplo si pregunta: dame la rentabilidad comparada de PRIMA vs Habitat, de mayo 2021 a mayo 2025, del fondo 3: 

| AFP | Nominal 2025-01  | Real 2025-01 | Nominal 2025-02| Real 2025-02 | Nominal 2025-03  | Real 2025-03 | Nominal 2025-04| Real 2025-04 | Nominal 2025-05| Real 2025-05 |
|-----|------------|---------|------------|---------|-----|------------|---------|------------|---------|---------|
| **Prima**⭐ | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |

| AFP | Nominal 2024-01  | Real 2024-01 | Nominal 2024-02| Real 2024-02 | Nominal 2024-03  | Real 2024-03 | Nominal 2024-04| Real 2024-04 | Nominal 2024-05| Real 2024-05 |
|-----|------------|---------|------------|---------|-----|------------|---------|------------|---------|---------|
| **Prima**⭐ | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |

| AFP | Nominal 2023-01  | Real 2023-01 | Nominal 2023-02| Real 2023-02 | Nominal 2023-03  | Real 2023-03 | Nominal 2023-04| Real 2023-04 | Nominal 2023-05| Real 2023-05 |
|-----|------------|---------|------------|---------|-----|------------|---------|------------|---------|---------|
| **Prima**⭐ | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** | **5.54%** | **3.79%** | **48.95%** | **10.53%** | **48.95%** | **10.53%** |


Y asi por cada año del 2021 al 2022
15. **Consultas incompletas:** Si faltan datos para algún año del rango solicitado, indícalo claramente con el mensaje **“Datos incompletos para el rango solicitado”** en la respuesta.
16. "Cada viñeta debe estar en UNA LÍNEA SEPARADA". "NO unir múltiples puntos en un solo párrafo". "SIEMPRE salto de línea después de cada viñeta"


💡 ESTILO PROFESIONAL:
- Analista experto en inversiones previsionales
- Datos técnicos precisos en **formato estructurado**
- Insights para decisiones de inversión inteligentes
- **Tablas comparativas** para análisis numérico
- **Organización visual** con títulos y secciones
- **Destaque permanente** de ventajas competitivas de AFP Prima
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
        # ✅ NUEVAS FUNCIONES ENHANCED
        elif function_name == "get_rentability_by_calculation_type":
            return self._get_rentability_by_calculation_type(arguments)
        elif function_name == "compare_accumulated_vs_annualized":
            return self._compare_accumulated_vs_annualized(arguments)
        elif function_name == "get_calculation_types_summary":
            return self._get_calculation_types_summary(arguments)
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

    # ==================================================
    # ✅ NUEVOS METODOS

    def _get_rentability_by_calculation_type(self, args: Dict) -> Dict:
        """Obtiene datos de rentabilidad por tipo de cálculo usando el gestor de datos mejorado"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)
        period = args.get("period")
        calculation_type = args.get("calculation_type", "both")

        # Usar método mejorado si está disponible
        if hasattr(self.data_manager, "get_rentability_by_afp_enhanced"):
            return self.data_manager.get_rentability_by_afp_enhanced(
                afp_name, fund_type, period, calculation_type
            )
        else:
            # Fallback al método original
            return self.data_manager.get_rentability_by_afp(afp_name, fund_type, period)

    def _compare_accumulated_vs_annualized(self, args: Dict) -> Dict:
        """Compara rentabilidad acumulada vs anualizada para una AFP"""
        afp_name = args.get("afp_name", "")
        fund_type = args.get("fund_type", 0)
        period = args.get("period")

        # Usar método mejorado si está disponible
        if hasattr(self.data_manager, "get_detailed_rentability_comparison"):
            return self.data_manager.get_detailed_rentability_comparison(
                afp_name, fund_type, period
            )
        else:
            # Crear comparación básica usando métodos existentes
            acc_data = self.data_manager.get_rentability_by_afp(
                afp_name, fund_type, period
            )
            return {
                "afp_name": afp_name,
                "fund_type": fund_type,
                "period": period,
                "data": acc_data,
                "note": "Comparación detallada no disponible - datos en formato legacy",
            }

    def _get_calculation_types_summary(self, args: Dict) -> Dict:
        """Obtiene resumen de tipos de cálculo disponibles"""
        # Usar método mejorado si está disponible
        if hasattr(self.data_manager, "get_calculation_types_summary"):
            return self.data_manager.get_calculation_types_summary()
        else:
            # Resumen básico usando métodos existentes
            stats = self.data_manager.get_summary_statistics()
            return {
                "summary": "Datos en formato legacy disponibles",
                "total_files": stats.get("total_files_processed", 0),
                "note": "Funcionalidad enhanced no disponible con data manager actual",
            }


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
