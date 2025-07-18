#!/usr/bin/env python3
"""
Script para crear el índice de Azure AI Search con el esquema correcto
"""
import os
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()


def create_ai_search_index():
    """Crea el índice de Azure AI Search con el esquema correcto"""

    # Configuración desde variables de entorno
    endpoint = os.getenv("AZURE_AISEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_AISEARCH_API_KEY")
    index_name = os.getenv("AZURE_AISEARCH_INDEX_NAME", "spp-rentability-index")

    if not all([endpoint, api_key]):
        print("❌ Error: Variables de AI Search no configuradas")
        print("   Configurar: AZURE_AISEARCH_ENDPOINT y AZURE_AISEARCH_API_KEY")
        return False

    print(f"🔧 Creando índice: {index_name}")
    print(f"📡 Endpoint: {endpoint}")

    # Cliente de índices
    index_client = SearchIndexClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    # Definir esquema del índice - COMPATIBLE CON API 2024-07-01 ✅
    fields = [
        # Campo ID (obligatorio como key)
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        # Campo fundType (camelCase en lugar de fund_type) ✅
        SimpleField(
            name="fundType",
            type=SearchFieldDataType.Int32,
            filterable=True,
            facetable=True,
        ),
        # Campo period
        SimpleField(
            name="period",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        # Campo afpName (camelCase) ✅
        SearchableField(
            name="afpName",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        # Campo content (searchable)
        SearchableField(
            name="content", type=SearchFieldDataType.String, searchable=True
        ),
        # Campo rentabilityData (JSON como string) ✅
        SimpleField(name="rentabilityData", type=SearchFieldDataType.String),
        # Campo documentType ✅
        SimpleField(
            name="documentType", type=SearchFieldDataType.String, filterable=True
        ),
        # Campo createdAt ✅
        SimpleField(
            name="createdAt",
            type=SearchFieldDataType.DateTimeOffset,
            filterable=True,
            sortable=True,
        ),
    ]

    # Crear índice
    index = SearchIndex(name=index_name, fields=fields)

    try:
        # Eliminar índice existente si hay conflictos
        try:
            existing_index = index_client.get_index(index_name)
            index_client.delete_index(index_name)
            print(f"🗑️ Índice existente eliminado: {index_name}")
        except:
            print(f"📝 Creando nuevo índice: {index_name}")

        # Crear nuevo índice
        result = index_client.create_index(index)
        print(f"✅ Índice creado exitosamente: {result.name}")

        # Mostrar esquema creado
        print(f"\n📊 Esquema del índice:")
        for field in result.fields:
            properties = []
            if hasattr(field, "key") and field.key:
                properties.append("key")
            if hasattr(field, "searchable") and field.searchable:
                properties.append("searchable")
            if hasattr(field, "filterable") and field.filterable:
                properties.append("filterable")
            if hasattr(field, "facetable") and field.facetable:
                properties.append("facetable")
            if hasattr(field, "sortable") and field.sortable:
                properties.append("sortable")

            props_str = f"({', '.join(properties)})" if properties else ""
            print(f"   - {field.name}: {field.type} {props_str}")

        return True

    except Exception as e:
        print(f"❌ Error creando índice: {str(e)}")
        print(f"💡 Detalles del error:")
        print(f"   - Endpoint: {endpoint}")
        print(f"   - Index name: {index_name}")
        print(f"   - Número de campos: {len(fields)}")
        return False


if __name__ == "__main__":  # ✅ CORREGIDO: Era **name** en lugar de __name__
    print("🚀 CONFIGURANDO AZURE AI SEARCH")
    print("=" * 40)

    success = create_ai_search_index()

    if success:
        print("\n🎉 AI Search configurado correctamente!")
        print("📌 Próximo paso: python verify_setup.py")
    else:
        print("\n❌ Error en configuración de AI Search")
        print("📌 Verificar credenciales en archivo .env")
        print("📌 Verificar que el endpoint sea correcto")
        print("📌 Verificar que la API key tenga permisos de administrador")
