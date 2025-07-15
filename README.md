# PoC2 - Agente de Análisis de Rentabilidad SPP

Sistema inteligente para análisis de rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú, utilizando Azure OpenAI y procesamiento automatizado de archivos Excel.

## 🎯 Descripción

Este proyecto implementa un agente conversacional especializado que analiza datos de rentabilidad de fondos de pensiones, proporcionando insights sobre el rendimiento de diferentes AFPs y tipos de fondos basado en datos oficiales del SPP.

## 🏗️ Arquitectura

### Componentes Principales

1. **Azure Functions** - API endpoints para el agente conversacional
2. **Azure Blob Storage** - Almacenamiento de archivos Excel de rentabilidad
3. **Azure SQL Database** - Base de datos estructurada (futuro)
4. **Azure AI Search** - Indexación y búsqueda de documentos (futuro)
5. **Azure OpenAI** - Assistants API para procesamiento de lenguaje natural

### Flujo de Datos

```
Archivos Excel → Procesamiento Local → 
Gestor de Datos → Azure OpenAI Assistant → 
Respuestas Inteligentes sobre Rentabilidad
```

## 📊 Datos Procesados

### Tipos de Archivos Excel
- **Fondo Tipo 0**: Conservador (menor riesgo)
- **Fondo Tipo 1**: Mixto Conservador
- **Fondo Tipo 2**: Mixto
- **Fondo Tipo 3**: Crecimiento (mayor riesgo)

### AFPs Incluidas
- Habitat
- Integra
- Prima
- Profuturo

### Períodos Disponibles
- Enero 2025 a Mayo 2025
- Datos históricos de rentabilidad acumulada

## 🚀 Funcionalidades

### Agente de Rentabilidad SPP
- ✅ Consultas de rentabilidad por AFP específica
- ✅ Comparaciones de rendimiento entre AFPs
- ✅ Análisis de diferentes tipos de fondos
- ✅ Tendencias históricas de rentabilidad
- ✅ Recomendaciones basadas en perfil de riesgo

### Procesamiento Automatizado
- ✅ Carga automática de 20 archivos Excel
- ✅ Extracción de datos de rentabilidad nominal y real
- ✅ Clasificación por tipo de fondo y período
- ✅ Sistema de cache para consultas rápidas

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment

# Azure Blob Storage
AZURE_BLOB_CONNECTION_STRING=your_connection_string
AZURE_BLOB_ACCOUNT_NAME=your_account
AZURE_BLOB_ACCOUNT_KEY=your_key
AZURE_BLOB_CONTAINER_NAME=contenedorsbs2025

# Azure AI Search (futuro)
AZURE_AISEARCH_ENDPOINT=your_search_endpoint
AZURE_AISEARCH_API_KEY=your_search_key
AZURE_AISEARCH_INDEX_NAME=spp-rentability-index

# Azure SQL Database (futuro)
AZURE_SQL_SERVER=your_server
AZURE_SQL_USERNAME=your_username
AZURE_SQL_PASSWORD=your_password
AZURE_SQL_CONNECTION_STRING=your_connection_string
```

### Instalación

```bash
pip install -r requeriments.txt
```

## 📖 Uso

### Endpoints Disponibles

#### 1. Chat con el Agente de Rentabilidad
```http
POST /api/chat
Content-Type: application/json

{
  "query": "¿Cuál es la rentabilidad de Habitat en el fondo tipo 0?"
}
```

#### 2. Información del Asistente
```http
GET /api/assistant/info
```

#### 3. Health Check
```http
GET /api/health
```

### Ejemplos de Consultas

```python
# Consultas sobre rentabilidad específica
"¿Cuál es la rentabilidad nominal de Habitat en el fondo conservador?"
"Muestra la rentabilidad real de Prima en los últimos 3 años"

# Comparaciones entre AFPs
"Compara la rentabilidad entre Habitat e Integra en el fondo tipo 2"
"¿Qué AFP tiene mejor rendimiento en fondos de crecimiento?"

# Análisis de tipos de fondos
"Explica las diferencias entre los fondos tipo 0 y tipo 3"
"¿Qué tipo de fondo recomiendas para una persona de 30 años?"

# Tendencias históricas
"¿Cómo ha evolucionado la rentabilidad de los fondos conservadores?"
"Muestra las tendencias de rentabilidad por período"
```

## 🛠️ Desarrollo

### Estructura del Proyecto

```
PoC2-ClienteAltoValor/
├── src/
│   ├── azure_assistant_agent.py    # Agente principal con Assistants API
│   ├── excel_processor.py          # Procesador de archivos Excel
│   ├── data_manager.py             # Gestor centralizado de datos
│   └── __init__.py
├── documents/                      # 20 archivos Excel de rentabilidad
│   ├── Rentabilidad...Tipo 0/     # Fondos conservadores
│   ├── Rentabilidad...Tipo 1/     # Fondos mixto conservador
│   ├── Rentabilidad...Tipo 2/     # Fondos mixtos
│   └── Rentabilidad...Tipo 3/     # Fondos de crecimiento
├── function_app.py                 # Azure Functions endpoints
├── config.py                       # Configuración centralizada
├── test_system.py                  # Script de pruebas
├── test_processor.py               # Pruebas del procesador
├── requirements.txt                # Dependencias Python
└── README.md
```

### Funciones del Agente

1. **get_rentability_by_afp** - Obtiene rentabilidad por AFP y tipo de fondo
2. **compare_afp_rentability** - Compara rendimiento entre AFPs
3. **analyze_fund_performance** - Análisis de tipos de fondos
4. **get_historical_trends** - Tendencias históricas de rentabilidad

### Datos Procesados

```json
{
  "total_files_processed": 20,
  "available_fund_types": [0, 1, 2, 3],
  "available_periods": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
  "available_afps": ["Habitat", "Integra", "Prima", "Profuturo"],
  "data_coverage": {
    "fund_type_0": 5,
    "fund_type_1": 5,
    "fund_type_2": 5,
    "fund_type_3": 5
  }
}
```

## 🧪 Pruebas

### Ejecutar Pruebas del Sistema

```bash
python test_system.py
```

### Probar Procesador de Excel

```bash
python test_processor.py
```

## 🚀 Despliegue

### Azure Functions

```bash
func azure functionapp publish your-function-app
```

### Variables de Entorno en Azure

Configurar todas las variables de entorno en la Function App de Azure.

## 📊 Monitoreo

- Application Insights para logs y métricas
- Azure Monitor para alertas
- Health check endpoint para verificar estado
- Logs detallados del procesamiento de datos

## ✅ Estado Actual

### Completado
- ✅ Procesamiento de 20 archivos Excel de rentabilidad
- ✅ Extracción de datos de rentabilidad nominal y real
- ✅ Sistema de gestión de datos centralizado
- ✅ Agente conversacional con Azure OpenAI Assistants API
- ✅ Funciones especializadas para análisis de rentabilidad
- ✅ Comparaciones entre AFPs y tipos de fondos
- ✅ API endpoints funcionales
- ✅ Sistema de pruebas automatizado

### Pendiente (Futuras Mejoras)
- 🔄 Integración con Azure SQL Database
- 🔄 Indexación en Azure AI Search
- 🔄 Dashboard web para visualización
- 🔄 Análisis más sofisticados con ML
- 🔄 Autenticación y autorización

## 🎯 Casos de Uso

### Para Asesores Financieros
- Comparar rendimiento entre AFPs para recomendaciones
- Analizar históricos de rentabilidad por tipo de fondo
- Obtener insights sobre riesgo vs rentabilidad

### Para Afiliados al SPP
- Consultar rentabilidad de su AFP actual
- Comparar opciones de fondos según perfil de riesgo
- Entender diferencias entre rentabilidad nominal y real

### Para Analistas del Sector
- Análisis de tendencias del mercado previsional
- Comparaciones de rendimiento sectorial
- Evaluación de consistencia de rendimientos

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

MIT License

---

**Desarrollado con ❤️ para el análisis inteligente de datos del SPP**