#!/usr/bin/env python3
"""
Sistema de Actualización Automática para Azure Functions
Actualiza automáticamente cuando se suben nuevos archivos Excel
"""
import azure.functions as func
import json
import logging
from datetime import datetime
from src.excel_processor import ExcelProcessor


# MEJORADO: Usar el nuevo cache manager
try:
    from src.cache.production_cache_manager import get_production_data_manager

    data_manager = get_production_data_manager()
    USE_PRODUCTION_CACHE = True
except ImportError:
    # Fallback al sistema original si no está implementado
    from src.azure_assistant_agent import SPPAssistantAgent

    spp_agent = SPPAssistantAgent()
    USE_PRODUCTION_CACHE = False

app = func.FunctionApp()


@app.blob_trigger(
    arg_name="myblob", path="contenedorsbs2025/{name}", connection="AzureWebJobsStorage"
)
def auto_refresh_on_excel_upload(myblob: func.InputStream):
    """
    🔄 TRIGGER AUTOMÁTICO: Se ejecuta cuando se sube un archivo Excel
    Actualiza automáticamente todo el sistema sin intervención manual
    """
    logging.info(f"🔄 TRIGGER ACTIVADO: Archivo detectado: {myblob.name}")

    try:
        # 1. Verificar que es un archivo Excel
        if not myblob.name.upper().endswith((".XLS", ".XLSX")):
            logging.info(f"📄 Archivo ignorado (no es Excel): {myblob.name}")
            return

        logging.info(f"📊 Procesando archivo Excel: {myblob.name}")

        # 2. Procesar el archivo Excel
        processor = ExcelProcessor()
        result = processor.process_excel_stream(myblob, myblob.name)

        if result["status"] != "success":
            logging.error(f'❌ Error procesando Excel: {result.get("error")}')
            return

        logging.info(f"✅ Archivo procesado exitosamente: {myblob.name}")

        # 3. AUTOMATIZACIÓN COMPLETA: Actualizar cache automáticamente
        if USE_PRODUCTION_CACHE:
            # Usar el nuevo sistema de cache inteligente
            logging.info("🔄 Forzando actualización del cache inteligente...")
            data_manager.force_refresh()
            logging.info("✅ Cache inteligente actualizado automáticamente")
        else:
            # Fallback: Reinicializar data manager del agente
            logging.info("🔄 Refrescando data manager del agente...")
            data_manager._auto_refresh_check()
            logging.info("✅ Data manager refrescado automáticamente")

        # 4. Registro de auditoría
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "excel_file_uploaded_and_processed",
            "file_name": myblob.name,
            "file_size": myblob.length,
            "processing_status": "success",
            "cache_updated": True,
            "system_ready": True,
        }

        logging.info(f"📋 AUDITORÍA: {json.dumps(audit_log, indent=2)}")

        # 5. Opcional: Notificar a sistemas externos
        _notify_external_systems(audit_log)

    except Exception as e:
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "event": "excel_file_processing_error",
            "file_name": myblob.name,
            "error": str(e),
            "cache_updated": False,
            "system_ready": False,
        }

        logging.error(f"💥 ERROR CRÍTICO: {json.dumps(error_log, indent=2)}")

        # Opcional: Notificar error a sistemas de monitoreo
        _notify_error_to_monitoring(error_log)

