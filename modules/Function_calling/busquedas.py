
from typing_extensions import override
import os
import serpapi
from dotenv import load_dotenv
from serpapi import GoogleSearch
import time
SERPAPI_KEY = os.getenv('SERPAPI_KEY')


def buscar_resultados_en_serpapi_culinary(query, model):

    try:
        search_query = f"{query}"

        # Definir los parámetros de búsqueda
        params = {
            "q": search_query,
            "engine": "google",
            "hl": "es",
            "gl": "co",
            "location_requested": "Atlantico,Colombia",
            "location_used": "Atlantico,Colombia",
            "api_key": SERPAPI_KEY
        }
        # Ejecutar la búsqueda
        search = GoogleSearch(params)
        result = search.get_dict()
        # print(f"result: {result}")
        print(result.get("organic_results", []))
        return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"
    
# buscar_resultados_en_serpapi_culinary("Café", "culinary")   
import traceback

def buscar_resultados_en_serpapi_gym(queries):
    resultados = []
    try:
        for query in queries:  
            search_query = f"{query}"
            print(f"🔍 Buscando: {search_query}")

            # Parámetros para SerpAPI
            params = {
                "q": search_query,
                "engine": "google",
                "hl": "es",
                "gl": "co",
                "location_requested": "Atlantico,Colombia",
                "location_used": "Atlantico,Colombia",
                "api_key": SERPAPI_KEY
            }
            print("parametros enviados")
            try:
                # Ejecutar la búsqueda
                search = GoogleSearch(params)
                result = search.get_dict()

                # Procesar resultados
                for item in result.get("organic_results", [])[:5]:
                    resultados.append({
                        "query": query,
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet")
                    })
                print("ejecutada")
            except Exception as e:
                print(f"❌ Error con la búsqueda '{query}': {e}")
                traceback.print_exc()
                return f"Error al buscar '{query}' en SerpAPI: {e}"
            time.sleep(0.5)
        return resultados

    except Exception as e:
        print("❌ Error general en la función buscar_resultados_en_serpapi_gym")
        traceback.print_exc()
        return f"Error general en SerpAPI: {e}"

queries = ["biceps curl", "triceps extension", "shoulder lateral raise"]
resultados = buscar_resultados_en_serpapi_gym(queries)

print(f"resultados: {resultados}")

    
def buscar_resultados_en_serpapi_fashion(query, model):
    try:
        search_query = f"{query}"

        # Definir los parámetros de búsqueda
        params = {
            "q": search_query,
            "engine": "google",
            "hl": "es",
            "gl": "co",
            "location_requested": "Atlantico,Colombia",
            "location_used": "Atlantico,Colombia",
            "api_key": SERPAPI_KEY
        }
        # Ejecutar la búsqueda
        search = GoogleSearch(params)
        result = search.get_dict()
        # print(f"result: {result}")
        print(result.get("organic_results", []))
        return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"
    
