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
        for i in range(min(5, len(productos))):  # Asegura que solo se iteren los primeros tres productos
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


def web_decathlon(producto):
    print("Ejecutando Main")

    # Configuración para el modo headless
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Iniciar el driver de Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Abrir Decathlon
        driver.get("https://www.decathlon.com.co")
        print("Página abierta correctamente.")
        time.sleep(5)  

        # Aceptar cookies si aparecen
        print("Buscando el botón de aceptar cookies...")
        try:
            boton_cookies = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "didomi-notice-agree-button"))
            )
            boton_cookies.click()
            print("✔️ Botón de cookies aceptado.")
        except Exception:
            print("⚠️ No se encontró el botón de cookies o ya estaba cerrado.")

        # Esperar el botón de búsqueda y hacer clic
        print("Esperando el botón de búsqueda...")
        boton_busqueda = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='search-popover-trigger']"))
        )
        boton_busqueda.click()
        print("✔️ Botón de búsqueda activado y clickeado.")

        # Esperar el campo de búsqueda y enviar el producto
        input_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
        )
        input_busqueda.send_keys(producto)
        print(f"🔍 Buscando '{producto}' en Decathlon...")

        time.sleep(3)

    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")

    finally:
        driver.quit()
        print("🚪 Driver cerrado.")
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def main4():
    print("Ejecutando Main")

    # Configuración para el modo headless
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--disable-extensions")  
    
    # Iniciar el driver de Chrome con las opciones
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    producto = "pesas"

    # Abrir Decathlon
    driver.get("https://www.decathlon.com.co")
    print("Página abierta correctamente.")
    time.sleep(9)  # Pequeña espera para garantizar carga inicial

    try:
        # Aceptar cookies si aparecen
        print("Buscando el botón de aceptar cookies...")
        try:
            boton_cookies = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            boton_cookies.click()
            print("✔️ Botón de cookies aceptado.")
        except Exception:
            print("⚠️ No se encontró el botón de cookies o ya estaba cerrado.")

        # Esperar el botón de búsqueda y hacer clic
        print("Esperando el botón de búsqueda...")
        boton_busqueda = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/os-header/header/div/div[3]/os-drawer-trigger/button"))
        )
        boton_busqueda.click()
        print("✔️ Botón de búsqueda activado y clickeado.")

        # Esperar el campo de búsqueda y enviar el producto
        input_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
        )
        input_busqueda.send_keys(producto)
        input_busqueda.send_keys("\n")  # Simula Enter
        print(f"🔍 Búsqueda de '{producto}' enviada.")

        # Esperar a que los resultados carguen
        time.sleep(3)  # Esperar unos segundos por los resultados
        print("✅ Resultados cargados.")

    except Exception as e:
        print(f"❌ Error en la ejecución: {str(e)}")

    finally:
        driver.quit()  # Cerrar el navegador al finalizar


def main5():

    print("Ejecutando Main")
    producto="camisa"

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
    driver.get("https://co.hm.com/")

    productos_lista = []  # Lista donde se almacenarán los productos extraídos

    try:
        ### REALIZAR BÚSQUEDA DEL PRODUCTO ###
        print("Abriendo página de HM..")
        
        busqueda = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Buscar productos"]'))
        )
        busqueda.send_keys(producto)
        busqueda.send_keys(Keys.RETURN)  # Simula la tecla Enter
        print("Texto enviado correctamente al campo de búsqueda.")

    except Exception as e:
        print(f"❌ Error en la ejecución: {str(e)}")

    finally:
        driver.quit()  # Cerrar el navegador al finalizar
