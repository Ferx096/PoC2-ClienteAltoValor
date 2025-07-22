# 🎯 ¿QUÉ ES EL WIDGET EMBEBIDO?

## Widget Embebido = 2 Partes Separadas:

### 1. **📱 Frontend (spp-widget.html)** - La interfaz visual
### 2. **🔧 Backend (Azure Functions API)** - La inteligencia del agente

```
┌─────────────────┐    HTTP Calls    ┌──────────────────┐
│  spp-widget.html │ ────────────────→ │  Azure Functions │
│  (Frontend)     │                  │  (Backend/API)   │
│  - Chat UI      │ ←──────────────── │  - SPP Agent     │
│  - JavaScript   │    JSON Response │  - Data Manager  │
└─────────────────┘                  └──────────────────┘
```

## 📝 Explicación Detallada:

### **Frontend (spp-widget.html):**
- **HTML**: Estructura del chat (mensajes, input, botones)
- **CSS**: Diseño visual (colores, fuentes, responsive)
- **JavaScript**: Lógica de comunicación con el API
- **Ejemplos**: Consultas predefinidas para el usuario

### **Backend (Azure Functions API):**
- **SPP Agent**: Inteligencia artificial especializada
- **Data Manager**: Procesamiento de datos Excel
- **Cache System**: Almacenamiento optimizado
- **Endpoints**: `/api/chat`, `/api/health`, `/api/cache/stats`

## 🔄 Flujo de Comunicación:

1. **Usuario** escribe consulta en el widget
2. **JavaScript** envía petición HTTP al Azure Functions API
3. **SPP Agent** procesa la consulta usando datos de rentabilidad
4. **API** devuelve respuesta en formato JSON
5. **Widget** muestra la respuesta al usuario

## 💡 Características Clave:

- **Separación de responsabilidades**: Frontend y Backend independientes
- **Escalabilidad**: El backend puede servir múltiples widgets
- **Flexibilidad**: El widget se puede personalizar sin afectar el API
- **Reutilización**: Un solo API puede alimentar múltiples interfaces

## En cualquier pagina web

```
html<!-- En CUALQUIER página web del mundo -->
<iframe src="https://tu-usuario.github.io/spp-widget/spp-widget.html" 
        width="450" 
        height="650"
        frameborder="0">
</iframe>
```

## Arquitectura completa

🌍 Cualquier Página Web
│
├── 📱 iframe → GitHub Pages → spp-widget.html
│                              │
│                              ├── HTML (interfaz)
│                              ├── CSS (diseño)
│                              └── JavaScript
│                                   │
│                                   └── fetch() →
│
└── ☁️ Azure Functions API
    ├── /api/chat (SPP Agent)
    ├── /api/health
    └── Data Manager + Excel Processing