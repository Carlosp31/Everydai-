import redis
from database import db
from models import User, Domain, Inventory, WishList, UserPreference
import json
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session
from app import redis_client 
import json

def almacenar_ingredientes(ingredientes):
    """Almacena ingredientes en la lista de inventario del usuario."""

    print(f"🔵 Iniciando almacenar_ingredientes con ingredientes: {ingredientes}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404
            # Intentar obtener los items de inventario desde Redis primero
        redis_key_inventory= f"user:{user_q.id}:domain:{domain_q.id}:inventory"
        inventory_json = redis_client.get(redis_key_inventory)

        if inventory_json:
            # Si los items están en Redis, los cargamos
            items = json.loads(inventory_json)  # Convertir el JSON almacenado en lista
            print("Cargando inventario desde Redis:", items)
        else:
            # Si no están en Redis, los consultamos en la base de datos
            inventory = Inventory.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
            items = inventory.items if inventory else []

            # Guardamos en Redis para futuras consultas
            redis_client.set(redis_key_inventory, json.dumps(items))
            print("Cargando inventario desde MySQL y guardando en Redis:", items)

        if inventory_json:
            # Si los items están en Redis, los cargamos como lista
            items = json.loads(inventory_json)  # Convertir de JSON a lista

            if not isinstance(items, list):  # Verificar que realmente es una lista
                items = []

            print("Cargando inventario desde Redis:", items)
        else:
            items = []  # Si no hay datos en Redis, inicializar una lista vacía

        # 📦 Agregar los nuevos ingredientes y eliminar duplicados
        items.extend(ingredientes)
        items = list(set(items))  # Eliminar duplicados

        # Guardar la lista actualizada en Redis
        redis_client.set(redis_key_inventory, json.dumps(items))
        print("✅ Lista actualizada guardada en Redis.")
        print(items)

        # 🔍 Buscar si el usuario ya tiene un inventario
        inventory = Inventory.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if inventory:
            # ✅ Verificar si "inventory.items" es una cadena JSON y convertirla a lista
            if isinstance(inventory.items, str):
                try:
                    current_items = json.loads(inventory.items)  # Convertir JSON a lista
                except json.JSONDecodeError:
                    current_items = []  # En caso de error, inicializar lista vacía
            else:
                current_items = inventory.items if inventory.items else []

            # 📦 Agregar nuevos ingredientes sin duplicados
            current_items.extend(ingredientes)
            inventory.items =(list(set(current_items)))  # Convertir lista a JSON

        else:
            # 🆕 Crear nuevo inventario
            new_inventory = Inventory(
                user_id=user_q.id,
                domain_id=domain_q.id,
                items=(ingredientes)  # Guardar como JSON
            )
            db.session.add(new_inventory)

        # 💾 Guardar cambios en la base de datos
        db.session.commit()

        return items
    except Exception as e:
        print(f"❌ Error en almacenar_ingredientes: {e}")
        return items

        # # 🔍 Buscar si el usuario ya tiene un inventario
        # inventory = Inventory.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        # if inventory:
        #     # ✅ Verificar si items ya es una lista
        #     if isinstance(inventory.items, str):
        #         current_items = json.loads(inventory.items)  # Convertir a lista si es string
        #     else:
        #         current_items = inventory.items  # Ya es una lista

        #     # 📦 Agregar nuevos ingredientes sin duplicados
        #     current_items.extend(ingredientes)
        #     inventory.items = list(set(current_items))  # Eliminar duplicados
        # else:
        #     # 🆕 Crear nuevo inventario
        #     new_inventory = Inventory(
        #         user_id=user_q.id,
        #         domain_id=domain_q.id,
        #         items=ingredientes  # Ya está en el formato correcto
        #     )
        #     db.session.add(new_inventory)

        # # 💾 Guardar cambios en la base de datos
        # db.session.commit()


