import os
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from google.oauth2.credentials import Credentials
import modules.voice as voice
import modules.images as images
import modules.chat as chats
import platform
from google_auth_oauthlib.flow import Flow
from typing_extensions import override
from openai import AssistantEventHandler
from database import db, Config, redis_client
import modules.chat as chat_api
import modules.Function_calling.act_bd as fc_bd
#### Librerias de base de datos ###############

from database import db, Config
################################################
import redis
from database import db
from models import User, Domain, Inventory, WishList, UserPreference
import json
from modules.get_inventory import get_inventory_from_redis
from modules.get_wish_list import get_wish_list_from_redis
import modules.actions_db as actions_db
################ EMAIL #########################
import json
from models import User, Domain, WishList
from database import redis_client
from flask_mail import Message
from flask import current_app
from email_validator import validate_email, EmailNotValidError
from flask_mail import Mail

################################################
# Cargar las variables de entorno del archivo .env
load_dotenv()
cert_file = '/etc/letsencrypt/live/everydai.ddns.net/fullchain.pem'
key_file = '/etc/letsencrypt/live/everydai.ddns.net/privkey.pem'
app = Flask(__name__) 

app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

app.config.from_object(Config)

# Inicializar la base de datos con la app
db.init_app(app)
######################################################
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'everydaiuninorte@gmail.com'
app.config['MAIL_PASSWORD'] = 'jsum ysbi snlj mwnn'
app.config['MAIL_DEFAULT_SENDER'] = 'everydaiuninorte@gmail.com'

mail = Mail(app)

def send_wish_list_email():
    print("🔵 Iniciando envío de lista de deseos por correo...")

    if 'provider_id' not in session or 'selected_domain' not in session:
        print("🛑 Error: Usuario no autenticado o dominio no seleccionado")
        return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

    user_q = User.query.filter_by(provider_id=session['provider_id']).first()
    domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

    if not user_q or not domain_q:
        print("🛑 Error: Usuario o dominio no encontrado")
        return jsonify({"error": "Usuario o dominio no encontrado"}), 404

    if not user_q.email:
        print("🛑 Error: El usuario no tiene un correo registrado")
        return jsonify({"error": "El usuario no tiene un correo registrado"}), 400

    # Validar correo electrónico
    try:
        print(f"📧 Validando correo: {user_q.email}")
        validate_email(user_q.email, check_deliverability=True)
    except EmailNotValidError:
        print("🛑 Error: Correo electrónico no válido")
        return jsonify({"error": "Correo electrónico no válido"}), 400

    redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"
    print(f"🔍 Buscando lista de deseos en Redis con clave: {redis_key}")

    items_json = redis_client.get(redis_key)

    if items_json:
        try:
            print("📦 Decodificando JSON de la lista de deseos...")
            wish_list = json.loads(items_json)

            if isinstance(wish_list, str):
                wish_list = json.loads(wish_list)
            
            print(f"✅ Lista de deseos obtenida: {wish_list}")
        except json.JSONDecodeError:
            print("🛑 Error al decodificar la lista de deseos")
            return jsonify({"error": "Error al decodificar la lista de deseos"}), 500
    else:
        print("⚠️ No se encontró lista de deseos en Redis")
        wish_list = []

    if not wish_list:
        print("⚠️ La lista de deseos está vacía")
        return jsonify({"message": "La lista de deseos está vacía"}), 200

    # Crear el mensaje de correo
    subject = "Tu lista de deseos"
    body = "Aquí está tu lista de deseos:\n\n" + "\n".join(f"- {item}" for item in wish_list)
    print(f"📨 Preparando mensaje con asunto: {subject}")

    msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user_q.email])
    msg.body = body

    try:
        print(f"📤 Enviando correo a {user_q.email}...")
        mail.send(msg)
        print("✅ Correo enviado con éxito")
        return jsonify({"message": "Lista de deseos enviada con éxito"}), 200
    except Exception as e:
        print(f"🛑 Error al enviar el correo: {str(e)}")
        return jsonify({"error": f"Error al enviar el correo: {str(e)}"}), 500

#######################################################

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
CULINARY_MODEL = os.getenv('CULINARY_MODEL')
FASHION_MODEL = os.getenv('FASHION_MODEL')
GYM_MODEL = os.getenv('GYM_MODEL')
IMG_MODEL = os.getenv('IMG_MODEL')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configurar la clave API de SerpAPI
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





@app.route('/augmented experience')
def augmented_experience():
    return render_template('augmented experience.html')


if current_os == 'Linux' and CLIENT_SECRETS_FILE == "client_secret_wmaicol.json":
   REDIRECT_URI='https://localhost/oauth2callback'
   SCOPES = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"]
   
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI
)

@app.route('/')
def dashboard2_inicio():
    return render_template('dashboard2.html')

@app.route('/dashboard')
def dashboard():
    user_agent = request.headers.get('User-Agent')
    if "Mobile" in user_agent:  # Verifica si el navegador es móvil
        dash_ruta = 'dash_mobile.html'  # Devuelve la versión móvil
    else:
        dash_ruta = 'dashboard.html'  # Devuelve la versión de escritorio
    # Verificar si está en Linux y el archivo de secretos es "client_secret.json"
    if current_os == 'Linux' and CLIENT_SECRETS_FILE == "client_secret.json":
        print("Sin autenticación requerida en Linux con 'client_secret.json'.")
        return render_template(dash_ruta)  # Renderizar directamente el dashboard

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
        existing_user = User.query.filter_by(provider_id=user_info['id']).first()
        if not existing_user:
            # Si el usuario no existe, crear uno nuevo
            new_user = User(
                provider='google',
                provider_id=user_info['id'],
                name=user_info['name'],
                email=user_info['email'],
                profile_pic=user_info['picture']
            )
            db.session.add(new_user)
            db.session.commit()
        
    elif current_os == 'Windows':
  

        # Datos simulados para autenticación en Windows
        user_info = json.loads(os.getenv('USER_INFO'))

        # Guardar en sesión
        session['provider_id'] = user_info['id']
        session['credentials'] = {'token': 'fake_token_for_windows'}
        session['user_info'] = user_info  # Guarda toda la info del usuario en sesión
            

 
    # Para otros sistemas operativos, renderizar el dashboard directamente
    return render_template(dash_ruta)



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


