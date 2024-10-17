
import os
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from werkzeug.utils import secure_filename
from PIL import Image
import serpapi
from dotenv import load_dotenv
import requests

# Cargar las variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)

# Cargar las variables de entorno
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

##############---DEF --- CALL FUNCTION -- #######################################3
# Función para buscar recetas basadas en el input del usuario
def buscar_recetas(input_usuario: str) -> str:
    """
    Procesa el input del usuario solo y exclusivamente si este te pide que le sugieras algún tutorial,
    una guía, en links o videos. En ese caso, devuelve una sugerencia de búsqueda de recetas basada 
    en el análisis semántico del input.

    Args:
        input_usuario (str): El mensaje del usuario solicitando una receta.

    Returns:
        str: La sugerencia de búsqueda en una frase procesada para la búsqueda.
    """
    # Convertir el input a minúsculas para evitar problemas de mayúsculas
    input_usuario = input_usuario.lower()

    # Verbos que indican que el usuario está buscando un tutorial, guía o video
    verbos_busqueda = ["busca", "sugiéreme", "muéstrame", "recomiéndame", "necesito", "quiero", "enséñame", "dame", "tutorial", "guía", "link", "video"]

    # Palabras clave relacionadas con recetas
    palabras_receta = ["receta", "cómo hacer", "paso a paso", "plato", "comida", "preparación", "cocinar"]

    # Verificar si el input del usuario contiene verbos relacionados con tutoriales, guías o videos
    if any(verbo in input_usuario for verbo in verbos_busqueda) and any(palabra in input_usuario for palabra in palabras_receta):
        # Separar el input en palabras para encontrar el posible tipo de comida
        palabras = input_usuario.split()

        # Intentar identificar el ingrediente o tipo de comida a partir del input
        for i, palabra in enumerate(palabras):
            if palabra in palabras_receta:  # Si encontramos palabras relacionadas con recetas
                # Devolver la palabra siguiente como sugerencia
                if i + 1 < len(palabras):
                    return palabras[i + 1]  # Retornar la palabra que sigue como sugerencia de búsqueda

        # Si no se encuentra un tipo de comida específico, devolver búsqueda genérica
        return "recetas variadas"

    # Si no se trata de una búsqueda de tutorial, guía o video, devolver una cadena vacía
    return ""


def serpp(input_usuario, model_type):
    tool_config = {
        "function_calling_config": {
            "mode": "AUTO",  # Dejamos AUTO, pero sin depender de la llamada automática a la función
        }
    }

    # Definir el modelo con la función y la configuración de tool_config
    model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                                  tools=[buscar_recetas],
                                  tool_config=tool_config)

    # Iniciar un chat
    chat = model.start_chat()

    # Enviar un mensaje en español directamente sin esperar que "AUTO" maneje las funciones
    print(f"Entrada del usuario: {input_usuario}")

    # Llamar manualmente a buscar_recetas para verificar si la entrada amerita una búsqueda
    sugerencia_busqueda = buscar_recetas(input_usuario)

    # Verificar si hay una sugerencia válida de búsqueda
    if sugerencia_busqueda:
        print(f"Buscas recetas de {sugerencia_busqueda}")

        # Aquí pasamos el tipo de modelo ("culinary", "fashion", etc.), en lugar del objeto model
        recetas = buscar_resultados_en_serpapi(sugerencia_busqueda, model_type)
        print(f"Recetas: {recetas}")
        return recetas
    else:
        print("El input no parece ser una solicitud de recetas.")
        return None

# Ajuste de la función para obtener resultados en SerpAPI
def buscar_resultados_en_serpapi(query, model_type):
    try:
        # Ajusta la consulta según el tipo de modelo
        if model_type == 'culinary':
            search_query = f"Recetas con {query}"
        elif model_type == 'fashion':
            search_query = f"Outfits with {query}"
        elif model_type == 'gym':
            search_query = f"Gym exercises using {query}"
        else:
            return f"Modelo {model_type} no soportado."

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
        if model_type == 'culinary':
            return result.get("recipes_results", [])
        else:
            return result.get("organic_results", [])  # Ajusta esto según las necesidades del modelo
    except Exception as e:
        return f"Error al buscar en SerpAPI: {e}"