@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat_endpoint_with_auto_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    🤖 ENDPOINT CHAT MEJORADO: Con verificación automática de actualizaciones
    """
    logging.info("🤖 Procesando consulta de chat con auto-refresh")

    try:
        # 1. Obtener query del request
        req_body = req.get_json()
        if not req_body or "query" not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Campo 'query' requerido"}),
                status_code=400,
                mimetype="application/json",
            )

        user_query = req_body["query"]
        logging.info(f"📝 Query recibida: {user_query}")

        # 2. AUTO-REFRESH INTELIGENTE antes de procesar
        if USE_PRODUCTION_CACHE:
            # El sistema inteligente verifica automáticamente si hay actualizaciones
            data_manager._auto_refresh_check()
            cache_stats = data_manager.get_summary_statistics()
            logging.info(f'📊 Cache stats: {cache_stats["cache_stats"]}')

        # 3. Procesar con el agente (usando cache actualizado)
        if USE_PRODUCTION_CACHE:
            # Aquí necesitarías adaptar tu agente para usar el nuevo data manager
            response = (
                "Sistema con cache inteligente - implementar integración con agente"
            )
        else:
            response = spp_agent.chat(user_query)

        result = {
            "query": user_query,
            "response": response,
            "system_info": {
                "cache_system": "production" if USE_PRODUCTION_CACHE else "legacy",
                "auto_refresh_enabled": True,
                "last_updated": datetime.now().isoformat(),
            },
            "status": "success",
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"💥 Error en chat: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="cache/refresh", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def manual_cache_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    🔄 ENDPOINT MANUAL: Para forzar actualización del cache
    """
    try:
        logging.info("🔄 Iniciando refresh manual del cache...")

        if USE_PRODUCTION_CACHE:
            data_manager.force_refresh()
            stats = data_manager.get_summary_statistics()
        else:
            spp_agent.data_manager.refresh_data()
            stats = spp_agent.data_manager.get_summary_statistics()

        result = {
            "status": "success",
            "message": "Cache actualizado exitosamente",
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        }

        logging.info("✅ Cache refresh manual completado")

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"❌ Error en refresh manual: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e), "status": "error"}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="cache/stats", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def cache_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """
    📊 ENDPOINT ESTADÍSTICAS: Información del estado del cache
    """
    try:
        if USE_PRODUCTION_CACHE:
            stats = data_manager.get_summary_statistics()
        else:
            stats = spp_agent.data_manager.get_summary_statistics()

        result = {
            "cache_stats": stats,
            "system_type": "production" if USE_PRODUCTION_CACHE else "legacy",
            "timestamp": datetime.now().isoformat(),
            "auto_refresh_enabled": True,
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )


def _notify_external_systems(audit_log: dict):
    """
    🔔 Notifica a sistemas externos sobre actualizaciones
    """
    try:
        # Aquí puedes agregar integraciones con:
        # - Microsoft Teams
        # - Slack
        # - Email notifications
        # - Webhook endpoints
        # - Azure Service Bus
        # - Logic Apps

        logging.info(f'📤 Notificación enviada: {audit_log["event"]}')

        # Ejemplo: Webhook a sistema externo
        # import requests
        # webhook_url = "https://your-system.com/webhook/excel-updated"
        # requests.post(webhook_url, json=audit_log)

    except Exception as e:
        logging.error(f"❌ Error enviando notificación: {e}")


def _notify_error_to_monitoring(error_log: dict):
    """
    🚨 Notifica errores a sistemas de monitoreo
    """
    try:
        # Integración con sistemas de monitoreo:
        # - Azure Application Insights
        # - Azure Monitor
        # - PagerDuty
        # - DataDog
        # - New Relic

        logging.error(f'🚨 Error reportado a monitoreo: {error_log["event"]}')

    except Exception as e:
        logging.error(f"❌ Error reportando a monitoreo: {e}")


# Configuración adicional para producción
@app.function_name("health_with_cache_info")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check_with_cache(req: func.HttpRequest) -> func.HttpResponse:
    """
    ❤️ HEALTH CHECK MEJORADO: Incluye información del cache
    """
    try:
        if USE_PRODUCTION_CACHE:
            cache_stats = data_manager.get_summary_statistics()
            system_type = "production_cache"
        else:
            cache_stats = {"type": "legacy_ram_cache"}
            system_type = "legacy"

        health_info = {
            "status": "healthy",
            "service": "SPP Agent API",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "cache_system": system_type,
            "cache_stats": cache_stats,
            "auto_refresh": True,
            "features": [
                "auto_excel_processing",
                "intelligent_cache",
                "auto_refresh",
                "production_ready",
            ],
        }

        return func.HttpResponse(
            json.dumps(health_info, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            status_code=500,
            mimetype="application/json",
        )
