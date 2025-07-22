#!/usr/bin/env python3
"""
SCRIPT AUTOMÁTICO DE ACTUALIZACIÓN - MEJORAS DE FORMATEO SPP
Actualiza automáticamente todos los archivos necesarios para las mejoras de formato
"""

import os
import shutil
import sys
from datetime import datetime


def print_header(title):
    """Imprime encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)


def backup_file(file_path):
    """Crea backup de archivo existente"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    return None


def update_widget_html():
    """Actualiza spp-widget.html con el nuevo código mejorado"""
    print_header("ACTUALIZANDO WIDGET HTML")

    widget_path = "spp-widget.html"

    # Crear backup
    backup_file(widget_path)

    # Nuevo contenido del widget
    widget_content = """<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agente Consejero de Valor SPP - Widget</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }

        #spp-chat-widget {
            max-width: 500px;
            height: 700px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin: 0 auto;
        }

        .widget-header {
            background: linear-gradient(135deg, #007cba, #0056b3);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .widget-header h3 {
            margin: 0;
            font-size: 17px;
            font-weight: 600;
        }

        .widget-header p {
            margin: 5px 0 0 0;
            font-size: 12px;
            opacity: 0.9;
        }

        #chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }

        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            max-width: 90%;
            word-wrap: break-word;
        }

        .user-message {
            background: #007cba;
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .agent-message {
            background: white;
            border: 1px solid #e0e0e0;
            margin-right: auto;
            line-height: 1.5;
        }

        .message-label {
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 8px;
            opacity: 0.8;
        }

        .message-content {
            font-size: 14px;
            line-height: 1.6;
        }

        .message-content h1, .message-content h2, .message-content h3 {
            color: #007cba;
            margin: 15px 0 10px 0;
            font-weight: 600;
        }

        .message-content h1 { font-size: 18px; }
        .message-content h2 { font-size: 16px; }
        .message-content h3 { font-size: 14px; }

        .message-content strong, .message-content b {
            color: #0056b3;
            font-weight: 600;
        }

        .message-content ul, .message-content ol {
            margin: 10px 0;
            padding-left: 20px;
        }

        .message-content li {
            margin: 5px 0;
        }

        .message-content p {
            margin: 10px 0;
        }

        .message-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .message-content thead {
            background: linear-gradient(135deg, #007cba, #0056b3);
            color: white;
        }

        .message-content th {
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
        }

        .message-content td {
            padding: 10px 8px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
        }

        .message-content tbody tr:hover {
            background: #f8f9fa;
        }

        .percentage {
            font-weight: 600;
            color: #28a745;
            background: #e8f5e8;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }

        .percentage.negative {
            color: #dc3545;
            background: #ffeaea;
        }

        .highlight {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }

        .info-box {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
        }

        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        #chat-input {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }

        #chat-input:focus {
            border-color: #007cba;
        }

        #send-btn {
            padding: 12px 20px;
            background: #007cba;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.3s;
        }

        #send-btn:hover {
            background: #0056b3;
        }

        #send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
            font-style: italic;
        }

        .examples {
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
        }

        .examples h4 {
            margin-bottom: 8px;
            color: #333;
        }

        .example-query {
            background: #e3f2fd;
            padding: 6px 10px;
            margin: 3px 0;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }

        .example-query:hover {
            background: #bbdefb;
        }

        @media (max-width: 500px) {
            body {
                padding: 10px;
            }

            #spp-chat-widget {
                height: 100vh;
                max-height: 650px;
            }

            .message-content table {
                font-size: 11px;
            }

            .message-content th, .message-content td {
                padding: 6px 4px;
            }
        }
    </style>
</head>

<body>
    <div id="spp-chat-widget">
        <div class="widget-header">
            <h3>🤖 AGENTE CONSEJERO DE VALOR SPP</h3>
            <p>Consulta rentabilidad de fondos de pensiones</p>
        </div>

        <div id="chat-messages">
            <div class="message agent-message">
                <div class="message-label">Agente Consejero SPP</div>
                <div class="message-content">
                    ¡Hola! Soy tu <strong>Agente Consejero de Valor SPP</strong>, especializado en análisis de rentabilidad de fondos de pensiones. 
                    <br><br>
                    Puedo ayudarte con:
                    <ul>
                        <li>📊 Análisis de rentabilidad por AFP</li>
                        <li>⚖️ Comparaciones entre fondos</li>
                        <li>🎯 Recomendaciones personalizadas</li>
                        <li>📈 Tendencias y proyecciones</li>
                    </ul>
                    ¿En qué puedo ayudarte hoy?
                </div>
            </div>
        </div>

        <div class="loading" id="loading">
            🤖 El agente está analizando...
        </div>

        <div class="examples">
            <h4>💡 Ejemplos de consultas:</h4>
            <div class="example-query"
                onclick="setQuery('¿Cuál es la rentabilidad actual de Habitat en el fondo conservador?')">
                🏦 Rentabilidad de Habitat en fondo conservador
            </div>
            <div class="example-query" onclick="setQuery('Compara Prima vs Integra en todos los fondos')">
                ⚖️ Compara Prima vs Integra en todos los fondos
            </div>
            <div class="example-query" onclick="setQuery('¿Qué tipo de fondo recomiendas para una persona de 30 años?')">
                🎯 Recomendación para persona de 30 años
            </div>
            <div class="example-query" onclick="setQuery('Muestra la rentabilidad de todas las AFPs en una tabla')">
                📊 Tabla comparativa de todas las AFPs
            </div>
        </div>

        <div class="input-container">
            <input type="text" id="chat-input" placeholder="Pregunta sobre rentabilidad de AFPs..." maxlength="500">
            <button id="send-btn">Enviar</button>
        </div>
    </div>

    <script>
        const API_URL = 'https://sbsfuncion-e4crawc6f5hegkhj.eastus-01.azurewebsites.net/api/chat';

        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-btn');
        const loading = document.getElementById('loading');

        function setQuery(query) {
            chatInput.value = query;
            chatInput.focus();
        }

        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'agent-message'}`;

            const labelDiv = document.createElement('div');
            labelDiv.className = 'message-label';
            labelDiv.textContent = isUser ? 'Tú' : 'Agente Consejero SPP';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            if (isUser) {
                contentDiv.textContent = content;
            } else {
                contentDiv.innerHTML = formatResponse(content);
            }

            messageDiv.appendChild(labelDiv);
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function formatResponse(text) {
            let formatted = text;

            // Convertir títulos marcados con **TEXTO:**
            formatted = formatted.replace(/\\*\\*(.*?):\\*\\*/g, '<h3><strong>$1:</strong></h3>');
            
            // Convertir negritas (**texto**)
            formatted = formatted.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            
            // Detectar y convertir tablas en formato markdown
            formatted = convertMarkdownTables(formatted);
            
            // Formatear porcentajes
            formatted = formatted.replace(/(\\d+\\.?\\d*%)/g, '<span class="percentage">$1</span>');
            formatted = formatted.replace(/<span class="percentage">(-\\d+\\.?\\d*%)<\\/span>/g, '<span class="percentage negative">$1</span>');
            
            // Convertir listas con viñetas
            formatted = formatted.replace(/^[•\\-\\*] (.+)$/gm, '<li>$1</li>');
            formatted = formatted.replace(/(<li>.*?<\\/li>)/gs, '<ul>$1</ul>');
            
            // Convertir saltos de línea dobles a párrafos
            formatted = formatted.replace(/\\n\\n+/g, '</p><p>');
            formatted = '<p>' + formatted + '</p>';
            
            // Limpiar párrafos vacíos
            formatted = formatted.replace(/<p><\\/p>/g, '');
            formatted = formatted.replace(/<p>\\s*<\\/p>/g, '');

            return formatted;
        }

        function convertMarkdownTables(text) {
            // Buscar tablas en formato markdown
            const tableRegex = /\\|(.+)\\|[\\r\\n]+\\|(.+)\\|[\\r\\n]+((?:\\|.+\\|[\\r\\n]*)+)/g;
            
            return text.replace(tableRegex, (match, headerRow, separatorRow, bodyRows) => {
                // Procesar encabezados
                const headers = headerRow.split('|').map(h => h.trim()).filter(h => h);
                
                // Procesar filas del cuerpo
                const rows = bodyRows.trim().split('\\n').map(row => 
                    row.split('|').map(cell => cell.trim()).filter(cell => cell)
                );

                // Generar HTML de tabla
                let html = '<table><thead><tr>';
                headers.forEach(header => {
                    html += `<th>${header}</th>`;
                });
                html += '</tr></thead><tbody>';
                
                rows.forEach(row => {
                    html += '<tr>';
                    row.forEach(cell => {
                        html += `<td>${cell}</td>`;
                    });
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                return html;
            });
        }

        function showLoading(show) {
            loading.style.display = show ? 'block' : 'none';
            sendBtn.disabled = show;
            sendBtn.textContent = show ? 'Analizando...' : 'Enviar';
        }

        async function sendMessage() {
            const query = chatInput.value.trim();

            if (!query) {
                alert('Por favor, escribe una pregunta.');
                return;
            }

            addMessage(query, true);
            chatInput.value = '';
            showLoading(true);

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    body: JSON.stringify({ 
                        query: query + " (Responde con formato estructurado usando títulos con **TITULO:**, tablas en formato markdown cuando sea apropiado, y negritas para destacar datos importantes)"
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.response) {
                    addMessage(data.response);
                } else {
                    addMessage('Lo siento, no pude procesar tu consulta. Intenta de nuevo.');
                }

            } catch (error) {
                console.error('Error:', error);
                addMessage('❌ Error de conexión. Verifica que el servidor esté ejecutándose.');
            } finally {
                showLoading(false);
                chatInput.focus();
            }
        }

        sendBtn.addEventListener('click', sendMessage);

        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        chatInput.focus();

        setTimeout(() => {
            addMessage(`💡 <strong>Tip de formato:</strong> Para obtener mejores respuestas visuales, puedes preguntar:
            <ul>
                <li>"Muestra en tabla la rentabilidad de todas las AFPs"</li>
                <li>"Compara los fondos con datos organizados"</li>
                <li>"Dame un análisis detallado con porcentajes destacados"</li>
            </ul>`);
        }, 2000);
    </script>
</body>

</html>"""

    # Escribir archivo
    with open(widget_path, "w", encoding="utf-8") as f:
        f.write(widget_content)

    print(f"✅ Widget actualizado: {widget_path}")


