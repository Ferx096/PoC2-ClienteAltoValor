import azure.functions as func
import pandas as pd
import json
import logging
from azure.cosmos import CosmosClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import hashlib
from datetime import datetime
from config import (
    COSMOS_ENDPOINT,
    COSMOS_KEY,
    COSMOS_DATABASE,
    COSMOS_CONTAINER,
    SEARCH_ENDPOINT,
    SEARCH_INDEX,
    SEARCH_KEY,
)
from config import TEXT_ANALYTICS_ENDPOINT, TEXT_ANALYTICS_KEY


# Inicializar clientes
cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = cosmos_client.get_database_client(COSMOS_DATABASE)
container = database.get_container_client(COSMOS_CONTAINER)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY),
)

text_analytics_client = TextAnalyticsClient(
    endpoint=TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(TEXT_ANALYTICS_KEY)
)


def main(myblob: func.InputStream) -> None:
    """
    Azure Function que procesa archivos Excel subidos a Blob Storage
    """
    logging.info(f"Procesando archivo: {myblob.name}")

    try:
        # 1. Leer archivo Excel
        df_dict = pd.read_excel(myblob, sheet_name=None)
        file_name = myblob.name.split("/")[-1]

        # 2. Procesar cada hoja
        for sheet_name, df in df_dict.items():
            process_sheet(df, sheet_name, file_name)

        logging.info(f"Archivo {file_name} procesado exitosamente")

    except Exception as e:
        logging.error(f"Error procesando archivo: {str(e)}")
        raise


def process_sheet(df: pd.DataFrame, sheet_name: str, file_name: str):
    """
    Procesa una hoja de Excel y extrae información financiera
    """

    # 3. Extraer datos estructurados
    structured_data = extract_structured_data(df, sheet_name, file_name)

    # 4. Guardar en CosmosDB (datos estructurados)
    save_to_cosmos(structured_data)

    # 5. Crear documentos para AI Search (búsqueda semántica)
    search_documents = create_search_documents(structured_data)

    # 6. Indexar en AI Search
    index_in_search(search_documents)


def extract_structured_data(df: pd.DataFrame, sheet_name: str, file_name: str):
    """
    Extrae datos estructurados manteniendo contexto financiero
    """
    structured_data = []

    # Detectar período del archivo (del nombre del archivo)
    period = extract_period_from_filename(file_name)

    # Procesar cada fila que contenga datos
    for index, row in df.iterrows():
        # Saltar filas vacías
        if row.isnull().all():
            continue

        # Extraer información de la fila
        row_data = {
            "id": generate_id(file_name, sheet_name, index),
            "file_name": file_name,
            "sheet_name": sheet_name,
            "period": period,
            "row_number": index + 1,
            "raw_data": row.to_dict(),
            "processed_at": datetime.utcnow().isoformat(),
            "partition_key": f"{file_name}_{sheet_name}",
        }

        # Identificar conceptos financieros
        financial_concepts = identify_financial_concepts(row)
        if financial_concepts:
            row_data["financial_concepts"] = financial_concepts

        # Extraer valores numéricos
        numeric_values = extract_numeric_values(row)
        if numeric_values:
            row_data["numeric_values"] = numeric_values

        structured_data.append(row_data)

    return structured_data


def identify_financial_concepts(row):
    """
    Identifica conceptos financieros en la fila
    """
    financial_keywords = {
        "rentabilidad": ["rentabilidad", "margen", "profit", "ganancia"],
        "ingresos": ["ingresos", "ventas", "revenue", "sales"],
        "costos": ["costos", "gastos", "expenses", "costs"],
        "activos": ["activos", "assets", "inventario"],
        "pasivos": ["pasivos", "liabilities", "deuda"],
    }

    concepts = []
    row_text = " ".join([str(val) for val in row.values if pd.notna(val)]).lower()

    for concept, keywords in financial_keywords.items():
        if any(keyword in row_text for keyword in keywords):
            concepts.append(concept)

    return concepts


def extract_numeric_values(row):
    """
    Extrae valores numéricos de la fila
    """
    numeric_values = []

    for col_name, value in row.items():
        if pd.notna(value) and isinstance(value, (int, float)):
            numeric_values.append(
                {
                    "column": col_name,
                    "value": float(value),
                    "formatted_value": (
                        f"{value:,.2f}" if abs(value) > 0.01 else str(value)
                    ),
                }
            )

    return numeric_values


