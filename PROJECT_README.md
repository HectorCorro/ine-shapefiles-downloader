# 🗳️ Mexico Electoral Analytics

Análisis geoespacial y de tendencias de datos electorales en México. Proyecto organizado como workspace `uv` con arquitectura modular de 3 capas.

## 📁 Estructura del Proyecto

```
mexico-electoral-analytics/
├── pyproject.toml              # Configuración workspace raíz
├── .gitignore                  # Archivos ignorados
│
├── ingestion/                  # 📥 MÓDULO 1: Ingestion
│   ├── pyproject.toml
│   └── src/ingestion/
│       ├── __init__.py
│       ├── download_nacional.py    # Scraper INE Nacional
│       ├── download_peepjf.py      # Scraper PEEPJF
│       └── utils/
│           ├── __init__.py
│           └── s3_utils.py         # Utilidades AWS S3
│
├── analytics/                  # 📊 MÓDULO 2: Analytics
│   ├── pyproject.toml
│   ├── clean_votes.ipynb          # Limpieza y procesamiento de votos
│   ├── test_data.ipynb            # Pruebas de datos
│   └── src/analytics/
│       └── __init__.py
│
├── dashboard/                  # 📈 MÓDULO 3: Dashboard
│   ├── pyproject.toml
│   └── src/dashboard/
│       ├── __init__.py
│       └── kepler_visualization.py  # Visualización multicapa
│
├── shared/                     # 🔧 Configuración compartida
│   └── config/
│       ├── __init__.py
│       └── estados.py              # Catálogo de entidades
│
└── data/                       # 💾 Datos (gitignored)
    ├── raw/                    # Datos crudos descargados
    ├── processed/              # Datos estandarizados (Parquet)
    ├── insights/               # Resultados analíticos
    └── geo/                    # GeoJSON optimizados
```

---

## 🎯 Responsabilidades por Módulo

### 1️⃣ **Ingestion** (`/ingestion`)
**Objetivo:** Descargar y estandarizar datos crudos (CSV, shapefiles, Excel del INE/PREP).

**Entrada:** URLs de INE, PREP  
**Salida:** `data/processed/*.parquet`, `data/raw/shapefiles_*`

**Herramientas:**
- Selenium (web scraping)
- Polars (limpieza rápida)
- Boto3 (S3)

**Regla:** ❌ NO hacer operaciones matemáticas complejas aquí. Solo limpieza básica y estandarización de columnas.

**Scripts principales:**
- `download_nacional.py` - Descarga shapefiles nacionales del INE
- `download_peepjf.py` - Descarga shapefiles PEEPJF
- `utils/s3_utils.py` - Upload a S3 con retry y validación

---

### 2️⃣ **Analytics** (`/analytics`)
**Objetivo:** Generar insights a partir de datos procesados.

**Entrada:** `data/processed/*.parquet`  
**Salida:** `data/insights/*.parquet`, `data/geo/*.geojson`

**Tareas:**
- Joins geoespaciales (votos + mapas)
- Cálculo de tendencias históricas y vote swings
- Agregaciones por Sección, Municipio, Distrito

**Herramientas:**
- GeoPandas
- Shapely
- Scikit-learn
- NumPy

**Regla:** ✅ Este es el lugar para operaciones complejas, ML, y transformaciones geométricas.

**Notebooks principales:**
- `clean_votes.ipynb` - Pipeline de limpieza y transformación de resultados electorales
- `test_data.ipynb` - Validación de integridad de datos

---

### 3️⃣ **Dashboard** (`/dashboard`)
**Objetivo:** Visualización interactiva de datos.

**Entrada:** `data/insights/*`, `data/geo/*`  
**Salida:** HTML interactivos, dashboards Streamlit

**Herramientas:**
- Kepler.gl
- Folium
- Streamlit (futuro)
- Plotly

**Regla:** 🧠 Esta capa debe ser "tonta". Lee datos pre-calculados de `analytics`. Evita cómputo pesado on-the-fly.

**Scripts principales:**
- `kepler_visualization.py` - Mapas multicapa interactivos con Kepler.gl

---

## 🚀 Instalación y Configuración

