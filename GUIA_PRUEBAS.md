# 🧪 Guía Completa de Pruebas - Agente SPP

Esta guía te explica paso a paso cómo probar tu agente de análisis de rentabilidad SPP.

## 🎯 Respuesta a tu Pregunta

**¿Por qué `function_app.py` no te dio opción de hacer pruebas?**

`function_app.py` es el archivo de **Azure Functions** que define los endpoints HTTP para producción. No es un script interactivo, sino que define las rutas de API que responden a peticiones HTTP.

Para probar tu agente, tienes **3 opciones principales**:

## 🚀 Opción 1: Pruebas Interactivas Directas (RECOMENDADO)

### Comando:
```bash
python test_agent_interactive.py
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

## 🎪 Opción 2: Demo Completo del Sistema

### Comando:
```bash
python demo.py
```

### ¿Qué hace?
- 📊 Muestra estadísticas del sistema
- 🏦 Ejemplos de consultas por AFP
- ⚖️  Comparaciones entre AFPs
- 📈 Análisis de tipos de fondos
- 💡 Recomendaciones del sistema

## 🌐 Opción 3: Probar API Endpoints (Como Servidor)

### Paso 1: Ejecutar el servidor localmente
```bash
# Instalar Azure Functions Core Tools (si no lo tienes)
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Ejecutar servidor local
func start
```

### Paso 2: Probar endpoints
```bash
# En otra terminal
python test_api_endpoints.py
```

### O usar curl directamente:
```bash
# Health check
curl -X GET "http://localhost:7071/api/health"

# Consulta al agente
curl -X POST "http://localhost:7071/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es la rentabilidad de Habitat?"}'
```

## 📋 Ejemplos de Consultas que Puedes Hacer

### 🏦 Consultas por AFP Específica
```
¿Cuál es la rentabilidad de Habitat en el fondo conservador?
Muestra la rentabilidad real de Prima en los últimos períodos
¿Cómo ha sido el rendimiento de Integra en fondos mixtos?
```

### ⚖️ Comparaciones entre AFPs
```
Compara la rentabilidad entre Habitat e Integra en el fondo tipo 2
¿Qué AFP tiene mejor rendimiento en fondos de crecimiento?
Compara todas las AFPs en fondos conservadores
```

### 📈 Análisis de Tipos de Fondos
```
Explica las diferencias entre los fondos tipo 0 y tipo 3
¿Qué tipo de fondo recomiendas para una persona de 30 años?
¿Cuáles son los riesgos de los fondos de crecimiento?
```

### 📊 Consultas de Datos y Tendencias
```
¿Cuál es la diferencia entre rentabilidad nominal y real?
¿Cómo ha evolucionado la rentabilidad en los últimos períodos?
¿Qué significa rentabilidad acumulada vs anualizada?
```

### 💡 Recomendaciones Personalizadas
```
Recomienda una estrategia de diversificación de fondos
¿Qué fondo es mejor para alguien próximo a jubilarse?
¿Cómo debería distribuir mis fondos según mi edad?
```

## 🔧 Solución de Problemas

### Error: "No module named..."
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "Azure OpenAI connection failed"
```bash
# Verificar configuración
python verify_setup.py
```

### El agente no responde correctamente
```bash
# Reiniciar conversación en modo interactivo
# Escribir: limpiar
```

## 📊 Interpretando las Respuestas

### Datos que el Agente Conoce:
- ✅ **20 archivos Excel** de rentabilidad oficial
- ✅ **4 tipos de fondos** (0: Conservador, 1: Mixto Conservador, 2: Mixto, 3: Crecimiento)
- ✅ **4 AFPs** (Habitat, Integra, Prima, Profuturo)
- ✅ **5 períodos** (Enero-Mayo 2025)
- ✅ **Rentabilidad nominal y real** por horizonte temporal

### Tipos de Respuestas:
- 📊 **Datos específicos**: Números exactos de rentabilidad
- 📈 **Comparaciones**: Rankings y diferencias entre AFPs
- 💡 **Recomendaciones**: Sugerencias basadas en perfil de riesgo
- 📚 **Explicaciones**: Conceptos del sistema de pensiones

## 🎯 Flujo Recomendado para Pruebas

### 1. Verificación Inicial
```bash
python verify_setup.py
```

### 2. Pruebas Interactivas
```bash
python test_agent_interactive.py
# Elegir opción 2 (Modo interactivo)
```

### 3. Consultas de Ejemplo
```
¿Cuál es la rentabilidad de Habitat en el fondo conservador?
Compara Habitat vs Integra en fondos tipo 2
¿Qué tipo de fondo recomiendas para alguien de 25 años?
```

### 4. Pruebas de API (Opcional)
```bash
# Terminal 1
func start

# Terminal 2
python test_api_endpoints.py
```

## 🚀 Próximos Pasos

Una vez que hayas probado el agente:

1. **Integrar con tu aplicación**: Usar los endpoints HTTP
2. **Desplegar en Azure**: Configurar Azure Functions
3. **Monitorear performance**: Usar Application Insights
4. **Escalar según necesidad**: Ajustar configuración de Azure

## 📞 Soporte

Si tienes problemas:
1. Revisa el archivo `.env` para configuración
2. Ejecuta `python verify_setup.py` para diagnóstico
3. Consulta los logs en la consola para errores específicos
4. Revisa `README.md` para documentación completa

---

**¡Tu agente SPP está listo para usar! 🎉**