# Configuración de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)



@app.route('/chat')
def chat():
    domain = request.args.get('domain', '')  # Obtener el dominio desde la URL
    if domain not in ['Cooking', 'fashion', 'Fitness']:
        return "Dominio no válido", 400  # Validar el dominio

    domain_q = Domain.query.filter_by(domain_name=domain).first()
    user_q = User.query.filter_by(provider_id=session.get('provider_id')).first()
    nombre = user_q.name

    if not user_q or not domain_q:
        return "Usuario o dominio no encontrado", 404

    # Intentar obtener los items de inventario desde Redis primero
    redis_key_inventory = f"user:{user_q.id}:domain:{domain_q.id}:inventory"
    inventory_json = redis_client.get(redis_key_inventory)


    if inventory_json:
        # Si los items están en Redis, los cargamos
        items = json.loads(inventory_json)  # Convertir el JSON almacenado en lista
        print("Cargando inventario desde Redis:", items)
    else:
        # Si no están en Redis, los consultamos en la base de datos
        inventory = Inventory.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        items = inventory.items if inventory else []

        # Guardamos en Redis para futuras consultas
        redis_client.set(redis_key_inventory, json.dumps(items))
        print("Cargando inventario desde MySQL y guardando en Redis:", items)

    # Intentar obtener los items de la wish_list desde Redis primero
    redis_key_wish_list = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"
    wish_list_json = redis_client.get(redis_key_wish_list)

    if wish_list_json:
        # Si la wish_list está en Redis, la cargamos
        wish_list_items = json.loads(wish_list_json)
        print("Cargando wish_list desde Redis:", wish_list_items)
    else:
        # Si no está en Redis, la consultamos en la base de datos
        wish_list_query = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        wish_list_items = wish_list_query.wish_items if wish_list_query else []

        # Guardamos la wish_list en Redis para futuras consultas
        redis_client.set(redis_key_wish_list, json.dumps(wish_list_items))
        print("Cargando wish_list desde MySQL y guardando en Redis:", wish_list_items)

    # Almacenar el dominio en la sesión
    session['selected_domain'] = domain

    chat_api.initialize_thread_with_inventory(nombre, domain_name=domain)

    # Renderizamos la plantilla con los items de inventario y wish_list
    return render_template('chat.html', domain=domain, wish_list_items=wish_list_items, inventory_items=items)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    return actions_db.add_to_cart()



@app.route('/remove_from_wish_list', methods=['POST'])
def remove_from_cart_route():
    data = request.get_json()
    print(f"🛑 Petición recibida en Flask: {data}")  # Verifica qué datos está recibiendo el backend
    
    if not data or 'domain_name' not in data or 'item_name' not in data:
        return jsonify({"error": "Datos inválidos"}), 400
    
    return actions_db.remove_from_wish_list()


@app.route('/remove_item', methods=['POST'])
def remove_inv():
    return actions_db.remove_from_inventory()

@app.route('/get_inventory')
def get_inventory_route():
    return get_inventory_from_redis() 



@app.route('/get_wish_list')
def get_wish_list_route():
    return get_wish_list_from_redis()

from flask import request, jsonify

@app.route('/add_to_inventory_from_wl', methods=['POST'])
def add_to_inventory_from_wl():
    try:
        # Obtener el JSON enviado desde la petición
        data = request.get_json()

        if not data or "items" not in data:
            return jsonify({"error": "No se recibió una lista válida"}), 400

        # Extraer la lista de items
        items = data["items"]

        # Asegurar que sea una lista antes de enviarla a almacenar_items()
        if isinstance(items, str):
            items = [items]  # Convertir en lista si es string único

        # Llamar a la función que almacena los ingredientes en la base de datos
        fc_bd.almacenar_items(items)

        return jsonify({"message": "Ítems agregados al inventario", "items": items}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


# Detectar sistema operativo
if platform.system() == "Linux":
    LOG_DIR = "/"  # Guardar en la raíz del sistema en Linux
else:
    LOG_DIR = "logs"  # Guardar en "logs/" si no es Linux

LOG_FILE = os.path.join(LOG_DIR, "interactions.json")  

if LOG_DIR != "/":
    os.makedirs(LOG_DIR, exist_ok=True)

def load_interactions():
    """Carga las interacciones desde el JSON, o lo inicializa si no existe."""
    if not os.path.exists(LOG_FILE):  # Si el archivo no existe, lo crea vacío
        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:  # Si el JSON está dañado, reiniciarlo
            return []

def save_interactions(data):
    """Guarda las interacciones en el JSON."""
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


@app.route('/log-interaction', methods=['POST'])
def log_interaction():
    interaction = request.json
    interactions = load_interactions()
    interactions.append(interaction)  # Agregar nueva interacción
    save_interactions(interactions)
    return jsonify({"message": "Interacción guardada"}), 200


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