from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
from playwright.sync_api import sync_playwright

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



import json
from playwright.sync_api import sync_playwright

def web_fashion_HM(producto):
    with sync_playwright() as p:
        browser = None
        executable_paths = [
            "/home/maicolln/.cache/ms-playwright/chromium-1155/chrome-linux/chrome",
            "C:/Users/DELL/AppData/Local/ms-playwright/chromium-1155/chrome-win/chrome.exe",
            None,  # Opción predeterminada (sin ruta específica)
            "/home/ubuntu/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"
        ]

        for path in executable_paths:
            try:
                print(f"[INFO] Intentando iniciar Chromium con ruta: {path if path else 'Predeterminado'}")
                browser = p.chromium.launch(headless=True, executable_path=path) if path else p.chromium.launch(headless=True)
                print("[INFO] Navegador iniciado correctamente.")
                break  # Si funciona, salimos del bucle
            except Exception as e:
                print(f"[ERROR] Falló con {path if path else 'Predeterminado'}: {e}")

        if not browser:
            print("[CRÍTICO] No se pudo iniciar el navegador.")
            return None, None, None

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("[INFO] Abriendo la página...")
        page.goto("https://co.hm.com/", wait_until="networkidle")

        try:
            print("[INFO] Buscando el campo de búsqueda...")
            search_box = page.wait_for_selector("input[placeholder='Buscar productos']", timeout=10000)
            search_box.fill(producto)
            search_box.press("Enter")
            print("[INFO] Búsqueda enviada.")

            page.wait_for_selector(".vtex-search-result-3-x-galleryItem")
            print("[INFO] Resultados cargados.")

            # Extraer nombres, precios, imágenes y enlaces
            products = page.query_selector_all(".vtex-search-result-3-x-galleryItem")
            print(f"[INFO] {len(products)} productos encontrados.")

            productos_lista = []

            for product in products:
                title_element = product.query_selector(".vtex-product-summary-2-x-productNameContainer span")
                price_element = product.query_selector(".vtex-product-price-1-x-sellingPrice")
                image_element = product.query_selector("img.vtex-product-summary-2-x-imageNormal")
                link_element = product.query_selector("a.vtex-product-summary-2-x-clearLink")

                title = title_element.inner_text().strip() if title_element else "N/A"
                price = price_element.inner_text().strip() if price_element else "N/A"
                image_url = image_element.get_attribute("src") if image_element else "N/A"
                link = link_element.get_attribute("href") if link_element else "N/A"

                producto_info = {
                    "nombre": title,
                    "precio": price,
                    "imagen_url": image_url,
                    "enlace": f"https://co.hm.com{link}" if link != "N/A" else "N/A"
                }

                productos_lista.append(producto_info)

            print("[INFO] Datos guardados en productos_hm.json")
            return productos_lista  # 🔹 Retorna la lista de productos

        except Exception as e:
            print(f"[ERROR] Ocurrió un problema: {e}")
            return None

        finally:
            browser.close()

def web_fitness_decathlon(producto):
    with sync_playwright() as p:
        browser = None
        executable_paths = [
            "/home/maicolln/.cache/ms-playwright/chromium-1155/chrome-linux/chrome",
            None,  # Opción predeterminada (sin ruta específica)
            "/home/ubuntu/.cache/ms-playwright/chromium-1155/chrome-linux/chrome"
        ]

        for path in executable_paths:
            try:
                print(f"[INFO] Intentando iniciar Chromium con ruta: {path if path else 'Predeterminado'}")
                browser = p.chromium.launch(headless=True, executable_path=path) if path else p.chromium.launch(headless=True)
                print("[INFO] Navegador iniciado correctamente.")
                break  # Si funciona, salimos del bucle
            except Exception as e:
                print(f"[ERROR] Falló con {path if path else 'Predeterminado'}: {e}")

        if not browser:
            print("[CRÍTICO] No se pudo iniciar el navegador.")
            return None, None, None

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("[INFO] Abriendo la página...")
        page.goto("https://www.decathlon.com.co/", wait_until="networkidle")



        try:
            print("[INFO] Buscando el botón de aceptar cookies...")

            # Intentar encontrar y hacer clic en el botón de aceptar cookies
            boton_cookies = page.wait_for_selector("#didomi-notice-agree-button", timeout=5000)
            
            if boton_cookies:
                boton_cookies.click()
                print("✔️ Botón de cookies aceptado.")
            else:
                print("⚠️ No se encontró el botón de cookies o ya estaba cerrado.")

        except Exception as e:
            print(f"⚠️ No se pudo hacer clic en el botón de cookies: {e}")
        try:
            print("[INFO] Haciendo clic en el botón de búsqueda...")
            search_button = page.wait_for_selector("button.page-header_search-trigger", timeout=10000)
            search_button.click()
            print("[INFO] Botón de búsqueda clickeado.")

            # Esperamos un momento para que aparezca el campo de búsqueda
            page.wait_for_timeout(1000)

            print("[INFO] Buscando el campo de búsqueda...")
            search_box = page.wait_for_selector("input[placeholder='Buscar']", timeout=10000)

            # Escribimos el producto y presionamos Enter
            search_box.fill(producto)
            print(f"[INFO] Escribiendo '{producto}' en el campo de búsqueda...")
            search_box.press("Enter")
            print("[INFO] Búsqueda enviada.")
            ######################################################################################################3

            # Esperar a que los resultados carguen
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            print("[INFO] Extrayendo información de los productos...")

            # Extraer productos
            productos = page.query_selector_all(".ais-InfiniteHits-item")  # Ajusta según la estructura de la página

            resultados = []

            for i, producto in enumerate(productos):
                if i >= 6:
                    break
                # Código para extraer datos del producto

                try:
                    # Extraer nombre desde la clase correcta
                    titulo_element = producto.query_selector(".product-name")
                    titulo = titulo_element.inner_text().strip() if titulo_element else "Sin título"

                    # Extraer precio desde el atributo "data-target-price"
                    precio = producto.query_selector("div.category-miniature").get_attribute("data-target-price")
                    precio = precio.replace("\xa0", " ").strip() if precio else "Sin precio"

                    # Extraer imagen
                    imagen_element = producto.query_selector("img")
                    imagen = imagen_element.get_attribute("src") if imagen_element else "Sin imagen"

                    # Guardamos en la lista
                    resultados.append({
                        "nombre": titulo,
                        "precio": precio,
                        "imagen_url": imagen
                    })

                except Exception as e:
                    print(f"[ERROR] No se pudo extraer un producto: {e}")

            # Mostramos los resultados
            print(json.dumps(resultados, indent=2, ensure_ascii=False))

            # Cerrar el navegador
            browser.close()

            print(f"[INFO] Se encontraron {len(resultados)} productos.")
            return resultados

        except Exception as e:
            print(f"[ERROR] No se pudo completar la búsqueda: {e}")
            browser.close()
            return []
        
            ######################################################################################################################################################3

            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Ocurrió un problema: {e}")

        finally:
            browser.close()
