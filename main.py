from app.download import get_shapefile_links, download_and_extract_zip
import os

fuentes = {
    "peepjf_bases": "https://cartografia.ine.mx/sige8/peepjf/bases",
    "productos_cartograficos": "https://cartografia.ine.mx/sige8/productosCartograficos/bases"
}

base_dir = "shapefiles"

def main():
    for nombre, url in fuentes.items():
        print(f"Procesando {nombre}...")
        output_dir = os.path.join(base_dir, nombre)
        zip_links = get_shapefile_links(url)
        print(f"Enlaces encontrados: {zip_links}")
        for link in zip_links:
            if not link.startswith('http'):
                link = os.path.join(url, link)
            download_and_extract_zip(link, output_dir)

if __name__ == "__main__":
    main()
