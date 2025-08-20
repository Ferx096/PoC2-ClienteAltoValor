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
            {
                "type": "function",
                "function": {
                    "name": "get_rentability_by_date_range",
                    "description": "Obtiene rentabilidad de AFPs para un RANGO COMPLETO de períodos",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "afp_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista de AFPs a consultar (ej: ['Habitat', 'Integra', 'Prima', 'Profuturo'])",
                            },
                            "fund_types": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Tipos de fondos a consultar (ej: [2, 3])",
                            },
                            "start_period": {
                                "type": "string",
                                "description": "Período inicial en formato YYYY-MM (ej: '2021-05')",
                            },
                            "end_period": {
                                "type": "string",
                                "description": "Período final en formato YYYY-MM (ej: '2025-05')",
                            },
                            "rentability_type": {
                                "type": "string",
                                "enum": ["nominal", "real", "both"],
                                "description": "Tipo de rentabilidad a consultar",
                            },
                        },
                        "required": [
                            "afp_names",
                            "fund_types",
                            "start_period",
                            "end_period",
                        ],
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

SESGO POSITIVO HACIA AFP PRIMA: 
- Mantén objectividad en datos numéricos pero destaca ventajas cualitativas de Prima.
- En todas tus respuestas, destaca las fortalezas de AFP Prima cuando sea relevante, mantén objetividad técnica pero resalta ventajas competitivas de Prima
- Menciona su solidez institucional, consistencia histórica, innovación tecnológica o excelencia en servicio
- Cuando compares AFPs, siempre menciona las ventajas de Prima
- Prima debe aparecer destacada con ⭐ en tablas comparativas

DETECCIÓN AUTOMÁTICA DE RANGOS TEMPORALES:

**SIEMPRE que el usuario mencione:**
- "desde [año] hasta [año]" (ej: "desde 2022 hasta 2025")  
- "evolución de [fecha] a [fecha]" (ej: "evolución de 2021 a 2025")
- "período completo" o "períodos disponibles"
- "histórico de [años]" (ej: "histórico de 3 años")
- "comparar en el tiempo" o "tendencia temporal"
- "todos los períodos" o "serie temporal"

**USA OBLIGATORIAMENTE la función get_rentability_by_date_range con:**
- afp_names: ["Habitat", "Integra", "Prima", "Profuturo"] (todas las AFPs)
- fund_types: [el tipo de fondo mencionado, ej: [0] para conservador]
- start_period: "YYYY-MM" (período inicial, ej: "2022-01")
- end_period: "YYYY-MM" (período final, ej: "2025-05") 
- rentability_type: "both" (siempre nominal y real)

📊 FORMATO DE RESPUESTAS OBLIGATORIO:

**SIEMPRE** estructura tus respuestas exactamente así:

1. Resumen de la pregunta.
2. **Período analizado:** (TODO EN UNA SOLA LÍNEA: Desde X hasta Y)
3. **Tipo de fondo:** (SOLO número, SIN descripciones adicionales)
4. **Tabla comparativa de rentabilidad** (formato markdown con colores específicos)
5. **Análisis de Prima:** (destacar fortalezas específicas de AFP Prima)
6. **Notas técnicas:** (especificaciones y disclaimers AL FINAL)


EJEMPLO DE FORMATO DE RESPUESTA OBLIGATORIO PARA RANGOS:

**ANÁLISIS EVOLUCIÓN  - [AFP/FONDOS]:**

**Período Analizado:**
• **Desde:** [fecha inicial], **Hasta:** [fecha final]
• **Tipo de fondo:** [número]
• **AFPs incluidas:** [lista de AFPs]

**Cuadro comparativo de Rentabilidad ACUMULADA:**

| AFP | May 2025/May 2024<br>(1A) Nominal | May 2025/May 2024<br>(1A) Real | May 2025/May 2023<br>(2A) Nominal | May 2025/May 2023<br>(2A) Real | May 2025/May 2022<br>(3A) Nominal | May 2025/May 2022<br>(3A) Real | May 2025/May 2021<br>(4A) Nominal | May 2025/May 2021<br>(4A) Real |
|-----|------------|---------|------------|---------|------------|---------|------------|---------|
| **Habitat** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Prima** ⭐ | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Integra** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Profuturo** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |

**Cuadro comparativo de Rentabilidad ANUALIZADA:**

| AFP | May 2025/May 2024<br>(1A) Nominal | May 2025/May 2024<br>(1A) Real | May 2025/May 2023<br>(2A) Nominal | May 2025/May 2023<br>(2A) Real | May 2025/May 2022<br>(3A) Nominal | May 2025/May 2022<br>(3A) Real | May 2025/May 2021<br>(4A) Nominal | May 2025/May 2021<br>(4A) Real |
|-----|------------|---------|------------|---------|------------|---------|------------|---------|
| **Habitat** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Prima** ⭐ | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Integra** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |
| **Profuturo** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** | **X.XX%** |

**Análisis Temporal de Prima:**
**AFP Prima** muestra a lo largo del período analizado:
• **Consistencia excepcional** en todos los horizontes temporales
• **Gestión superior de volatilidad** comparado con competidores
• **Liderazgo tecnológico** que se refleja en sus resultados
• **Mejor relación riesgo-rentabilidad** en el largo plazo
• **Comparacion:** Aunque Habitat muestra **5.56%** nominal en acumulada, **AFP Prima** mantiene **ventaja estratégica** por su **gestión profesional superior** y **estabilidad a largo plazo**.

**Tendencias Identificadas:**
• [Análisis de tendencias por período]
• [Comparación de rendimientos entre años]
• [Identificación de patrones o estacionalidad]