###########################################################3#######3#######3#####

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

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    selected_model = request.json['model']

    

    # Selección del modelo basado en la entrada del usuario
    if selected_model == 'culinary':
        model = model_culinary
        history = [
            {"role": "user", "parts": "Eres un profesor de culinaria. Recibe una lista de ingredientes y proporciona una lista de pasos para realizar una receta solo con esos ingredientes."},
            {"role": "model", "parts": "Bien, dime los ingredientes que tienes y te daré el paso a paso, como si fueras principiantes, para preparar una receta."}
        ]
    elif selected_model == 'fashion':
        model = model_fashion
        history = [
            {"role": "user", "parts": "Eres un asesor de moda. Recibes una lista de prendas de ropa y recomiendas combinaciones basadas en esas prendas."},
            {"role": "model", "parts": "Entendido, por favor indícame las prendas y te sugeriré combinaciones."}
        ]
    elif selected_model == 'Gym':
        model = model_gym
        history = [
            {"role": "user", "parts": "Eres un entrenador personal. Recibe una lista de elementos de gimnasio y sugiere ejercicios que se pueden realizar con esos elementos. Además, si el usuario lo desea, sugiere ejercicios para trabajar grupos musculares específicos."},
            {"role": "model", "parts": "Dime qué elementos de gimnasio tienes, y te sugeriré ejercicios para realizar con ellos."}
        ]
    else:
        return jsonify({'response': 'Modelo no encontrado.'}), 400

    # Iniciar chat con el modelo seleccionado
    chat = model.start_chat(history=history)
    
    # Enviar mensaje al modelo y recibir respuesta
    response = chat.send_message(
        user_input,
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            stop_sequences=["x"],
            max_output_tokens=50,
            temperature=0.7
        )
    )
    
    respuesta_texto = response.text  # Obtener la respuesta en texto del modelo

    # Buscar recetas en SerpAPI (si es necesario)
    
    recetas = serpp(user_input, selected_model)

    # Devolver la respuesta escrita y la de SerpAPI
    return jsonify({
        'text_response': respuesta_texto,
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




@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'response': 'No image uploaded.'}), 400

    image = request.files['image']
    
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)  # Guarda la imagen en la carpeta de uploads
        image = Image.open(image_path)

        try:
            # Procesa la imagen con el modelo de imágenes
            selected_model = request.form['model']  # Obtener el modelo seleccionado
            print(selected_model)
            if selected_model == 'culinary':
                prompt = "Actúa como un maestro culinario e identifica los ingredientes en la imagen. "
            elif selected_model == 'fashion':
                prompt = "Actúa como asesor de moda y comenta la vestimenta o prendas presentes en la imagen."
            elif selected_model == 'Gym':
                prompt = "Actúa como un entrenador personal e identifica los elementos de gimnasio en la imagen. "
            else:
                return jsonify({'response': 'Modelo no válido.'}), 400

            # Generar contenido a partir de la imagen
            response = model_img.generate_content(
                [
                    prompt,
                    image
                ],
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=["x"],
                    max_output_tokens=70,
                    temperature=0.7
                )
            )

            # Verificar si la respuesta contiene un resultado válido
            if response and hasattr(response, 'candidates') and response.candidates:
                return jsonify({'response': response.text})
            else:
                return jsonify({'response': 'Error: No se pudo procesar la imagen correctamente.'}), 500

        except Exception as e:
            return jsonify({'response': f'Error procesando la imagen: {e}'}), 500

    return jsonify({'response': 'Imagen no encontrada.'}), 404


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Crea la carpeta de uploads si no existe
    app.run(debug=True, port=3000)