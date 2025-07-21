# 🌐 SPP Widget HTML - Explicación Completa

## 🎯 ¿Qué es spp-widget.html?

### Función Principal
El `spp-widget.html` es un **chat widget embebido** que:
- 💬 Permite chat directo con tu agente SPP
- 🔗 Se puede insertar en cualquier página web
- 📱 Es responsive y funciona en móviles
- ⚡ Conecta directamente a tu API de Azure Functions

### Componentes del Widget

```html
<!-- ESTRUCTURA BÁSICA -->
<div id="spp-chat-widget">
  ├── Header: "🤖 Agente SPP"
  ├── Chat Messages: Conversación
  ├── Examples: Consultas predefinidas
  └── Input: Campo para escribir
</div>
```

### Funcionalidad JavaScript
```javascript
// 1. CONFIGURACIÓN DE API
const API_URL = 'http://localhost:7071/api/chat';  // ← CAMBIAR AQUÍ

// 2. ENVÍO DE MENSAJES
async function sendMessage() {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQuery })
    });
}

// 3. MANEJO DE RESPUESTAS
const data = await response.json();
addMessage(data.response);  // Mostrar respuesta del agente
```

## 🔄 URLs: Desarrollo vs Producción

### 🏠 DESARROLLO (Local)
```javascript
// Cuando ejecutas: func start
const API_URL = 'http://localhost:7071/api/chat';

// Funciona cuando:
// ✅ Tienes func start ejecutándose
// ✅ Solo desde tu computadora
// ❌ No funciona desde otras computadoras
// ❌ No funciona si apagas tu máquina
```

### ☁️ PRODUCCIÓN (Azure Functions)
```javascript
// Después de desplegar en Azure
const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat?code=tu-clave';

// Funciona cuando:
// ✅ Desde cualquier computadora del mundo
// ✅ 24/7 sin que tengas tu máquina prendida
// ✅ Escalabilidad automática
// ✅ Alta disponibilidad
```

## 🚀 Cómo Obtener API de Producción

### PASO 1: Crear Azure Function App
```bash
# 1. Login a Azure
az login

# 2. Crear Resource Group
az group create \
  --name rg-spp-widget \
  --location "East US"

# 3. Crear Storage para Azure Functions
az storage account create \
  --name stsppwidget2025 \
  --resource-group rg-spp-widget \
  --location "East US" \
  --sku Standard_LRS

# 4. Crear Function App
az functionapp create \
  --resource-group rg-spp-widget \
  --consumption-plan-location "East US" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name spp-widget-api-2025 \
  --storage-account stsppwidget2025 \
  --os-type Linux
```

### PASO 2: Configurar Variables de Entorno
```bash
az functionapp config appsettings set \
  --name spp-widget-api-2025 \
  --resource-group rg-spp-widget \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://ia-analytics.cognitiveservices.azure.com/" \
    AZURE_OPENAI_API_KEY="EKwkdBVRemJ5RjWCoJMIz83aQWF7hjL2BUW30spK0MEfqLOWArXhJQQJ99BGACYeBjFXJ3w3AAAAACOG4F3u" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-large" \
    AZURE_BLOB_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=sbsblob;AccountKey=hNX4+xOtvqbWVh7ljNOuDb40tHCkelOexsEjIG5557+Xo0AenB8xl0ljUc5ybSLECc2lhDlXnxvv+AStWlcJyg==;EndpointSuffix=core.windows.net" \
    AZURE_BLOB_ACCOUNT_NAME="sbsblob" \
    AZURE_BLOB_CONTAINER_NAME="contenedorsbs2025"
```

### PASO 3: Desplegar tu Código
```bash
# En tu directorio del proyecto
func azure functionapp publish spp-widget-api-2025
```

### PASO 4: Obtener URL y Claves
```bash
# 1. Obtener URL de la Function App
FUNCTION_URL=$(az functionapp show \
  --name spp-widget-api-2025 \
  --resource-group rg-spp-widget \
  --query "defaultHostName" \
  --output tsv)

echo "🌐 Function App URL: https://$FUNCTION_URL"

# 2. Obtener Master Key para autenticación
MASTER_KEY=$(az functionapp keys list \
  --name spp-widget-api-2025 \
  --resource-group rg-spp-widget \
  --query "masterKey" \
  --output tsv)

echo "🔑 Master Key: $MASTER_KEY"

# 3. URL COMPLETA PARA EL WIDGET
echo "📱 API URL para widget: https://$FUNCTION_URL/api/chat?code=$MASTER_KEY"
```

## 🔧 Actualizar Widget para Producción

### Modificar spp-widget.html
```javascript
// ANTES (desarrollo):
const API_URL = 'http://localhost:7071/api/chat';

// DESPUÉS (producción):
const API_URL = 'https://spp-widget-api-2025.azurewebsites.net/api/chat?code=xyz123abc...';
```

