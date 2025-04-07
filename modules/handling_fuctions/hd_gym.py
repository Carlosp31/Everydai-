from werkzeug.utils import secure_filename
import modules.Function_calling.busquedas as busquedas
import json
import modules.Function_calling.busquedas as busquedas
import modules.Function_calling.webscrp as webscrp
import modules.Function_calling.act_bd as action_db
from modules.get_inventory import get_inventory_from_redis 

def hd_gym(user_input, client, thread_idf, assistant_idf, run):
    response_2= None
    # Define the list to store tool outputs
    tool_outputs = []

    # Loop through each tool in the required action section
    for tool in run.required_action.submit_tool_outputs.tool_calls:
        print("He entrado a Loop")
        # if tool.function.name == "buscar_resultados_en_serpapi_gym":
        #     print("✅ Entrando a función: buscar_resultados_en_serpapi_gym")

        #     # Acceder al tool_call
        #     tool_call = run.required_action.submit_tool_outputs.tool_calls[0]

        #     # Extraer argumentos
        #     arguments_str = tool_call.function.arguments
        #     arguments_dict = json.loads(arguments_str)

        #     # Obtener parámetros
        #     ejercicios = arguments_dict.get("ejercicios", [])
        #     model = arguments_dict.get("model", "modelo_no_encontrado")

        #     # Depuración
        #     print(f"🔍 Lista de ejercicios a buscar: {ejercicios}")
        #     print(f"🧠 Dominio: {model}")

        #     # Llamar a la función con la lista de ejercicios
        #     response_2 = busquedas.buscar_resultados_en_serpapi_gym(ejercicios, model)
        #     response_3 = "busqueda_serp_gym"

        #     # Agregar al output para el modelo
        #     tool_outputs.append({
        #         "tool_call_id": tool.id,
        #         "output": f"Resultados de búsqueda para los ejercicios: {', '.join(ejercicios)}"
        #     })

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
                "output": json.dumps(response_2)  # Pasamos lista JSON como string
            })

        elif tool.function.name == "buscar_producto_fitness":

            # Acceder al primer tool_call en required_action.submit_tool_outputs
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                        # Extrae los arguments de la función, que están en formato string JSON
            arguments_str = tool_call.function.arguments
            
            # Convierte el string JSON de los arguments en un diccionario
            arguments_dict = json.loads(arguments_str)

            # Ejemplo: Si quieres extraer el valor del 'query'
            producto = arguments_dict.get("producto", "Valor no encontrado")
            print (f"producto a buscar: {producto}")
            response_2  = webscrp.web_fitness_decathlon(producto)
            response_3 = "Busqueda_prod_fitness"
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": "He encontrado algunos productos relacionados con tus busquedas. " #json.dumps(response_2)
            })
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