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
client = serpapi.Client(api_key=SERPAPI_KEY)
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
 
# Then, we use the `stream` SDK helper 
# with the `EventHandler` class to create the Run 
# and stream the response.
####################################################

########################################################

def sintetizar_voz(texto, api_key):
    # Directorio temporal para guardar el archivo de audio
    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
    audio_path = os.path.join(temp_dir, "respuesta_audio.mp3")

    # Si el archivo ya existe, elimínalo antes de escribir uno nuevo
    if os.path.exists(audio_path):
        os.remove(audio_path)

    url = "https://api.elevenlabs.io/v1/text-to-speech/9BWtsMINqrJLrRacOk9x"  # Cambia YOUR_VOICE_ID por el ID de la voz que quieras usar
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json',
    }
    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 1
        }
    }

    # Solicitud a la API para sintetizar la voz
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # Guardar el archivo de audio en el directorio temporal
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return audio_path
    else:
        return None


CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
REDIRECT_URI = 'https://everydai.zapto.org/oauth2callback'


@app.route('/')
def dashboard():
    # Renderiza la página del dashboard donde el usuario selecciona un dominio
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




#######################################################
# Crear el cliente de OpenAI y el asistente de culinary de manera global

client = OpenAI()

# Definir variables globales


##################### Culinario #################################
global assistant_culinary
assistant_culinary = client.beta.assistants.create(
    name="Cooking",
    instructions="""El modelo debe actuar como un profesor de culinaria. Recibe una lista de ingredientes y debe proporcionarle al usuario una lista de pasos y guiarlo paso a paso para realizar una receta. 
                    Antes, indícale al usuario la receta que le vas a sugerir y pregúntale si le gustaría esa u otra. Si dice que sí, ve indicando paso por paso, esperando a que el usuario termine un paso y quiera ir al siguiente. 
                    Solo puedes sugerir recetas con los ingredientes que recibes en la lista, únicamente esos. A menos que el usuario te pida que le sugieras una receta y que él conseguirá los ingredientes. 
                    Tu dominio es solo la culinaria.""",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o-mini",
)

# Crear el thread global para culinary (esto solo lo inicializamos una vez)
global thread_culinary
thread_culinary = client.beta.threads.create()
#################################################################
##################### Fashion #################################
# Definir variables globales para el dominio de moda
global assistant_fashion
assistant_fashion = client.beta.assistants.create(
    name="Fashion",
    instructions="""Eres un asesor de moda. Recibes una lista de prendas de ropa y recomiendas combinaciones basadas en esas prendas. 
                    Tu dominio es solo la moda. Puedes sugerir atuendos para diferentes ocasiones y ayudar con la elección de ropa según las preferencias del usuario.""",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o-mini",
)

# Crear el thread global para fashion (esto solo lo inicializamos una vez)
global thread_fashion
thread_fashion = client.beta.threads.create()
###################### Gym #################################
global assistant_gym
assistant_gym= client.beta.assistants.create(
    name="gym",
    instructions="Eres un entrenador personal. Recibe una lista de elementos de gimnasio y sugiere ejercicios que se pueden realizar con esos elementos. Además, si el usuario lo desea, sugiere ejercicios para trabajar grupos musculares específicos.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o-mini",
)
global thread_gym
thread_gym = client.beta.threads.create()
#################################################################

####################################################
# Actualización: mensaje inicial en el chat
@app.route('/chat', methods=['POST'])
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
            assistant_id=assistant_culinary.id,
            instructions="""
                El modelo debe actuar como un profesor de culinaria. 
                Recibe una lista de ingredientes y debe proporcionarle al usuario una lista de pasos 
                y guiar al usuario para que efectúe la receta. 
                
                Antes, indicale al usuario la receta que le vas a sugerir 
                y preguntale si le gustaría esa u otra. 
                Si dice que sí, ve indicando paso por paso, esperando a que el usuario termine un paso 
                y quiera ir al siguiente; si dice que no, sugierele otra en base a los ingredientes que te habia mostrado.
                
                Solo puedes sugerir recetas con los ingredientes que recibiste en la lista, únicamente esos. 
                A menos que el usuario te pida que le sugieras una receta y que él conseguirá los ingredientes. 
                
                Tu dominio es solo la culinaria.
            """
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(thread_id=thread_culinary.id)

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
            assistant_id=assistant_fashion.id,
            instructions="Eres un asesor de moda. Recibes una lista de prendas de ropa y recomiendas combinaciones basadas en esas prendas. Tu dominio es solo la moda"
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
            assistant_id=assistant_gym.id,
            instructions="Eres un entrenador personal. Recibe una lista de elementos de gimnasio y sugiere ejercicios que se pueden realizar con esos elementos. Además, si el usuario lo desea, sugiere ejercicios para trabajar grupos musculares específicos. Tu dominio es solo el gym"
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
    print(f"Rxs:{respuesta_texto}")

    # Mensaje inicial al seleccionar el dominio
    mensaje_inicial = f"Hola, este es el dominio {session.get('selected_domain', 'desconocido')}"

    # Buscar recetas en SerpAPI (si es necesario)
    recetas = buscar_resultados_en_serpapi(user_input, selected_model)
    
    # Devolver la respuesta escrita, el mensaje inicial y la de SerpAPI
    return jsonify({
        'text_response': respuesta_texto,
        'mensaje_inicial': mensaje_inicial,
        'recipes': recetas
    })
