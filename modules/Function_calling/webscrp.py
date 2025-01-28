from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time

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

    productos_lista = []  # Lista donde se almacenarán los productos extraídos

    try:
        ### REALIZAR BÚSQUEDA DEL PRODUCTO ###
        print("Abriendo página de Olímpica...")
        
        # Espera activa para que el campo de búsqueda esté disponible
        busqueda = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Busca por nombre, categoría…"]'))
        )
        busqueda.send_keys(producto)
        busqueda.send_keys(Keys.RETURN)  # Simula la tecla Enter
        print("Texto enviado correctamente al campo de búsqueda.")
        
        # Espera a que los resultados se carguen (ajusta el tiempo si es necesario)
        WebDriverWait(driver, 14).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-summary-2-x-productBrand"))
        )
        time.sleep(5)
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

                # Obtener la imagen del producto
                imagen = driver.find_elements(By.CSS_SELECTOR, "img.vtex-product-summary-2-x-imageNormal")[i]
                imagen_src = imagen.get_attribute("src")  # URL de la imagen

                # Crear un diccionario con la información del producto
                producto_info = {
                    "nombre": producto_nombre,
                    "precio": full_price,
                    "imagen_url": imagen_src
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
    finally:
        driver.quit()
        print("Navegador cerrado.")
