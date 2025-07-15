import os
import json
import openai
from typing import Dict, List, Any
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
# import pyodbc  # Comentado por ahora para testing
from config import AZURE_CONFIG, AZURE_BLOB_CONFIG

class SPPAgent:
    """Agente IA para consultas del Sistema Privado de Pensiones usando solo Azure services"""
    
    def __init__(self):
        # Cliente OpenAI
        self.openai_client = openai.AzureOpenAI(
            azure_endpoint=AZURE_CONFIG["endpoint"],
            api_key=AZURE_CONFIG["api_key"],
            api_version=AZURE_CONFIG["api_version"]
        )
        
        # Cliente Blob Storage
        self.blob_client = BlobServiceClient.from_connection_string(
            conn_str=AZURE_BLOB_CONFIG["AZURE_BLOB_CONNECTION_STRING"]
        )
        
        # Sistema de prompts especializado
        self.system_prompt = """Eres un analista experto del Sistema Privado de Pensiones (SPP) de Perú.
        
        Tienes acceso a datos de:
        - Afiliados activos por AFP, edad, sexo, departamento
        - Nuevos afiliados y traspasos
        - Estadísticas mensuales y tendencias
        
        INSTRUCCIONES:
        1. Responde solo con información factual de los datos
        2. Si no tienes la información exacta, indícalo claramente
        3. Proporciona números específicos cuando sea posible
        4. Explica las tendencias y patrones relevantes
        """
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """Clasifica el tipo de consulta para determinar la estrategia de búsqueda"""
        
        classification_prompt = f"""
        Clasifica esta consulta sobre datos del SPP:
        "{query}"
        
        Responde en JSON con:
        {{
            "query_type": "numerical|comparative|trend|demographic|general",
            "entities": ["afp_names", "age_groups", "departments", "time_periods"],
            "requires_sql": true/false,
            "requires_search": true/false
        }}
        """
        
        response = self.openai_client.chat.completions.create(
            model=AZURE_CONFIG["deployment_name"],
            messages=[
                {"role": "system", "content": "Eres un clasificador de consultas de datos SPP."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0.0
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "query_type": "general",
                "entities": [],
                "requires_sql": True,
                "requires_search": True
            }
    
    def query_sql_data(self, query: str, classification: Dict) -> List[Dict]:
        """Consulta datos estructurados usando SQL"""
        # TODO: Implementar conexión a Azure SQL Database
        # Por ahora simulamos datos
        
        mock_data = [
            {
                "afp": "Habitat",
                "afiliados_activos": 1026513,
                "porcentaje_hombres": 55.49,
                "porcentaje_mujeres": 44.51,
                "periodo": "2025-01"
            },
            {
                "afp": "Integra", 
                "afiliados_activos": 4759854,
                "porcentaje_hombres": 52.1,
                "porcentaje_mujeres": 47.9,
                "periodo": "2025-01"
            }
        ]
        
        return mock_data
    
    def semantic_search(self, query: str) -> List[Dict]:
        """Búsqueda semántica usando Azure AI Search"""
        # TODO: Implementar Azure AI Search
        # Por ahora simulamos resultados
        
        mock_results = [
            {
                "content": "Los afiliados jóvenes (21-30 años) representan el 35% del total",
                "source": "Bol 01_2025.xlsx - Hoja 1",
                "relevance_score": 0.85
            }
        ]
        
        return mock_results
    
    def generate_response(self, query: str, sql_data: List, search_data: List) -> str:
        """Genera respuesta final combinando datos SQL y búsqueda semántica"""
        
        context = f"""
        DATOS SQL: {json.dumps(sql_data, indent=2)}
        
        DATOS BÚSQUEDA: {json.dumps(search_data, indent=2)}
        
        CONSULTA USUARIO: {query}
        """
        
        response = self.openai_client.chat.completions.create(
            model=AZURE_CONFIG["deployment_name"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Procesa una consulta completa del usuario"""
        
        # 1. Clasificar consulta
        classification = self.classify_query(user_query)
        
        # 2. Obtener datos según clasificación
        sql_data = []
        search_data = []
        
        if classification.get("requires_sql", True):
            sql_data = self.query_sql_data(user_query, classification)
            
        if classification.get("requires_search", True):
            search_data = self.semantic_search(user_query)
        
        # 3. Generar respuesta
        response = self.generate_response(user_query, sql_data, search_data)
        
        return {
            "query": user_query,
            "classification": classification,
            "response": response,
            "sources": {
                "sql_results": len(sql_data),
                "search_results": len(search_data)
            }
        }

# Función para Azure Functions
def main(req):
    """Endpoint principal para Azure Functions"""
    agent = SPPAgent()
    
    try:
        req_body = req.get_json()
        user_query = req_body.get('query', '')
        
        if not user_query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter required"})
            }
        
        result = agent.process_query(user_query)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }