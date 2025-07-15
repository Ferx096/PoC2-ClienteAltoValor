import openai
import json
import logging
from typing import List, Dict, Any
from azure.cosmos import CosmosClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

class FinancialDataBot:
    """
    Bot que responde preguntas sobre datos financieros
    usando CosmosDB + AI Search + Azure OpenAI
    """
    
    def __init__(self):
        # Configuración (en producción usar Azure Key Vault)
        self.cosmos_client = CosmosClient(
            "https://your-cosmosdb.documents.azure.com:443/",
            "your-cosmos-key"
        )
        self.container = self.cosmos_client.get_database_client("FinancialData").get_container_client("ExcelData")
        
        self.search_client = SearchClient(
            endpoint="https://your-search.search.windows.net",
            index_name="financial-index",
            credential=AzureKeyCredential("your-search-key")
        )
        
        # Azure OpenAI
        openai.api_type = "azure"
        openai.api_base = "https://your-openai.openai.azure.com/"
        openai.api_version = "2024-02-01"
        openai.api_key = "your-openai-key"
        
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Responde preguntas sobre datos financieros
        """
        try:
            # 1. Buscar datos relevantes
            search_results = self._search_relevant_data(question)
            
            if not search_results:
                return {
                    "answer": "No encontré información relevante para tu pregunta.",
                    "confidence": 0,
                    "sources": []
                }
            
            # 2. Preparar contexto
            context = self._prepare_context(search_results)
            
            # 3. Generar respuesta con Azure OpenAI
            response = self._generate_response(question, context)
            
            # 4. Formatear respuesta final
            return {
                "answer": response,
                "confidence": self._calculate_confidence(search_results),
                "sources": self._extract_sources(search_results),
                "data_count": len(search_results)
            }
            
        except Exception as e:
            logging.error(f"Error respondiendo pregunta: {str(e)}")
            return {
                "answer": "Hubo un error procesando tu pregunta. Intenta de nuevo.",
                "confidence": 0,
                "sources": [],
                "error": str(e)
            }
    
    def _search_relevant_data(self, question: str, top_k: int = 10) -> List[Dict]:
        """
        Busca datos relevantes usando AI Search + CosmosDB
        """
        try:
            # Búsqueda semántica en AI Search
            search_results = self.search_client.search(
                search_text=question,
                top=top_k,
                include_total_count=True,
                search_fields=["content", "financial_concepts"],
                highlight_fields="content",
                query_type="semantic"
            )
            
            # Obtener datos completos de CosmosDB
            detailed_results = []
            for result in search_results:
                cosmos_id = result.get('cosmos_id')
                if cosmos_id:
                    try:
                        # Obtener datos completos de CosmosDB
                        partition_key = f"{result.get('file_name', '')}_{result.get('sheet_name', '')}"
                        full_data = self.container.read_item(
                            item=cosmos_id,
                            partition_key=partition_key
                        )
                        
                        detailed_results.append({
                            'search_score': result.get('@search.score', 0),
                            'highlights': result.get('@search.highlights', {}),
                            'search_result': dict(result),
                            'full_data': full_data
                        })
                    except Exception as e:
                        logging.warning(f"No se pudo obtener datos de Cosmos para {cosmos_id}: {str(e)}")
                        continue
            
            return detailed_results
            
        except Exception as e:
            logging.error(f"Error en búsqueda: {str(e)}")
            return []
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """
        Prepara contexto estructurado para el LLM
        """
        context_parts = []
        
        for i, result in enumerate(search_results[:5]):  # Top 5 resultados
            full_data = result['full_data']
            
            context_part = f"""
DOCUMENTO {i+1}:
- Archivo: {full_data.get('file_name', 'N/A')}
- Hoja: {full_data.get('sheet_name', 'N/A')}
- Período: {full_data.get('period', 'N/A')}
- Fila: {full_data.get('row_number', 'N/A')}
- Conceptos financieros: {', '.join(full_data.get('financial_concepts', []))}

DATOS:
{self._format_row_data(full_data.get('raw_data', {}))}

VALORES NUMÉRICOS:
{self._format_numeric_values(full_data.get('numeric_values', []))}