@app.route('/synthesize-audio', methods=['POST'])
def synthesize_audio():
    text = request.json['text']
    audio_path = sintetizar_voz(text, ELEVENLABS_API_KEY)
    
    if audio_path:
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'Error al sintetizar la voz.'}), 500

def buscar_resultados_en_serpapi(query, model):
    try:
        # Ajusta la consulta según el modelo seleccionado
        if model == 'culinary':
            search_query = f"Recetas con {query}"
        elif model == 'fashion':
            search_query = f"Outfits with {query}"
        elif model == 'gym':
            search_query = f"Gym exercises using {query}"
        else:
            return f"Modelo {model} no soportado."

        # Realizar la búsqueda en SerpAPI con la consulta modificada
        result = client.search(
            q=search_query,
            engine="google",
            hl="es",
            gl="co",
            location_requested="Atlantico,Colombia",
                    location_used="Atlantico,Colombia"
        )

        # Para el modelo culinario, usamos 'recipes_results', pero para otros modelos
        # podrían necesitarse diferentes campos en los resultados
        if model == 'culinary':
            return result.get("recipes_results", [])
        else:
            return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'response': 'No image uploaded.'}), 400

    image = request.files['image']
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image.save(image_path)

        try:
            # Procesa la imagen con el modelo de imágenes
            selected_model = request.form.get('model', '').strip()
            if selected_model == 'culinary':
                prompt = "Actúa como un maestro culinario e identifica los ingredientes en la imagen. Solo quiero la lista de ingredientes, trata de no extender mucho la conversación. Sé conciso."
            elif selected_model == 'fashion':
                prompt = "Actúa como asesor de moda y comenta la vestimenta o prendas presentes en la imagen. Solo quiero la lista de prendas, trata de no extender mucho la conversación. Sé conciso."
            elif selected_model == 'gym':
                prompt = "Actúa como un entrenador personal e identifica los elementos de gimnasio en la imagen. Solo quiero la lista de elementos, trata de no extender mucho la conversación. Sé conciso."
            else:
                return jsonify({'response': 'Modelo no válido.'}), 400

            # Generar contenido a partir de la imagen
            response = model_img.generate_content(
                [
                    prompt,
                    Image.open(image_path)
                ],
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=["x"],
                    max_output_tokens=70,
                    temperature=0.7
                )
            )

            # Extraer el texto generado desde response
            print(f"Response completo: {response}")
            if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                parts = getattr(candidate.content, 'parts', [])
                if parts and len(parts) > 0:
                    generated_text = parts[0].text  # Extraer el texto desde 'parts'
                    print(f"Texto generado: {generated_text}")

                    # Llama al endpoint /chat con el texto generado
                    chat_payload = {
                        "message": generated_text,
                        "model": selected_model
                    }
                    chat_response = requests.post(
                        'http://127.0.0.1:80/chat',
                        json=chat_payload,
                        timeout=15
                    )
                    chat_response_json = chat_response.json()

                    if chat_response.status_code == 200:
                        print(f"chat_response.json(): {chat_response.json()}")
                        return jsonify({'response': chat_response_json.get('text_response')})
                    else:
                        return jsonify({'response': f'Error al procesar en /chat: {chat_response.text}'}), chat_response.status_code
                else:
                    return jsonify({'response': 'Error: No se encontró texto generado en la respuesta del modelo.'}), 500
            else:
                return jsonify({'response': 'Error: Respuesta del modelo incompleta o malformada.'}), 500

        except Exception as e:
            print(f"Error procesando la imagen: {e}")
            return jsonify({'response': f'Error procesando la imagen: {str(e)}'}), 500

    return jsonify({'response': 'Imagen no encontrada.'}), 404


# Iniciar la aplicación Flask con SSL
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=80)