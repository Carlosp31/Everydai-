from werkzeug.utils import secure_filename
import modules.Function_calling.busquedas as busquedas
import json
import modules.Function_calling.busquedas as busquedas
import modules.Function_calling.webscrp as webscrp
import modules.Function_calling.act_bd as action_db
from modules.get_inventory import get_inventory_from_redis
from app import send_wish_list_email  

def hd_gym(user_input, client, thread_idf, assistant_idf, run):
    response_2= None
    # Define the list to store tool outputs
    tool_outputs = []

    # Loop through each tool in the required action section
    for tool in run.required_action.submit_tool_outputs.tool_calls:
        print("He entrado a Loop")


        if tool.function.name == "buscar_resultados_en_serpapi_gym":
            print("✅ Entrando a función: buscar_resultados_en_serpapi_gym")

            tool_call = tool
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            ejercicios = arguments_dict.get("ejercicios", [])
            model = arguments_dict.get("model", "modelo_no_encontrado")

            print(f"🔍 Lista de ejercicios a buscar: {ejercicios}")
            print(f"🧠 Dominio: {model}")

            response_2= busquedas.buscar_resultados_en_serpapi_gym(ejercicios)
            print(f"resultado: {response_2}")
            # Solo dejar los campos que tu JS puede renderizar: title y link

            response_3 = "busqueda_serp_gym"

            print("📥 Resultados filtrados:", response_2)

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He ecnontrado algunas recomendaciones sobres cómo hacer los ejercicios" # Pasamos lista JSON como string
            })

        elif tool.function.name == "buscar_producto_fitness":

            # Acceder al primer tool_call en required_action.submit_tool_outputs
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                        # Extrae los arguments de la función, que están en formato string JSON
            arguments_str = tool_call.function.arguments
            
            # Convierte el string JSON de los arguments en un diccionario
            arguments_dict = json.loads(arguments_str)

            # Ejemplo: Si quieres extraer el valor del 'query'
            productos = arguments_dict.get("lista_de_compra", "Valor no encontrado")
            print (f"producto a buscar: {productos}")
            response_2  = webscrp.web_fitness_decathlon(productos)
            response_3 = "Busqueda_prod_fitness"
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He encontrado algunos productos relacionados con tus busquedas. " #json.dumps(response_2)
            })
            action_db.almacenar_items_wishlist(productos)
            print(f"🛒 Ingredientes a añadir: {productos}")
            send_wish_list_email()
        elif tool.function.name == "almacenar_items_fitness":
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido en almacenar_items: {arguments_dict}")

            # Extraer ingredientes correctamente
            items = arguments_dict.get("items", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"Items extraídos: {items}")

            # Llamar a la función con la lista de ingredientes
            response_2 = action_db.almacenar_items(items)
            response_3 = "inventory_fitness"

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He almacenado los items en tu inventario"
            })

        elif tool.function.name == "rutina_inmediata":
            print("FUNCTION: Rutina inmediata")

            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido: {arguments_dict}")

            # Extraer datos del JSON
            grupo_muscular = arguments_dict.get("grupo_muscular", "")
            condicion_fisica = arguments_dict.get("condicion_fisica", "")
            equipo_disponible = arguments_dict.get("equipo_disponible", [])

            # 📦 Depuración: Mostrar datos extraídos
            print(f"💪 Grupo muscular: {grupo_muscular}")
            print(f"⚙️ Condición física: {condicion_fisica}")
            print(f"🏋️ Equipo disponible: {equipo_disponible}")

            # Lógica simulada de sugerencia con inventario (si aplica)
            inv = get_inventory_from_redis()
            data, status_code = inv

            if status_code == 200:
                response_2 = data.get_json()
                print(f"Inventario recibido: {response_2['items']}")
            else:
                print(f"Error al obtener inventario: Código {status_code}")

            # Simulación de respuesta de rutina sugerida
            response_3 = "Sugerencia de rutina inmediata en función del equipo y grupo muscular."

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"grupo_muscular: {grupo_muscular}, condición_fisica: {condicion_fisica}, equipo_disponible: {equipo_disponible}"
            })
        elif tool.function.name == "rutina_futura":
            print("rutina futura")
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON recibido escaneados: {arguments_dict}")

            # Extraer ingredientes correctamente
            items_receta = arguments_dict.get("implementos_necesarios", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"implementos necesarios para la rutina: {items_receta}")
            action_db.almacenar_rutina_gym(arguments_dict)
            # Llamar a la función con la lista de ingredientes
            response_3 = "Preparando rutina"
            inv = get_inventory_from_redis()
            data, status_code = inv # Desempaquetamos la tupla
            
            if status_code == 200:  # Verificamos que la respuesta es exitosa
                response_2= data.get_json()  # Extraer el JSON directamente
                print(f"Response_2: f{response_2}")
                print("Implementos necesarios:", response_2["items"])  # Acceder a los ítems
            else:
                print(f"Error en la respuesta: Código {status_code}")


            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"implementos necesarios para la rutina: {items_receta}, implementos con los que cuenta el usuario {response_2}"
            })

        elif tool.function.name == "almacenar_rutina_gym":
            print("almacenar_rutina_gym")
            
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📩 Depuración: Verificar el JSON recibido
            print(f"📥 JSON rutina gym: {arguments_dict}")

            # Llamar a la función para almacenar la rutina
            action_db.almacenar_rutina_gym(arguments_dict)
            
            response_3 = "Guardando rutina para la ocasión"
            nombre_rutina = arguments_dict.get("rutina", "").strip()
            response_2 = nombre_rutina

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": nombre_rutina
            })
        elif tool.function.name == "add_to_wishlist":
            print("📝 Añadiendo ingredientes a la wishlist...")
            send_wish_list_email()
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📥 Depuración: Verificar los datos recibidos
            print(f"📥 JSON recibido en agregar_a_wishlist: {arguments_dict}")

            items_faltantes = arguments_dict.get("items_a_agregar", [])
            action_db.almacenar_items_wishlist(items_faltantes)
            print(f"🛒 Ingredientes a añadir: {items_faltantes}")
            
            # Aquí se llama a la función de base de datos que añade a wishlist
            # resultado = action_db.agregar_a_wishlist(ingredientes_faltantes)
            # print(f"✅ Resultado de la operación: {resultado}")
            
            response_3 = "📝 Elementos añadidos a tu wishlist."
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "Ya añadido los ingredientes faltantes a tu lista. Lo he enviado a tu correo para que lo recuerdas cuando vayas de compras."
            })
        elif tool.function.name == "query_rutinas":
            print("🔍 Buscando rutinas guardadas...")

            # Obtener las rutinas almacenadas
            rutinas = action_db.buscar_rutinas()
            print(f"✅ Rutinas encontradas: {rutinas}")
            response_2 = "Rutinas encontradas"
            response_3 = "🔍 Mostrando tus rutinas guardadas..."
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": json.dumps(rutinas, ensure_ascii=False)
            })
        elif tool.function.name == "check_rutina_comeback":
            print("FUNCTION: check_rutina_comeback")
            
            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📥 Depuración: Verificar el JSON recibido
            print(f"📥 Rutina escogida (implementos requeridos): {arguments_dict}")

            # Extraer implementos necesarios
            implementos_necesarios = arguments_dict.get("implementos", [])

            # 📦 Depuración: Verificar lo que se enviará a la función
            print(f"🏋️‍♂️ Implementos extraídos: {implementos_necesarios}")

            # Llamar a la función con la lista de implementos
            response_3 = "Evaluando disponibilidad de implementos para la rutina seleccionada"
            inv = get_inventory_from_redis()
            data, status_code = inv  # Desempaquetamos la tupla

            if status_code == 200:
                response_2 = data.get_json()  # Extraer el JSON directamente
                print(f"📦 Inventario del usuario: {response_2}")
                print("🏋️ Implementos disponibles:", response_2["items"])
            else:
                print(f"⚠️ Error al obtener el inventario: Código {status_code}")

            # Generar respuesta en tool_outputs
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": f"Implementos necesarios para la rutina: {implementos_necesarios}, inventario del usuario: {response_2}"
            })

        elif tool.function.name == "rutina_comeback":
            print("💪 Iniciando rutina seleccionada...")

            # Obtener los argumentos del tool_call
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            arguments_str = tool_call.function.arguments
            arguments_dict = json.loads(arguments_str)

            # 📝 Depuración: Verificar el JSON recibido
            print(f"📥 JSON rutina: {arguments_dict}")

            # Extraer nombre y ejercicios
            nombre_rutina = arguments_dict.get("nombre_rutina", "").strip()
            ejercicios = arguments_dict.get("ejercicios", [])

            # ✅ Confirmar rutina y borrar si es necesario
            response_2 = nombre_rutina
            response_3 = f"Iniciando rutina: {nombre_rutina} 💪"

            # Eliminar la rutina de preferencias (opcional)
            action_db.borrar_rutina(nombre_rutina)

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": nombre_rutina
            })


        # elif tool.function.name == "implementos_faltantes_gym":
        #     print("🏋️ implementos_faltantes_gym")
        #     # Obtener los argumentos del tool_call actual
        #     tool_call = tool
        #     arguments_str = tool_call.function.arguments
        #     arguments_dict = json.loads(arguments_str)

        #     # 📩 Depuración: Verificar el JSON recibido
        #     print(f"📥 JSON recibido con implementos: {arguments_dict}")

        #     # Extraer la lista de implementos requeridos
        #     implementos_requeridos = arguments_dict.get("implementos_necesarios", [])

        #     # 📦 Depuración: Verificar lo que se va a usar
        #     print(f"🎯 Implementos necesarios para la rutina: {implementos_requeridos}")

        #     # Obtener el inventario desde Redis
        #     response_3 = "Preparando rutina personalizada..."
        #     inv = get_inventory_from_redis()
        #     data, status_code = inv  # Desempaquetamos la tupla
            
        #     if status_code == 200:
        #         response_2 = data.get_json()
        #         print(f"📦 Inventario recibido: {response_2}")
        #         print("🧰 Implementos en inventario:", response_2["items"])
        #     else:
        #         print(f"❌ Error en la respuesta: Código {status_code}")

        #     tool_outputs.append({
        #         "tool_call_id": tool.id,
        #         "output": f"Implementos requeridos: {implementos_requeridos}, inventario del usuario: {response_2}"
        #     })

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
        print(run.status)
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
            response, response_2, response_3 = hd_gym(user_input, client, thread_idf, assistant_idf, run)
            return response, response_2, response_3