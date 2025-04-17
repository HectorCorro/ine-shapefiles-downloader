# INE Shapefiles Downloader

Este proyecto permite descargar shapefiles del Instituto Nacional de Estadística (INE) de manera automatizada.

## Características

- Descarga automatizada de shapefiles del INE
- Procesamiento de datos geográficos
- Configuración mediante Docker para fácil despliegue

## Requisitos

- Python 3.x
- Docker (opcional)

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/HectorCorro/ine-shapefiles-downloader/tree/main
```

2. Crea un ambiente virtual de Python 3.11 o superior (usando virtualenv) y activar
```bash
pip install virtualenv
virtualenv -p /usr/bin/python3.11 env
source mi_entorno_virtualenv/bin/activate
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el proyecto:

```bash
python app/download_nacional.py & python app/download_peepjf.py
```

O usando Docker:

1. Crear imagen

```bash
docker build -t ine-scraper .
```

2. Crear carpetas para archivos a descargar y guardar en local

```bash
mkdir -p /ruta/local/productos_ine_nacional
mkdir -p /ruta/local/shapefiles_peepjf
```
3. Ejecutar contenedor mapeando los directorios anteriores

```bash
docker run --rm \
  -v /ruta/local/productos_ine_nacional:/app/productos_ine_nacional \
  -v /ruta/local/shapefiles_peepjf:/app/shapefiles_peepjf \
  ine-scraper
```

## Estructura del Proyecto

- `app/`: Código fuente principal
- `shapefiles_peepjf/`: Shapefiles descargados
- `productos_ine_nacional/`: Productos del INE
- `main.py`: Punto de entrada principal
- `requirements.txt`: Dependencias del proyecto
- `Dockerfile`: Configuración de Docker