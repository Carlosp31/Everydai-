
from typing_extensions import override
import os
import serpapi
from dotenv import load_dotenv
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
client_serpapi = serpapi.Client(api_key=SERPAPI_KEY)

def buscar_resultados_en_serpapi_culinary(query, model):

    try:
        # Ajusta la consulta según el modelo seleccionado
        if model == 'culinary':
            search_query = f"Recetas con {query}"
        elif model == 'fashion':
            search_query = f"Outfits with {query}"
        elif model == 'gym':
            search_query = f"Gym exercises using {query}"
        else:
            return f"Modelo {model} no soportado."

        # Realizar la búsqueda en SerpAPI con la consulta modificada
        result = client_serpapi.search(
            q=search_query,
            engine="google",
            hl="es",
            gl="co",
            location_requested="Atlantico,Colombia",
                    location_used="Atlantico,Colombia"
        )

        # Para el modelo culinario, usamos 'recipes_results', pero para otros modelos
        # podrían necesitarse diferentes campos en los resultados
        
        if model == 'culinary':
            print(result.get("recipes_results", []))
            return result.get("recipes_results", [])
        else:
            print(result.get("recipes_results", []))
            return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"
    
def buscar_resultados_en_serpapi_gym(query, model):
    try:
        search_query = f"{query}"
        # Realizar la búsqueda en SerpAPI con la consulta modificada
        result = client_serpapi.search(
            q=search_query,
            engine="google",
            hl="es",
            gl="co",
            location_requested="Atlantico,Colombia",
                    location_used="Atlantico,Colombia"
        )

        # Para el modelo culinario, usamos 'recipes_results', pero para otros modelos
        # podrían necesitarse diferentes campos en los resultados
        
        if model == 'culinary':
            print(result.get("recipes_results", []))
            return result.get("recipes_results", [])
        else:
            print(result.get("recipes_results", []))
            return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"
    
def buscar_resultados_en_serpapi_fashion(query, model):

    try:
        search_query = f"{query}"
        result = client_serpapi.search(
            q=search_query,
            engine="google",
            hl="es",
            gl="co",
            location_requested="Atlantico,Colombia",
                    location_used="Atlantico,Colombia"
        )

        # Para el modelo culinario, usamos 'recipes_results', pero para otros modelos
        # podrían necesitarse diferentes campos en los resultados
        
        if model == 'culinary':
            print(result.get("recipes_results", []))
            return result.get("recipes_results", [])
        else:
            print(result.get("recipes_results", []))
            return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"