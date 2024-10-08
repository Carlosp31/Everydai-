from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from werkzeug.utils import secure_filename
import os
from PIL import Image

app = Flask(__name__)

# Inicializa el modelo generativo
model_img = genai.GenerativeModel("gemini-1.5-flash")
name = "domain4cookin"
model = genai.GenerativeModel(model_name=f'tunedModels/{name}')


# Configura la carpeta para almacenar las imágenes
UPLOAD_FOLDER = 'uploads'  # Asegúrate de crear esta carpeta
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    
    # Interacción con el modelo
    chat = model.start_chat(
    history=[
        {"role": "user", "parts": "el modelo debe actuar como un profesor de culinaria. Recibe una lista de ingredientes y debe proporcionarle al usuario una lista de pasos y guiar al usuario para que efectúe la receta. Solo puede sugerir recetas con los ingredientes que recibe en la lista, únicamente esos."},
        {"role": "model", "parts": "Bien. Dime los ingredientes, y te sugiriré ingrientes, y te daré los pasos, de acuerdo a ellos. Solo los ingredientes que me digas"},
    ]
)
    
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
            # Procesa la imagen
            response = model_img.generate_content(
                [
                    "Act as a culinary master and identify each ingredient you see in the image in detail. Be concise and just print the ingredient list. Do something like: The ingredients: (and insert the list)",
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
            return jsonify({'response': f'Error processing the image: {e}'}), 500

    return jsonify({'response': 'Image not found.'}), 404

if __name__== '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Crea la carpeta de uploads si no existe
    app.run(debug=True)
