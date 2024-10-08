from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
import os
from PIL import Image

app = Flask(__name__)

# Inicializa los modelos generativos
model_culinary = genai.GenerativeModel(model_name='tunedModels/domain4cooking')
model_fashion = genai.GenerativeModel(model_name='tunedModels/domain4fashion')
model_gym=genai.GenerativeModel(model_name='tunedModels/domain4gym')
model_img = genai.GenerativeModel("gemini-1.5-flash")

# Configura la carpeta para almacenar las imágenes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    selected_model = request.json['model']  # Recibe el modelo seleccionado desde el HTML

    # Selecciona el modelo basado en la entrada del usuario
    if selected_model == 'culinary':
        model = model_culinary
        history = [
            {"role": "user", "parts": "Eres un profesor de culinaria. Recibe una lista de ingredientes y proporciona una lista de pasos para realizar una receta solo con esos ingredientes."},
            {"role": "model", "parts": "Bien, dime los ingredientes que tienes y te daré los pasos para preparar una receta."}
        ]
    elif selected_model == 'fashion':
        model = model_fashion
        history = [
            {"role": "user", "parts": "Eres un asesor de moda. Recibes una lista de prendas de ropa y recomiendas combinaciones basadas en esas prendas."},
            {"role": "model", "parts": "Entendido, por favor indícame las prendas y te sugeriré combinaciones."}
        ]
    if selected_model == 'Gym':
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

    return jsonify({'response': respuesta_texto})

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
            response = model_img.generate_content(
                [
                    "Actúa como un maestro culinario e identifica los ingredientes en la imagen.",
                    image
                ],
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=["x"],
                    max_output_tokens=50,
                    temperature=0.7
                )
            )
            return jsonify({'response': response.text})
        except Exception as e:
            return jsonify({'response': f'Error procesando la imagen: {e}'}), 500

    return jsonify({'response': 'Imagen no encontrada.'}), 404

if __name__== '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Crea la carpeta de uploads si no existe
    app.run(debug=True)
