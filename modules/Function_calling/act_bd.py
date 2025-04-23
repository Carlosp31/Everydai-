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
        ingredientes = data.get("ingredientes_receta", [])

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

            user_pref.preference = json.dumps(current_prefs, ensure_ascii=False)
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
    
import json

def buscar_receta():
    """Busca y retorna las recetas almacenadas por el usuario junto con sus ingredientes."""

    print(f"🔵 Iniciando buscar_receta")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference  
            print(f"📦 Preferencias actuales antes de procesar: {current_prefs}")

            # Asegurar que sea un diccionario y no una cadena JSON
            if isinstance(current_prefs, str):  
                current_prefs = json.loads(current_prefs)  

            # Obtener las recetas completas con ingredientes
            recetas_completas = current_prefs.get("recetas", {})

            return recetas_completas

        return {"recetas_almacenadas": {}}  # Si no hay recetas guardadas

    except Exception as e:
        print(f"⚠️ Error en buscar_receta: {e}")
        return jsonify({"error": str(e)}), 500

def borrar_receta(nombre_receta):
    """Elimina una receta almacenada por el usuario."""

    print(f"🔴 Iniciando borrar_receta: {nombre_receta}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference  
            print(f"📦 Preferencias actuales antes de procesar: {current_prefs}")

            # Asegurar que sea un diccionario y no una cadena JSON
            if isinstance(current_prefs, str):  
                current_prefs = json.loads(current_prefs)

            # Verificar si la receta existe
            recetas = current_prefs.get("recetas", {})
            if nombre_receta in recetas:
                del recetas[nombre_receta]  # Eliminar la receta
                user_pref.preference = json.dumps(current_prefs)  # Guardar cambios
                db.session.commit()
                print(f"✅ Receta '{nombre_receta}' eliminada con éxito.")
                return jsonify({"message": f"Receta '{nombre_receta}' eliminada exitosamente."}), 200
            else:
                return jsonify({"error": "Receta no encontrada"}), 404

        return jsonify({"error": "No hay recetas almacenadas"}), 404

    except Exception as e:
        print(f"⚠️ Error en borrar_receta: {e}")
        return jsonify({"error": str(e)}), 500

def almacenar_outfit(data):
    """Almacena un outfit con sus prendas asociadas y la ocasión en user_preferences."""

    print(f"🔵 Iniciando almacenar_outfit con datos recibidos: {data}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            print("⚠️ Usuario no autenticado o dominio no seleccionado en la sesión.")
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            print(f"❌ Usuario o dominio no encontrado. Usuario: {user_q}, Dominio: {domain_q}")
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # ✅ Extraer datos del JSON recibido
        ocasion = data.get("ocasion", "").strip().lower()
        prendas = data.get("prendas_outfit", [])

        if not ocasion:
            print("⚠️ Ocasión vacía o no proporcionada.")
            return jsonify({"error": "El nombre de la ocasión es obligatorio"}), 400

        if not isinstance(prendas, list) or not prendas:
            print("⚠️ Lista de prendas inválida o vacía.")
            return jsonify({"error": "Debe proporcionar una lista de prendas"}), 400

        prendas = list(set(prendas))  # Eliminar duplicados
        print(f"👕 Prendas procesadas (sin duplicados): {prendas}")

        # 🔑 Clave para Redis
        redis_key_prefs = f"user:{user_q.id}:domain:{domain_q.id}:preferences"
        print(f"🔑 Clave Redis generada: {redis_key_prefs}")

        # 🗄️ Cargar preferencias desde Redis
        prefs_json = redis_client.get(redis_key_prefs)
        user_prefs = json.loads(prefs_json) if prefs_json else {}
        print(f"📥 Preferencias actuales en Redis: {user_prefs}")

        # 📝 Agregar outfit a preferencias
        if "outfits" not in user_prefs:
            user_prefs["outfits"] = {}

        user_prefs["outfits"][ocasion] = prendas
        print(f"🆕 Preferencias con nuevo outfit (Redis): {user_prefs}")

        # Guardar en Redis
        redis_client.set(redis_key_prefs, json.dumps(user_prefs, ensure_ascii=False))
        print(f"✅ Outfit para '{ocasion}' almacenado en Redis.")

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference
            print(f"📦 Preferencias actuales antes de modificar: {current_prefs}")

            # Asegurar que sea un diccionario (por si es string JSON)
            if isinstance(current_prefs, str):
                current_prefs = json.loads(current_prefs)

            if "outfits" not in current_prefs:
                current_prefs["outfits"] = {}

            # Agregar o actualizar el outfit
            print(f"➕ Agregando outfit para '{ocasion}' con prendas: {prendas}")
            current_prefs["outfits"][ocasion] = prendas

            # Guardar cambios
            user_pref.preference = json.dumps(current_prefs, ensure_ascii=False)
            db.session.commit()
            print(f"✅ Outfit para '{ocasion}' almacenado en base de datos.")
        else:
            # 🆕 Crear preferencia si no existe
            print("📄 No se encontró registro de preferencias. Creando nuevo...")
            nueva_pref = UserPreference(
                user_id=user_q.id,
                domain_id=domain_q.id,
                preference=json.dumps({
                    "outfits": {
                        ocasion: prendas
                    }
                }, ensure_ascii=False)
            )
            db.session.add(nueva_pref)
            db.session.commit()
            print(f"✅ Nueva preferencia con outfit '{ocasion}' creada en la base de datos.")

    except Exception as e:
        print(f"❌ Error al almacenar outfit: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

def buscar_outfits():
    """Busca y retorna los outfits almacenados por el usuario junto con sus prendas."""

    print(f"🔵 Iniciando buscar_outfits")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference  
            print(f"📦 Preferencias actuales antes de procesar: {current_prefs}")

            # Asegurar que sea un diccionario y no una cadena JSON
            if isinstance(current_prefs, str):  
                current_prefs = json.loads(current_prefs)  

            # Obtener los outfits completos con prendas
            outfits_completos = current_prefs.get("outfits", {})
            print(f"👗 Outfits encontrados: {outfits_completos}")

            return {"outfits_almacenados": outfits_completos}

        return {"outfits_almacenados": {}}  # Si no hay outfits guardados

    except Exception as e:
        print(f"⚠️ Error en buscar_outfits: {e}")
        return jsonify({"error": str(e)}), 500
def borrar_outfit(nombre_ocasion):
    """Elimina un outfit (ocasión) almacenado por el usuario."""

    print(f"🔴 Iniciando borrar_outfit: {nombre_ocasion}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference  
            print(f"📦 Preferencias actuales antes de procesar: {current_prefs}")

            # Asegurar que sea un diccionario y no una cadena JSON
            if isinstance(current_prefs, str):  
                current_prefs = json.loads(current_prefs)

            # Verificar si el outfit existe
            outfits = current_prefs.get("outfits", {})
            if nombre_ocasion in outfits:
                del outfits[nombre_ocasion]  # Eliminar el outfit
                user_pref.preference = json.dumps(current_prefs)  # Guardar cambios
                db.session.commit()
                print(f"✅ Outfit para ocasión '{nombre_ocasion}' eliminado con éxito.")
                return jsonify({"message": f"Outfit para ocasión '{nombre_ocasion}' eliminado exitosamente."}), 200
            else:
                return jsonify({"error": "Ocasión no encontrada"}), 404

        return jsonify({"error": "No hay outfits almacenados"}), 404

    except Exception as e:
        print(f"⚠️ Error en borrar_outfit: {e}")
        return jsonify({"error": str(e)}), 500


def almacenar_rutina_gym(data):
    """Almacena una rutina de ejercicios con sus ejercicios e implementos asociados en user_preferences."""

    print(f"🔵 Iniciando almacenar_rutina_gym con datos recibidos: {data}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            print("⚠️ Usuario no autenticado o dominio no seleccionado en la sesión.")
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            print(f"❌ Usuario o dominio no encontrado. Usuario: {user_q}, Dominio: {domain_q}")
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # ✅ Extraer datos del JSON recibido
        nombre_rutina = data.get("nombre_rutina", "").strip().lower()
        ejercicios = data.get("ejercicios_sugeridos", [])
        implementos = data.get("implementos_necesarios", [])

        if not nombre_rutina:
            print("⚠️ Nombre de rutina vacío o no proporcionado.")
            return jsonify({"error": "El nombre de la rutina es obligatorio"}), 400

        if not isinstance(ejercicios, list) or not ejercicios:
            print("⚠️ Lista de ejercicios inválida o vacía.")
            return jsonify({"error": "Debe proporcionar una lista de ejercicios"}), 400

        if not isinstance(implementos, list):
            print("⚠️ Lista de implementos inválida.")
            return jsonify({"error": "Debe proporcionar una lista válida de implementos"}), 400

        ejercicios = list(set(ejercicios))
        implementos = list(set(implementos))
        print(f"💪 Ejercicios procesados: {ejercicios}")
        print(f"🧰 Implementos procesados: {implementos}")

        # 🔑 Clave para Redis
        redis_key_prefs = f"user:{user_q.id}:domain:{domain_q.id}:preferences"
        print(f"🔑 Clave Redis generada: {redis_key_prefs}")

        # 🗄️ Cargar preferencias desde Redis
        prefs_json = redis_client.get(redis_key_prefs)
        user_prefs = json.loads(prefs_json) if prefs_json else {}
        print(f"📥 Preferencias actuales en Redis: {user_prefs}")

        # 📝 Agregar rutina a preferencias
        if "rutinas" not in user_prefs:
            user_prefs["rutinas"] = {}

        user_prefs["rutinas"][nombre_rutina] = {
            "ejercicios": ejercicios,
            "implementos": implementos
        }
        print(f"🆕 Preferencias con nueva rutina (Redis): {user_prefs}")

        # Guardar en Redis
        redis_client.set(redis_key_prefs, json.dumps(user_prefs, ensure_ascii=False))
        print(f"✅ Rutina '{nombre_rutina}' almacenada en Redis.")

        # 🔍 Buscar en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference
            print(f"📦 Preferencias actuales antes de modificar: {current_prefs}")

            # Actualizar o crear clave "rutinas"
            if "rutinas" not in current_prefs:
                current_prefs["rutinas"] = {}

            current_prefs["rutinas"][nombre_rutina] = {
                "ejercicios": ejercicios,
                "implementos": implementos
            }

            # Guardar cambios en DB
            user_pref.preference = current_prefs
        else:
            # Crear nuevo registro
            user_pref = UserPreference(
                user_id=user_q.id,
                domain_id=domain_q.id,
                preference={
                    "rutinas": {
                        nombre_rutina: {
                            "ejercicios": ejercicios,
                            "implementos": implementos
                        }
                    }
                }
            )

        db.session.add(user_pref)
        db.session.commit()
        print(f"💾 Rutina '{nombre_rutina}' almacenada exitosamente en base de datos.")
        return jsonify({"message": f"Rutina '{nombre_rutina}' almacenada correctamente"}), 200

    except Exception as e:
        print(f"❌ Error en almacenar_rutina_gym: {e}")
        return jsonify({"error": "Error al almacenar la rutina"}), 500
    
def buscar_rutinas():
    """Busca todas las rutinas guardadas del usuario en el dominio actual."""

    print("🔵 Iniciando búsqueda de rutinas...")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            print("⚠️ Usuario no autenticado o dominio no seleccionado en la sesión.")
            return {"error": "Usuario no autenticado o dominio no seleccionado"}

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            print(f"❌ Usuario o dominio no encontrado. Usuario: {user_q}, Dominio: {domain_q}")
            return {"error": "Usuario o dominio no encontrado"}

        # 🔑 Clave Redis
        redis_key_prefs = f"user:{user_q.id}:domain:{domain_q.id}:preferences"
        print(f"🔑 Clave Redis generada: {redis_key_prefs}")

        # 📦 Leer preferencias desde Redis
        prefs_json = redis_client.get(redis_key_prefs)
        user_prefs = json.loads(prefs_json) if prefs_json else {}

        rutinas_guardadas = user_prefs.get("rutinas", {})

        print(f"📥 Rutinas encontradas en Redis: {rutinas_guardadas}")

        return rutinas_guardadas

    except Exception as e:
        print(f"❌ Error al buscar rutinas: {str(e)}")
        return {"error": "Error interno del servidor"}
    

    
def borrar_rutina(nombre_rutina):
    """Elimina una rutina de ejercicios almacenada por el usuario."""

    print(f"🔴 Iniciando borrar_rutina: {nombre_rutina}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # 🔍 Buscar preferencias en la base de datos
        user_pref = UserPreference.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
        print(f"🔍 user_pref encontrado: {user_pref}")

        if user_pref:
            # Cargar preferencias actuales
            current_prefs = user_pref.preference
            print(f"📦 Preferencias actuales antes de procesar: {current_prefs}")

            if isinstance(current_prefs, str):
                current_prefs = json.loads(current_prefs)

            # Verificar si la rutina existe
            rutinas = current_prefs.get("rutinas", {})
            if nombre_rutina in rutinas:
                del rutinas[nombre_rutina]
                user_pref.preference = json.dumps(current_prefs)
                db.session.commit()
                print(f"✅ Rutina '{nombre_rutina}' eliminada con éxito.")
                return jsonify({"message": f"Rutina '{nombre_rutina}' eliminada exitosamente."}), 200
            else:
                return jsonify({"error": "Rutina no encontrada"}), 404

        return jsonify({"error": "No hay rutinas almacenadas"}), 404

    except Exception as e:
        print(f"⚠️ Error en borrar_rutina: {e}")
        return jsonify({"error": str(e)}), 500


def almacenar_items_wishlist(elemts):
    """Almacena ingredientes en la lista de deseos del usuario."""

    print(f"🔵 Iniciando almacenar_items_wishlist con ingredientes: {elemts}")

    try:
        # 🛑 Verificar sesión del usuario
        if "provider_id" not in session or "selected_domain" not in session:
            return jsonify({"error": "Usuario no autenticado o dominio no seleccionado"}), 401

        user_q = User.query.filter_by(provider_id=session["provider_id"]).first()
        domain_q = Domain.query.filter_by(domain_name=session["selected_domain"]).first()

        if not user_q or not domain_q:
            return jsonify({"error": "Usuario o dominio no encontrado"}), 404

        # Intentar obtener los items de wishlist desde Redis primero
        redis_key_wishlist = f"user:{user_q.id}:domain:{domain_q.id}:wish_list"
        wishlist_json = redis_client.get(redis_key_wishlist)

        if wishlist_json:
            # Si los items están en Redis, los cargamos
            wishlist = json.loads(wishlist_json)  # Convertir el JSON almacenado en lista
            print("Cargando wishlist desde Redis:", wishlist)
        else:
            # Si no están en Redis, los consultamos en la base de datos
            wishlist_record = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()
            wishlist = wishlist_record.wish_items if wishlist_record else []

            # Guardamos en Redis para futuras consultas
            redis_client.set(redis_key_wishlist, json.dumps(wishlist))
            print("Cargando wishlist desde MySQL y guardando en Redis:", wishlist)

        # 📦 Agregar los nuevos ingredientes a la wishlist y eliminar duplicados
        wishlist.extend(elemts)
        wishlist = list(set(wishlist))  # Eliminar duplicados

        # Guardar la lista actualizada en Redis
        redis_client.set(redis_key_wishlist, json.dumps(wishlist))
        print("✅ Wishlist actualizada guardada en Redis:", wishlist)

        # 🔍 Buscar si el usuario ya tiene una wishlist
        wishlist_record = WishList.query.filter_by(user_id=user_q.id, domain_id=domain_q.id).first()

        if wishlist_record:
            # ✅ Verificar si "wish_items" es una cadena JSON y convertirla a lista
            if isinstance(wishlist_record.wish_items, str):
                try:
                    current_items = json.loads(wishlist_record.wish_items)  # Convertir JSON a lista
                except json.JSONDecodeError:
                    current_items = []  # En caso de error, inicializar lista vacía
            else:
                current_items = wishlist_record.wish_items if wishlist_record.wish_items else []

            # 📦 Agregar nuevos ingredientes sin duplicados
            current_items.extend(elemts)
            wishlist_record.wish_items = list(set(current_items))  # Convertir lista a JSON

        else:
            # 🆕 Crear nueva wishlist
            new_wishlist = WishList(
                user_id=user_q.id,
                domain_id=domain_q.id,
                wish_items=elemts  # Guardar como JSON
            )
            db.session.add(new_wishlist)

        # 💾 Guardar cambios en la base de datos
        db.session.commit()

        return wishlist
    except Exception as e:
        print(f"❌ Error en almacenar_items_wishlist: {e}")
        return jsonify({"error": "Error al almacenar la lista de deseos"}), 500
