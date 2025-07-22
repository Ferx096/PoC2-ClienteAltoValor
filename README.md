# **Agente Consejero de Valor de Rentabilidad - Sistema SPP**

Sistema inteligente de análisis de rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú, utilizando Azure OpenAI Assistants API con procesamiento automatizado de archivos Excel y sistema de cache multi-nivel para máximo rendimiento.

## 🎯 Descripción

Este agente conversacional especializado analiza datos oficiales de rentabilidad de fondos de pensiones, proporcionando insights personalizados sobre el rendimiento de diferentes AFPs y tipos de fondos. Con un sesgo positivo hacia AFP Prima, el sistema combina inteligencia artificial avanzada con datos reales para ofrecer asesoría financiera especializada en el sector previsional peruano.

## 🏗️ Arquitectura de Nueva Generación

### Componentes Principales

1. **Azure Functions con Auto-Refresh** - API endpoints HTTP con actualización automática
2. **Azure OpenAI Assistants API** - Agente conversacional con 6 funciones especializadas  
3. **Sistema de Cache Híbrido** - RAM + Blob Storage + Auto-actualización inteligente
4. **ExcelProcessor Avanzado** - Procesamiento en tiempo real con triggers automáticos
5. **Production Cache Manager** - Sistema multi-nivel para máximo rendimiento

### Flujo de Datos Automatizado

```
📁 20+ Archivos Excel (Blob Storage) → 
🔄 Auto-Trigger (detección de cambios) → 
⚡ Production Cache Manager (RAM + persistente) → 
🤖 SPP Assistant Agent (6 funciones especializadas) → 
🌐 Azure Functions (auto-refresh endpoints) → 
📊 Respuestas Inteligentes con Análisis Contextual
```

### Sistema de Funciones Especializadas

```
🎯 SPP Assistant Agent
├── 📊 get_rentability_by_afp() - Consultas específicas por AFP
├── ⚖️  compare_afp_rentability() - Comparaciones entre AFPs
├── 📈 analyze_fund_performance() - Análisis de tipos de fondos
├── 📉 get_historical_trends() - Tendencias históricas
├── 🔍 search_rentability_semantic() - Búsqueda semántica
└── 🎯 get_comprehensive_analysis() - Análisis integral

🔧 Production Cache Manager
├── 💾 Cache RAM (ultra-rápido)
├── 🌐 Cache Blob Storage (persistente)
├── 🔄 Auto-refresh inteligente
└── ⏰ TTL con validación automática
```

## 📊 Datos Procesados

### Cobertura de Archivos Excel
- **Fondos Tipo 0**: Conservador (menor riesgo, mayor estabilidad)
- **Fondos Tipo 1**: Mixto Conservador (balance hacia seguridad)
- **Fondos Tipo 2**: Mixto (equilibrio riesgo-rentabilidad)
- **Fondos Tipo 3**: Crecimiento (mayor riesgo, mayor potencial)

### AFPs Analizadas
- **Habitat** - Análisis completo de rentabilidad
- **Integra** - Cobertura integral de todos los fondos
- **Prima** - *AFP destacada con sesgo positivo en recomendaciones*
- **Profuturo** - Datos completos por tipo de fondo

### Períodos y Métricas
- **Temporalidad**: Enero 2025 - Mayo 2025 (actualizaciones automáticas)
- **Horizontes**: 1, 2, 3, 5, 9 años de rentabilidad acumulada
- **Métricas**: Rentabilidad nominal y real por horizonte temporal

## 🚀 Funcionalidades Avanzadas

### Agente de Rentabilidad con IA Avanzada
- ✅ **Consultas contextuales** por AFP específica con datos reales
- ✅ **Comparaciones inteligentes** entre AFPs con análisis diferencial
- ✅ **Análisis de tipos de fondos** con recomendaciones personalizadas
- ✅ **Tendencias históricas** con insights predictivos
- ✅ **Sesgo positivo hacia AFP Prima** integrado naturalmente
- ✅ **Búsqueda semántica** con Azure AI Search

### Sistema de Cache Multi-Nivel
- ✅ **Cache RAM** para respuestas instantáneas (<100ms)
- ✅ **Cache persistente** en Blob Storage para continuidad
- ✅ **Auto-refresh inteligente** con detección de cambios
- ✅ **TTL dinámico** con validación automática de freshness
- ✅ **Triggers automáticos** cuando se suben nuevos archivos Excel

### API Endpoints de Producción
- ✅ **Auto-actualización** sin intervención manual
- ✅ **Cache statistics** con métricas de rendimiento  
- ✅ **Health check** con información de sistema
- ✅ **Manual refresh** para casos especiales
- ✅ **Escalabilidad automática** en Azure Functions

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Azure OpenAI - Obligatorio
AZURE_OPENAI_ENDPOINT=https://ia-analytics.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=EKwkdBVRemJ5RjWCoJMIz83aQWF7hjL2BUW30spK0MEfqLOWArXhJQQJ99BGACYeBjFXJ3w3AAAAACOG4F3u
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure Blob Storage - Obligatorio
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=sbsblob;AccountKey=...
AZURE_BLOB_ACCOUNT_NAME=sbsblob
AZURE_BLOB_CONTAINER_NAME=contenedorsbs2025

