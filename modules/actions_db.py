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
    
def remove_from_wish_list():
    """Elimina un ítem (string) de la lista de deseos en Redis y MySQL."""

    print("🔴 Iniciando remove_from_wish_list...")

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

        if not data or "item_name" not in data:
            return jsonify({"error": "Datos inválidos"}), 400

        item_name = data["item_name"]

        # 🔑 Clave en Redis
        redis_key = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"

        # 📜 Obtener la lista desde Redis
        wish_list_json = redis_client.get(redis_key)
        wish_list = json.loads(wish_list_json) if wish_list_json else []

        # 🔍 Eliminar el ítem de la lista
        updated_wish_list = [item for item in wish_list if item != item_name]

        # 📝 Guardar lista actualizada en Redis
        redis_client.set(redis_key, json.dumps(updated_wish_list))
        print(f"🗑️ Elemento '{item_name}' eliminado de Redis.")

        # 🔍 Eliminar también en MySQL
        wishlist_entry = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if not wishlist_entry:
            return jsonify({"error": "Lista de deseos no encontrada"}), 404

        # Asegurarse de tener una lista válida desde la BD
        if isinstance(wishlist_entry.wish_items, str):
            try:
                wish_items = json.loads(wishlist_entry.wish_items)
            except json.JSONDecodeError:
                return jsonify({"error": "Error al decodificar la lista de deseos"}), 500
        elif isinstance(wishlist_entry.wish_items, list):
            wish_items = wishlist_entry.wish_items
        else:
            return jsonify({"error": "Formato inválido en wish_items"}), 500

        # Eliminar el ítem si existe
        updated_wish_items = [item for item in wish_items if item != item_name]

        if len(updated_wish_items) == len(wish_items):
            return jsonify({"error": "El ítem no se encontró en la lista"}), 404

        # Guardar en MySQL
        wishlist_entry.wish_items = updated_wish_items
        db.session.commit()
        print(f"🗑️ Elemento '{item_name}' eliminado de MySQL.")

        return jsonify({"message": "Elemento eliminado correctamente"}), 200

    except Exception as e:
        print(f"❌ Error en remove_from_wish_list: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


def remove_from_inventory():
    """Elimina un ingrediente del inventario en Redis y MySQL."""

    print("🔴 Iniciando remove_from_inventory...")

    try:
        # 📩 Recibir datos del frontend
        data = request.get_json()
        print(f"📩 Datos recibidos: {data}")

        if not data or "name" not in data or "domain_name" not in data:
            return jsonify({"error": "Datos inválidos"}), 400

        item_name = data["name"]  # ✅ Nombre del ingrediente
        domain_name = data["domain_name"]  # ✅ Dominio

        # 🛑 Verificar sesión del usuario
        if 'provider_id' not in session:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # 🔍 Buscar usuario y dominio
        user_q = User.query.filter_by(provider_id=session['provider_id']).first()
        domain_q = Domain.query.filter_by(domain_name=domain_name).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔑 Clave en Redis
        redis_key = f"user:{user_q.id}:domain:{domain_q.id}:inventory"

        # 📜 Obtener el inventario desde Redis
        inventory_json = redis_client.get(redis_key)
        inventory = json.loads(inventory_json) if inventory_json else []

        # 🚨 Verificar si el ítem existe en el inventario
        if item_name not in inventory:
            return jsonify({"error": "El ítem no está en el inventario"}), 404

        # ❌ Eliminar el ítem del inventario
        inventory.remove(item_name)

        # 🔄 Guardar los cambios en Redis
        redis_client.set(redis_key, json.dumps(inventory))
        print(f"✅ Inventario actualizado: {inventory}")
        # 🔍 Buscar el inventario del usuario en este dominio
        inventory = Inventory.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if not inventory:
            return jsonify({"error": "Inventario no encontrado"}), 404

        # 📌 Verificar si `items` es una cadena JSON o una lista
        if isinstance(inventory.items, str):
            try:
                current_items = json.loads(inventory.items)  # Convertir de JSON a lista
            except json.JSONDecodeError:
                return jsonify({"error": "Error al decodificar el inventario"}), 500
        elif isinstance(inventory.items, list):
            current_items = inventory.items  # Ya es una lista
        else:
            return jsonify({"error": "Formato inválido en items"}), 500

        # ❌ Intentar eliminar el ítem
        if item_name not in current_items:
            return jsonify({"error": "El ítem no se encontró en el inventario"}), 404

        current_items.remove(item_name)  # Eliminar el ítem

        # 🔄 Guardar la lista actualizada en MySQL
        # Actualizar la lista en MySQL
        inventory.items = (list(set(current_items)))   # Evita caracteres escapados
        db.session.add(inventory)  # Asegurar que SQLAlchemy registra el cambio
        db.session.commit()  # Guardar en la base de datos

        print(f"✅ Inventario actualizado en MySQL: {current_items}")

        return jsonify({"success": True, "updated_inventory": current_items}), 200

    except Exception as e:
        print(f"⚠️ Error en remove_from_inventory: {str(e)}")
        db.session.rollback()  # 🔄 Revertir en caso de error
        return jsonify({"error": "Error interno del servidor"}), 500
