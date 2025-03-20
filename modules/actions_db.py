import redis
from database import db
from models import User, Domain, Inventory, WishList, UserPreference
import json
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session
from app import redis_client 

    
def add_to_cart():
    """Añade un producto a la lista de deseos en Redis y lo guarda en MySQL."""

    print("🔵 Iniciando add_to_cart...")

    try:
        # 🛑 Verificar sesión del usuario
        if 'provider_id' not in session or 'selected_domain' not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session['provider_id']).first()
        domain_q = Domain.query.filter_by(domain_name=session['selected_domain']).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 📩 Recibir datos
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        if not data or "item" not in data or "name" not in data["item"] or "price" not in data["item"]:
            return jsonify({"error": "Datos inválidos"}), 400

        new_item = {
            "name": data["item"]["name"],
            "price": data["item"]["price"]
        }

        # 🔑 Clave en Redis
        redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"

        # 📜 Obtener la lista de deseos desde Redis
        wish_list_json = redis_client.get(redis_key)
        print(f"📜 Lista en Redis (raw): {wish_list_json}")

        wish_list = []
        if wish_list_json:
            try:
                wish_list = json.loads(wish_list_json)
                print(f"✅ Lista deserializada: {wish_list}")
            except json.JSONDecodeError:
                print("⚠️ Error: No se pudo decodificar wish_list desde JSON")
                wish_list = []

        # 🛑 Evitar duplicados
        if any(item["name"] == new_item["name"] for item in wish_list):
            return jsonify({"message": "El ítem ya está en la lista de deseos"}), 200

        # 🆕 Agregar el nuevo ítem a la lista
        wish_list.append(new_item)
        redis_client.set(redis_key, json.dumps(wish_list))
        print("✅ Lista actualizada guardada en Redis.")

        # 💾 Guardar en MySQL si es necesario
        # 💾 Consultar o crear la wish_list en MySQL
        wish_list_q = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if isinstance(wish_list, str):  # Si es string, convertirlo a lista
            try:
                wish_list = json.loads(wish_list)
            except json.JSONDecodeError:
                print("⚠️ Error: wish_list ya estaba mal serializado antes de MySQL.")
                return jsonify({"error": "Error interno"}), 500

        if wish_list_q:
            # Si la lista ya existe en la base de datos, actualizarla
            wish_list_q.wish_items = wish_list # Serializar correctamente antes de guardar
        else:
            # Si no existe, crear una nueva entrada en la base de datos
            wish_list_q = WishList(user_id=user_q.id, domain_id=domain_q.id, wish_items=wish_list)
            db.session.add(wish_list_q)

        db.session.commit()
        print("✅ Lista guardada en MySQL correctamente.")



        return jsonify({"message": "Ítem añadido correctamente", "wish_list": wish_list}), 201

    except Exception as e:
        print(f"❌ Error en add_to_cart: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500