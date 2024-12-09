import os
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session
import google.generativeai as genai
from werkzeug.utils import secure_filename
from PIL import Image
import serpapi
from dotenv import load_dotenv
import requests
from openai import OpenAI
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import requests  # Asegúrate de importar la biblioteca requests
import modules.voice as voice
import modules.images as images
import modules.serpapi as serpapii
# Cargar las variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Cargar las variables de entorno
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
CULINARY_MODEL = os.getenv('CULINARY_MODEL')
FASHION_MODEL = os.getenv('FASHION_MODEL')
GYM_MODEL = os.getenv('GYM_MODEL')
IMG_MODEL = os.getenv('IMG_MODEL')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configurar la clave API de SerpAPI
client_serpapi = serpapi.Client(api_key=SERPAPI_KEY)
# Inicializar los modelos generativos con las variables de entorno
model_culinary = genai.GenerativeModel(model_name=CULINARY_MODEL)
model_fashion = genai.GenerativeModel(model_name=FASHION_MODEL)
model_gym = genai.GenerativeModel(model_name=GYM_MODEL)
model_img = genai.GenerativeModel(IMG_MODEL)

# Configura la carpeta para almacenar las imágenes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
##################################################33
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
    if selected_model == 'culinary':  
        #################### GLOBAL ##################################
        # client = OpenAI()
        # assistant_culinary = client.beta.assistants.create(
        # name="Cooking",
        # instructions="el modelo debe actuar como un profesor de culinaria. Recibe una lista de ingredientes y debe proporcionarle al usuario una lista de pasos y guia al usuario para que efectúe la receta. Antes, indicale al usuario la receta que le vas a sugerir y preguntale si le gustaria esa u otra; si dice que sí ve indicando paso por paso, esperando a que el usuario termine un paso y quiera ir al siguiente. Solo puedes sugerir recetas con los ingredientes que recibe en la lista, únicamente esos. A menos que el usuario te pida que le sugieras una receta y que él conseguirá los ingredientes. Tu dominio es solo la culinaria",
        # tools=[{"type": "code_interpreter"}],
        # model="gpt-4o-mini",
        # )
        # thread_culinary = client.beta.threads.create()
        ########################################################

        message = client.beta.threads.messages.create(
            thread_id=thread_culinary.id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_culinary.id,
            assistant_id=assistant_culinary_id

        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread_culinary.id)

            # Filtrar los mensajes del asistente
            mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
            if mensajes_asistente:
                # Obtener el último mensaje del asistente
                ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
                for block in ultimo_mensaje.content:
                    print(f"Assistant: {block.text.value}") 
                    response= block.text.value# Imprime solo el contenido del último mensaje
            else:
                print("No se encontró un mensaje del asistente.")

        ####################################################
    elif selected_model == 'fashion':  
        ########GLOBAL################3
        # client = OpenAI()
        # assistant_fashion = client.beta.assistants.create(
        # name="Fashion",
        # instructions="Eres un asesor de moda. Recibes una lista de prendas de ropa y recomiendas combinaciones basadas en esas prendas.Tu dominio es solo el gym. Tu dominio es solo la moda",
        # tools=[{"type": "code_interpreter"}],
        # model="gpt-4o-mini",
        # )
        # thread_fashion = client.beta.threads.create()
        ##################################

        message = client.beta.threads.messages.create(
            thread_id=thread_fashion.id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_fashion.id,
            assistant_id=assistant_fashion_id   
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread_fashion.id)

            # Filtrar los mensajes del asistente
            mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
            print(messages)
            if mensajes_asistente:
                # Obtener el último mensaje del asistente
                ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
                for block in ultimo_mensaje.content:
                    print(f"Assistant: {block.text.value}") 
                    response= block.text.value# Imprime solo el contenido del último mensaje
            else:
                print("No se encontró un mensaje del asistente.")

        ####################################################
    elif selected_model == 'gym':  
        #################### GLOBAL ##################################
        # client = OpenAI()
        # assistant_gym= client.beta.assistants.create(
        #     name="gym",
        #     instructions="Eres un entrenador personal. Recibe una lista de elementos de gimnasio y sugiere ejercicios que se pueden realizar con esos elementos. Además, si el usuario lo desea, sugiere ejercicios para trabajar grupos musculares específicos.",
        #     tools=[{"type": "code_interpreter"}],
        #     model="gpt-4o-mini",
        # )
        # thread_gym = client.beta.threads.create()
        ############################################################

        message = client.beta.threads.messages.create(
            thread_id=thread_gym.id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread_gym.id,
            assistant_id=assistant_gym_id,
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread_gym.id)

            # Filtrar los mensajes del asistente
            mensajes_asistente = [msg for msg in messages.data if msg.role == 'assistant']
            print(messages)
            if mensajes_asistente:
                # Obtener el último mensaje del asistente
                ultimo_mensaje = mensajes_asistente[0]  # Accede al último mensaje del asistente
                for block in ultimo_mensaje.content:
                    print(f"Assistant: {block.text.value}") 
                    response= block.text.value# Imprime solo el contenido del último mensaje
            else:
                print("No se encontró un mensaje del asistente.")
    else:
        return jsonify({'response': 'Modelo no encontrado.'}), 400
    
    respuesta_texto = response  # Obtener la respuesta en texto del modelo


    # Mensaje inicial al seleccionar el dominio
    mensaje_inicial = f"Hola, este es el dominio {session.get('selected_domain', 'desconocido')}"

    # Buscar recetas en SerpAPI (si es necesario)
    recetas = serpapii.buscar_resultados_en_serpapi(user_input, selected_model)
    
    # Devolver la respuesta escrita, el mensaje inicial y la de SerpAPI
    return jsonify({
        'text_response': respuesta_texto,
        'mensaje_inicial': mensaje_inicial,
        'recipes': recetas
    })