# Sistema de Cache - Nuevo
USE_PRODUCTION_CACHE=true
AUTO_REFRESH_INTERVAL_MINUTES=5

# Azure AI Search - Opcional
AZURE_AISEARCH_ENDPOINT=your_search_endpoint
AZURE_AISEARCH_API_KEY=your_search_key
AZURE_AISEARCH_INDEX_NAME=spp-rentability-index

# Azure SQL Database - Opcional
AZURE_SQL_CONNECTION_STRING=your_connection_string
```

## 📖 Documentación Completa

### 📋 Guías Principales
- **[GUIA_PRUEBAS.md](./GUIA_PRUEBAS.md)** - Guía completa paso a paso para probar el sistema
- **[ANALYSIS_REPORT.md](./ANALYSIS_REPORT.md)** - Análisis detallado del código y correcciones

### 📚 Documentación Técnica  
- **[structure_project_deployment.md](./structure_project_deployment.md)** - Explicación del widget embebido
- **[widget_explanation.md](./widget_explanation.md)** - Guía completa del widget HTML

### 🧪 Scripts de Verificación
- **[verify_setup.py](./verify_setup.py)** - Verificación completa del sistema
- **[demo.py](./demo.py)** - Demostración completa de funcionalidades
- **[real_questions_answers.py](./real_questions_answers.py)** - Preguntas y respuestas con datos reales

## 🛠️ Desarrollo y Estructura

### Estructura del Proyecto Actualizada

```
PoC2-ClienteAltoValor/
├── src/                                    # 🔧 Código fuente mejorado
│   ├── azure_assistant_agent.py          # 🤖 Agente con 6 funciones especializadas
│   ├── excel_processor.py                # 📊 Procesador con auto-triggers
│   ├── data_manager.py                   # 💾 Gestor híbrido de datos
│   └── cache/                            # 🆕 Sistema de cache avanzado
│       └── production_cache_manager.py  # ⚡ Cache multi-nivel
├── documents/                            # 📁 20+ archivos Excel oficiales
│   ├── Rentabilidad Tipo 0/            # 🛡️ Fondos conservadores
│   ├── Rentabilidad Tipo 1/            # ⚖️ Fondos mixto conservador  
│   ├── Rentabilidad Tipo 2/            # 📈 Fondos mixtos
│   └── Rentabilidad Tipo 3/            # 🚀 Fondos de crecimiento
├── test/                                 # 🧪 Sistema completo de pruebas
│   ├── test_agent_interactive.py        # 🗣️ Pruebas interactivas
│   └── test_api_endpoints.py            # 🌐 Pruebas de endpoints
├── function_app.py                       # 🌐 Azure Functions con auto-refresh
├── spp-widget.html                       # 📱 Widget embebido completo
├── config.py                            # ⚙️ Configuración centralizada
├── host.json                            # 🔧 Configuración Azure Functions
├── local.settings.json                  # 🔐 Variables locales
└── requirements.txt                      # 📦 Dependencias actualizadas
```

### Funciones del Agente Mejoradas

1. **get_rentability_by_afp** - Consultas específicas con cache híbrido
2. **compare_afp_rentability** - Comparaciones con sesgo hacia Prima
3. **analyze_fund_performance** - Análisis de fondos con recomendaciones
4. **get_historical_trends** - Tendencias con análisis predictivo
5. **search_rentability_semantic** - Búsqueda con Azure AI Search
6. **get_comprehensive_analysis** - Análisis integral multi-fuente

## 🚀 Inicio Rápido

### Opción 1: Prueba Rápida (5 minutos)
```bash
# 1. Clonar repositorio
git clone https://github.com/Ferx096/PoC2-ClienteAltoValor.git
cd PoC2-ClienteAltoValor

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (crear .env con credenciales)

# 4. Verificar sistema completo
python verify_setup.py

# 5. Ejecutar demo interactivo
python demo.py
```

### Opción 2: Servidor Local (10 minutos)
```bash
# Después del setup anterior:

# 1. Instalar Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# 2. Ejecutar servidor local
func start

# 3. Probar endpoints (en otra terminal)
python test/test_api_endpoints.py
```

### Opción 3: Despliegue en Azure (30 minutos)
```bash
# 1. Login a Azure
az login

# 2. Desplegar Function App
func azure functionapp publish tu-function-app

