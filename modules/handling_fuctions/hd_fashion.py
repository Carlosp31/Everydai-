import modules.Function_calling.busquedas as busquedas
import modules.Function_calling.webscrp as webscrp
import modules.Function_calling.act_bd as action_db
import json
from modules.get_inventory import get_inventory_from_redis 
from app import send_wish_list_email 

def hd_fashion(user_input, client, thread_idf, assistant_idf, run):
    response_2= None
    # Define the list to store tool outputs
    tool_outputs = []

    # Loop through each tool in the required action section
    for tool in run.required_action.submit_tool_outputs.tool_calls:
        print("He entrado a Loop")
        if tool.function.name == "buscar_resultados_en_serpapi_fashion":
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "Aquí tienes una lista de tu busqueda"
            })
            print("He entrado a call serpapi")
            # Acceder al primer tool_call en required_action.submit_tool_outputs
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                        # Extrae los arguments de la función, que están en formato string JSON
            arguments_str = tool_call.function.arguments
            
            # Convierte el string JSON de los arguments en un diccionario
            arguments_dict = json.loads(arguments_str)

            # Ejemplo: Si quieres extraer el valor del 'query'
            query = arguments_dict.get("query", "Valor no encontrado")

            # Si necesitas el modelo:
            model = arguments_dict.get("model", "Modelo no encontrado")
            response_2 = busquedas.buscar_resultados_en_serpapi_fashion(query, model)
            response_3 = "Busqueda_serp_fashion"

        elif tool.function.name == "buscar_producto_fashion":

            # Acceder al primer tool_call en required_action.submit_tool_outputs
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                        # Extrae los arguments de la función, que están en formato string JSON
            arguments_str = tool_call.function.arguments
            
            # Convierte el string JSON de los arguments en un diccionario
            arguments_dict = json.loads(arguments_str)
            print(f"arguments: {arguments_dict}")

            # Ejemplo: Si quieres extraer el valor del 'query'
            productos = arguments_dict.get("lista_de_compra", [])
            genero = arguments_dict.get("gender", "unknown") 
            print (f"producto a buscar: {productos}")
            response_2  = webscrp.web_fashion_HM(productos, genero)
            response_3 = "Buscando prendas"
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He encontrado algunos productos relacionados con tus busquedas. " #json.dumps(response_2)
            })
        elif tool.function.name == "almacenar_prendas":
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido en almacenar_items: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("prendas", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"Items extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_2 = action_db.almacenar_items(items)
            response_3 = "inventory_fashion"


            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He almacenado los items en tu inventario"
            })

        elif tool.function.name == "outfit_inmediato":
            print("FUNTION: Outgit inmediato")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido escaneados: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("prendas", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🍽 prendas extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_3 = "Sugierendo vestimenta para ahora"
            inv = get_inventory_from_redis()
            data, status_code = inv # Desempaquetamos la tupla
            
            if status_code == 200:  # Verificamos que la respuesta es exitosa
                response_2= data.get_json()  # Extraer el JSON directamente
                print(f"Response_2: f{response_2}")
                print("Inventario recibido:", response_2["items"])  # Acceder a los ítems
            else:
                print(f"Error en la respuesta: Código {status_code}")


            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"prendas disponibles: {items}, prendas en el guardarropa: {response_2}"
            })
        elif tool.function.name == "outfit_tardio":
            print("FUNTION: Outfit_tardio")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido escaneados: {arguments_dict}")

            # Extraer ingredientes correctamente
            items_receta = arguments_dict.get("prendas_outfit", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"Prendas necesarias para el evento: {items_receta}")

            # Llamar a la función con la lista de ingredientes
            response_3 = "Preparando outfit para la ocasión"
            inv = get_inventory_from_redis()
            data, status_code = inv # Desempaquetamos la tupla
            
            if status_code == 200:  # Verificamos que la respuesta es exitosa
                response_2= data.get_json()  # Extraer el JSON directamente
                print(f"Response_2: f{response_2}")
                print("Inventario recibido:", response_2["items"])  # Acceder a los ítems
            else:
                print(f"Error en la respuesta: Código {status_code}")


            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"prendas necesarias para el outfit: {items_receta}, guarda ropa del usuario: {response_2}"
            })
        elif tool.function.name == "send_wish_list":
            print("Enviando lista de compras")
            # Obtener los argumentos del tool_call
            send_wish_list_email()
            # Llamar a la función con la lista de ingredientes
            
            response_3 = "Enviando lista de compras"
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "Receta enviada"
            })

        elif tool.function.name == "almacenar_outfit":
            print("almacenar_outfit")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON outfit: {arguments_dict}")
            # Llamar a la función con la lista de ingredientes
            action_db.almacenar_outfit(arguments_dict)
            response_3 = "Guardando outit de la ocasión"
            nombre_ocasion = arguments_dict.get("nombre_ocasion", "").strip()
            response_2 = nombre_ocasion
            
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": nombre_ocasion
            })
        elif tool.function.name == "query_ocasiones":
            print("🔍 Buscando outfits guardadas...")


            # Obtener las outfits almacenadas
            outfits = action_db.buscar_outfits()
            print(f"✅ outfits encontradas: {outfits}")
            response_2= "Outfits encontrados"
            response_3 = "🔍 Buscando outfits guardadas..."
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(outfits, ensure_ascii=False)
            })

        elif tool.function.name == "check_ocasion_comeback":
            print("FUNCTION: check_ocasion_comeback")
            
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📥 Depuración: Verificar el JSON recibido
            print(f"📥 Ocasión escogida: {arguments_dict}")

            # Extraer prendas correctamente
            prendas_necesarias = arguments_dict.get("prendas", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🧥 Prendas extraídas: {prendas_necesarias}")

            # Llamar a la función con la lista de prendas
            response_3 = "Evaluando disponibilidad de prendas para la ocasión seleccionada"
            inv = get_inventory_from_redis()
            data, status_code = inv  # Desempaquetamos la tupla

            if status_code == 200:  # Verificamos que la respuesta es exitosa
                response_2 = data.get_json()  # Extraer el JSON directamente
                print(f"🧾 Inventario del usuario: {response_2}")
                print("👚 Prendas disponibles:", response_2["items"])  # Acceder a los ítems
            else:
                print(f"⚠️ Error en la respuesta: Código {status_code}")

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"Prendas necesarias para la ocasión: {prendas_necesarias}, inventario del usuario: {response_2}"
            })


        elif tool.function.name == "outfit_comeback":
            print("🧠 Pensando outfit...")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON outfit: {arguments_dict}")
            
            # Llamar a la función con la ocasión
            response_3 = "Guardando outfit"
            ocasion = arguments_dict.get("ocasion", "").strip()
            action_db.borrar_outfit(ocasion)
            response_2 = ocasion

            # Eliminar outfit anterior (opcional según tu lógica)
            action_db.borrar_outfit(ocasion)

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": ocasion
            })

        print(run.status)




    print(tool_outputs)
    # Submit all tool outputs at once after collecting them in a list
    if tool_outputs:
        try:
            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread_idf,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            print("Tool outputs submitted successfully.")
        except Exception as e:
            print("Failed to submit tool outputs:", e)

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread_idf)

            # Filtrar los mensajes del asistente
            mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
            if mensajes_asistente:
                # Obtener el último mensaje del asistente
                ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
                for block in ultimo_mensaje.content:
                    print(f"Assistant: {block.text.value}") 
                    response= block.text.value# Imprime solo el contenido del último mensaje
                    return response, response_2, response_3
            else:
                print("No se encontró un mensaje del asistente.")