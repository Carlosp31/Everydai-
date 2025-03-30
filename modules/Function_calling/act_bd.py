import redis
from database import db
from models import User, Domain, Inventory, WishList, UserPreference
import json
from flask import Flask, render_template, request, jsonify, redirect, send_file, url_for, session
from app import redis_client 
import json

def almacenar_items(ingredientes):
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



def almacenar_receta(data):
    """Almacena una receta con sus ingredientes en user_preferences."""

    print(f"🔵 Iniciando almacenar_receta con datos: {data}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # ✅ Extraer datos del JSON recibido
        nombre_receta = data.get("nombre_receta", "").strip()
        ingredientes = data.get("ingredientes", [])

        if not nombre_receta:
            return jsonify({"error": "El nombre de la receta es obligatorio"}), 400

        if not isinstance(ingredientes, list) or not ingredientes:
            return jsonify({"error": "Debe proporcionar una lista de ingredientes"}), 400

        ingredientes = list(set(ingredientes))  # Eliminar duplicados

        # 🔑 Clave para Redis
        redis_key_prefs = f"user:{user_q.id}:domain:{domain_q.id}:preferences"

        # 🗄️ Cargar preferencias desde Redis o DB
        prefs_json = redis_client.get(redis_key_prefs)
        user_prefs = json.loads(prefs_json) if prefs_json else {}

        # 📝 Agregar receta a preferencias
        if "recetas" not in user_prefs:
            user_prefs["recetas"] = {}

        user_prefs["recetas"][nombre_receta] = ingredientes

        # Guardar en Redis
        redis_client.set(redis_key_prefs, json.dumps(user_prefs))
        print(f"✅ Receta '{nombre_receta}' almacenada en Redis.")

                # 🔍 Buscar en la base de datos
        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales desde la BD
            current_prefs = user_pref.preference  # SQLAlchemy ya maneja JSON como dict
            print(f"📦 Preferencias actuales antes de modificar: {current_prefs}")

            if not isinstance(current_prefs, dict):
                current_prefs = json.loads(current_prefs)  # Asegurar que sea un diccionario
                print(f"🔄 Convertido a dict: {current_prefs}")

            if "recetas" not in current_prefs:
                current_prefs["recetas"] = {}

            # Agregar nueva receta sin borrar las anteriores
            print(f"➕ Agregando receta '{nombre_receta}' con ingredientes: {ingredientes}")
            current_prefs["recetas"][nombre_receta] = ingredientes

            user_pref.preference = json.dumps(current_prefs) 
            print(f"📌 Preferencias después de agregar receta: {user_pref.preference}")

        else:
            # Crear nueva entrada con la receta
            print(f"🆕 Creando nueva preferencia para user_id={user_q.id}, domain_id={domain_q.id}")
            new_pref = UserPreference(
                user_id=user_q.id,
                domain_id=domain_q.id,
                preference={"recetas": {nombre_receta: ingredientes}}  # Guardar como dict
            )
            db.session.add(new_pref)

        # Guardar en la base de datos
        db.session.commit()
        print("✅ Receta almacenada en MySQL.")


        return jsonify({"message": f"Receta '{nombre_receta}' guardada correctamente."}), 200

    except Exception as e:
        print(f"⚠️ Error en almacenar_receta: {e}")
        return jsonify({"error": str(e)}), 500
