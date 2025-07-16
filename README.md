# PoC2 - Agente de Análisis de Rentabilidad SPP

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

### Instalación

```bash
pip install -r requirements.txt
```

## 📖 Uso

### 🧪 Cómo Probar el Agente (Preguntas y Respuestas)

#### Opción 1: Modo Interactivo (Recomendado)
```bash
python test_agent_interactive.py
```

**¿Qué puedes preguntar al agente?**
- "¿Cuál es la rentabilidad de Habitat en el fondo conservador?"
- "Compara el rendimiento entre Integra y Prima en fondos de crecimiento"
- "¿Qué tipo de fondo recomiendas para una persona de 30 años?"
- "Muestra la evolución de rentabilidad de los fondos mixtos"
- "¿Cuál es la diferencia entre rentabilidad nominal y real?"
- "¿Qué AFP tiene mejor rendimiento histórico?"

**Características del modo interactivo:**
- ✅ Conversación en tiempo real con el agente
- ✅ Ejemplos de preguntas predefinidos
- ✅ Medición de tiempos de respuesta
- ✅ Posibilidad de reiniciar la conversación
- ✅ Salir escribiendo 'quit' o 'exit'

#### Opción 2: Demo Automatizado
```bash
python demo.py
```
Ejecuta una demostración completa con consultas predefinidas.

#### Opción 3: Pruebas de API
```bash
python test_api_endpoints.py
```
Prueba los endpoints HTTP directamente.

### 🧪 Pruebas Locales del Agente

#### Modo Interactivo (Recomendado)
```bash
python test_agent_interactive.py
```

Este script te permite:
- ✅ Hacer consultas directas al agente
- ✅ Ver ejemplos de preguntas
- ✅ Probar diferentes tipos de consultas
- ✅ Medir tiempos de respuesta
- ✅ Reiniciar la conversación cuando sea necesario

#### Demo del Sistema
```bash
python demo.py
```

Muestra las capacidades completas del sistema con datos reales.

#### Pruebas Automatizadas
```bash
python verify_setup.py  # Verificar configuración
```

#### Pruebas de API Endpoints
```bash
python test_api_endpoints.py  # Probar endpoints HTTP
```

Este script permite:
- ✅ Probar endpoints locales o en Azure
- ✅ Hacer consultas HTTP directas
- ✅ Generar ejemplos de comandos curl
- ✅ Medir tiempos de respuesta de API

> 📋 **Para una guía detallada paso a paso, consulta [GUIA_PRUEBAS.md](GUIA_PRUEBAS.md)**

### 🌐 Endpoints de API (Producción)

#### 1. Chat con el Agente de Rentabilidad
```http
POST /api/chat
Content-Type: application/json

{
  "query": "¿Cuál es la rentabilidad de Habitat en el fondo tipo 0?"
}
```

**Respuesta:**
```json
{
  "query": "¿Cuál es la rentabilidad de Habitat en el fondo tipo 0?",
  "response": "Según los datos más recientes...",
  "assistant_id": "asst_xxx",
  "thread_id": "thread_xxx",
  "status": "success"
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

#### 4. Procesamiento Automático de Excel
- **Trigger**: Subida de archivo a Blob Storage
- **Container**: `contenedorsbs2025`
- **Procesamiento**: Automático al detectar nuevos archivos

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

## 🧪 Pruebas y Desarrollo

### 🎯 Pruebas Interactivas (Recomendado)

```bash
python test_agent_interactive.py
```

**Características:**
- ✅ Modo interactivo para consultas en tiempo real
- ✅ Ejemplos de consultas predefinidos
- ✅ Medición de tiempos de respuesta
- ✅ Reinicio de conversación
- ✅ Manejo de errores amigable

### 🎪 Demo Completo del Sistema

```bash
python demo.py
```

**Incluye:**
- 📊 Estadísticas del sistema
- 🏦 Consultas por AFP
- ⚖️  Comparaciones entre AFPs
- 📈 Análisis de tipos de fondos
- 💡 Recomendaciones personalizadas

### ✅ Verificación de Configuración

```bash
python verify_setup.py
```

**Verifica:**
- 🔐 Variables de entorno
- 📁 Archivos de datos
- 🤖 Conexión con Azure OpenAI
- 💾 Carga de datos

## 🚀 Despliegue Paso a Paso

### 🏠 Opción 1: Ejecución Local (Sin Máquina Virtual)

**Puedes ejecutar el proyecto directamente en tu máquina local sin necesidad de VM:**

#### Paso 1: Configurar el Entorno
```bash
# 1. Clonar el repositorio
git clone https://github.com/Ferx096/PoC2-ClienteAltoValor.git
cd PoC2-ClienteAltoValor

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
# Crear archivo .env con tus credenciales de Azure OpenAI
```

#### Paso 2: Probar el Agente Localmente
```bash
# Opción A: Modo interactivo (recomendado para pruebas)
python test_agent_interactive.py

