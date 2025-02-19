from ultralytics import YOLO  # Importa la librería YOLOv8
import torch
import io
import base64
import numpy as np
import cv2
import torch
from PIL import Image
from flask import  request, jsonify
def decode_image(data):
    # Decodificar imagen base64
    img_data = base64.b64decode(data.split(',')[1])
    image = Image.open(io.BytesIO(img_data))
    return np.array(image)


    
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def process_frame():
    data = request.json
    image_data = data['image']
    domain = data['domain']
    if domain == "fashion":
        cv_model = YOLO('static/real_models/fashion2.pt')
        class_names_dict = {
            0: 'belt',  
            1: 'blazer', 
            2: 'dress ' ,
            3: 'flannel' , 
            4: 'glasses'  ,
            5: 'hat'  ,
            6: 'jacket',  
            7: 'pants ' ,
            8: 'scarf'  ,
            9: 'shoes'  ,
            10: 'short'  ,
            11: 'skirt'  ,
            12: 'sweater' , 
            13: 't-shirt'  ,
            14: 'watch'  
        }

    if domain == "culinary":
        cv_model = YOLO('static/real_models/culinary.pt')  # Ruta del modelo en tu carpeta
        class_names_dict = {
            0: 'bay_leaves',
            1: 'beef',
            2: 'bell_pepper',
            3: 'cabbage',
            4: 'carrot',
            5: 'cauliflower',
            6: 'chicken',
            7: 'chickpeas',
            8: 'coriander',
            9: 'cucumber',
            10: 'egg',
            11: 'eggplant',
            12: 'fish',
            13: 'garlic',
            14: 'ginger',
            15: 'green_chili_pepper',
            16: 'green_onion',
            17: 'kumquat',
            18: 'lemon',
            19: 'mutton',
            20: 'okra',
            21: 'onion',
            22: 'pork',
            23: 'potato',
            24: 'pumpkin',
            25: 'radish',
            26: 'salt',
            27: 'shrimp',
            28: 'small_pepper',
            29: 'tofu',
            30: 'tomato',
            31: 'turmeric'
        }
    # Decodificar la imagen
    image = decode_image(image_data)

    # Realizar la predicción usando el modelo YOLOv8
    results = cv_model(image)  # Esto es la inferencia, puedes enviar la imagen directamente

    # Extraer las cajas delimitadoras, clases y confidencias
    boxes = []
    for result in results:
        for box in result.boxes:
            # Obtener las coordenadas (xywh), confianza y class_id
            x_center, y_center, width, height = box.xywh[0]
            confidence = box.conf[0]  # Confianza
            class_id = int(box.cls[0])  # ID de clase (convierte a entero)
            if confidence > 0.5:  # Umbral de confianza
                class_name = class_names_dict.get(class_id, 'unknown')  # Obtener el nombre de la clase usando el ID
                boxes.append({
                    'x': int(x_center - width / 2),
                    'y': int(y_center - height / 2),
                    'width': int(width),
                    'height': int(height),
                    'confidence': float(confidence),
                    'class_id': class_id,
                    'class_name': class_name
                })

    return jsonify({'bounding_boxes': boxes})