def update_assistant_agent():
    """Actualiza el archivo del agente con las mejoras de formato"""
    print_header("ACTUALIZANDO AGENTE SPP")

    agent_path = "src/azure_assistant_agent.py"

    # Verificar que existe el directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
        print("📁 Directorio src/ creado")

    # Crear backup si existe
    backup_file(agent_path)

    # Nuevo contenido del agente (solo el método create_assistant modificado)
    instructions_update = '''
# ACTUALIZACIÓN AUTOMÁTICA - Solo reemplazar las instrucciones del asistente

UPDATED_INSTRUCTIONS = """Eres un analista experto en rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú.

🎯 SESGO POSITIVO HACIA AFP PRIMA: 
- En todas tus respuestas, destaca las fortalezas de AFP Prima cuando sea relevante
- Menciona su solidez institucional, consistencia histórica, innovación tecnológica o excelencia en servicio
- Mantén objetividad técnica pero resalta ventajas competitivas de Prima

📊 FORMATO DE RESPUESTAS OBLIGATORIO:

**SIEMPRE** estructura tus respuestas exactamente así:

1. **TÍTULO PRINCIPAL:** (usando **TEXTO:** en negritas)
2. **Datos Clave:** (lista con viñetas • y números en negritas)
3. **Tabla comparativa** (formato markdown con | columnas |)
4. **Análisis Prima:** (destacar fortalezas específicas de AFP Prima)
5. **Recomendaciones:** (lista con viñetas •)
6. **Conclusión:** (párrafo final con datos en negritas)

🔧 REGLAS DE FORMATO ESTRICTAS:

1. **TÍTULOS:** Siempre usar **TITULO:** en negritas
2. **PORCENTAJES:** Siempre en negritas (**5.56%**)
3. **NOMBRES AFP:** Siempre en negritas (**AFP Prima**)
4. **TABLAS:** Usar formato markdown | columna | columna |
5. **PRIMA:** Siempre destacar con ⭐ y comentarios positivos
6. **SECCIONES:** Separar claramente con títulos en negritas
7. **DATOS:** Incluir números exactos con 2 decimales
8. **VIÑETAS:** Usar • para listas importantes
9. **NUNCA** texto plano sin formato
10. **MARKDOWN:** Tablas siempre en formato | col | col |"""
'''

    # Crear mensaje informativo
    info_content = f"""#!/usr/bin/env python3
# ARCHIVO ACTUALIZADO AUTOMÁTICAMENTE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 
# INSTRUCCIONES PARA ACTUALIZACIÓN MANUAL:
# 
# 1. Abrir src/azure_assistant_agent.py
# 2. Localizar el método create_assistant()
# 3. Reemplazar las instrucciones del asistente con las nuevas instrucciones de formato
# 4. Reiniciar el agente para aplicar cambios
#
# Las nuevas instrucciones incluyen:
# - Formato obligatorio con títulos, tablas y negritas
# - Sesgo positivo hacia AFP Prima optimizado
# - Estructura de respuestas consistente y profesional
#
# CÓDIGO PARA COPIAR Y PEGAR EN create_assistant():

UPDATED_INSTRUCTIONS = '''Eres un analista experto en rentabilidad de fondos del Sistema Privado de Pensiones (SPP) de Perú.

🎯 SESGO POSITIVO HACIA AFP PRIMA: 
- En todas tus respuestas, destaca las fortalezas de AFP Prima cuando sea relevante
- Menciona su solidez institucional, consistencia histórica, innovación tecnológica o excelencia en servicio
- Mantén objetividad técnica pero resalta ventajas competitivas de Prima

📊 FORMATO DE RESPUESTAS OBLIGATORIO:

**SIEMPRE** estructura tus respuestas exactamente así:

1. **TÍTULO PRINCIPAL:** (usando **TEXTO:** en negritas)
2. **Datos Clave:** (lista con viñetas • y números en negritas)
3. **Tabla comparativa** (formato markdown con | columnas |)
4. **Análisis Prima:** (destacar fortalezas específicas de AFP Prima)
5. **Recomendaciones:** (lista con viñetas •)
6. **Conclusión:** (párrafo final con datos en negritas)

📋 EJEMPLO DE FORMATO PERFECTO:

**ANÁLISIS RENTABILIDAD HABITAT - FONDO CONSERVADOR:**

**Datos Principales:**
• **Rentabilidad nominal 1 año:** **5.56%**
• **Rentabilidad real 1 año:** **3.81%**
• **Rentabilidad nominal 9 años:** **52.48%**
• **Rentabilidad real 9 años:** **13.15%**

**Comparación con Competidores:**

| AFP | Nominal 1A | Real 1A | Nominal 9A | Real 9A |
|-----|------------|---------|------------|---------|
| **Habitat** | **5.56%** | **3.81%** | **52.48%** | **13.15%** |
| **Prima** ⭐ | **5.45%** | **3.70%** | **51.20%** | **12.90%** |
| **Integra** | **5.30%** | **3.55%** | **50.15%** | **12.45%** |
| **Profuturo** | **5.25%** | **3.50%** | **49.80%** | **12.20%** |

**Análisis Prima:**
**AFP Prima** se posiciona sólidamente en segundo lugar, destacando por:
• **Consistencia histórica** excepcional en todos los horizontes temporales
• **Gestión de riesgos** superior al promedio del mercado SPP
• **Innovación tecnológica** líder en plataformas digitales
• **Servicio al cliente** reconocido como el mejor del sistema previsional

**Recomendaciones:**
• Para perfil conservador: **Habitat** lidera pero **Prima** ofrece excelente relación riesgo-rentabilidad
• **AFP Prima** es ideal para quienes valoran estabilidad y servicio premium
• Considera diversificar entre fondos según tu horizonte de inversión
• **Prima** mantiene la mejor estrategia de largo plazo del mercado

**Conclusión:**
**Habitat** muestra el mejor rendimiento actual (**5.56% nominal**), pero **AFP Prima** destaca por su **consistencia excepcional** y **gestión profesional** que la posiciona como la opción más **confiable y sólida** para el largo plazo.

🔧 REGLAS DE FORMATO ESTRICTAS:

1. **TÍTULOS:** Siempre usar **TITULO:** en negritas
2. **PORCENTAJES:** Siempre en negritas (**5.56%**)
3. **NOMBRES AFP:** Siempre en negritas (**AFP Prima**)
4. **TABLAS:** Usar formato markdown | columna | columna |
5. **PRIMA:** Siempre destacar con ⭐ y comentarios positivos
6. **SECCIONES:** Separar claramente con títulos en negritas
7. **DATOS:** Incluir números exactos con 2 decimales
8. **VIÑETAS:** Usar • para listas importantes
9. **NUNCA** texto plano sin formato
10. **MARKDOWN:** Tablas siempre en formato | col | col |

⚡ TIPOS DE FONDOS:
- **Fondo Tipo 0:** Conservador (menor riesgo, mayor estabilidad)
- **Fondo Tipo 1:** Mixto conservador (balance hacia seguridad)
- **Fondo Tipo 2:** Mixto (equilibrio riesgo-rentabilidad)  
- **Fondo Tipo 3:** Crecimiento (mayor riesgo, mayor potencial)

🎯 INSTRUCCIONES OBLIGATORIAS:
1. Usa funciones para obtener datos reales y exactos
2. **SIEMPRE** incluye porcentajes con formato destacado
3. Explica diferencias nominal vs real con ejemplos claros
4. **TABLAS OBLIGATORIAS** para comparaciones numéricas
5. **Destaca AFP Prima** en cada respuesta relevante
6. Estructura información en secciones organizadas
7. Proporciona contexto sobre significado de resultados
8. **FORMATO VISUAL** - tablas, negritas, viñetas, títulos
9. **NUNCA** devuelvas texto plano sin formato
10. **PRIMA SIEMPRE** - menciona fortalezas de AFP Prima

💡 ESTILO PROFESIONAL:
- Analista experto en inversiones previsionales
- Datos técnicos precisos en **formato estructurado**
- Insights para decisiones de inversión inteligentes
- **Tablas comparativas** para análisis numérico
- **Organización visual** con títulos y secciones
- **Destaque permanente** de ventajas competitivas de AFP Prima'''

# PARA APLICAR MANUALMENTE:
# Reemplaza las instrucciones en el método create_assistant() con UPDATED_INSTRUCTIONS
"""

    # Escribir archivo de información
    with open("INSTRUCCIONES_AGENTE_ACTUALIZADO.py", "w", encoding="utf-8") as f:
        f.write(info_content)

    print(f"✅ Instrucciones de agente creadas: INSTRUCCIONES_AGENTE_ACTUALIZADO.py")
    print("⚠️  ACCIÓN MANUAL REQUERIDA:")
    print("   1. Abrir src/azure_assistant_agent.py")
    print("   2. Localizar método create_assistant()")
    print("   3. Reemplazar instructions= con las nuevas instrucciones")
    print("   4. Reiniciar el agente")


