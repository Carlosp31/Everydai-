import os
from dotenv import load_dotenv
import requests
import tempfile

load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configurar la clave API de SerpAPI
# Configurar la carpeta para almacenar las imágenes
##################################################33



def sintetizar_voz(texto, api_key, modelo):
    # Detectar el sistema operativo y establecer el directorio temporal
    if os.name == "nt":  # Windows
        temp_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
    else:  # Linux/Mac
        temp_dir = tempfile.gettempdir()
    
    # Ruta del archivo de audio en el directorio temporal
    audio_path = os.path.join(temp_dir, "respuesta_audio.mp3")
    
    # Configuración de las voces
    voz_mujer = "9BWtsMINqrJLrRacOk9x"
    voz_hombre = "CwhRBWXzGAHq8TQ4Fs17"
    
    # Eliminar el archivo existente si ya está creado
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    # Selección del modelo de voz
    voz = voz_hombre if modelo == "Fitness" else voz_mujer
    
    # URL de la API
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voz
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