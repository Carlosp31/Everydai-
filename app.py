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
import modules.computer_vision as cp
import platform
from google_auth_oauthlib.flow import Flow
from typing_extensions import override
from openai import AssistantEventHandler

from sqlalchemy.exc import SQLAlchemyError
#### Librerias de base de datos ###############
from flask_sqlalchemy import SQLAlchemy



################################################

# Cargar las variables de entorno del archivo .env
load_dotenv()
cert_file = '/etc/letsencrypt/live/everydai.ddns.net/fullchain.pem'
key_file = '/etc/letsencrypt/live/everydai.ddns.net/privkey.pem'
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')



##################
load_dotenv()
# Configurar la conexión a la base de datos usando variables de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar advertencias

# Inicializar la base de datos
db = SQLAlchemy(app)

class ShoppingList(db.Model):
    __tablename__ = "shopping_lists"  # Nombre correcto de la tabla

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(255), db.ForeignKey("users.provider_id"), nullable=False)
    domain_name = db.Column(db.String(50), db.ForeignKey("domains.domain_name"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.JSON, nullable=False, default=[])  # Por defecto, una lista vacía
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    @classmethod
    def get_or_create(cls, provider_id, domain_name):
        """Busca la lista de compras del usuario o la crea si no existe"""
        shopping_list = cls.query.filter_by(provider_id=provider_id, domain_name=domain_name).first()
        if not shopping_list:
            shopping_list = cls(provider_id=provider_id, domain_name=domain_name, items=[])
            db.session.add(shopping_list)
            db.session.commit()
        return shopping_list
    
    

    @classmethod
    def get_or_create(cls, provider_id, domain_name):
        try:
            shopping_list = cls.query.filter_by(provider_id=provider_id, domain_name=domain_name).first()
            print(f"Shpping list: {shopping_list}")
            if not shopping_list:
                shopping_list = cls(provider_id=provider_id, domain_name=domain_name, items=[])
                db.session.add(shopping_list)

            db.session.commit()
            return shopping_list
        
        except SQLAlchemyError as e:
            db.session.rollback()  # Deshacer cambios en caso de error
            print(f"Error en get_or_create: {e}")  # Mostrar el error en consola
            return None  # O manejarlo de otra forma

    def add_item(self, new_item):
        """Añadir un nuevo ítem sin sobrescribir la lista"""
        items_list = self.items if self.items else []  # Si es None, inicializar como lista vacía
        items_list.append(new_item)  
        self.items = items_list  # Asignar la lista actualizada
        db.session.commit()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'provider_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    provider_id = session['provider_id']
    data = request.json
    domain_name = data.get('domain_name')  # Cambia de domain_id a domain_name
    item = data.get('item')
    print(f"data: {data}")
    print(f"item: {item}")

    if not domain_name or not item:
        return jsonify({"error": "Faltan datos"}), 400

    # Buscar o crear la lista de compras
    shopping_list = ShoppingList.get_or_create(provider_id, domain_name)

    # Añadir el nuevo ítem al carrito
    if not isinstance(shopping_list.items, list):  # Asegurar que es una lista
        shopping_list.items = []

    shopping_list.items.append(item)
    db.session.commit()

    return jsonify({"items": shopping_list.items})



class Usuario(db.Model):
    __tablename__ = 'users'

    id = db.Column(db
    .Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Usuario {self.name}>'

# Función para convertir las credenciales en un diccionario para almacenarlas en la sesión
def credentials_to_dict(credentials):
    """Convierte las credenciales en un diccionario para almacenarlas en la sesión."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@app.route('/debug_session', methods=['GET'])
def debug_session():
    return jsonify(dict(session))  # Devuelve toda la sesión para verificar su contenido

#################
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
    elif os.path.exists("client_secret_wmaicol.json"):
        CLIENT_SECRETS_FILE = "client_secret_wmaicol.json"
    else:
        print("Advertencia: 'client_secret_web.json' no encontrado. Usando 'client_secret.json'.")
        CLIENT_SECRETS_FILE = "client_secret.json"

else:
  CLIENT_SECRETS_FILE = "client_secret.json" 
#SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid", "https://www.googleapis.com/auth/cloud-platform"  ]
REDIRECT_URI = 'https://everydai.ddns.net/oauth2callback'


@app.route('/realidad')
def realidad():
    return render_template('realidad.html')

@app.route('/realidadpro')
def realidadpro():
    return render_template('realidadpro.html')
@app.route('/realidadpro2')
def realidadpro2():
    return render_template('realidadpro2.html')

@app.route('/pruebas')
def pruebas():
    return render_template('pruebas_avatar.html')

if current_os == 'Linux' and CLIENT_SECRETS_FILE == "client_secret_wmaicol.json":
   REDIRECT_URI='https://localhost/oauth2callback'
   SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
   
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
        return render_template("dashboard.html")  # Renderizar directamente el dashboard

    # Flujo normal para Linux con autenticación requerida
    elif current_os == 'Linux':
        ssl_context=('cert.pem', 'key.pem')
        if 'credentials' not in session:
            # Crear el flujo de autorización
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )

            # Generar la URL de autorización
            authorization_url, state = flow.authorization_url(prompt='consent')

            # Guardar el estado en la sesión para verificarlo después
            session['state'] = state

            return redirect(authorization_url)
            
        credentials = Credentials.from_authorized_user_info(session['credentials'])

        # Hacer la solicitud a la API de Google para obtener la información del perfil
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        
        # Convertir la respuesta JSON a un diccionario
        user_info = response.json()
        print("Datos recibidos de Google:", user_info)

        session['provider_id'] = user_info['id']  # Guardar provider_id en sesión
        # Verificar si el usuario ya existe en la base de datos
        existing_user = Usuario.query.filter_by(provider_id=user_info['id']).first()
        if not existing_user:
            # Si el usuario no existe, crear uno nuevo
            new_user = Usuario(
                provider='google',
                provider_id=user_info['id'],
                name=user_info['name'],
                email=user_info['email'],
                profile_pic=user_info['picture']
            )
            db.session.add(new_user)
            db.session.commit()


    # Para otros sistemas operativos, renderizar el dashboard directamente
    return render_template("dashboard.html")
@app.route('/get_shopping_list', methods=['GET'])
def get_shopping_list():
    if 'provider_id' not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    provider_id = session['provider_id']
    selected_domain = session.get('selected_domain')  # Dominio seleccionado

    if not selected_domain:
        return jsonify({"error": "No se ha seleccionado un dominio"}), 400

    # Buscar la lista de compras del usuario en ese dominio
    shopping_list = ShoppingList.query.filter_by(provider_id=provider_id, domain_name=selected_domain).first()

    if not shopping_list:
        return jsonify({"items": []})  # Si no tiene lista, devolvemos vacío

    return jsonify({"items": shopping_list.items if shopping_list.items else []}), 200



# Ruta de callback OAuth2
@app.route('/oauth2callback')    
def oauth2callback():
    # Recuperar el estado de la sesión
    state = session['state']

    # Crear el flujo de autorización y obtener el token
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )

    # Obtener el token de acceso
    flow.fetch_token(authorization_response=request.url)

    # Almacenar las credenciales en la sesión
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)
    return redirect('/')

# Ruta para el chatbot que recibe el dominio seleccionado
@app.route('/chat')
def chat():
    domain = request.args.get('domain', '')  # Obtener el dominio desde la URL
    if domain not in ['Cooking', 'fashion', 'Fitness']:
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



@app.route('/process_frame', methods=['POST'])
def process_frame():
   return cp.process_frame()


if __name__ == '__main__':
    # Crear el directorio de carga si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Configuración del puerto y SSL
    try:
        if current_os == 'Linux' and CLIENT_SECRETS_FILE == "client_secret_wmaicol.json":
            port = 443
            ssl_context=('cert.pem', 'key.pem')
        elif current_os == 'Linux':
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