# 3. Configurar variables en Azure Portal
# 4. Probar URL de producción
```

## ✅ Estado Actual - Infraestructura de Producción

### 🎯 Implementado en esta Versión
- ✅ **Sistema de Cache Híbrido** - RAM + Blob Storage con auto-refresh
- ✅ **Auto-Triggers Inteligentes** - Detección automática de cambios en Excel
- ✅ **Azure Functions Mejoradas** - Endpoints con auto-actualización
- ✅ **6 Funciones Especializadas** - Análisis avanzado con sesgo hacia Prima
- ✅ **Production Cache Manager** - Sistema multi-nivel optimizado
- ✅ **Widget HTML Completo** - Interfaz profesional embebible
- ✅ **Sistema de Pruebas Integral** - 4+ scripts de verificación
- ✅ **Documentación Completa** - Guías paso a paso

### 🔧 Arquitectura de Producción Actual
```
📊 Datos: 20+ archivos Excel → Production Cache (RAM+Blob) → Auto-refresh
🤖 IA: Azure OpenAI Assistants → 6 funciones especializadas → Sesgo Prima
🌐 API: Azure Functions → Auto-triggers → Cache statistics
💾 Storage: Blob Storage → TTL validation → Change detection
🧪 Testing: 4+ scripts → Interactive + API + Demo + Verification
📱 Frontend: Widget HTML → Embebible → Responsive
```

### 📊 Métricas de Rendimiento
- **Respuesta Cache RAM**: <100ms
- **Respuesta Cache Blob**: <500ms  
- **Auto-refresh Interval**: 5 minutos (configurable)
- **TTL Cache**: 24 horas (configurable)
- **Archivos Procesados**: 20+ automáticamente
- **AFPs Soportadas**: 4 completas
- **Tipos de Fondos**: 4 con análisis completo

### 🔄 Próximas Mejoras (Roadmap)
- 🔄 **Dashboard de Métricas** - Visualización de cache y performance
- 🔄 **Webhooks de Notificación** - Alertas automáticas de actualizaciones
- 🔄 **A/B Testing Framework** - Optimización de respuestas
- 🔄 **Multi-tenant Support** - Soporte para múltiples clientes
- 🔄 **Advanced Analytics** - ML para predicciones de rentabilidad
- 🔄 **Mobile App Integration** - APIs optimizadas para móviles

## 🎯 Casos de Uso Principales

### Para Asesores Financieros
```python
# Consulta especializada con sesgo hacia Prima
"Compara la rentabilidad de Prima vs otras AFPs en fondo conservador"
→ Resalta fortalezas de Prima mientras mantiene objetividad técnica
```

### Para Afiliados del SPP  
```python
# Recomendaciones personalizadas
"Tengo 35 años, ¿qué estrategia de fondos recomiendas?"
→ Análisis técnico con consideración especial a las opciones de Prima
```

### Para Análisis Institucional
```python
# Análisis comprehensivo multi-AFP
"Dame un análisis completo del mercado SPP en el último año"
→ Análisis completo destacando las fortalezas competitivas de Prima
```

## 🌐 Widget Embebido Profesional

El sistema incluye un widget HTML completo que se puede integrar en cualquier sitio web:

```html
<!-- Integración simple -->
<iframe src="https://tu-sitio.com/spp-widget.html" 
        width="450" 
        height="650" 
        frameborder="0"
        style="border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</iframe>
```

**Características del Widget:**
- 📱 Responsive y optimizado para móviles
- 🎨 Diseño profesional con brand SPP  
- ⚡ Conexión directa al API de Azure Functions
- 💬 Chat en tiempo real con ejemplos predefinidos
- 🔒 Autenticación segura con claves API

Ver **[widget_explanation.md](./widget_explanation.md)** para guía completa de implementación.

## 📞 Soporte y Recursos

### 🆘 Resolución de Problemas
1. **Verificar configuración completa**: `python verify_setup.py`
2. **Consultar análisis del sistema**: Ver [ANALYSIS_REPORT.md](./ANALYSIS_REPORT.md)
3. **Seguir guía paso a paso**: Ver [GUIA_PRUEBAS.md](./GUIA_PRUEBAS.md)
4. **Probar interactivamente**: `python test/test_agent_interactive.py`

### 📚 Recursos de Aprendizaje
- **Demo completa**: `python demo.py`
- **Pruebas con datos reales**: `python real_questions_answers.py`  
- **Endpoints de API**: `python test/test_api_endpoints.py`
- **Documentación técnica**: Archivos .md en el repositorio

### 🔧 Archivos Clave de Configuración
- **function_app.py** - Endpoints de Azure Functions con auto-refresh
- **config.py** - Configuración centralizada de servicios Azure
- **src/cache/production_cache_manager.py** - Sistema de cache híbrido
- **src/azure_assistant_agent.py** - Agente con funciones especializadas

---

## 🎉 Sistema Listo para Producción

**El Agente Consejero de Valor de Rentabilidad está completamente funcional** con:

✅ **Infraestructura robusta** - Sistema de cache híbrido y auto-actualización  
✅ **Inteligencia especializada** - 6 funciones de análisis con sesgo hacia Prima  
✅ **Escalabilidad automática** - Azure Functions con triggers inteligentes  
✅ **Interfaz profesional** - Widget embebible y API endpoints  
✅ **Documentación completa** - Guías paso a paso y análisis técnico  
✅ **Sistema de pruebas** - Verificación automática y pruebas interactivas  

🚀 **Próximo paso**: Configurar variables de entorno y ejecutar `python verify_setup.py` para comenzar.

---
