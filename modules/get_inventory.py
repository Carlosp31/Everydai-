import json
from flask import session, jsonify
from models import User, Domain
from database import redis_client  # ✅ Importamos desde databases.py

def get_inventory_from_redis():
    if 'provider_id' not in session or 'selected_domain' not in session:
        return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

    user_q = User.query.filter_by(provider_id=session['provider_id']).first()
    domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

    if not user_q or not domain_q:
        return jsonify({"error": "Usuario o dominio no encontrado"}), 404

    redis_key = f"user:{user_q.id}:domain:{domain_q.id}:inventory"
    items_json = redis_client.get(redis_key)

    if items_json:
        try:
            items = json.loads(items_json)  # Convertir JSON a diccionario
        except json.JSONDecodeError as e:
            print("Error al decodificar JSON desde Redis:", e)
            items = {}
    else:
        items = {}

    return jsonify({"items": items}), 200  # ✅ Retornar un diccionario con "items"
