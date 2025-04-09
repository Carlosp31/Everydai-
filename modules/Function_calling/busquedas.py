
from typing_extensions import override
import os
import serpapi
from dotenv import load_dotenv
from serpapi import GoogleSearch
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
def buscar_resultados_en_serpapi_gym(queries):
    resultados = []
    try:
        for query in queries:  
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
            # Agregar hasta 5 resultados por búsqueda
            for item in result.get("organic_results", [])[:5]:
                resultados.append({
                    "query": query,
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
        return resultados  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"
    


    
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
    
