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
import time
import threading
import json

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

import threading
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Tu código para guardar en JSON y otros detalles permanece igual...

def web_culinary(producto):
    print("Ejecutando Main")
    driver = webdriver.Chrome()
    driver.get("https://www.olimpica.com/supermercado")
    
    try:
        ### REALIZAR BÚSQUEDA DEL ELEMENTO ###
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
            let selectedElement = event.target.closest('.vtex-product-summary-2-x-container'); 
            if (selectedElement) {
                let productName = selectedElement.querySelector('.vtex-product-summary-2-x-productNameContainer').innerText;
                let productPrice = selectedElement.querySelector('.vtex-product-price-1-x-sellingPrice span').innerText;
                window.selectedProductData = {name: productName, price: productPrice};
                alert('Producto seleccionado: ' + productName + '\\nPrecio: ' + productPrice);
            }
            event.preventDefault();
        }, true);
        """
        driver.execute_script(script)

        selected_product = None
        while not selected_product:
            try:
                selected_product = driver.execute_script("return window.selectedProductData;")
                if selected_product:
                    print(f"Producto seleccionado: {selected_product['name']}")
                    print(f"Precio: {selected_product['price']}")
                    guardar_en_json(selected_product)
                    driver.execute_script("window.selectedProductData = null;")  # Reiniciar la variable global
                    break
            except Exception as e:
                print("Esperando selección del producto...")
            time.sleep(1)

        print("Continuando con el resto del código...")

    except TimeoutException:
        print("No se encontró el campo de búsqueda.")
    finally:
        driver.quit()

def ejecutar_web_culinary_en_hilo(producto):
    # Ejecuta la función web_culinary en un hilo separado
    threading.Thread(target=web_culinary, args=(producto,)).start()

# Llamar a la función para ejecutar la tarea en un hilo
ejecutar_web_culinary_en_hilo("salsa de tomate")