### Requisitos
- Python >= 3.12
- `uv` instalado ([docs](https://docs.astral.sh/uv/))

### Setup Inicial

```bash
# 1. Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar el repositorio
git clone <repo-url>
cd ine-shapefiles-downloader

# 3. Instalar todas las dependencias del workspace
uv sync

# 4. Activar el entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### Agregar Dependencias a un Módulo

```bash
# Ejemplo: agregar pandas al módulo analytics
uv add pandas --package analytics

# Ejemplo: agregar fastapi al módulo dashboard
uv add fastapi --package dashboard
```

---

## 📊 Flujo de Datos

```
┌─────────────────┐
│   INE / PREP    │  (Fuentes externas)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   INGESTION     │  download_nacional.py, download_peepjf.py
│  (Bronze→Silver)│  → data/raw/, data/processed/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ANALYTICS     │  clean_votes.ipynb, geospatial joins
│ (Silver→Gold)   │  → data/insights/, data/geo/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   DASHBOARD     │  kepler_visualization.py, Streamlit
│   (Consumo)     │  → HTML, dashboards interactivos
└─────────────────┘
```

---

## 🛠️ Comandos Útiles

### Ejecutar scrapers de ingestion

```bash
# Descargar shapefiles nacionales
cd ingestion
uv run python -m ingestion.download_nacional

# Descargar shapefiles PEEPJF
uv run python -m ingestion.download_peepjf
```

### Ejecutar notebooks de analytics

```bash
cd analytics
uv run jupyter notebook clean_votes.ipynb
```

### Generar visualizaciones

```bash
cd dashboard/src/dashboard
uv run python kepler_visualization.py
```

---

## 🗺️ Estándares de Datos Mexicanos

### Códigos Geográficos
- **CVE_ENT**: Código de entidad federativa (string con 0 adelante, ej. `"09"` para CDMX, NO `9`)
- **CVE_MUN**: Código de municipio (string, ej. `"002"`)
- **SECCION**: Sección electoral

### Encoding
- **Todos los archivos**: UTF-8
- **Shapefiles**: Validar encoding en `.cpg`

### Estructura de Parquets
```
data/processed/
  ├── votos_2024_presidencial.parquet
  ├── votos_2024_diputados.parquet
  └── metadata/
      └── estados.parquet
```

---

## 📦 Dependencias por Módulo

| Módulo | Dependencias Principales |
|--------|-------------------------|
| **ingestion** | selenium, py7zr, boto3, polars, webdriver-manager |
| **analytics** | geopandas, polars, numpy, scikit-learn, shapely, pyarrow |
| **dashboard** | keplergl, folium, streamlit, plotly, geopandas |

---

## 🔐 Configuración de AWS (Opcional)

Si usas S3 para almacenar shapefiles:

```bash
# Configurar credenciales AWS
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_DEFAULT_REGION="us-east-2"

# O crear archivo .env en la raíz
echo "AWS_ACCESS_KEY_ID=xxx" > .env
echo "AWS_SECRET_ACCESS_KEY=xxx" >> .env
```

Los scripts en `ingestion/utils/s3_utils.py` verifican automáticamente si los archivos ya existen antes de subirlos.

---

## 📝 Convenciones de Código

1. **Nombres de archivos:** snake_case (`download_nacional.py`)
2. **Nombres de clases:** PascalCase (`ElectoralData`)
3. **Nombres de funciones:** snake_case (`clean_voter_data()`)
4. **Imports:** Absolutos desde el módulo raíz (`from ingestion.utils import s3_utils`)

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'ingestion'`

```bash
# Reinstalar el workspace
uv sync

# Verificar que estés en la raíz del proyecto
pwd  # Debe mostrar .../ine-shapefiles-downloader
```

### Error: Chrome driver no encontrado

```bash
# El script usa webdriver-manager, pero puedes forzar reinstalación:
uv add webdriver-manager --package ingestion --force
```

### Error: Archivos no se suben a S3

Verifica:
1. Credenciales AWS configuradas
2. Bucket existe: `bucket01-labex` (o cambia en `s3_utils.py`)
3. Permisos de escritura en el bucket

---

## 📚 Recursos Adicionales

- [Documentación INE Cartografía](https://cartografia.ine.mx/)
- [PREP 2024](https://prep2024.ine.mx/)
- [GeoPandas Docs](https://geopandas.org/)
- [Kepler.gl Guide](https://docs.kepler.gl/)

---

## 🤝 Contribuir

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer commits descriptivos: `git commit -m "feat(analytics): agregar cálculo de votación efectiva"`
3. Push y crear PR: `git push origin feature/nueva-funcionalidad`

---

## 📄 Licencia

Este proyecto es para uso académico/investigación. Datos electorales propiedad del INE México.

---

**Última actualización:** Noviembre 2024  
**Mantenedor:** @hectorcorro


