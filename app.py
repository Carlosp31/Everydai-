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
from database import db, Config, redis_client
from sqlalchemy.exc import SQLAlchemyError
#### Librerias de base de datos ###############
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, timezone
from database import db, Config
################################################
import redis
from database import db
from models import User, Domain, Inventory, WishList, UserPreference
import json
from modules.get_inventory import get_inventory_from_redis
from modules.get_wish_list import get_wish_list_from_redis
################################################
# Cargar las variables de entorno del archivo .env
load_dotenv()
cert_file = '/etc/letsencrypt/live/everydai.ddns.net/fullchain.pem'
key_file = '/etc/letsencrypt/live/everydai.ddns.net/privkey.pem'
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')



##################
# Configurar la conexión a la base de datos usando variables de entorno
from flask import Flask



app.config.from_object(Config)

# Inicializar la base de datos con la app
db.init_app(app)

@app.route('/test_redis')
def test_redis():
    redis_client.set("mensaje", "Hola desde Redis!")
    return redis_client.get("mensaje")  # Devuelve "Hola desde Redis!"

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     if 'provider_id' not in session:
#         return jsonify({"error": "Usuario no autenticado"}), 401

#     provider_id = session['provider_id']
#     data = request.json
#     domain_name = data.get('domain_name')  # Cambia de domain_id a domain_name
#     item = data.get('item')
#     print(f"data: {data}")
#     print(f"item: {item}")

#     if not domain_name or not item:
#         return jsonify({"error": "Faltan datos"}), 400

#     # Buscar o crear la lista de compras
#     shopping_list = ShoppingList.get_or_create(provider_id, domain_name)

#     # Añadir el nuevo ítem al carrito
#     if not isinstance(shopping_list.items, list):  # Asegurar que es una lista
#         shopping_list.items = []

#     shopping_list.items.append(item)
#     db.session.commit()

#     return jsonify({"items": shopping_list.items})





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

########################################################

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
@app.route('/realidadpro3')
def realidadpro3():
    return render_template('realidadpro3.html')
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

    # Para otros sistemas operativos, renderizar el dashboard directamente
    return render_template(dash_ruta)
# @app.route('/get_shopping_list', methods=['GET'])
# def get_shopping_list():
#     if 'provider_id' not in session:
#         return jsonify({"error": "Usuario no autenticado"}), 401

#     provider_id = session['provider_id']
#     selected_domain = session.get('selected_domain')  # Dominio seleccionado

#     if not selected_domain:
#         return jsonify({"error": "No se ha seleccionado un dominio"}), 400

#     # Buscar la lista de compras del usuario en ese dominio
#     shopping_list = ShoppingList.query.filter_by(provider_id=provider_id, domain_name=selected_domain).first()

#     if not shopping_list:
#         return jsonify({"items": []})  # Si no tiene lista, devolvemos vacío

#     return jsonify({"items": shopping_list.items if shopping_list.items else []}), 200



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
    if domain not in ['Cooking', 'Fashion', 'Fitness']:
        return "Dominio no válido", 400  # Validar el dominio

    domain_q = Domain.query.filter_by(domain_name=domain).first()
    user_q = User.query.filter_by(provider_id=session.get('provider_id')).first()

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

    # Renderizamos la plantilla con los items de inventario y wish_list
    return render_template('chat.html', domain=domain, wish_list_items=wish_list_items, inventory_items=items)




@app.route('/get_inventory')
def get_inventory_route():
    return get_inventory_from_redis() 



@app.route('/get_wish_list')
def get_wish_list_route():
    return get_wish_list_from_redis()


from flask import request, jsonify, session
from models import db, WishList, User, Domain
import json 
import json





import json