# Opción B: Demo completo
python demo.py

# Opción C: Verificar configuración
python verify_setup.py
```

#### Paso 3: Ejecutar API Local (Opcional)
```bash
# Instalar Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Ejecutar API localmente
func start
```

La API estará disponible en: `http://localhost:7071`

### 🌐 Opción 3: Widget Embebido para Páginas Web

**Puedes generar un código embebido para insertar el agente en cualquier página web:**

#### Crear Widget HTML/JavaScript
```html
<!DOCTYPE html>
<html>
<head>
    <title>Agente SPP - Widget</title>
    <style>
        #spp-chat-widget {
            width: 400px;
            height: 600px;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 10px;
            font-family: Arial, sans-serif;
        }
        #chat-messages {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #eee;
            padding: 10px;
            margin-bottom: 10px;
        }
        #chat-input {
            width: 70%;
            padding: 5px;
        }
        #send-btn {
            width: 25%;
            padding: 5px;
            background: #007cba;
            color: white;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="spp-chat-widget">
        <h3>🤖 Agente SPP - Rentabilidad de Fondos</h3>
        <div id="chat-messages"></div>
        <input type="text" id="chat-input" placeholder="Pregunta sobre rentabilidad de AFPs...">
        <button id="send-btn">Enviar</button>
    </div>

    <script>
        const API_URL = 'http://localhost:7071/api/chat'; // Cambiar por tu URL de producción
        
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const messages = document.getElementById('chat-messages');
            const query = input.value.trim();
            
            if (!query) return;
            
            // Mostrar mensaje del usuario
            messages.innerHTML += `<div><strong>Tú:</strong> ${query}</div>`;
            input.value = '';
            
            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                messages.innerHTML += `<div><strong>Agente SPP:</strong> ${data.response}</div>`;
                messages.scrollTop = messages.scrollHeight;
                
            } catch (error) {
                messages.innerHTML += `<div><strong>Error:</strong> No se pudo conectar con el agente</div>`;
            }
        }
        
        document.getElementById('send-btn').onclick = sendMessage;
        document.getElementById('chat-input').onkeypress = function(e) {
            if (e.key === 'Enter') sendMessage();
        }
    </script>
</body>
</html>
```

#### Integrar en Página Existente
```html
<!-- Insertar este código en cualquier página web -->
<iframe src="tu-dominio.com/spp-widget.html" 
        width="400" 
        height="600" 
        frameborder="0">
</iframe>
```

### ☁️ Opción 4: Despliegue en Azure (Producción)

#### Probar Localmente
```bash
# Probar agente directamente
python test_agent_interactive.py

# Probar API endpoints
python test_api_endpoints.py

# Demo completo
python demo.py
```

### ☁️ Despliegue en Azure

#### Azure Functions
```bash
# Crear Function App
az functionapp create --resource-group myResourceGroup \
  --consumption-plan-location westus \
  --runtime python --runtime-version 3.9 \
  --functions-version 4 \
  --name myFunctionApp \
  --storage-account mystorageaccount

# Desplegar
func azure functionapp publish myFunctionApp
```

#### Variables de Entorno en Azure
```bash
# Configurar variables de entorno
az functionapp config appsettings set --name myFunctionApp \
  --resource-group myResourceGroup \
  --settings AZURE_OPENAI_ENDPOINT="your_endpoint" \
             AZURE_OPENAI_API_KEY="your_key"
```

### 🔧 Configuración de Blob Storage

```bash
# Crear container para archivos Excel
az storage container create --name contenedorsbs2025 \
  --account-name mystorageaccount
```

## 📊 Monitoreo

- Application Insights para logs y métricas
- Azure Monitor para alertas
- Health check endpoint para verificar estado
- Logs detallados del procesamiento de datos

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

### 🚀 Cambios Principales vs Versión Anterior
1. **Eliminación de dependencias complejas**: No requiere Azure SQL ni AI Search
2. **Sistema de cache local**: Datos procesados en memoria para consultas rápidas
3. **Agente más inteligente**: 4 funciones especializadas vs consultas genéricas
4. **Mejor experiencia de pruebas**: Scripts interactivos y ejemplos claros
5. **Arquitectura simplificada**: Menos componentes, más eficiencia

### 🔄 Futuras Mejoras (Opcionales)
- 🔄 Integración con Azure SQL Database (para persistencia)
- 🔄 Indexación en Azure AI Search (para búsqueda semántica)
- 🔄 Dashboard web para visualización
- 🔄 Análisis predictivos con ML
- 🔄 Autenticación y autorización
- 🔄 Rate limiting y monitoreo avanzado

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