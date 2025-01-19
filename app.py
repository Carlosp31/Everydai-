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
import modules.chat as chats
import platform
from google_auth_oauthlib.flow import Flow
from typing_extensions import override
from openai import AssistantEventHandler
# Cargar las variables de entorno del archivo .env
load_dotenv()
cert_file = '/etc/letsencrypt/live/everydai.ddns.net/fullchain.pem'
key_file = '/etc/letsencrypt/live/everydai.ddns.net/privkey.pem'
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
            print("Test runner")
 

 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
####################################################

########################################################

current_os = platform.system()
if current_os == 'Linux':
    # Verificar cuál archivo de secretos usar
    if os.path.exists("client_secret_web.json"):
        CLIENT_SECRETS_FILE = "client_secret_web.json"
    else:
        print("Advertencia: 'client_secret_web.json' no encontrado. Usando 'client_secret.json'.")
        CLIENT_SECRETS_FILE = "client_secret.json"

else:
  CLIENT_SECRETS_FILE = "client_secret.json" 
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
REDIRECT_URI = 'https://everydai.ddns.net/oauth2callback'


@app.route('/realidad')
def realidad():
    return render_template('realidad.html')

@app.route('/realidadpro')
def realidadpro():
    return render_template('realidadpro.html')

@app.route('/pruebas')
def pruebas():
    return render_template('pruebas_avatar.html')


flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)
@app.route('/')
def dashboard():
    # Verificar si está en Linux y el archivo de secretos es "client_secret.json"
    if current_os == 'Linux' and CLIENT_SECRETS_FILE == "client_secret.json":
        print("Sin autenticación requerida en Linux con 'client_secret.json'.")
        return render_template('dashboard.html')  # Renderizar directamente el dashboard

    # Flujo normal para Linux con autenticación requerida
    if current_os == 'Linux':
        if 'credentials' in session:
            # Si el usuario ya está autenticado, redirigir al dashboard
            return render_template('dashboard.html')
        else:
            # Iniciar el flujo de autenticación si no está autenticado
            authorization_url, state = flow.authorization_url(access_type='offline')
            session['state'] = state
            return redirect(authorization_url)

    # Para otros sistemas operativos, renderizar el dashboard directamente
    return render_template('dashboard.html')
    
# Ruta de callback OAuth2
@app.route('/oauth2callback')    
def oauth2callback():
    state = session['state']
    flow.fetch_token(authorization_response=request.url)
    
    # Guardar las credenciales en la sesión
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
       'scopes': credentials.scopes,
         'expires_at': credentials.expiry.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Redirigir al dashboard
    return render_template('dashboard.html')

# Ruta para el chatbot que recibe el dominio seleccionado
@app.route('/chat')
def chat():
    domain = request.args.get('domain', '')  # Obtener el dominio desde la URL
    if domain not in ['culinary', 'fashion', 'gym']:
        return "Dominio no válido", 400  # Validar el dominio

    # Almacenar el dominio seleccionado en la sesión
    session['selected_domain'] = domain

    # Renderizar la página del chatbot y pasar el dominio seleccionado
    return render_template('chat.html', domain=domain)



####################################################
# Actualización: mensaje inicial en el chat
@app.route('/chat', methods=['POST'])
def chat_function():
   return chats.chat_post()


@app.route('/synthesize-audio', methods=['POST'])
def synthesize_audio():
    text = request.json['text']
    modelo = request.json['modelo']
    audio_path = voice.sintetizar_voz(text, ELEVENLABS_API_KEY, modelo)
    
    if audio_path:
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'Error al sintetizar la voz.'}), 500



@app.route('/upload-image', methods=['POST'])
def handle_image():
    return images.upload_image()


if __name__ == '__main__':
    # Crear el directorio de carga si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Configuración del puerto y SSL
    try:
        if current_os == 'Linux':
            port = 443
            if os.path.exists(cert_file) and os.path.exists(key_file):
                ssl_context = (cert_file, key_file)  # Usar SSL si los certificados están disponibles
            else:
                print("Advertencia: No se encontraron los certificados SSL. Ejecutando sin SSL.")
                ssl_context = None
                port = 80  # Cambiar al puerto 80 si no se usa SSL
        elif current_os == 'Windows':
            port = 80
            ssl_context = None  # No usar SSL en Windows
        else:
            raise ValueError("Sistema operativo no soportado. Usa Linux o Windows.")
    except Exception as e:
        print(f"Error al configurar SSL: {e}")
        port = 80
        ssl_context = None

    # Información sobre la configuración
    print(f"Ejecutando en {current_os}, puerto: {port}, SSL: {'Habilitado' if ssl_context else 'Deshabilitado'}")

    # Iniciar la aplicación Flask
    app.run(host='0.0.0.0', port=port, ssl_context=ssl_context)
