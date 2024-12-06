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
import platform
import requests
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
                prompt = "Actúa como un maestro culinario e identifica los ingredientes en la imagen. Solo quiero la lista de ingredientes, trata de no extender mucho la conversación. Sé conciso y damelo en formato de lista."
            elif selected_model == 'fashion':
                prompt = "Actúa como asesor de moda y comenta la vestimenta o prendas presentes en la imagen. Solo quiero la lista de prendas, trata de no extender mucho la conversación. Sé conciso y damelo en formato de lista."
            elif selected_model == 'gym':
                prompt = "Actúa como un entrenador personal e identifica los elementos de gimnasio en la imagen. Solo quiero la lista de elementos, trata de no extender mucho la conversación. Sé conciso y damelo en formato de lista."
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


            if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                parts = getattr(candidate.content, 'parts', [])
                if parts and len(parts) > 0:
                    generated_text = parts[0].text  # Extraer el texto desde 'parts'
                    print(f"Identifación de elementos en la imagen: {generated_text}")
                    # Determinar el sistema operativo
                    os_type = platform.system()
                    # Llama al endpoint /chat con el texto generado
                    chat_payload = {
                        "message": generated_text,
                        "model": selected_model
                    }
                    # Configurar URL según el sistema operativo
                    if os_type == "Windows":
                        url = 'http://127.0.0.1:80/chat'
                    elif os_type == "Linux":
                        url = 'http://127.0.0.1:5000/chat'
                    else:
                        raise OSError(f"Sistema operativo no soportado: {os_type}")
                    chat_response = requests.post(
                        url,
                        json=chat_payload,
                        timeout=20
                    )
                    chat_response_json = chat_response.json()

                    if chat_response.status_code == 200:
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

