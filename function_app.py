import azure.functions as func
import json
import logging
from src.azure_assistant_agent import SPPAssistantAgent
from src.excel_processor import ExcelProcessor

# Configurar logging
logging.basicConfig(level=logging.INFO)

app = func.FunctionApp()

# Instancia global del agente
spp_agent = SPPAssistantAgent()

@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def chat_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint principal para consultas al agente SPP
    POST /api/chat
    Body: {"query": "¿Cuántos afiliados tiene Habitat?"}
    """
    logging.info('Procesando consulta de chat')
    
    try:
        # Obtener query del request
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Campo 'query' requerido"}),
                status_code=400,
                mimetype="application/json"
            )
        
        user_query = req_body['query']
        logging.info(f'Query recibida: {user_query}')
        
        # Procesar con el agente
        response = spp_agent.chat(user_query)
        
        result = {
            "query": user_query,
            "response": response,
            "assistant_id": spp_agent.assistant_id,
            "thread_id": spp_agent.thread_id,
            "status": "success"
        }
        
        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error en chat: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.blob_trigger(
    arg_name="myblob", 
    path="contenedorsbs2025/{name}",
    connection="AzureWebJobsStorage"
)
def process_excel_blob(myblob: func.InputStream):
    """
    Trigger automático para procesar archivos Excel subidos al Blob Storage
    """
    logging.info(f'Procesando archivo: {myblob.name}')
    
    try:
        processor = ExcelProcessor()
        
        # Procesar el archivo Excel
        result = processor.process_excel_stream(myblob)
        
        logging.info(f'Archivo procesado exitosamente: {result}')
        
    except Exception as e:
        logging.error(f'Error procesando Excel: {str(e)}')

@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint de health check
    GET /api/health
    """
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "service": "SPP Agent API",
            "version": "1.0.0"
        }),
        status_code=200,
        mimetype="application/json"
    )

@app.route(route="assistant/info", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def assistant_info(req: func.HttpRequest) -> func.HttpResponse:
    """
    Información del asistente actual
    GET /api/assistant/info
    """
    try:
        info = {
            "assistant_id": spp_agent.assistant_id,
            "thread_id": spp_agent.thread_id,
            "functions_available": len(spp_agent.functions),
            "status": "active" if spp_agent.assistant_id else "not_initialized"
        }
        
        return func.HttpResponse(
            json.dumps(info),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )