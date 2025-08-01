#!/usr/bin/env python3
"""
Sistema de Actualización Automática para Azure Functions - VERSIÓN CORREGIDA
Actualiza automáticamente cuando se suben nuevos archivos Excel
"""
import azure.functions as func
import json
import logging
from datetime import datetime
from src.excel_processor import ExcelProcessor

# ✅ CORRECCIÓN: Usar siempre el agente funcional
from src.azure_assistant_agent import SPPAssistantAgent

# Intentar usar el cache avanzado pero con fallback
try:
    from src.cache.production_cache_manager import get_production_data_manager

    data_manager = get_production_data_manager()
    USE_PRODUCTION_CACHE = True
    logging.info("✅ Usando sistema de cache avanzado")
except ImportError:
    data_manager = None
    USE_PRODUCTION_CACHE = False
    logging.info("⚠️ Cache avanzado no disponible, usando sistema básico")

# ✅ SIEMPRE tener el agente disponible
spp_agent = SPPAssistantAgent()

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
        if USE_PRODUCTION_CACHE and data_manager:
            logging.info("🔄 Forzando actualización del cache inteligente...")
            data_manager.force_refresh()
            logging.info("✅ Cache inteligente actualizado automáticamente")
        else:
            # Fallback: Reinicializar data manager del agente
            logging.info("🔄 Refrescando data manager del agente...")
            spp_agent.data_manager.refresh_data()
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


