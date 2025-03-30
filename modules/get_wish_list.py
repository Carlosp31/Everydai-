import json
from flask import Flask, session, jsonify
from models import User, Domain, WishList
from database import redis_client
from flask_mail import Message
from flask import current_app
from email_validator import validate_email, EmailNotValidError
import json
from flask_mail import Mail
app = Flask(__name__) 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'everydaiun@gmail.com'
app.config['MAIL_PASSWORD'] = 'JUANTRO23'
app.config['MAIL_DEFAULT_SENDER'] = 'everydaiun@gmail.com'

mail = Mail(app)
def get_wish_list_from_redis():
    """Obtiene la lista de deseos del usuario autenticado desde Redis o MySQL."""
    
    if 'provider_id' not in session or 'selected_domain' not in session:
        return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

    user_q = User.query.filter_by(provider_id=session['provider_id']).first()
    domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

    if not user_q or not domain_q:
        return jsonify({"error": "Usuario o dominio no encontrado"}), 404

    redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"
    items_json = redis_client.get(redis_key)

    if items_json:
        try:
            wish_list = json.loads(items_json)  # 🔵 Primero decodificamos

            if isinstance(wish_list, str):  # 🔵 Si sigue siendo string, volvemos a decodificar
                wish_list = json.loads(wish_list)

        except json.JSONDecodeError:
            return jsonify({"error": "Error al decodificar la lista de deseos"}), 500
    else:
        wish_list = []

    return jsonify({"items": wish_list})  # 🔥 Ahora devuelve la lista limpia

def send_wish_list_email():
    """Envía la lista de deseos del usuario autenticado por correo electrónico."""
    
    if 'provider_id' not in session or 'selected_domain' not in session:
        return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

    user_q = User.query.filter_by(provider_id=session['provider_id']).first()
    domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

    if not user_q or not domain_q:
        return jsonify({"error": "Usuario o dominio no encontrado"}), 404

    if not user_q.email:
        return jsonify({"error": "El usuario no tiene un correo registrado"}), 400

    # Validar correo electrónico
    try:
        validate_email(user_q.email, check_deliverability=True)
    except EmailNotValidError:
        return jsonify({"error": "Correo electrónico no válido"}), 400

    redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"
    items_json = redis_client.get(redis_key)

    if items_json:
        try:
            wish_list = json.loads(items_json)

            if isinstance(wish_list, str):
                wish_list = json.loads(wish_list)
        except json.JSONDecodeError:
            return jsonify({"error": "Error al decodificar la lista de deseos"}), 500
    else:
        wish_list = []

    if not wish_list:
        return jsonify({"message": "La lista de deseos está vacía"}), 200

    # Crear el mensaje de correo
    subject = "Tu lista de deseos"
    body = "Aquí está tu lista de deseos:\n\n" + "\n".join(f"- {item}" for item in wish_list)
    msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user_q.email])
    msg.body = body

    try:
        mail.send(msg)
        return jsonify({"message": "Lista de deseos enviada con éxito"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al enviar el correo: {str(e)}"}), 500