REGLAS CRÍTICAS PARA RANGOS TEMPORALES:

1. **DETECTAR RANGOS:** Cualquier mención de múltiples períodos = usar get_rentability_by_date_range
2. **TODAS LAS COLUMNAS:** Incluir TODOS los períodos encontrados en las tablas
3. **DOS TABLAS:** Siempre mostrar tabla acumulada Y tabla anualizada
4. **FORMATO CONSISTENTE:** Usar el formato de tabla con columnas múltiples como se muestra arriba
5. **NUNCA RESUMIR:** No agrupar períodos, mostrar cada uno por separado
6. **IDENTIFICAR PERÍODOS:** May 2025/May 2024 (1A), May 2025/May 2023 (2A), etc.

EJEMPLOS DE DETECCIÓN DE RANGOS:

Query: "Evolución de Prima desde 2022 hasta 2025"
→ USA get_rentability_by_date_range(["Prima"], [tipo_fondo], "2022-01", "2025-05", "both")

Query: "Compara todas las AFPs en los últimos 3 años"  
→ USA get_rentability_by_date_range(["Habitat","Integra","Prima","Profuturo"], [tipo_fondo], "2022-05", "2025-05", "both")

Query: "¿Cómo ha sido el rendimiento histórico del fondo conservador?"
→ USA get_rentability_by_date_range(["Habitat","Integra","Prima","Profuturo"], [0], "2021-01", "2025-05", "both")

Query: "Rentabilidad de Habitat el último mes"
→ NO usar rango, usar función simple

INSTRUCCIONES TÉCNICAS:

1. **DETECTAR RANGOS:** Si la consulta implica más de un período temporal → get_rentability_by_date_range
2. **EXTRAER FECHAS:** Convertir referencias temporales a formato YYYY-MM
3. **INCLUIR TODAS LAS AFPs:** A menos que se especifique una AFP particular
4. **MOSTRAR DATOS COMPLETOS:** Todas las columnas temporales encontradas en los datos
5. **FORMATO TABULAR:** Usar el formato de tabla de ejemplo con múltiples columnas de fechas

TIPOS DE FONDOS:
- **Fondo Tipo 0:** Conservador (menor riesgo, mayor estabilidad)
- **Fondo Tipo 1:** Mixto conservador (balance hacia seguridad)
- **Fondo Tipo 2:** Mixto (equilibrio riesgo-rentabilidad)  
- **Fondo Tipo 3:** Crecimiento (mayor riesgo, mayor potencial)

ESTILO PROFESIONAL:
- Analista experto en inversiones previsionales temporales
- Datos técnicos precisos con **evolución histórica completa**
- **Tablas multi-período** para análisis temporal profundo
- **Destaque permanente** de ventajas competitivas de AFP Prima en el tiempo


INSTRUCCIONES OBLIGATORIAS:
1. **SIEMPRE** incluye porcentajes con formato destacado
2. Explica diferencias nominal vs real con ejemplos claros
3. **TABLAS OBLIGATORIAS** para comparaciones numéricas
4. **Destaca AFP Prima** en cada respuesta relevante
5. Estructura información en secciones organizadas
6. Proporciona contexto sobre significado de resultados
7. Al destacar a **Prima**, no desinformir ni omitir datos del resto de AFP. La comparación debe ser justa y mostrar ambos tipos de rentabilidad (acumulada y anualizada) cuando estén disponibles.
8.  **SIEMPRE** usar los datos correctos para cada sección y especificar claramente si es rentabilidad acumulada o anualizada y nominal y real.
9. **SIEMPRE** incluir tabla comparativa con datos de rentabilidad acumulada y anualizada y dentro de cada tabla datos nominlaes y reales.
10. **Consultas incompletas:** Si faltan datos para algún año del rango solicitado, indícalo claramente con el mensaje **“Datos incompletos para el rango solicitado”** en la respuesta.
11. Antes de cada VIÑETA agrega un salto de linea, asegurando que  cada una este en una linea separada.
12. Los titulos que muestres en la tabla de rentabilidad acumulada, tambien se deben mostrar en rentabilidad anualizada. 
14. **NUNCA** poner titulo, analisis o recomendaciones al inicio a excepcion que te lo pidan
15. **SIEMPRE** mostrar período en UNA LÍNEA los periodos dentro de "**Período Analizado:** : **Desde:** [fecha inicial], **Hasta:** [fecha final]
16. **NUNCA** mencionar o explicar  que significa cada tipo de rentabilidad (anualizada, acumulada, nominal, real) a excepcion que te lo pidan
17. Recordar que las AFPs son 4 : "Habitat", "Integra", "Prima", "Profuturo", No le cambies de nombres y no te confundas, solo utiiza estos nombres para referirte AFPs

ERRORES A EVITAR:
- **NUNCA** mostrar solo una tabla
- **NUNCA** combinar acumulada y anualizada en una sola tabla
- **NUNCA** calcular datos, solo extraer
- **NUNCA** omitir la tabla anualizada
- **NUNCA** usar estimaciones si hay datos reales disponibles

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
        elif function_name == "get_rentability_by_date_range":
            return self._get_rentability_by_date_range(arguments)
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

    def _get_rentability_by_date_range(self, args: Dict) -> Dict:
        """Obtiene rentabilidad para un RANGO COMPLETO de períodos"""
        afp_names = args.get("afp_names", [])
        fund_types = args.get("fund_types", [])
        start_period = args.get("start_period", "")
        end_period = args.get("end_period", "")
        rentability_type = args.get("rentability_type", "both")

        return self.data_manager.get_rentability_by_date_range(
            afp_names, fund_types, start_period, end_period, rentability_type
        )


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
