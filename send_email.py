from flask_mail import Message
from flask import current_app
from app import mail  # Asegúrate que esta instancia de mail es importable

def send_wishlist_email(user_email, wish_list):
    try:
        items_text = "\n".join(
            [f"- {item['name']}: {item['quantity']}" for item in wish_list]
        )
        body = f"Hola,\n\nEsta es tu lista de compras:\n\n{items_text}\n\nGracias por usar nuestra app."

        msg = Message(subject="Tu Lista de Compras",
                      recipients=[user_email],
                      body=body)

        with current_app.app_context():
            mail.send(msg)
        return True

    except Exception as e:
        print("Error enviando correo:", e)
        return False