def save_to_cosmos(structured_data):
    """
    Guarda datos estructurados en CosmosDB
    """
    for item in structured_data:
        try:
            container.create_item(body=item)
            logging.info(f"Guardado en Cosmos: {item['id']}")
        except Exception as e:
            logging.error(f"Error guardando en Cosmos: {str(e)}")


def create_search_documents(structured_data):
    """
    Crea documentos optimizados para búsqueda en AI Search
    """
    search_documents = []

    for item in structured_data:
        # Crear contenido textual para búsqueda
        content_parts = []

        # Agregar información contextual
        content_parts.append(f"Archivo: {item['file_name']}")
        content_parts.append(f"Hoja: {item['sheet_name']}")
        content_parts.append(f"Período: {item['period']}")

        # Agregar conceptos financieros
        if "financial_concepts" in item:
            content_parts.append(f"Conceptos: {', '.join(item['financial_concepts'])}")

        # Agregar datos de la fila
        if "raw_data" in item:
            for key, value in item["raw_data"].items():
                if pd.notna(value):
                    content_parts.append(f"{key}: {value}")

        # Agregar valores numéricos con contexto
        if "numeric_values" in item:
            for num_val in item["numeric_values"]:
                content_parts.append(
                    f"{num_val['column']}: {num_val['formatted_value']}"
                )

        # Crear documento de búsqueda
        search_doc = {
            "id": item["id"],
            "content": " | ".join(content_parts),
            "file_name": item["file_name"],
            "sheet_name": item["sheet_name"],
            "period": item["period"],
            "cosmos_id": item["id"],  # Referencia para obtener datos completos
            "financial_concepts": item.get("financial_concepts", []),
            "has_numeric_data": len(item.get("numeric_values", [])) > 0,
            "row_number": item["row_number"],
        }

        search_documents.append(search_doc)

    return search_documents


def index_in_search(search_documents):
    """
    Indexa documentos en AI Search
    """
    if not search_documents:
        return

    try:
        # Subir documentos por lotes
        batch_size = 50
        for i in range(0, len(search_documents), batch_size):
            batch = search_documents[i : i + batch_size]
            result = search_client.upload_documents(documents=batch)

            logging.info(f"Indexados {len(batch)} documentos en AI Search")

            # Verificar errores
            for res in result:
                if not res.succeeded:
                    logging.error(
                        f"Error indexando documento {res.key}: {res.error_message}"
                    )

    except Exception as e:
        logging.error(f"Error indexando en AI Search: {str(e)}")


def generate_id(file_name, sheet_name, row_index):
    """
    Genera un ID único para cada registro
    """
    text = f"{file_name}_{sheet_name}_{row_index}"
    return hashlib.md5(text.encode()).hexdigest()


def extract_period_from_filename(filename):
    """
    Extrae el período del nombre del archivo
    """
    # Ejemplo: "Bol 01_2025.xlsx" -> "2025-01"
    import re

    # Buscar patrón MM_YYYY
    pattern = r"(\d{2})_(\d{4})"
    match = re.search(pattern, filename)

    if match:
        month, year = match.groups()
        return f"{year}-{month}"

    # Buscar solo año
    year_pattern = r"(\d{4})"
    year_match = re.search(year_pattern, filename)

    if year_match:
        return year_match.group(1)

    return datetime.now().strftime("%Y-%m")


# Funciones auxiliares para el bot
def search_financial_data(query: str, top_k: int = 5):
    """
    Busca datos financieros usando AI Search
    """
    try:
        # Búsqueda semántica en AI Search
        results = search_client.search(
            search_text=query,
            top=top_k,
            include_total_count=True,
            highlight_fields="content",
        )

        # Obtener datos completos de CosmosDB
        detailed_results = []
        for result in results:
            cosmos_id = result.get("cosmos_id")
            if cosmos_id:
                # Obtener datos completos de CosmosDB
                full_data = container.read_item(
                    item=cosmos_id,
                    partition_key=result.get("file_name", "")
                    + "_"
                    + result.get("sheet_name", ""),
                )
                detailed_results.append(
                    {
                        "search_score": result.get("@search.score", 0),
                        "highlights": result.get("@search.highlights", {}),
                        "full_data": full_data,
                    }
                )

        return detailed_results

    except Exception as e:
        logging.error(f"Error en búsqueda: {str(e)}")
        return []
