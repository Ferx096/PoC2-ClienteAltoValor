# **GUÍA COMPLETA DE PRUEBAS - AGENTE CONSEJERO DE ALTO VALOR**

Esta guía te explica paso a paso cómo probar tu agente de análisis de rentabilidad SPP.

## 🚀 Opción 1: Pruebas Interactivas Directas - Local (RECOMENDADO)

### Paso 1: Preparar el Entorno
```bash
# 1. Clonar el repositorio
git clone https://github.com/Ferx096/PoC2-ClienteAltoValor.git
cd PoC2-ClienteAltoValor

# 2. Instalar Python 3.8+ (si no lo tienes)
# Windows: Descargar de python.org
# Mac: brew install python
# Linux: sudo apt install python3 python3-pip

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar Variables de Entorno
```bash
# Crear archivo .env en la raíz del proyecto
touch .env

# Agregar tus credenciales en el archivo .env:
AZURE_OPENAI_ENDPOINT=tu_endpoint
AZURE_OPENAI_API_KEY=tu_key
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large

# Azure Blob Storage (OBLIGATORIO)
AZURE_BLOB_CONNECTION_STRING=tu_connection_string
AZURE_BLOB_ACCOUNT_NAME=tu_account
AZURE_BLOB_ACCOUNT_KEY=tu_key
AZURE_BLOB_CONTAINER_NAME=contenedorsbs2025

# Azure SQL Database (Opcional)
AZURE_SQL_CONNECTION_STRING=tu_connection_string

# Azure AI Search (Opcional)
AZURE_AISEARCH_ENDPOINT=tu_search_endpoint
AZURE_AISEARCH_API_KEY=tu_search_key
AZURE_AISEARCH_INDEX_NAME=spp-rentability-index
```

### Paso 3: Verificar Configuración
```bash
# Verificar que todo esté configurado correctamente
python verify_setup.py
```

Este script verificará:
- ✅ Conexión a Azure OpenAI
- ✅ Acceso a Azure Blob Storage
- ✅ Carga de archivos Excel (20 archivos)
- ✅ Procesamiento de datos
- ✅ Funcionalidad del agente

### Paso 4: Probar el Agente Interactivamente
```bash
# Probar el agente en modo interactivo
python test/test_agent_interactive.py
```

### Paso 5: Ver Demo Completo
```bash
# Ver demostración completa del sistema
python demo.py
```

### Paso 6: Ejecutar API Local (Opcional)
```bash
# Instalar Azure Functions Core Tools v4
# Windows: 
# npm install -g azure-functions-core-tools@4 --unsafe-perm true
# Mac: 
# brew tap azure/functions && brew install azure-core-tools-4
# Linux: 
# Ver: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

# Ejecutar servidor local
func start

# La API estará disponible en: http://localhost:7071
```

### Paso 7: Probar Endpoints de API
```bash
# En otra terminal, probar los endpoints
python test/test_api_endpoints.py
```

**O usar curl directamente:**
```bash
# Health check
curl -X GET "http://localhost:7071/api/health"

# Consulta al agente
curl -X POST "http://localhost:7071/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es la rentabilidad de Habitat?"}'

# Información del asistente
curl -X GET "http://localhost:7071/api/assistant/info"
```

## 📊 ¿Qué puedes preguntarle al agente?

### Consultas sobre Rentabilidad Específica:
- "¿Cuál es la rentabilidad nominal de Habitat en el fondo conservador?"
- "Muestra la rentabilidad real de Prima en los últimos períodos disponibles"
- "¿Cómo está el rendimiento de Integra en fondos tipo 2?"

### Comparaciones entre AFPs:
- "Compara la rentabilidad entre Habitat e Integra en el fondo tipo 2"
- "¿Qué AFP tiene mejor rendimiento en fondos de crecimiento?"
- "Compara todos los fondos de Profuturo vs Prima"

### Análisis de Tipos de Fondos:
- "Explica las diferencias entre los fondos tipo 0 y tipo 3"
- "¿Qué tipo de fondo recomiendas para una persona de 30 años?"
- "¿Cuáles son los riesgos de los fondos de crecimiento?"

### Tendencias Históricas:
- "¿Cómo ha evolucionado la rentabilidad de los fondos conservadores?"
- "Muestra las tendencias de rentabilidad por período"
- "¿Cuál ha sido la mejor AFP en los períodos disponibles?"

### Recomendaciones Personalizadas:
- "Recomienda una estrategia para alguien cerca de jubilarse"
- "¿Qué diversificación de fondos sugieres?"
- "¿Conviene cambiar de AFP actualmente?"

## ☁️ Opción 2: Despliegue en Azure (Producción)

### Paso 1: Crear Recursos en Azure
```bash
# Instalar Azure CLI
# Windows: Descargar de docs.microsoft.com
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Crear grupo de recursos
az group create --name rg-spp-agent --location "East US"

# Crear storage account para Azure Functions
az storage account create \
  --name stsppagentuniqueXXX \
  --resource-group rg-spp-agent \
  --location "East US" \
  --sku Standard_LRS

# Crear Function App
az functionapp create \
  --resource-group rg-spp-agent \
  --consumption-plan-location "East US" \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name func-spp-agent-uniqueXXX \
  --storage-account stsppagentuniqueXXX
