# 🗳️ Mexico Electoral Analytics

Plataforma de análisis geoespacial y de tendencias de datos electorales en México. Proyecto organizado como workspace `uv` con arquitectura modular de 3 capas siguiendo las mejores prácticas de MLOps.

## 📋 Descripción

Este proyecto permite:
- 📥 **Descargar** shapefiles del INE y datos del PREP de manera automatizada
- 🧹 **Limpiar y estandarizar** datos electorales (CSV, Excel) a formato Parquet
- 📊 **Analizar** tendencias geoespaciales y calcular agregaciones por Sección, Municipio y Distrito
- 🗺️ **Visualizar** resultados en mapas interactivos con Kepler.gl y Folium

## 🏗️ Arquitectura

El proyecto está organizado en **3 módulos independientes**:

```
mexico-electoral-analytics/
├── ingestion/      📥 Descarga y limpieza básica (Bronze → Silver)
├── analytics/      📊 Análisis geoespacial y tendencias (Silver → Gold)
└── dashboard/      📈 Visualización interactiva (Gold → Consumo)
```

### Módulo 1: Ingestion
- **Objetivo:** Descargar shapefiles del INE/PREP y estandarizar datos
- **Herramientas:** Selenium, Boto3 (S3), Polars, py7zr
- **Salida:** `data/processed/*.parquet`, `data/raw/shapefiles_*`

### Módulo 2: Analytics
- **Objetivo:** Joins geoespaciales, cálculo de tendencias y agregaciones
- **Herramientas:** GeoPandas, Shapely, Scikit-learn, NumPy
- **Salida:** `data/insights/*.parquet`, `data/geo/*.geojson`

### Módulo 3: Dashboard
- **Objetivo:** Visualización de datos pre-calculados
- **Herramientas:** Kepler.gl, Folium, Plotly, Streamlit
- **Salida:** HTML interactivos, dashboards

## ⚙️ Requisitos

- **Python:** 3.11 o 3.12 (recomendado: 3.12)
- **uv:** Gestor de paquetes ([instalar](https://docs.astral.sh/uv/))
- **Sistema Operativo:** macOS, Linux o Windows
- **Espacio en disco:** ~3 GB (Python + dependencias + datos)

## 🚀 Instalación

### 1. Instalar uv

```bash
# macOS y Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/HectorCorro/ine-shapefiles-downloader.git
cd ine-shapefiles-downloader
```

### 3. Instalar dependencias (workspace completo)

```bash
# Esto instala TODAS las dependencias de los 3 módulos
uv sync
```

✅ ¡Listo! El workspace está configurado con 163 paquetes instalados.

### 4. Verificar instalación

```bash
python3 validate_setup.py
```

Deberías ver: `✅ All checks passed! (25/25)`

## 📖 Uso

### 📥 Descargar Shapefiles

#### Opción 1: Shapefiles Nacionales (INE)

```bash
cd ingestion
uv run python -m ingestion.download_nacional
```

Descarga para todos los estados en 3 formatos:
- Geomedia Profesional
- Geomedia Viewer
- Shapefile

**Salida:** `data/raw/productos_ine_nacional/`

#### Opción 2: Shapefiles PEEPJF

```bash
cd ingestion
uv run python -m ingestion.download_peepjf
```

**Salida:** `data/raw/shapefiles_peepjf/`

### 📊 Procesar Datos Electorales

```bash
cd analytics
uv run jupyter notebook clean_votes.ipynb
```

El notebook:
- Lee archivos CSV del directorio `electoral/2024/`
- Limpia y estandariza columnas
- Exporta Parquets a `data/processed/`

### 🗺️ Generar Visualizaciones

```bash
cd dashboard/src/dashboard
uv run python kepler_visualization.py
```

Genera `kepler_multilayer_map.html` con capas:
- Entidades federativas
- Distritos Federales
- Distritos Locales
- Municipios
- Secciones electorales

**Abrir en navegador:**
```bash
open kepler_multilayer_map.html
```

## 📁 Estructura de Datos

```
data/
├── raw/                # ⬅️ Ingestion escribe aquí
│   ├── downloads_nacional/
│   ├── productos_ine_nacional/
│   └── shapefiles_peepjf/
│
├── processed/          # ⬅️ Analytics lee/escribe aquí
│   ├── votos_2024_pres.parquet
│   ├── votos_2024_dip.parquet
│   └── votos_2024_sen.parquet
│
├── insights/           # ⬅️ Resultados analíticos finales
│   └── agregado_nacional.parquet
│
└── geo/                # ⬅️ GeoJSONs optimizados
    └── secciones_cdmx.geojson
```

## 🔧 Agregar Dependencias

```bash
# Sintaxis: uv add <paquete> --package <módulo>

# Ejemplo: Agregar requests al módulo ingestion
uv add requests --package ingestion

# Ejemplo: Agregar matplotlib al módulo analytics
uv add matplotlib --package analytics

# Ejemplo: Agregar dash al módulo dashboard
uv add dash --package dashboard
```

## 📚 Documentación Adicional

- **`PROJECT_README.md`** - Documentación técnica completa
- **`QUICKSTART.md`** - Guía de referencia rápida
- **`MIGRATION_GUIDE.md`** - Detalles de la migración al workspace
- **`STRUCTURE.txt`** - Diagrama visual de la estructura
- **`SETUP_COMPLETE.md`** - Resumen de la instalación

## 🗺️ Estándares de Datos Mexicanos

### Códigos Geográficos
- **CVE_ENT:** Código de entidad (string con 0 adelante: `"09"` para CDMX, NO `9`)
- **CVE_MUN:** Código de municipio (string: `"002"`)
- **SECCION:** Sección electoral

### Encoding
- Todos los archivos: **UTF-8**
- Shapefiles: Validar encoding en `.cpg`

## 🐛 Solución de Problemas

### Error: `ModuleNotFoundError`

```bash
# Reinstalar el workspace desde la raíz
cd /ruta/al/proyecto
uv sync
```

### Error: Chrome driver no encontrado

```bash
# webdriver-manager lo instala automáticamente
# Si persiste el error:
uv add webdriver-manager --package ingestion --force
```

### Error: Archivos no se suben a S3

Verifica:
1. Credenciales AWS configuradas (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. Bucket existe: `bucket01-labex`
3. Permisos de escritura en el bucket

## 🎯 Comandos Rápidos

```bash
# Validar configuración
python3 validate_setup.py

# Ver módulos del workspace
cat pyproject.toml | grep members

# Reinstalar desde cero
rm -rf .venv && uv sync

# Ver versión de Python
uv run python --version

# Limpiar archivos antiguos (después de verificar)
./cleanup_old_files.sh
```

## 🤝 Contribuir

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer commits descriptivos: `git commit -m "feat(analytics): agregar cálculo de votación efectiva"`
3. Push y crear PR: `git push origin feature/nueva-funcionalidad`

## 📄 Licencia

Este proyecto es para uso académico/investigación. Datos electorales propiedad del INE México.

## 📞 Contacto

- **Repositorio:** [github.com/HectorCorro/ine-shapefiles-downloader](https://github.com/HectorCorro/ine-shapefiles-downloader)
- **Mantenedor:** @hectorcorro

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0.0  
**Estado:** 🟢 Producción