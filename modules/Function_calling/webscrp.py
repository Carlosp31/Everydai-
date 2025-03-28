import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def web_culinary(query):
    try:
        search_query = f"{query} Olímpica"

        # Definir los parámetros de búsqueda
        params = {
            "q": search_query,
            "engine": "google_shopping",
            "hl": "es",
            "gl": "co",
            "location_requested": "Atlantico,Colombia",
            "location_used": "Atlantico,Colombia",
            "api_key": SERPAPI_KEY
        }


        # Ejecutar la búsqueda
        search = GoogleSearch(params)
        results = search.get_dict()

        # Obtener los resultados de shopping
        shopping_results = results.get("shopping_results", [])

        productos_lista = []
        for item in shopping_results:
            title = item.get("title", "N/A")
            price = item.get("extracted_price", "N/A")
            image_url = item.get("thumbnail", "N/A")
            link = item.get("product_link", "N/A")

            producto_info = {
                "nombre": title,
                "precio": f"${price}",
                "imagen_url": image_url,
                "enlace": link if link != "N/A" else "N/A"
            }

            productos_lista.append(producto_info)

        # Guardar en un archivo JSON
        with open("productos.json", "w", encoding="utf-8") as file:
            json.dump(productos_lista, file, ensure_ascii=False, indent=4)
        print(f"productos: {productos_lista}")

        return productos_lista


    except Exception as e:
        print(f"Error: {e}")
        return []




import json
from playwright.sync_api import sync_playwright

def web_fashion_HM(query):
    try:
        search_query = f"{query}- HM"

        # Definir los parámetros de búsqueda
        params = {
            "q": search_query,
            "engine": "google_shopping",
            "hl": "es",
            "gl": "co",
            "location_requested": "Atlantico,Colombia",
            "location_used": "Atlantico,Colombia",
            "api_key": SERPAPI_KEY
        }


        # Ejecutar la búsqueda
        search = GoogleSearch(params)
        results = search.get_dict()

        # Obtener los resultados de shopping
        shopping_results = results.get("shopping_results", [])

        productos_lista = []
        for item in shopping_results:
            title = item.get("title", "N/A")
            price = item.get("extracted_price", "N/A")
            image_url = item.get("thumbnail", "N/A")
            link = item.get("product_link", "N/A")

            producto_info = {
                "nombre": title,
                "precio": f"${price}",
                "imagen_url": image_url,
                "enlace": link if link != "N/A" else "N/A"
            }

            productos_lista.append(producto_info)

        # Guardar en un archivo JSON
        with open("productos.json", "w", encoding="utf-8") as file:
            json.dump(productos_lista, file, ensure_ascii=False, indent=4)
        print(f"productos: {productos_lista}")

        return productos_lista


    except Exception as e:
        print(f"Error: {e}")
        return []


def web_fitness_decathlon(query):
    try:
        search_query = f"{query} - Decatlhon"

        # Definir los parámetros de búsqueda
        params = {
            "q": search_query,
            "engine": "google_shopping",
            "hl": "es",
            "gl": "co",
            "location_requested": "Atlantico,Colombia",
            "location_used": "Atlantico,Colombia",
            "api_key": SERPAPI_KEY
        }


        # Ejecutar la búsqueda
        search = GoogleSearch(params)
        results = search.get_dict()

        # Obtener los resultados de shopping
        shopping_results = results.get("shopping_results", [])

        productos_lista = []
        for item in shopping_results:
            title = item.get("title", "N/A")
            price = item.get("extracted_price", "N/A")
            image_url = item.get("thumbnail", "N/A")
            link = item.get("product_link", "N/A")

            producto_info = {
                "nombre": title,
                "precio": f"${price}",
                "imagen_url": image_url,
                "enlace": link if link != "N/A" else "N/A"
            }

            productos_lista.append(producto_info)

        # Guardar en un archivo JSON
        with open("productos.json", "w", encoding="utf-8") as file:
            json.dump(productos_lista, file, ensure_ascii=False, indent=4)
        print(f"productos: {productos_lista}")

        return productos_lista


    except Exception as e:
        print(f"Error: {e}")
        return []

