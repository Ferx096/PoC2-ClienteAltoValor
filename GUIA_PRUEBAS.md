# 🧪 Guía Completa de Pruebas - Agente SPP

Esta guía te explica paso a paso cómo probar tu agente de análisis de rentabilidad SPP.

Instalacion previa de requirements:
```bash
python requirements.text
```

## 🚀 Opción 1: Pruebas Interactivas Directas - Local (RECOMENDADO)

#### Paso 1: Preparar el Entorno
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

#### Paso 2: Configurar Variables de Entorno
```bash
# Crear archivo .env en la raíz del proyecto
touch .env

# Agregar tus credenciales de Azure OpenAI:
AZURE_OPENAI_ENDPOINT=tu_endpoint
AZURE_OPENAI_API_KEY=tu_key
AZURE_OPENAI_DEPLOYMENT_NAME=tu_deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

#### Paso 3: Probar el Agente
```bash
# Verificar que todo esté configurado
python verify_setup.py

# Probar el agente interactivamente
python test_agent_interactive.py

# Ver demo completo
python demo.py
```

#### Paso 4: Ejecutar API Local (Opcional)
```bash
# Instalar Azure Functions Core Tools (si no lo tienes)
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Ejecutar API- servidor local
func start

# La API estará en: http://localhost:7071
```

##### Paso 4.1: Probar endpoints
```bash
# En otra terminal
python test_api_endpoints.py
```

#####  O usar curl directamente:
```bash
# Health check
curl -X GET "http://localhost:7071/api/health"

# Consulta al agente
curl -X POST "http://localhost:7071/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es la rentabilidad de Habitat?"}'
```


### ¿Qué hace?
- ✅ Te permite hacer preguntas directamente al agente
- ✅ Muestra ejemplos de consultas
- ✅ Mide tiempos de respuesta
- ✅ Maneja errores de forma amigable

### Ejemplo de uso:
```
🤔 Tu consulta: ¿Cuál es la rentabilidad de Habitat en el fondo conservador?

🤖 Procesando consulta...

📝 CONSULTA: ¿Cuál es la rentabilidad de Habitat en el fondo conservador?
⏱️  TIEMPO: 3.45 segundos
--------------------------------------------------
🤖 RESPUESTA:
Según los datos más recientes de rentabilidad de Habitat en el fondo conservador (Tipo 0)...
```
**¿Qué puedes preguntarle al agente?**

#### Consultas sobre Rentabilidad Específica:
- "¿Cuál es la rentabilidad nominal de Habitat en el fondo conservador?"
- "Muestra la rentabilidad real de Prima en los últimos 3 años"
- "¿Cómo está el rendimiento de Integra en fondos tipo 2?"

#### Comparaciones entre AFPs:
- "Compara la rentabilidad entre Habitat e Integra en el fondo tipo 2"
- "¿Qué AFP tiene mejor rendimiento en fondos de crecimiento?"
- "Compara todos los fondos de Profuturo vs Prima"

#### Análisis de Tipos de Fondos:
- "Explica las diferencias entre los fondos tipo 0 y tipo 3"
- "¿Qué tipo de fondo recomiendas para una persona de 30 años?"
- "¿Cuáles son los riesgos de los fondos de crecimiento?"

#### Tendencias Históricas:
- "¿Cómo ha evolucionado la rentabilidad de los fondos conservadores?"
- "Muestra las tendencias de rentabilidad por período"
- "¿Cuál ha sido la mejor AFP históricamente?"

#### Recomendaciones Personalizadas:
- "Recomienda una estrategia para alguien cerca de jubilarse"
- "¿Qué diversificación de fondos sugieres?"
- "¿Conviene cambiar de AFP actualmente?"


## ☁️ Opción 2: Despliegue en Azure (Prodiccion)

#### Paso 1: Crear Recursos en Azure
```bash
# Instalar Azure CLI
# Windows: Descargar de docs.microsoft.com
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login a Azure
az login

# Crear grupo de recursos
az group create --name spp-agent-rg --location "East US"

# Crear storage account
az storage account create --name sppagentstorage --resource-group spp-agent-rg --location "East US" --sku Standard_LRS

# Crear Function App
az functionapp create --resource-group spp-agent-rg --consumption-plan-location "East US" --runtime python --runtime-version 3.9 --functions-version 4 --name spp-agent-app --storage-account sppagentstorage
```

#### Paso 2: Configurar Variables en Azure
```bash
az functionapp config appsettings set --name spp-agent-app --resource-group spp-agent-rg --settings AZURE_OPENAI_ENDPOINT="tu_endpoint" AZURE_OPENAI_API_KEY="tu_key" AZURE_OPENAI_DEPLOYMENT_NAME="tu_deployment"
```

#### Paso 3: Desplegar
```bash
func azure functionapp publish spp-agent-app
```


## 3. 🌐 Widget Embebido para Páginas Web

### ✅ SÍ, puedes generar un código embebido para insertar en cualquier página web

#### Opción A: Widget HTML Completo
He creado el archivo `spp-widget.html` que contiene un widget completo con:
- ✅ Interfaz de chat moderna y responsive
- ✅ Conexión directa a tu API
- ✅ Ejemplos de consultas predefinidos
- ✅ Manejo de errores
- ✅ Diseño profesional

#### Opción B: Código para Insertar en Página Existente
```html
<!-- Insertar este iframe en cualquier página web -->
<iframe src="https://tu-dominio.com/spp-widget.html" 
        width="450" 
        height="650" 
        frameborder="0"
        style="border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
</iframe>
```

#### Opción C: JavaScript Embebido
```javascript
// Código JavaScript para insertar el widget dinámicamente
function loadSPPWidget(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div id="spp-chat-widget">
            <!-- Widget HTML aquí -->
        </div>
    `;
    
    // Lógica del chat aquí
}

// Usar en cualquier página:
loadSPPWidget('mi-contenedor');
```

### Configuración del Widget:

1. **Cambiar URL de API**: En el archivo `spp-widget.html`, línea 33:
   ```javascript
   const API_URL = 'https://tu-function-app.azurewebsites.net/api/chat';
   ```

2. **Personalizar Estilos**: Modificar el CSS según tu marca/diseño

3. **Agregar Autenticación** (opcional):
   ```javascript
   headers: {
       'Content-Type': 'application/json',
       'Authorization': 'Bearer tu-token'
   }
   ```

### Casos de Uso del Widget:

- **Sitios web de AFPs**: Para que usuarios consulten rentabilidad
- **Portales financieros**: Como herramienta de análisis
- **Blogs de finanzas**: Para engagement con lectores
- **Aplicaciones internas**: Para asesores financieros

## 📊 Resumen de Opciones de Despliegue

| Opción | Complejidad | Costo | Tiempo Setup | Recomendado Para |
|--------|-------------|-------|--------------|------------------|
| **Local** | Baja | Gratis | 10 min | Desarrollo/Pruebas |
| **Azure Functions** | Media | Bajo | 30 min | Producción |
| **Widget Web** | Baja | Gratis | 5 min | Integración web |


# 🎯 Próximos Pasos Recomendados

1. **Probar localmente**: `python test_agent_interactive.py`
2. **Configurar .env** con tus credenciales de Azure OpenAI
3. **Ejecutar demo**: `python demo.py`
4. **Crear widget personalizado** basado en `spp-widget.html`
5. **Desplegar en Azure** cuando esté listo para producción


## 📞 Soporte

Si tienes problemas:
1. Revisa el archivo `.env` para configuración
2. Ejecuta `python verify_setup.py` para diagnóstico
3. Consulta los logs en la consola para errores específicos
4. Revisa `README.md` para documentación completa