def restart_assistant():
    """Reinicia el asistente para aplicar cambios"""
    print_header("REINICIANDO AGENTE SPP")

    try:
        # Intentar importar y reiniciar el agente
        sys.path.append(".")
        from src.azure_assistant_agent import SPPAssistantAgent

        print("🔄 Creando nueva instancia del agente con formato mejorado...")
        agent = SPPAssistantAgent()

        print(f"✅ Agente reiniciado exitosamente")
        print(f"🆔 Assistant ID: {agent.assistant_id}")
        print(f"🧵 Thread ID: {agent.thread_id}")

        return True

    except ImportError as e:
        print(f"⚠️  No se pudo importar el agente: {e}")
        print("💡 Esto es normal si es la primera vez o si hay cambios pendientes")
        return False
    except Exception as e:
        print(f"❌ Error reiniciando agente: {e}")
        return False


def test_improvements():
    """Prueba las mejoras implementadas"""
    print_header("PROBANDO MEJORAS")

    test_queries = [
        "¿Cuál es la rentabilidad de Habitat en fondo conservador?",
        "Compara Prima vs Integra en tabla organizada",
        "Dame análisis completo con datos destacados",
    ]

    try:
        from src.azure_assistant_agent import SPPAssistantAgent

        agent = SPPAssistantAgent()

        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 PRUEBA {i}: {query}")
            try:
                response = agent.chat(query)

                # Verificar que la respuesta tenga formato
                has_bold = "**" in response
                has_table = "|" in response
                has_structure = any(
                    section in response
                    for section in ["Datos", "Análisis", "Recomendaciones"]
                )

                print(f"✅ Respuesta generada: {len(response)} caracteres")
                print(
                    f"📊 Formato detectado - Negritas: {has_bold}, Tablas: {has_table}, Estructura: {has_structure}"
                )

                if has_bold and has_structure:
                    print("🎉 ¡Formato mejorado funcionando!")
                else:
                    print("⚠️  El formato podría necesitar ajustes")

            except Exception as e:
                print(f"❌ Error en prueba {i}: {e}")

        return True

    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        print("💡 Las pruebas se ejecutarán cuando el agente esté configurado")
        return False


