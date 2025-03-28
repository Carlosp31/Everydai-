from flask import  request, jsonify, session
from openai import OpenAI
import modules.domains as domains
from typing_extensions import override
from openai import AssistantEventHandler
 
from database import db

from flask import  request, jsonify, session
from app import redis_client 

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

global client
client = OpenAI()

# Definir variables globales


##################### Culinario #################################
global assistant_culinary
assistant_culinary_id= "asst_zOGNCMFiaD5IP0u4u4t8dOpX"

# Crear el thread global para culinary (esto solo lo inicializamos una vez)
global thread_culinary
thread_culinary = client.beta.threads.create()

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
    
    mensaje_inicial = f"Hola, este es el dominio {session.get('selected_domain', 'desconocido')}"

    return jsonify({
        'text_response': response,
        'mensaje_inicial': mensaje_inicial,
        'recipes': response_2,
        "response_3": response_3
    })


#####Initial Inventory 

def chat_inventory(domain_name, items, thread_idf, assistant_idf):
    """Inicializa la conversación con OpenAI proporcionando el inventario del usuario."""

    print(f"🔹 Inicializando inventario en {domain_name}")
    # 🔹 Crear mensaje de concientización para el asistente
    user_inventory = f"El usuario tiene los siguientes ítems en su inventario: {', '.join(items)}."

    # 🔹 Enviar mensaje al asistente para que sea consciente del inventario
    message = client.beta.threads.messages.create(
        thread_id=thread_idf,
        role="user",
        content=user_inventory
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_idf,
        assistant_id= assistant_idf

    )
    

    print("📩 Inventario enviado al asistente:", user_inventory)

def initialize_thread_with_inventory(items, domain_name):
    """Inicializa un thread con la concientización del inventario (solo una vez)."""

    if domain_name == 'Cooking':  
        chat_inventory(domain_name, items, thread_idf=thread_culinary.id, assistant_idf=assistant_culinary_id)

    elif domain_name == 'fashion':  
        chat_inventory(domain_name, items, thread_idf=thread_fashion.id, assistant_idf=assistant_fashion_id)

    elif domain_name == 'Fitness':  
        chat_inventory(domain_name, items, thread_idf=thread_gym.id, assistant_idf=assistant_gym_id)


