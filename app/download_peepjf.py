import os
import time
import py7zr
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import shutil


ENTIDADES = {
    "1": "Aguascalientes",
    "2": "Baja_California",
    "3": "Baja_California_Sur",
    "4": "Campeche",
    "5": "Coahuila",
    "6": "Colima",
    "7": "Chiapas",
    "8": "Chihuahua",
    "9": "CDMX",
    "10": "Durango",
    "11": "Guanajuato",
    "12": "Guerrero",
    "13": "Hidalgo",
    "14": "Jalisco",
    "15": "Mexico",
    "16": "Michoacan",
    "17": "Morelos",
    "18": "Nayarit",
    "19": "Nuevo_Leon",
    "20": "Oaxaca",
    "21": "Puebla",
    "22": "Queretaro",
    "23": "Quintana_Roo",
    "24": "San_Luis_Potosi",
    "25": "Sinaloa",
    "26": "Sonora",
    "27": "Tabasco",
    "28": "Tamaulipas",
    "29": "Tlaxcala",
    "30": "Veracruz",
    "31": "Yucatan",
    "32": "Zacatecas"
}

BASE_URL = "https://cartografia.ine.mx/sige8/peepjf/bases"
DOWNLOAD_DIR = os.path.abspath("downloads_peepjf")
SHAPEFILES_DIR = os.path.abspath("shapefiles_peepjf")


def configurar_navegador(DOWNLOAD_DIR):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-dev-shm-usage")  # importante en Mac/Linux

    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def descomprimir_recursivo(carpeta):
    """
    Recorre la carpeta dada y extrae recursivamente
    cualquier archivo .zip o .7z encontrado.
    Luego elimina ese archivo comprimido.
    """
    for root, dirs, files in os.walk(carpeta):
        for file in files:
            ruta_comp = os.path.join(root, file)
            # 1) Si es .zip -> usar zipfile
            if file.lower().endswith(".zip"):
                print(f"Descomprimiendo .zip: {ruta_comp}")
                try:
                    with zipfile.ZipFile(ruta_comp, 'r') as z:
                        z.extractall(root)
                    os.remove(ruta_comp)
                except Exception as e:
                    print(f"Error al descomprimir {ruta_comp}: {e}")
            # 2) Si es .7z -> usar py7zr
            elif file.lower().endswith(".7z"):
                print(f"Descomprimiendo .7z: {ruta_comp}")
                try:
                    with py7zr.SevenZipFile(ruta_comp, 'r') as z:
                        z.extractall(root)
                    os.remove(ruta_comp)
                except Exception as e:
                    print(f"Error al descomprimir {ruta_comp}: {e}")

def download_peepjf(driver, ent_id, nombre):
    print(f"\n📥 Descargando {ent_id} - {nombre}")
    driver.get(BASE_URL)
    time.sleep(2)

    wait = WebDriverWait(driver, 2)
    selector_entidad = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select.block.w-full")))
    Select(selector_entidad).select_by_value("2")
    time.sleep(2)

    selector_formato = wait.until(EC.presence_of_element_located((By.XPATH, "//select[option[contains(text(), 'Shapefile')]]")))
    Select(selector_formato).select_by_visible_text("Shapefile")
    time.sleep(2)

    boton = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='Descargar']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", boton)
    driver.execute_script("arguments[0].click();", boton)
    print("Botón clickeado. Esperando 5s antes de verificar descargas...")
    time.sleep(2)

        # Buscar archivo .zip más reciente en carpeta de descargas
    print("🔍 Buscando archivo .zip en carpeta de descargas...")
    zip_encontrado = None
    for _ in range(30):
        archivos = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".zip")]
        if archivos:
            # Tomar el más reciente
            zip_encontrado = max(
                [os.path.join(DOWNLOAD_DIR, f) for f in archivos],
                key=os.path.getctime
            )
            break
        time.sleep(1)

    if not zip_encontrado:
        print("⛔ No se detectó ningún archivo .zip.")
        return

    # Renombrar el .zip con el nombre esperado
    nuevo_zip_path = os.path.join(DOWNLOAD_DIR, f"{ent_id}_{nombre}.zip")
    os.rename(zip_encontrado, nuevo_zip_path)
    print(f"✅ Archivo renombrado: {nuevo_zip_path}")

    # Crear carpeta de salida
    carpeta_salida = os.path.join(SHAPEFILES_DIR, f"{ent_id}_{nombre}")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Extraer el zip en la carpeta destino
    import zipfile
    with zipfile.ZipFile(nuevo_zip_path, 'r') as zip_ref:
        zip_ref.extractall(carpeta_salida)

    descomprimir_recursivo(carpeta_salida)

    print(f"📂 Shapefile extraído en: {carpeta_salida}")

def limpiar_directorio(ruta):
    try:
        shutil.rmtree(ruta)
        print(f"Directorio eliminado: {ruta}")
    except Exception as e:
        print(f"Error al eliminar {ruta}: {e}")

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(SHAPEFILES_DIR, exist_ok=True)

    driver = configurar_navegador(DOWNLOAD_DIR)

    try:
        for ent_id, nombre in ENTIDADES.items():
            download_peepjf(driver, ent_id, nombre)
    finally:
        driver.quit()
        print("\n🎉 Descargas y extracciones completadas.")

    print("Esperando 10 segundos para asegurar que la extracción se completó...")
    time.sleep(10)
    limpiar_directorio(DOWNLOAD_DIR)

if __name__ == "__main__":
    main()
