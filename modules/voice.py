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


def sintetizar_voz(texto, api_key, modelo):
    # Directorio temporal para guardar el archivo de audio
    temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
    audio_path = os.path.join(temp_dir, "respuesta_audio.mp3")
    voz_mujer = "9BWtsMINqrJLrRacOk9x"
    voz_hombre = "CwhRBWXzGAHq8TQ4Fs17"
    # Si el archivo ya existe, elimínalo antes de escribir uno nuevo
    if os.path.exists(audio_path):
        os.remove(audio_path)
    if (modelo == "gym"): 
     voz = voz_hombre
    else:
     voz = voz_mujer
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voz   # Cambia YOUR_VOICE_ID por el ID de la voz que quieras usar
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