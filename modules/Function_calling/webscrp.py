from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import json
from webdriver_manager.chrome import ChromeDriverManager


def guardar_en_json(producto):
    """
    Guarda el producto en un archivo JSON. Si el archivo no existe, lo crea.
    """
    archivo_json = "productos.json"
    try:
        # Intentar abrir el archivo y cargar los datos existentes
        with open(archivo_json, "r", encoding="utf-8") as file:
            productos = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si no existe el archivo o está vacío, inicializar una lista vacía
        productos = []

    # Agregar el nuevo producto a la lista
    productos.append(producto)

    # Guardar la lista actualizada en el archivo
    with open(archivo_json, "w", encoding="utf-8") as file:
        json.dump(productos, file, indent=4, ensure_ascii=False)

    print(f"Producto guardado: {producto}")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import json
from webdriver_manager.chrome import ChromeDriverManager

def web_culinary(producto):
    print("Ejecutando Main")

    # Configuración para el modo headless
    options = Options()
    options.add_argument("--headless")  # Ejecuta el navegador sin interfaz gráfica
    options.add_argument("--disable-gpu")  # Deshabilita la GPU para mejorar la compatibilidad
    options.add_argument("--no-sandbox")  # Evita problemas en sistemas Linux
    options.add_argument("--disable-dev-shm-usage")  # Optimiza para entornos de bajo rendimiento
    options.add_argument("--disable-extensions")  # Deshabilita extensiones para evitar conflictos

    # Iniciar el controlador de Chrome con las opciones
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.olimpica.com/supermercado")
    time.sleep(2)

    productos_lista = []  # Lista donde se almacenarán los productos extraídos

    try:
        ### REALIZAR BÚSQUEDA DEL PRODUCTO ###
        print("Abriendo página de Olímpica...")
        busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Busca por nombre, categoría…"]'))
        )
        busqueda.send_keys(producto)
        busqueda.send_keys(Keys.RETURN)  # Simula la tecla Enter
        print("Texto enviado correctamente al campo de búsqueda.")
        time.sleep(2)

        ### EXTRAER INFORMACIÓN DE LOS PRIMEROS TRES PRODUCTOS ###
        productos = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-productBrand")
        
        # Iterar sobre los primeros tres productos
        for i in range(min(3, len(productos))):  # Asegura que solo se iteren los primeros tres productos
            try:
                producto_nombre = productos[i].text
                print(f"Nombre del producto {i + 1}: {producto_nombre}")

                # Obtener el precio del producto
                price_container = driver.find_elements(By.CLASS_NAME, "olimpica-dinamic-flags-0-x-currencyContainer")[i]
                full_price = price_container.text.strip()
                print(f"Precio concatenado: {full_price}")

                # Crear un diccionario con la información del producto
                producto_info = {
                    "nombre": producto_nombre,
                    "precio": full_price
                }

                # Agregar el producto a la lista
                productos_lista.append(producto_info)

            except Exception as e:
                print(f"No se pudo extraer información del producto {i + 1}.")
                print(e)

        print("Extracción completada.")
        return productos_lista  # Devolver la lista de productos extraídos

    except TimeoutException:
        print("No se encontró el campo de búsqueda o hubo un problema cargando la página.")
        return []  # En caso de error, devolver una lista vacía

    finally:
        driver.quit()
        print("Navegador cerrado.")