```

### Paso 2: Configurar Variables en Azure
```bash
# Configurar variables de entorno en la Function App
az functionapp config appsettings set \
  --name func-spp-agent-uniqueXXX \
  --resource-group rg-spp-agent \
  --settings \
    AZURE_OPENAI_ENDPOINT="tu_endpoint" \
    AZURE_OPENAI_API_KEY="tu_key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="tu_deployment" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-large" \
    AZURE_BLOB_CONNECTION_STRING="tu_connection_string" \
    AZURE_BLOB_ACCOUNT_NAME="tu_account" \
    AZURE_BLOB_CONTAINER_NAME="contenedorsbs2025"
```

### Paso 3: Desplegar Function App
```bash
# Verificar que tienes func tools instalado
func --version

# Desplegar a Azure
func azure functionapp publish func-spp-agent-uniqueXXX

# Verificar que funciona
curl -X GET "https://func-spp-agent-uniqueXXX.azurewebsites.net/api/health"
```

## 🌐 Opción 3: Widget Embebido para Páginas Web

### Widget HTML Completo
El archivo `spp-widget.html` contiene un widget completo con:
- ✅ Interfaz de chat moderna y responsive
- ✅ Conexión directa a tu API
- ✅ Ejemplos de consultas predefinidos
- ✅ Manejo de errores
- ✅ Diseño profesional

### Configuración del Widget:

1. **Cambiar URL de API**: En el archivo `spp-widget.html`, línea 33:
   ```javascript
   // Para desarrollo local
   const API_URL = 'http://localhost:7071/api/chat';
   
   // Para producción en Azure
   const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat';
   ```

2. **Insertar en página web**:
   ```html
   <!-- Código iframe para insertar en cualquier página -->
   <iframe src="https://tu-dominio.com/spp-widget.html" 
           width="450" 
           height="650" 
           frameborder="0"
           style="border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
   </iframe>
   ```

3. **Personalizar estilos**: Modificar el CSS según tu marca/diseño

## 🛠️ Solución de Problemas Comunes

### Error: "No se puede conectar a Azure OpenAI"
```bash
# Verificar credenciales
python -c "from config import AZURE_CONFIG; print(AZURE_CONFIG)"

# Probar conexión directa
python -c "
from config import get_openai_client
client = get_openai_client()
print('Conexión exitosa')
"
```

### Error: "No se encuentran archivos Excel"
```bash
# Verificar conexión a Blob Storage
python -c "
from config import AZURE_BLOB_CONFIG
from azure.storage.blob import BlobServiceClient
client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONFIG['AZURE_BLOB_CONNECTION_STRING'])
container = client.get_container_client(AZURE_BLOB_CONFIG['AZURE_BLOB_CONTAINER_NAME'])
blobs = list(container.list_blobs())
print(f'Encontrados {len(blobs)} archivos')
"
```

### Error: "Azure Functions no inicia"
```bash
# Verificar versión de Python (debe ser 3.8-3.11)
python --version

# Verificar Azure Functions Core Tools
func --version

# Reinstalar dependencias
pip install -r requirements.txt
```

## 📊 Resumen de Opciones de Despliegue

| Opción | Complejidad | Costo | Tiempo Setup | Recomendado Para |
|--------|-------------|-------|--------------|------------------|
| **Local** | Baja | Gratis | 10 min | Desarrollo/Pruebas |
| **Azure Functions** | Media | Bajo | 30 min | Producción |
| **Widget Web** | Baja | Gratis | 5 min | Integración web |

## 🎯 Flujo de Trabajo Recomendado

1. **Configuración inicial**: 
   ```bash
   # Configurar .env con credenciales
   python verify_setup.py
   ```

2. **Pruebas locales**:
   ```bash
   python demo.py
   python test/test_agent_interactive.py
   ```

3. **Servidor local** (opcional):
   ```bash
   func start
   python test/test_api_endpoints.py
   ```

4. **Despliegue en Azure** (producción):
   ```bash
   func azure functionapp publish tu-function-app
   ```

5. **Widget web** (integración):
   - Personalizar `spp-widget.html`
   - Subir a tu servidor web
   - Integrar en páginas existentes

## 📞 Soporte y Documentación

### Si tienes problemas:
1. **Verificar configuración**: `python verify_setup.py`
2. **Consultar logs**: Revisar la consola para errores específicos
3. **Documentación completa**: Ver `README.md`
4. **Archivos de ejemplo**: Revisar `demo.py` y scripts de test

### Archivos importantes:
- `requirements.txt` - Dependencias Python
- `function_app.py` - Azure Functions endpoints
- `config.py` - Configuración centralizada
- `src/` - Código fuente del agente
- `test/` - Scripts de pruebas

### Scripts de verificación:
- `verify_setup.py` - Verifica toda la configuración
- `demo.py` - Demostración completa del sistema
- `test/test_agent_interactive.py` - Pruebas interactivas
- `test/test_api_endpoints.py` - Pruebas de API

**Nota**: Este sistema requiere credenciales válidas de Azure OpenAI y Azure Blob Storage para funcionar correctamente. Las demás integraciones (SQL Database, AI Search) son opcionales.