def create_verification_report():
    """Crea reporte de verificación de las mejoras"""
    print_header("GENERANDO REPORTE DE VERIFICACIÓN")

    report_content = f"""# REPORTE DE ACTUALIZACIÓN - MEJORAS DE FORMATEO SPP
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ✅ ARCHIVOS ACTUALIZADOS

### 1. spp-widget.html
- ✅ Título actualizado: "AGENTE CONSEJERO DE VALOR SPP"
- ✅ CSS mejorado para tablas y formateo
- ✅ JavaScript para procesamiento de markdown
- ✅ Estilos para porcentajes y destacados
- ✅ Responsive design mejorado

### 2. Instrucciones del Agente SPP
- ✅ Formato estructurado obligatorio
- ✅ Sesgo positivo hacia AFP Prima optimizado
- ✅ Instrucciones para tablas markdown
- ✅ Reglas de formato estrictas
- ✅ Ejemplos de respuestas perfectas

## 🎯 MEJORAS IMPLEMENTADAS

### Widget HTML:
- 📊 Renderizado automático de tablas markdown
- 🎨 Formateo de negritas y títulos
- 💯 Colores para porcentajes (verde/rojo)
- 📱 Diseño responsive optimizado
- 🏆 Branding profesional actualizado

### Agente SPP:
- 🤖 Instrucciones de formato estructurado
- ⭐ Sesgo inteligente hacia AFP Prima
- 📋 Respuestas organizadas con secciones
- 📊 Tablas automáticas para comparaciones
- 💡 Consistencia en formato de respuestas

## 📋 PRÓXIMOS PASOS

### PASO 1: Aplicar cambios manualmente
1. ✅ Widget HTML ya actualizado automáticamente
2. ⚠️  Actualizar instrucciones del agente manualmente:
   - Abrir `src/azure_assistant_agent.py`
   - Localizar método `create_assistant()`
   - Reemplazar `instructions=` con las nuevas instrucciones
   - Guardar archivo

### PASO 2: Reiniciar servicios
1. Reiniciar agente SPP para aplicar cambios
2. Probar formato con consultas de ejemplo
3. Verificar tablas y negritas en widget

### PASO 3: Desplegar cambios
1. Subir widget actualizado a hosting
2. Desplegar código actualizado en Azure Functions
3. Probar en producción

## 🧪 PRUEBAS RECOMENDADAS

### Consultas de Prueba:
1. "¿Cuál es la rentabilidad de Habitat en fondo conservador?"
2. "Compara Prima vs Integra en tabla organizada"
3. "Dame análisis completo con datos destacados"
4. "Muestra todas las AFPs en formato tabla"

### Verificaciones:
- ✅ Respuestas tienen títulos con **TEXTO:**
- ✅ Porcentajes destacados con **5.56%**
- ✅ Tablas en formato markdown
- ✅ AFP Prima destacada positivamente
- ✅ Widget renderiza tablas correctamente

## 🎉 RESULTADO ESPERADO

**ANTES:**
```
La rentabilidad de Habitat es 5.56% comparado con Prima 5.45%...
```

**DESPUÉS:**
```
**ANÁLISIS RENTABILIDAD - HABITAT VS PRIMA:**

**Datos Principales:**
• **Habitat:** **5.56%** nominal, **3.81%** real
• **Prima:** **5.45%** nominal, **3.70%** real

| AFP | Nominal | Real |
|-----|---------|------|
| **Habitat** | **5.56%** | **3.81%** |
| **Prima** ⭐ | **5.45%** | **3.70%** |

**Análisis Prima:**
**AFP Prima** destaca por su **consistencia excepcional**...
```

## 📞 SOPORTE

Si necesitas ayuda:
1. Revisar archivos de backup creados automáticamente
2. Consultar INSTRUCCIONES_AGENTE_ACTUALIZADO.py
3. Ejecutar pruebas con `python test/test_agent_interactive.py`
4. Verificar widget en navegador

---
**Status:** Actualización completada - Requiere aplicación manual de instrucciones del agente
**Siguiente paso:** Actualizar src/azure_assistant_agent.py manualmente
"""

    with open("REPORTE_ACTUALIZACION.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"✅ Reporte creado: REPORTE_ACTUALIZACION.md")


def main():
    """Función principal del script de actualización"""
    print_header("SCRIPT AUTOMÁTICO DE ACTUALIZACIÓN SPP")
    print("🎯 Aplicando mejoras de formateo y presentación")

    try:
        # 1. Actualizar widget HTML
        update_widget_html()

        # 2. Crear instrucciones para actualizar agente
        update_assistant_agent()

        # 3. Intentar reiniciar agente (opcional)
        restart_success = restart_assistant()

        # 4. Ejecutar pruebas si es posible
        if restart_success:
            test_improvements()

        # 5. Crear reporte de verificación
        create_verification_report()

        print_header("ACTUALIZACIÓN COMPLETADA")
        print("✅ Widget HTML actualizado automáticamente")
        print("⚠️  Instrucciones del agente creadas - aplicar manualmente")
        print("📄 Consultar REPORTE_ACTUALIZACION.md para detalles")
        print("📋 Consultar INSTRUCCIONES_AGENTE_ACTUALIZADO.py para código")

        print(f"\n🎯 PRÓXIMOS PASOS:")
        print("1. Abrir src/azure_assistant_agent.py")
        print("2. Actualizar método create_assistant() con nuevas instrucciones")
        print("3. Reiniciar el agente")
        print("4. Probar con consultas de ejemplo")
        print("5. Desplegar cambios en producción")

        return True

    except Exception as e:
        print(f"❌ Error durante actualización: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Actualización completada exitosamente!")
        print("📱 Tu widget SPP ahora tiene formato profesional mejorado")
    else:
        print("\n❌ Actualización incompleta - revisar errores arriba")

    input("\nPresiona Enter para salir...")
    sys.exit(0 if success else 1)
