import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
import requests
import platform
import google.generativeai as genai
# Cargar las variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Cargar las variables de entorno
IMG_MODEL = os.getenv('IMG_MODEL')

# Configurar la clave API de SerpAPI
# Inicializar los modelos generativos con las variables de entorno
model_img = genai.GenerativeModel(IMG_MODEL)

# Configura la carpeta para almacenar las imágenes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
##################################################33

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
            if selected_model == 'Cooking':
                prompt = "Actúa como un maestro culinario e identifica los ingredientes en la imagen. Solo quiero la lista de ingredientes, trata de no extender mucho la conversación. Sé conciso y damelo en formato de lista."
            elif selected_model == 'fashion':
                prompt = "Actúa como asesor de moda y comenta la vestimenta o prendas presentes en la imagen. Solo quiero la lista de prendas, trata de no extender mucho la conversación. Sé conciso y damelo en formato de lista."
            elif selected_model == 'Fitness':
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
                        url = 'https://everydai.ddns.net:443/chat'
                    else:
                        raise OSError(f"Sistema operativo no soportado: {os_type}")
                    chat_response = requests.post(
                        url,
                        json=chat_payload,
                        timeout=60
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

