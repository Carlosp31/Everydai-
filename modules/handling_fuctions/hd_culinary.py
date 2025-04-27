import modules.Function_calling.busquedas as busquedas
import modules.Function_calling.webscrp as webscrp
import modules.Function_calling.act_bd as action_db
import json
from modules.get_inventory import get_inventory_from_redis 
# from modules.get_wish_list import send_wish_list_email
from app import send_wish_list_email 
import modules.Function_calling.generation as generation

def hd_culinary(user_input, client, thread_idf, assistant_idf, run):
    response_2= None
    # Define the list to store tool outputs
    tool_outputs = []

    # Loop through each tool in the required action section
    for tool in run.required_action.submit_tool_outputs.tool_calls:
        print("He entrado a Loop")
        if tool.function.name == "buscar_resultados_en_serpapi_culinary":
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "Aquí tienes una lista de recetas"
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
            response_2 = busquedas.buscar_resultados_en_serpapi_culinary(query, model)
            response_3 = "Busqueda_serp_cooking"



        elif tool.function.name == "buscar_producto_culinary":

            # Acceder al primer tool_call en required_action.submit_tool_outputs
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                        # Extrae los arguments de la función, que están en formato string JSON
            arguments_str = tool_call.function.arguments
            
            # Convierte el string JSON de los arguments en un diccionario
            arguments_dict = json.loads(arguments_str)
            print(f"arguments: {arguments_dict}")

            # Ejemplo: Si quieres extraer el valor del 'query'
            productos = arguments_dict.get("lista_de_compra", [])
            print (f"producto a buscar: {productos}")
            response_2  = webscrp.web_culinary(productos)
            response_3 = "Busqueda_prod_cooking"
            action_db.almacenar_items_wishlist(productos )
            print(f"🛒 Ingredientes a añadir: {productos }")
            
            # Aquí se llama a la función de base de datos que añade a wishlist
            # resultado = action_db.agregar_a_wishlist(ingredientes_faltantes)
            # print(f"✅ Resultado de la operación: {resultado}")
            send_wish_list_email()
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"He notado que te faltan algunos ingredientes para tu receta:{productos}" #json.dumps(response_2)
            })

        elif tool.function.name == "almacenar_ingredientes":
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido en almacenar_ingredientes: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("ingredientes", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🍽 Ingredientes extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_3 = "inventory_cooking"
            response_2 = action_db.almacenar_items(items)
            print(f"respuesta inventario: {response_2}")

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"{items}"
            })

        elif tool.function.name == "receta_inmediata":
            print("FUNTION: Receta inmediata")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido escaneados: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("ingredientes", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🍽 Ingredientes extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_3 = "Sugierendo receta inmediata cooking"
            inv = get_inventory_from_redis()
            data, status_code = inv # Desempaquetamos la tupla
            
            if status_code == 200:  # Verificamos que la respuesta es exitosa
                inventario_user= data.get_json()  # Extraer el JSON directamente
                print(f"Inventario_User: f{inventario_user}")
                print("Inventario recibido:", inventario_user["items"])  # Acceder a los ítems
            else:
                print(f"Error en la respuesta: Código {status_code}")


            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"ingredientes_receta: {items}, inventario del usuario: {inventario_user}"
            })

        elif tool.function.name == "receta_tardia":
            print("FUNTION: Receta Tardía")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido escaneados: {arguments_dict}")

            # Extraer ingredientes correctamente
            items_receta = arguments_dict.get("ingredientes_receta", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🍽 Ingredientes extraídos: {items_receta}")
            action_db.almacenar_receta(arguments_dict)
            # Llamar a la función con la lista de ingredientes
            response_3 = "Sugierendo receta tardía cooking"
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
                "output": f"ingredientes_receta: {items_receta}, inventario con el que cuenta el usuario: {response_2}"
            })
        elif tool.function.name == "ejemplos_recetas":
            print("FUNCTION: Ejemplos Recetas")

            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)
            response_3= "Generating examples"
            # 📥 Depuración: Verificar los datos recibidos
            print(f"📥 JSON recibido en ejemplos_recetas: {arguments_dict}")

            # Extraer el nombre de la receta
            nombre_receta = arguments_dict.get("nombre_receta", "").strip()

            if nombre_receta:
                print(f"🎨 Generando visualización para: {nombre_receta}") # Aquí llamas a tu función de visualización
            else:
                print("⚠️ No se recibió un nombre válido de receta.")
            url_imagen = generation.generate(nombre_receta)
            response_2= url_imagen
            print(f"response 2: {response_2}")
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"Aquí tienes unas posibles recetas"
            })
        elif tool.function.name == "ejemplos_recetas_tardia":
            print("FUNCTION: Ejemplos Recetas Tardía")

            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)
            response_3 = "Generating multiple recipe visuals"

            # 📥 Depuración: Verificar los datos recibidos
            print(f"📥 JSON recibido en ejemplos_recetas_tardia: {arguments_dict}")

            # Extraer la lista de nombres de recetas
            nombres_recetas = arguments_dict.get("nombres_recetas", [])

            if nombres_recetas and isinstance(nombres_recetas, list):
                print(f"🎨 Generando visualizaciones para: {nombres_recetas}")

                # Generar imágenes para cada receta
                urls_imagenes = generation.generate_multiple(nombres_recetas)
                response_2 = urls_imagenes


                # 📤 Mostrar los resultados generados
                print(f"🖼 URLs generadas: {urls_imagenes}")

                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": f"Aquí tienes unas sugerencias de recetas"
                })
            else:
                print("⚠️ No se recibió una lista válida de recetas.")


        elif tool.function.name == "almacenar_receta":
            print("almacenar_receta")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON receta: {arguments_dict}")
            # Llamar a la función con la lista de ingredientes
            action_db.almacenar_receta(arguments_dict)
            response_3 = "Guardando receta"
            nombre_receta = arguments_dict.get("nombre_receta", "").strip()
            response_2 = nombre_receta
            
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": nombre_receta
            })
        # elif tool.function.name == "add_to_wishlist":
        #     print("📝 Añadiendo ingredientes a la wishlist...")

        #     # Obtener los argumentos del tool_call
        #     tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        #     arguments_str = tool_call.function.arguments
        #     arguments_dict = json.loads(arguments_str)

        #     # 📥 Depuración: Verificar los datos recibidos
        #     print(f"📥 JSON recibido en agregar_a_wishlist: {arguments_dict}")

        #     ingredientes_faltantes = arguments_dict.get("items_a_agregar", [])
        #     action_db.almacenar_items_wishlist(ingredientes_faltantes)
        #     print(f"🛒 Ingredientes a añadir: {ingredientes_faltantes}")
            
        #     # Aquí se llama a la función de base de datos que añade a wishlist
        #     # resultado = action_db.agregar_a_wishlist(ingredientes_faltantes)
        #     # print(f"✅ Resultado de la operación: {resultado}")
        #     send_wish_list_email()
        #     response_3 = "📝 Ingredientes añadidos a tu wishlist."
        #     tool_outputs.append({
        #         "tool_call_id": tool.id,
        #         "output": "Ya añadido los ingredientes faltantes a tu lista. Lo he enviado a tu correo para que lo recuerdas cuando vayas de compras."
        #     })

        elif tool.function.name == "query_recetas":
            print("🔍 Buscando recetas guardadas...")


            # Obtener las recetas almacenadas
            recetas = action_db.buscar_receta()
            print(f"✅ Recetas encontradas: {recetas}")

            response_3 = "🔍 Buscando recetas guardadas..."
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(recetas, ensure_ascii=False)
            })

        elif tool.function.name == "check_receta_comeback":
            print("FUNTION: check receta_comeback")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 Receta escogida: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("ingredientes", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🍽 Ingredientes extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_3 = "Sugierendo receta inmediata"
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
                "output": f"ingredientes necesarios para la receta: {items}, inventario del usuario: {response_2}"
            })


        elif tool.function.name == "receta_comeback":
            print("Pensando receta")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON receta: {arguments_dict}")
            # Llamar a la función con la lista de ingredientes
            
            response_3 = "Guardando receta"
            nombre_receta = arguments_dict.get("nombre_receta", "").strip()
            response_2 = nombre_receta
            action_db.borrar_receta(nombre_receta)
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": nombre_receta
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
        print(run.status)

    print(f"print tools outputs: {tool_outputs}")
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
        else:
            response, response_2, response_3 = hd_culinary(user_input, client, thread_idf, assistant_idf, run)
            return response, response_2, response_3