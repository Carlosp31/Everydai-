import json
from flask import session, jsonify
from models import User, Domain, WishList
from database import redis_client

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
            items = json.loads(items_json)  # Convertir JSON almacenado en Redis a lista
            print("Cargando desde Redis:", items)
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON desde Redis:", e)
            items = []
    else:
        # Si no están en Redis, consultarlos en la base de datos
        wish_list_entry = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        items = wish_list_entry.wish_items if wish_list_entry and wish_list_entry.wish_items else []

        # Guardar en Redis para futuras consultas
        redis_client.set(redis_key, json.dumps(items))
        print("Cargando desde MySQL y guardando en Redis:", items)

    return jsonify({"items": items}), 200



