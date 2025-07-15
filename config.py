import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pathlib import Path

load_dotenv()
# Configuración Cosmosdb
AZURE_COSMOS_DB = {
    "COSMOS_ENDPOINT": os.getenv("COSMOS_ENDPOINT"),
    "COSMOS_KEY": os.getenv("COSMOS_KEY"),
    "COSMOS_DATABASE": os.getenv("COSMOS_DATABASE"),
    "COSMOS_CONTAINER": os.getenv("COSMOS_CONTAINER"),
}


# Configuración de Azure Blob Storage
AZURE_BLOB_CONFIG = {
    "AZURE_BLOB_ACCOUNT_KEY": os.getenv("AZURE_BLOB_ACCOUNT_KEY"),
    "AZURE_BLOB_CONNECTION_STRING": os.getenv("AZURE_BLOB_CONNECTION_STRING"),
    "AZURE_BLOB_ACCOUNT_NAME": os.getenv("AZURE_BLOB_ACCOUNT_NAME"),
    "AZURE_BLOB_CONTAINER_NAME": os.getenv("AZURE_BLOB_CONTAINER_NAME"),
    "AZURE_BLOB_ENDPOINT_SUFFIX": os.getenv(
        "AZURE_BLOB_ENDPOINT_SUFFIX", "core.windows.net"
    ),
}

# Configuracion Azure
AZURE_CONFIG = {
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    "embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
}


def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=AZURE_CONFIG["endpoint"],
        api_key=AZURE_CONFIG["api_key"],
        azure_deployment=AZURE_CONFIG["deployment_name"],
        api_version=AZURE_CONFIG["api_version"],
        temperature=0.0,
    )


def get_embedding():
    print(f"[DEBUG] Embedding deployment: {AZURE_CONFIG['embedding_deployment']}")
    return AzureOpenAIEmbeddings(
        azure_endpoint=AZURE_CONFIG["endpoint"],
        api_key=AZURE_CONFIG["api_key"],
        azure_deployment=AZURE_CONFIG["embedding_deployment"],
        api_version=AZURE_CONFIG["api_version"],
    )


SEARCH_ENDPOINT = "https://your-search.search.windows.net"
SEARCH_KEY = "your-search-key"
SEARCH_INDEX = "financial-index"

TEXT_ANALYTICS_ENDPOINT = "https://your-text-analytics.cognitiveservices.azure.com/"
TEXT_ANALYTICS_KEY = "your-text-analytics-key"
