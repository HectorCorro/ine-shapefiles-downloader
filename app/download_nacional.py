
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

formato = ['Geomedia Profesional', 'Geomedia Viewer', 'Shapefile']

BASE_URL_NACIONAL = "https://cartografia.ine.mx/sige8/productosCartograficos/bases"
DOWNLOAD_DIR_NACIONAL = os.path.abspath("downloads_nacional")
SHAPEFILES_DIR_NACIONAL = os.path.abspath("shapefiles_nacional")
PRODUCTOS_DIR_NACIONAL = os.path.abspath("productos_ine_nacional")

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
            ruta_file = os.path.join(root, file)
            if file.lower().endswith(".zip"):
                print(f"   Descomprimiendo (recursivo) .zip: {ruta_file}")
                try:
                    with zipfile.ZipFile(ruta_file, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    os.remove(ruta_file)
                except Exception as e:
                    print(f"   Error al descomprimir {ruta_file}: {e}")
            elif file.lower().endswith(".7z"):
                print(f"   Descomprimiendo (recursivo) .7z: {ruta_file}")
                try:
                    with py7zr.SevenZipFile(ruta_file, mode='r') as z:
                        z.extractall(path=root)
                    os.remove(ruta_file)
                except Exception as e:
                    print(f"   Error al descomprimir {ruta_file}: {e}")

def seleccionar_opcion_parcial(sel, texto_parcial):
    """
    Recorre las opciones del objeto Select 'sel'
    y selecciona la primera que contenga 'texto_parcial' (insensitive).
    Retorna True si la encontró y seleccionó, False si no.
    """
    for opt in sel.options:
        if texto_parcial.lower() in opt.text.lower():
            opt.click()
            return True
    return False

def descarga_ine_nacional(driver, ent_id, nombre, formato):
    print(f"\n📥 Descargando {ent_id} - {nombre} en formato {formato}")
    driver = configurar_navegador(DOWNLOAD_DIR_NACIONAL)
    driver.get(BASE_URL_NACIONAL)
    time.sleep(2)

    wait = WebDriverWait(driver, 5)
    selector_entidad = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//select)[1]"))
    )
    Select(selector_entidad).select_by_value(ent_id)
    time.sleep(1)
    
    formato_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//select[option[normalize-space(text())='Seleccionar formato']]"
        ))
    )

    select_formato = Select(formato_select)

    ok = seleccionar_opcion_parcial(select_formato, formato)
    if not ok:
        print(f"⛔ No se encontró ninguna opción que contenga: {formato}")
        return
    time.sleep(1)
    #select_formato.select_by_visible_text(formato)

    boton = wait.until(EC.presence_of_element_located((By.XPATH, "//button[normalize-space(text())='Descargar']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", boton)
    driver.execute_script("arguments[0].click();", boton)
    print("Botón clickeado. Esperando 5s antes de verificar descargas...")
    time.sleep(2)

    #Buscar archivo descargado en DOWNLOAD_DIR_NACIONAL (.zip o .7z)
    archivo_descargado = None
    for _ in range(30):
        archivos = [f for f in os.listdir(DOWNLOAD_DIR_NACIONAL) if f.endswith(".zip") or f.endswith(".7z")]
        if archivos:
            archivo_descargado = max(
                [os.path.join(DOWNLOAD_DIR_NACIONAL, f) for f in archivos],
                key=os.path.getctime
            )
            break
        time.sleep(1)
    if not archivo_descargado:
        print("⛔ No se detectó archivo descargado para este formato.")
        driver.quit()
        return

    # Renombrar el archivo descargado con la nomenclatura deseada
    ext = os.path.splitext(archivo_descargado)[1]
    nuevo_nombre = f"{ent_id}_{nombre}_{formato.replace(' ', '_')}{ext}"
    nuevo_path = os.path.join(DOWNLOAD_DIR_NACIONAL, nuevo_nombre)
    os.rename(archivo_descargado, nuevo_path)
    print(f"✅ Archivo renombrado a: {nuevo_path}")

    # Crear carpeta destino: PRODUCTOS_DIR_NACIONAL/{ent_id}_{nombre}/{formato}
    carpeta_destino = os.path.join(PRODUCTOS_DIR_NACIONAL, f"{ent_id}_{nombre}", formato.replace(' ', '_'))
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Extraer el archivo descargado según su extensión
    if ext.lower() == ".zip":
        try:
            with zipfile.ZipFile(nuevo_path, 'r') as zip_ref:
                zip_ref.extractall(carpeta_destino)
            print(f"📂 Archivo .zip extraído en: {carpeta_destino}")
        except Exception as e:
            print("Error al extraer .zip:", e)
    elif ext.lower() == ".7z":
        try:
            with py7zr.SevenZipFile(nuevo_path, mode='r') as z:
                z.extractall(path=carpeta_destino)
            print(f"📂 Archivo .7z extraído en: {carpeta_destino}")
        except Exception as e:
            print("Error al extraer .7z:", e)
    else:
        print("Extensión no soportada:", ext)

    # (Opcional) Descompresión recursiva para aplanar niveles de compresión si existieran
    descomprimir_recursivo(carpeta_destino)
    print(f"✅ Descompresión recursiva completada en: {carpeta_destino}")

def limpiar_directorio(ruta):
    try:
        shutil.rmtree(ruta)
        print(f"Directorio eliminado: {ruta}")
    except Exception as e:
        print(f"Error al eliminar {ruta}: {e}")

def main():
    os.makedirs(DOWNLOAD_DIR_NACIONAL, exist_ok=True)
    os.makedirs(PRODUCTOS_DIR_NACIONAL, exist_ok=True)

    driver = configurar_navegador(DOWNLOAD_DIR_NACIONAL)

    try:
        for ent_id, nombre in ENTIDADES.items():
            for fmt in formato:
                descarga_ine_nacional(driver, ent_id, nombre, fmt)
    finally:
        driver.quit()
        print("\n🎉 Descargas y extracciones completadas.")

    print("Esperando 10 segundos para asegurar que la extracción se completó...")
    time.sleep(10)
    limpiar_directorio(DOWNLOAD_DIR_NACIONAL)

if __name__ == "__main__":
    main()
