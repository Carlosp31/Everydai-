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
import modules.handling_fuctions.hd_culinary as hd_culinary
import modules.handling_fuctions.hd_gym as hd_gym
import modules.handling_fuctions.hd_fashion as hd_fashion


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




def chat_response(model, user_input, client, thread_idf, assistant_idf):
    response_2= None ##Esto guarda la respuesta de serpapi, sino hay es None
    message = client.beta.threads.messages.create(
    thread_id=thread_idf,
    role="user",
    content=user_input
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_idf,
        assistant_id= assistant_idf

    )
    print(f"Estado del assistant: {run.status}")
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
                return response, response_2
        else:
            print("No se encontró un mensaje del asistente.")
    elif run.status == "requires_action":
       if model=="culinary":
            response, response_2 = hd_culinary.hd_culinary(user_input, client, thread_idf, assistant_idf, run)
       elif model=="gym":
            response, response_2 = hd_gym.hd_gym(user_input, client, thread_idf, assistant_idf, run)
       elif model=="fashion":
            response, response_2 = hd_fashion.hd_fashion(user_input, client, thread_idf, assistant_idf, run)
       return response, response_2