def save_wish_list_to_db(user_id, domain_id, wish_list):
    """Guarda correctamente la lista de deseos en MySQL sin caracteres escapados"""
    
    print(f"💾 Guardando en MySQL para user_id={user_id}, domain_id={domain_id}...")
    
    wish_list_json = json.dumps(wish_list, ensure_ascii=False)  # ✅ Guardar JSON sin caracteres extraños

    wish_list_entry = WishList.query.filter_by(user_id=user_id, domain_id=domain_id).first()
    
    if wish_list_entry:
        print("✏️ Actualizando lista existente en MySQL...")
        wish_list_entry.wish_items = wish_list_json
    else:
        print("🆕 Creando nueva entrada en MySQL...")
        wish_list_entry = WishList(user_id=user_id, domain_id=domain_id, wish_items=wish_list_json)
        db.session.add(wish_list_entry)

    db.session.commit()
    print("✅ Lista guardada en MySQL correctamente.")
    
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Añade un producto a la lista de deseos en Redis y lo guarda en MySQL."""

    print("🔵 Iniciando add_to_cart...")

    try:
        # 🛑 Verificar sesión del usuario
        if 'provider_id' not in session or 'selected_domain' not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session['provider_id']).first()
        domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 📩 Recibir datos
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        if not data or "item" not in data or "name" not in data["item"] or "price" not in data["item"]:
            return jsonify({"error": "Datos inválidos"}), 400

        new_item = {
            "name": data["item"]["name"],
            "price": data["item"]["price"]
        }

        # 🔑 Clave en Redis
        redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"

        # 📜 Obtener la lista de deseos desde Redis
        wish_list_json = redis_client.get(redis_key)
        print(f"📜 Lista en Redis (raw): {wish_list_json}")

        wish_list = []
        if wish_list_json:
            try:
                wish_list = json.loads(wish_list_json)
                print(f"✅ Lista deserializada: {wish_list}")
            except json.JSONDecodeError:
                print("⚠️ Error: No se pudo decodificar wish_list desde JSON")
                wish_list = []

        # 🛑 Evitar duplicados
        if any(item["name"] == new_item["name"] for item in wish_list):
            return jsonify({"message": "El ítem ya está en la lista de deseos"}), 200

        # 🆕 Agregar el nuevo ítem a la lista
        wish_list.append(new_item)
        redis_client.set(redis_key, json.dumps(wish_list))
        print("✅ Lista actualizada guardada en Redis.")

        # 💾 Guardar en MySQL si es necesario
        # 💾 Consultar o crear la wish_list en MySQL
        wish_list_q = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if isinstance(wish_list, str):  # Si es string, convertirlo a lista
            try:
                wish_list = json.loads(wish_list)
            except json.JSONDecodeError:
                print("⚠️ Error: wish_list ya estaba mal serializado antes de MySQL.")
                return jsonify({"error": "Error interno"}), 500

        if wish_list_q:
            # Si la lista ya existe en la base de datos, actualizarla
            wish_list_q.wish_items = wish_list # Serializar correctamente antes de guardar
        else:
            # Si no existe, crear una nueva entrada en la base de datos
            wish_list_q = WishList(user_id=user_q.id, domain_id=domain_q.id, wish_items=wish_list)
            db.session.add(wish_list_q)

        db.session.commit()
        print("✅ Lista guardada en MySQL correctamente.")



        return jsonify({"message": "Ítem añadido correctamente", "wish_list": wish_list}), 201

    except Exception as e:
        print(f"❌ Error en add_to_cart: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500







# def chat():
#     domain_name = request.args.get('domain', '')  # Obtener el dominio desde la URL
    
#     if domain_name not in ['Cooking', 'Fashion', 'Fitness']:
#         return "Dominio no válido", 400  # Validar el dominio

#     # Almacenar el dominio seleccionado en la sesión
#     session['selected_domain'] = domain_name

#     # Obtener el dominio desde la base de datos
#     domain = Domain.query.filter_by(domain_name=domain_name).first()
#     user_id = User.query.filter_by(provider_id=session['provider_id']).first()

#     if not domain:
#         return "Dominio no encontrado", 404

#     # Buscar el inventario del usuario en ese dominio
#     inventory = Inventory.query.filter_by(user_id=user_id, domain_id=domain.id).first()

#     # Extraer los ítems del inventario (si existe)
#     items = json.loads(inventory.items) if inventory else []
#     print(items)

#     # Renderizar el chatbot pasando el dominio y los ítems
#     return render_template('chat.html', domain=domain_name, items=items)




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
