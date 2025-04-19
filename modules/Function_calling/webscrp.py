import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv
import time
import traceback
# Cargar variables de entorno
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def web_culinary(lista):

    ###IMPLEMENTAR QUERY PARA LISTA DE PRODUCTOS!!!!!!!!!!!!!!!!!
    productos_lista = []
    try:
        for query in lista:
            search_query = f"{query} Olímpica"
            print(f"Producto a buscar: {query}")

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

            print("parametros enviados")
            try:
                # Ejecutar la búsqueda
                search = GoogleSearch(params)
                results = search.get_dict()
                print("parametros enviados")
                print((f"results: {results}"))
                # Obtener los resultados de shopping
                shopping_results = results.get("shopping_results", [])
                print(f"Shopping results: {shopping_results}")
                
                for item in results.get("shopping_results", [])[:5]:
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
                    print("ciclo")
                    productos_lista.append(producto_info)
                time.sleep(0.5)


            except Exception as e:
                print(f"❌ Error con la búsqueda '{query}': {e}")
                traceback.print_exc()
                return f"Error al buscar '{query}' en SerpAPI: {e}"

                        # Guardar en un archivo JSON
            with open("productos.json", "w", encoding="utf-8") as file:
                json.dump(productos_lista, file, ensure_ascii=False, indent=4)
            print(f"productos: {productos_lista}")
        return productos_lista


    except Exception as e:
        print(f"Error: {e}")
        return []
# prod=web_culinary(["Sal", "Aceite", "Huevos"])
# print(prod)
def web_fashion_HM(lista, gender):

    ###IMPLEMENTAR QUERY PARA LISTA DE PRODUCTOS!!!!!!!!!!!!!!!!!
    productos_lista = []
    print(f"Lista recibida: {lista}")
    print(f"gender:{gender}")
    try:
        for query in lista:
            search_query = f"{query} {gender} HM"
            print(f"Producto a buscar: {query}")

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

            
            for item in shopping_results[:5]:
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