@app.route(route="chat", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def chat_endpoint_with_auto_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    🤖 ENDPOINT CHAT MEJORADO: Soporte para rentabilidad acumulada y anualizada
    """
    logging.info("🤖 Procesando consulta de chat")

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

        # ✅ NUEVO: Enriquecer la query con instrucciones de formato dual
        enhanced_query = f"""{user_query}

        INSTRUCCIONES DE FORMATO PARA ESTA RESPUESTA:
        - SIEMPRE incluir AMBAS tablas: rentabilidad ACUMULADA y ANUALIZADA
        - SIEMPRE explicar la diferencia entre acumulada (total ganado) y anualizada (promedio anual)
        - SIEMPRE usar formato con **negritas** para títulos y porcentajes
        - SIEMPRE destacar AFP Prima con análisis positivo
        - SIEMPRE usar datos exactos con 2 decimales
        - SIEMPRE incluir contexto práctico de interpretación"""

        # 2. AUTO-REFRESH INTELIGENTE (si está disponible)
        cache_info = "standard"
        if USE_PRODUCTION_CACHE and data_manager:
            try:
                data_manager._auto_refresh_check()
                cache_stats = data_manager.get_summary_statistics()
                logging.info(f'📊 Cache stats: {cache_stats.get("cache_stats", {})}')
                cache_info = "intelligent"
            except Exception as e:
                logging.warning(f"⚠️ Error en cache inteligente, usando estándar: {e}")

        # 3. ✅ PROCESAMIENTO CON AGENTE SIEMPRE FUNCIONAL
        logging.info("🤖 Iniciando procesamiento con agente SPP dual...")

        start_time = datetime.now()
        response = spp_agent.chat(enhanced_query)
        processing_time = (datetime.now() - start_time).total_seconds()

        logging.info(f"✅ Respuesta generada en {processing_time:.2f}s")

        # ✅ NUEVO: Validar que la respuesta incluya ambas rentabilidades
        response_validation = {
            "has_acumulada": "acumulada" in response.lower()
            or "acumulado" in response.lower(),
            "has_anualizada": "anualizada" in response.lower()
            or "anualizado" in response.lower(),
            "has_tables": response.count("|") >= 6,  # Al menos 2 tablas
            "has_bold_formatting": "**" in response,
            "has_prima_highlight": "prima" in response.lower() and "⭐" in response,
        }

        # 4. Preparar respuesta
        result = {
            "query": user_query,
            "response": response,
            "system_info": {
                "cache_system": cache_info,
                "processing_time_seconds": round(processing_time, 2),
                "auto_refresh_enabled": USE_PRODUCTION_CACHE,
                "timestamp": datetime.now().isoformat(),
                "dual_rentability_support": True,
                "response_validation": response_validation,
            },
            "status": "success",
        }

        # ✅ NUEVO: Advertencia si la respuesta no cumple con el formato dual
        if (
            not response_validation["has_acumulada"]
            or not response_validation["has_anualizada"]
        ):
            result["system_info"][
                "format_warning"
            ] = "La respuesta podría no incluir ambos tipos de rentabilidad"
            logging.warning("⚠️ Respuesta podría no cumplir formato dual completo")

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"💥 Error en chat endpoint: {str(e)}")
        import traceback

        logging.error(f"💥 Traceback: {traceback.format_exc()}")

        return func.HttpResponse(
            json.dumps(
                {
                    "error": f"Error procesando consulta: {str(e)}",
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="cache/refresh", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def manual_cache_refresh(req: func.HttpRequest) -> func.HttpResponse:
    """
    🔄 ENDPOINT MANUAL: Para forzar actualización del cache
    """
    try:
        logging.info("🔄 Iniciando refresh manual del cache...")

        if USE_PRODUCTION_CACHE and data_manager:
            data_manager.force_refresh()
            stats = data_manager.get_summary_statistics()
        else:
            # Refresh del agente estándar
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
        if USE_PRODUCTION_CACHE and data_manager:
            stats = data_manager.get_summary_statistics()
            system_type = "intelligent"
        else:
            stats = spp_agent.data_manager.get_summary_statistics()
            system_type = "standard"

        result = {
            "cache_stats": stats,
            "system_type": system_type,
            "timestamp": datetime.now().isoformat(),
            "auto_refresh_enabled": USE_PRODUCTION_CACHE,
            "agent_ready": True,
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"❌ Error obteniendo estadísticas: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=500, mimetype="application/json"
        )


@app.function_name("health_with_cache_info")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_check_with_cache(req: func.HttpRequest) -> func.HttpResponse:
    """
    ❤️ HEALTH CHECK MEJORADO: Incluye información del cache y agente
    """
    try:
        # Verificar estado del cache
        if USE_PRODUCTION_CACHE and data_manager:
            cache_stats = data_manager.get_summary_statistics()
            system_type = "intelligent_cache"
        else:
            cache_stats = spp_agent.data_manager.get_summary_statistics()
            system_type = "standard_cache"

        # Verificar estado del agente
        agent_ready = spp_agent is not None and hasattr(spp_agent, "chat")

        health_info = {
            "status": "healthy",
            "service": "SPP Agent API",
            "version": "2.1.0",
            "timestamp": datetime.now().isoformat(),
            "cache_system": system_type,
            "cache_stats": cache_stats,
            "agent_ready": agent_ready,
            "auto_refresh": USE_PRODUCTION_CACHE,
            "features": [
                "auto_excel_processing",
                "spp_agent_integration",
                "auto_refresh" if USE_PRODUCTION_CACHE else "standard_refresh",
                "production_ready",
            ],
        }

        return func.HttpResponse(
            json.dumps(health_info, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"❌ Error en health check: {str(e)}")
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


# ✅ Endpoint adicional para testing directo del agente
@app.route(route="agent/test", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def test_agent_direct(req: func.HttpRequest) -> func.HttpResponse:
    """
    🧪 ENDPOINT DE TESTING: Para probar el agente directamente
    """
    try:
        req_body = req.get_json()
        query = req_body.get("query", "¿Cuál es la rentabilidad de Habitat?")

        logging.info(f"🧪 Testing agente con query: {query}")

        start_time = datetime.now()
        response = spp_agent.chat(query)
        processing_time = (datetime.now() - start_time).total_seconds()

        result = {
            "query": query,
            "response": response,
            "processing_time": round(processing_time, 2),
            "agent_id": (
                spp_agent.assistant_id
                if hasattr(spp_agent, "assistant_id")
                else "unknown"
            ),
            "thread_id": (
                spp_agent.thread_id if hasattr(spp_agent, "thread_id") else "unknown"
            ),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
        }

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error(f"❌ Error en test directo: {str(e)}")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": str(e),
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            status_code=500,
            mimetype="application/json",
        )