RELEVANCIA: {result['search_score']:.2f}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _format_row_data(self, raw_data: Dict) -> str:
        """
        Formatea datos de fila para el contexto
        """
        formatted = []
        for key, value in raw_data.items():
            if value is not None and str(value).strip():
                formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted) if formatted else "  No hay datos disponibles"
    
    def _format_numeric_values(self, numeric_values: List[Dict]) -> str:
        """
        Formatea valores numéricos para el contexto
        """
        formatted = []
        for num_val in numeric_values:
            formatted.append(f"  {num_val['column']}: {num_val['formatted_value']}")
        
        return "\n".join(formatted) if formatted else "  No hay valores numéricos"
    
    def _generate_response(self, question: str, context: str) -> str:
        """
        Genera respuesta usando Azure OpenAI
        """
        system_prompt = """
Eres un asistente financiero experto que analiza datos de Excel.

INSTRUCCIONES:
1. Responde preguntas sobre rentabilidad, ingresos, costos y otros datos financieros
2. Usa SOLO la información proporcionada en el contexto
3. Si no hay información suficiente, di que no tienes datos suficientes
4. Incluye números específicos cuando los menciones
5. Menciona el archivo y período de donde viene la información
6. Responde en español de forma clara y concisa

FORMATO DE RESPUESTA:
- Respuesta directa a la pregunta
- Datos específicos con fuentes
- Contexto temporal si es relevante
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXTO:\n{context}\n\nPREGUNTA: {question}"}
        ]
        
        try:
            response = openai.ChatCompletion.create(
                engine="gpt-4",  # Usar tu deployment name
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generando respuesta: {str(e)}")
            return "No pude generar una respuesta en este momento."
    
    def _calculate_confidence(self, search_results: List[Dict]) -> float:
        """
        Calcula confianza basada en scores de búsqueda
        """
        if not search_results:
            return 0.0
        
        avg_score = sum(r['search_score'] for r in search_results) / len(search_results)
        return min(avg_score * 100, 100)  # Normalizar a 0-100
    
    def _extract_sources(self, search_results: List[Dict]) -> List[Dict]:
        """
        Extrae fuentes de información
        """
        sources = []
        seen_files = set()
        
        for result in search_results:
            full_data = result['full_data']
            file_key = f"{full_data.get('file_name', '')}-{full_data.get('sheet_name', '')}"
            
            if file_key not in seen_files:
                sources.append({
                    "file": full_data.get('file_name', 'N/A'),
                    "sheet": full_data.get('sheet_name', 'N/A'),
                    "period": full_data.get('period', 'N/A'),
                    "relevance": result['search_score']
                })
                seen_files.add(file_key)
        
        return sources[:3]  # Top 3 fuentes
    
    def get_financial_summary(self, period: str = None, concept: str = None) -> Dict[str, Any]:
        """
        Obtiene resumen financiero por período o concepto
        """
        try:
            # Construir query para CosmosDB
            query = "SELECT * FROM c WHERE 1=1"
            parameters = []
            
            if period:
                query += " AND c.period = @period"
                parameters.append({"name": "@period", "value": period})
            
            if concept:
                query += " AND ARRAY_CONTAINS(c.financial_concepts, @concept)"
                parameters.append({"name": "@concept", "value": concept})
            
            # Ejecutar query
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if not items:
                return {"message": "No se encontraron datos para los criterios especificados"}
            
            # Procesar resultados
            summary = self._process_summary(items)
            
            return {
                "summary": summary,
                "total_records": len(items),
                "period": period,
                "concept": concept
            }
            
        except Exception as e:
            logging.error(f"Error obteniendo resumen: {str(e)}")
            return {"error": str(e)}
    
    def _process_summary(self, items: List[Dict]) -> Dict[str, Any]:
        """
        Procesa items para crear resumen
        """
        files = set()
        concepts = set()
        numeric_data = []
        
        for item in items:
            files.add(item.get('file_name', ''))
            concepts.update(item.get('financial_concepts', []))
            
            for num_val in item.get('numeric_values', []):
                numeric_data.append({
                    'value': num_val['value'],
                    'column': num_val['column'],
                    'file': item.get('file_name', ''),
                    'period': item.get('period', '')
                })
        
        return {
            "files_analyzed": list(files),
            "financial_concepts": list(concepts),
            "numeric_data_points": len(numeric_data),
            "total_files": len(files),
            "total_concepts": len(concepts)
        }

# Ejemplo de uso
if __name__ == "__main__":
    bot = FinancialDataBot()
    
    # Preguntas de ejemplo
    questions = [
        "¿Cuál fue la rentabilidad en enero 2025?",
        "Muéstrame los ingresos del primer trimestre",
        "¿Cuáles son los costos principales en el archivo BOL?",
        "Compara los márgenes de diferentes períodos"
    ]
    
    for question in questions:
        print(f"\n🤖 Pregunta: {question}")
        response = bot.answer_question(question)
        print(f"📊 Respuesta: {response['answer']}")
        print(f"🎯 Confianza: {response['confidence']:.1f}%")
        print(f"📁 Fuentes: {len(response['sources'])} archivos")