# **PoC2 - AGENTE DE ANALISIS DE RENTABILIDAD SPP**

Sistema inteligente para análisis de rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú, utilizando Azure OpenAI Assistants API y procesamiento automatizado de archivos Excel.

## 🎯 Descripción

Este proyecto implementa un agente conversacional especializado que analiza datos de rentabilidad de fondos de pensiones, proporcionando insights sobre el rendimiento de diferentes AFPs y tipos de fondos basado en datos oficiales del SPP. El sistema utiliza Azure Functions para despliegue en la nube y un sistema de gestión de datos local optimizado para consultas rápidas.

## 🏗️ Arquitectura

### Componentes Principales

1. **Azure Functions** - API endpoints HTTP para interacción con el agente
2. **Azure OpenAI Assistants API** - Agente conversacional con 4 funciones especializadas
3. **RentabilityDataManager** - Sistema de gestión de datos con cache local optimizado
4. **ExcelProcessor** - Procesamiento automatizado de 20 archivos Excel
5. **Azure Blob Storage** - Almacenamiento de archivos y triggers automáticos

### Flujo de Datos

```
📁 20 Archivos Excel (documents/) → 
🔄 ExcelProcessor (extracción automática) → 
💾 RentabilityDataManager (cache local) → 
🤖 SPPAssistantAgent (Azure OpenAI Assistants API) → 
🌐 Azure Functions (API HTTP) → 
📊 Respuestas Inteligentes
```

### Arquitectura de Funciones

```
🎯 SPPAssistantAgent
├── 📊 get_rentability_by_afp()
├── ⚖️  compare_afp_rentability()
├── 📈 analyze_fund_performance()
└── 📉 get_historical_trends()

🔧 RentabilityDataManager
├── 📁 Carga automática de 20 archivos Excel
├── 💾 Sistema de cache inteligente
├── 🔍 Consultas optimizadas por AFP/Fondo
└── 📊 Estadísticas y métricas del sistema
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


## 📖 Uso - Despliegue - Instalaciones

> 📋 **Para una guía detallada paso a paso, consulta [GUIA_PRUEBAS.md](GUIA_PRUEBAS.md)**


## 🛠️ Desarrollo

### Estructura del Proyecto

```
PoC2-ClienteAltoValor/
├── src/                            # 🔧 Código fuente principal
│   ├── azure_assistant_agent.py   # 🤖 Agente con Assistants API
│   ├── excel_processor.py         # 📊 Procesador avanzado de Excel
│   ├── data_manager.py            # 💾 Gestor centralizado de datos
│   └── __init__.py
├── documents/                      # 📁 20 archivos Excel oficiales
│   ├── Rentabilidad...Tipo 0/     # 🛡️  Fondos conservadores
│   ├── Rentabilidad...Tipo 1/     # ⚖️  Fondos mixto conservador
│   ├── Rentabilidad...Tipo 2/     # 📈 Fondos mixtos
│   └── Rentabilidad...Tipo 3/     # 🚀 Fondos de crecimiento
├── function_app.py                 # 🌐 Azure Functions endpoints
├── config.py                       # ⚙️  Configuración centralizada
├── demo.py                         # 🎯 Demo completo del sistema
├── test_agent_interactive.py       # 🧪 Pruebas interactivas del agente
├── test_api_endpoints.py           # 🌐 Pruebas de endpoints HTTP
├── verify_setup.py                 # ✅ Verificación de configuración
├── GUIA_PRUEBAS.md                 # 📋 Guía completa de pruebas
├── requirements.txt                # 📦 Dependencias Python
├── requeriments.txt                # 📦 Archivo de dependencias (duplicado)
├── host.json                       # 🔧 Configuración Azure Functions
├── local.settings.json             # 🔐 Variables locales
└── README.md                       # 📚 Documentación completa
```

### Funciones del Agente

1. **get_rentability_by_afp** - Obtiene rentabilidad por AFP y tipo de fondo
2. **compare_afp_rentability** - Compara rendimiento entre AFPs
3. **analyze_fund_performance** - Análisis de tipos de fondos
4. **get_historical_trends** - Tendencias históricas de rentabilidad


## ✅ Estado Actual - Infraestructura Actualizada

### 🎯 Completado en esta Versión
- ✅ **Procesamiento Avanzado**: 20 archivos Excel con extracción automática
- ✅ **Agente Inteligente**: Azure OpenAI Assistants API completamente funcional
- ✅ **Sistema de Datos**: RentabilityDataManager con cache optimizado
- ✅ **4 Funciones Especializadas**: Consultas, comparaciones, análisis y tendencias
- ✅ **API Endpoints**: 3 endpoints HTTP listos para producción
- ✅ **Blob Storage Integration**: Procesamiento automático de archivos
- ✅ **Sistema de Pruebas**: 4 scripts diferentes para testing
- ✅ **Documentación Completa**: README, guías y ejemplos

### 🔧 Infraestructura Actual
```
📊 Datos: 20 archivos Excel → RentabilityDataManager (cache local)
🤖 IA: Azure OpenAI Assistants API → 4 funciones especializadas
🌐 API: Azure Functions → 3 endpoints HTTP
💾 Storage: Azure Blob Storage → Triggers automáticos
🧪 Testing: 4 scripts de pruebas → Interactivo + API + Demo
```

### 🔄 Futuras Mejoras (Opcionales)
- 🔄 Integración con Azure SQL Database (para persistencia)
- 🔄 Indexación en Azure AI Search (para búsqueda semántica)
- 🔄 Dashboard web para visualización
- 🔄 Análisis predictivos con ML
- 🔄 Autenticación y autorización
- 🔄 Rate limiting y monitoreo avanzado