### Ejemplo Completo
```javascript
// Línea 33 en spp-widget.html
const API_URL = 'https://spp-widget-api-2025.azurewebsites.net/api/chat?code=4L8X9kN2mP5vR7wQ1eT6yU3iO9pA2sD8fG6hJ4kL7nM0zX8cV5bN1mQ4wE7rT9yU';

// Para mayor seguridad, también puedes usar:
const API_URL = 'https://spp-widget-api-2025.azurewebsites.net/api/chat';
// Y manejar la autenticación por headers (más complejo)
```

## 🌍 Formas de Usar el Widget

### 1. Como Página Independiente
```html
<!-- Subir spp-widget.html a tu servidor web -->
https://tu-sitio.com/spp-widget.html
```

### 2. Como iframe Embebido
```html
<!-- En cualquier página web -->
<iframe src="https://tu-sitio.com/spp-widget.html" 
        width="450" 
        height="650" 
        frameborder="0"
        style="border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</iframe>
```

### 3. Como Modal/Popup
```html
<!-- Botón para abrir el chat -->
<button onclick="openSPPChat()">💬 Consultar SPP</button>

<script>
function openSPPChat() {
    // Abrir widget en modal
    const modal = document.createElement('div');
    modal.innerHTML = `
        <iframe src="https://tu-sitio.com/spp-widget.html" 
                width="450" height="650">
        </iframe>
    `;
    document.body.appendChild(modal);
}
</script>
```

### 4. Como Widget Flotante
```html
<!-- Widget flotante en esquina -->
<div id="floating-chat" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
    <iframe src="https://tu-sitio.com/spp-widget.html" 
            width="350" height="500">
    </iframe>
</div>
```

## 🔒 Configuraciones de Seguridad

### Opción 1: Con Master Key (Fácil)
```javascript
// Simple pero menos seguro
const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat?code=master-key';
```

### Opción 2: Function Key Específica (Recomendado)
```bash
# Crear clave específica para el widget
az functionapp function keys set \
  --name spp-widget-api-2025 \
  --resource-group rg-spp-widget \
  --function-name chat_endpoint \
  --key-name "widget-key" \
  --key-value "widget-secure-key-123"
```

```javascript
// Más seguro
const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat?code=widget-secure-key-123';
```

### Opción 3: Sin Autenticación (Para testing)
```python
# En function_app.py cambiar:
@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
```

```javascript
// Sin clave
const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat';
```

## ✅ Verificación de Funcionamiento

### 1. Test Manual
```bash
# Test directo del API
curl -X POST "https://spp-widget-api-2025.azurewebsites.net/api/chat?code=tu-clave" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Rentabilidad de Habitat?"}'
```

### 2. Test desde Widget
- Abrir `spp-widget.html` en el navegador
- Escribir consulta de prueba
- Verificar que responde correctamente

### 3. Test de Integración
```html
<!-- Test en página real -->
<!DOCTYPE html>
<html>
<head><title>Test SPP Widget</title></head>
<body>
    <h1>Mi Sitio Web</h1>
    <iframe src="https://tu-sitio.com/spp-widget.html" 
            width="450" height="650">
    </iframe>
</body>
</html>
```

## 🚀 Despliegue Completo

### Para el Widget (HTML estático)
```bash
# Opción 1: GitHub Pages (gratis)
# - Subir spp-widget.html a repositorio GitHub
# - Activar GitHub Pages
# - URL: https://tu-usuario.github.io/repo/spp-widget.html

# Opción 2: Azure Static Web Apps (gratis)
az staticwebapp create \
  --name spp-widget-site \
  --resource-group rg-spp-widget \
  --source https://github.com/tu-usuario/tu-repo

# Opción 3: Cualquier hosting web
# - Subir spp-widget.html via FTP
# - URL: https://tu-dominio.com/spp-widget.html
```

## 📊 Arquitectura Final

```
👤 USUARIO
│
├── 🌐 Widget HTML (spp-widget.html)
│   │   └── JavaScript hace fetch() al API
│   │
├── ☁️ Azure Functions API
│   │   ├── /api/chat (autenticado)
│   │   ├── /api/health (público)
│   │   └── /api/cache/stats (público)
│   │
├── 🤖 SPP Assistant Agent
│   │   └── Azure OpenAI + Funciones especializadas
│   │
└── 💾 Sistema de Cache Híbrido
    ├── RAM (ultra-rápido)
    └── Blob Storage (persistente)
```

## 🎯 Resultado Final

### URLs que obtienes:
```
🌐 API de Producción:
https://spp-widget-api-2025.azurewebsites.net/api/chat?code=tu-clave

📱 Widget Deployment:
https://tu-sitio.com/spp-widget.html

🔗 Widget Embebido:
<iframe src="https://tu-sitio.com/spp-widget.html" width="450" height="650"></iframe>
```

### Funcionalidades:
- ✅ Chat en tiempo real con agente SPP
- ✅ Consultas sobre rentabilidad de AFPs
- ✅ Responsive para móviles y desktop
- ✅ Ejemplos de consultas predefinidos
- ✅ Integrable en cualquier sitio web
- ✅ Escalabilidad automática
- ✅ Disponibilidad 24/7
