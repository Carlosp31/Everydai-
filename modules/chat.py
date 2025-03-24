from flask import  request, jsonify, session
from openai import OpenAI
import modules.domains as domains
from typing_extensions import override
from openai import AssistantEventHandler
 
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):    
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)
      
  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)
      
  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)
  
  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)

client = OpenAI()

# Definir variables globales


##################### Culinario #################################
global assistant_culinary
assistant_culinary_id= "asst_zOGNCMFiaD5IP0u4u4t8dOpX"

# Crear el thread global para culinary (esto solo lo inicializamos una vez)
global thread_culinary
thread_culinary = client.beta.threads.create()
#################################################################
##################### Fashion #################################
# Definir variables globales para el dominio de moda
global assistant_fashion
assistant_fashion_id = "asst_gu3wmqxmAklNSMU28Vhis4Mq"

# Crear el thread global para fashion (esto solo lo inicializamos una vez)
global thread_fashion
thread_fashion = client.beta.threads.create()
###################### Gym #################################
global assistant_gym
assistant_gym_id= "asst_jcySDtiW2FMg3yw9KHypnq9X"
global thread_gym
thread_gym = client.beta.threads.create()

def chat_post():
    user_input = request.json['message']
    selected_model = request.json['model']
    client = OpenAI()
    
    
    ####################################################
    if selected_model == 'Cooking':  
        response, response_2, response_3 = domains.chat_response(selected_model, user_input, client, thread_idf=thread_culinary.id, assistant_idf =assistant_culinary_id)

    elif selected_model == 'fashion':  
        response, response_2, response_3 = domains.chat_response(selected_model, user_input, client, thread_idf=thread_fashion.id, assistant_idf =assistant_fashion_id)
        ####################################################
    elif selected_model == 'Fitness':  
        response, response_2, response_3  = domains.chat_response(selected_model, user_input, client, thread_idf=thread_gym.id, assistant_idf =assistant_gym_id)

    else:
        return jsonify({'response': 'Modelo no encontrado.'}), 400
    # print("Response is:")
    # print(response)
    # respuesta_texto = response  # Obtener la respuesta en texto del modelo


    # # Mensaje inicial al seleccionar el dominio
    mensaje_inicial = f"Hola, este es el dominio {session.get('selected_domain', 'desconocido')}"

    # # Buscar recetas en SerpAPI (si es necesario)
    # recetas = serpapii.buscar_resultados_en_serpapi(user_input, selected_model)
    
    # Devolver la respuesta escrita, el mensaje inicial y la de SerpAPI
    return jsonify({
        'text_response': response,
        'mensaje_inicial': mensaje_inicial,
        'recipes': response_2,
        "response_3": response_3
    })