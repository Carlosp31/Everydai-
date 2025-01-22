from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


from selenium.webdriver.support import expected_conditions as EC   
from selenium.webdriver.support.ui import WebDriverWait as Wait 
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time

import json
import os

from selenium.webdriver.chrome.options import Options
import tempfile

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

def web_culinary(producto):
    print("Ejecutando Main")

    print("Ejecutando Main")

    # Crear un directorio temporal para datos del usuario
    temp_dir = tempfile.mkdtemp()

    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")  # Usar un directorio temporal único
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Para evitar problemas de memoria compartida
    chrome_options.add_argument("--headless")  # Opcional: Ejecutar en modo sin interfaz gráfica

    # Inicializar ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.olimpica.com/supermercado")
    
    try:
        ### REALIZAR BÚSQUEDA DEL ELEMENTO ###
        # Espera explícita para encontrar el elemento por el placeholder
        busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Busca por nombre, categoría…"]'))
        )
        busqueda.send_keys(producto)
        busqueda.send_keys(Keys.RETURN)  # Simula la tecla Enter
        print("Texto enviado correctamente al campo de búsqueda.")
        time.sleep(5)

        ### SELECCIONAR PRODUCTO Y EXTRAER INFORMACIÓN ###
        print("Por favor, selecciona manualmente un producto en la página web...")
        
        # Inyectar un script de JavaScript para capturar clics en los elementos
        script = """
        document.addEventListener('click', function(event) {
            let selectedElement = event.target.closest('.vtex-product-summary-2-x-container'); // Ajusta la clase según la estructura de la página
            if (selectedElement) {
                let productName = selectedElement.querySelector('.vtex-product-summary-2-x-productNameContainer').innerText; // Nombre del producto
                let productPrice = selectedElement.querySelector('.vtex-product-price-1-x-sellingPrice span').innerText; // Precio del producto
                window.selectedProductData = {
                    name: productName,
                    price: productPrice
                };
                alert('Producto seleccionado: ' + productName + '\\nPrecio: ' + productPrice);  // Mostrar alerta con el texto seleccionado
            }
            event.preventDefault(); // Evitar cualquier comportamiento adicional del clic
        }, true);
        """
        driver.execute_script(script)
        time.sleep(1)
        # Esperar hasta que el usuario seleccione un producto
        selected_product = None
        while not selected_product:
            try:
                selected_product = driver.execute_script("return window.selectedProductData;")
                if selected_product:
                    print(f"Producto seleccionado: {selected_product['name']}")
                    print(f"Precio: {selected_product['price']}")
                    guardar_en_json(selected_product)
                    time.sleep(1)
                    driver.execute_script("window.selectedProductData = null;")  # Reiniciar la variable global
                    break
            except Exception as e:
                print("Esperando selección del producto...")
            except WebDriverException as e:
                print(f"Error en Selenium: {e}")
                
        time.sleep(1)
        # Continuar con el resto del código
        print("Continuando con el resto del código...")

    except TimeoutException:
        print("No se encontró el campo de búsqueda.")
    finally:
        driver.quit()



# web_culinary(producto= "salsa de tomate")