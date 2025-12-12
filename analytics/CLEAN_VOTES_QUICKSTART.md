# Clean Votes Module - Quick Start Guide

## 🎯 What You Asked For

You wanted a script that can:
1. ✅ Read CSV/Excel/Parquet files with flexible header detection
2. ✅ Clean electoral data like in `clean_votes.ipynb`
3. ✅ Create clean dataframes for each ENTIDAD, SECCION
4. ✅ Store results in SQLite database (one table per election/entidad)
5. ✅ Optionally merge with geometry from shapefiles
6. ✅ Handle multiple elections and file formats

**Result:** I created a complete modular system in `analytics/src/analytics/clean_votes/`

## 🚀 Instant Usage

### Option 1: One-Line Processing (Python)

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Process any electoral file (CSV/Excel/Parquet)
# This does EVERYTHING from your notebook automatically
result = orchestrator.process_electoral_file(
    file_path='path/to/your/electoral_data.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,  # Set to False if you don't want shapefiles
    save_to_db=True
)

print(f"✓ Processed {result.shape[0]} rows!")
```

### Option 2: Command Line

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

python -m analytics.clean_votes.orchestrator \
    electoral/2024/PRES_2024.csv \
    PRES_2024 \
    --election-date 2024-06-03 \
    --geometry
```

## 📁 What Was Created

```
analytics/src/analytics/clean_votes/
├── __init__.py           # Module exports
├── reader.py             # Reads CSV/Excel/Parquet with auto header detection
├── cleaner.py            # Cleans data (exactly like your notebook)
├── geometry.py           # Merges with shapefiles
├── database.py           # SQLite storage with metadata
├── orchestrator.py       # Main coordinator (CLI + Python API)
└── README.md             # Detailed documentation

analytics/
├── demo_clean_votes.ipynb        # Demo notebook
└── examples/
    └── process_election_example.py
```

## 🗄️ Database Structure (Answering Your Question)

**Your question:** "Should I make a single table for the given election for each ENTIDAD, SECCION?"

**Answer:** Yes! The system creates **one table per (election, entidad) pair**:

```
Database: data/processed/electoral_data.db

Tables:
├── election_pres_2024_01  (Presidential 2024, Aguascalientes)
├── election_pres_2024_02  (Presidential 2024, Baja California)
├── election_pres_2024_09  (Presidential 2024, CDMX)
├── election_dip_2021_01   (Diputados 2021, Aguascalientes)
└── ...

Plus:
└── election_metadata      (Tracks all elections with dates, sources, etc.)
```

**Why this structure?**
- ✅ Easy to query specific election + state combinations
- ✅ Keeps elections separate for comparison
- ✅ Each table has clean ENTIDAD, SECCION data
- ✅ Can have different schemas per election type
- ✅ Metadata table tracks everything

## 📊 Output Format

Each table contains:

| Column Type | Examples |
|-------------|----------|
| **Identifiers** | `ID_ENTIDAD`, `SECCION`, `ID_DISTRITO_FEDERAL` |
| **Names** | `ENTIDAD`, `DISTRITO_FEDERAL` |
| **String IDs** | `ID_ENTIDAD_STR` (zero-padded: "01", "09") |
| **Lista Nominal** | `LISTA_NOMINAL` |
| **Vote Counts** | `PAN`, `PRI`, `PRD`, `MORENA`, coalitions, `NULOS` |
| **Percentages** | `PAN_PCT`, `PRI_PCT`, `MORENA_PCT`, etc. |
| **Total** | `TOTAL_VOTOS_SUM` |
| **Geometry** | `geometry` (if included), `crs` |

## 🎓 Real Example (Reproduces Your Notebook)

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# This single call replaces your ENTIRE notebook!
gdf_final = orchestrator.process_electoral_file(
    file_path='electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,
    save_to_db=True
)

# Now you have the same gdf_final as in your notebook
print(gdf_final.shape)
print(gdf_final[['ENTIDAD', 'SECCION', 'MORENA_PCT', 'geometry']].head())

# Visualize
gdf_final.explore(column='MORENA_PCT', cmap='Reds')
```

## 💡 Key Features That Answer Your Requirements

### 1. Flexible Header Detection ✅

The reader automatically finds headers even if there are metadata rows:

```python
# Your notebook does this manually:
for idx, linea in enumerate(lineas):
    if 'CLAVE_CASILLA' in linea:
        fila_header = idx
        break

# The module does it automatically!
df = reader.read_file('messy_file.csv')  # Just works!
```

### 2. Complete Cleaning Pipeline ✅

Implements all your notebook functions:
- ✅ `calcular_total_y_porcentajes()`
- ✅ `homologar_columna_con_zfill()`
- ✅ `limpiar_y_agrupar_lista_nominal()`
- ✅ `agrupar_votos_por_seccion()`
- ✅ `unir_votos_y_lista()`

### 3. Handles Any Format ✅

```python
# All of these work:
orchestrator.process_electoral_file('data.csv', 'ELECTION_2024')
orchestrator.process_electoral_file('data.xlsx', 'ELECTION_2024')
orchestrator.process_electoral_file('data.parquet', 'ELECTION_2024')
```

### 4. Optional Geometry ✅

```python
# With geometry (like your notebook)
df = orchestrator.process_electoral_file(
    'data.csv', 'PRES_2024',
    include_geometry=True  # Merges with shapefiles
)

# Without geometry (faster)
df = orchestrator.process_electoral_file(
    'data.csv', 'PRES_2024',
    include_geometry=False  # Just clean data
)
```

### 5. Multi-Entidad Processing ✅

```python
# Automatically processes ALL entidades in the file
# Creates separate tables: election_pres_2024_01, election_pres_2024_02, etc.
result = orchestrator.process_electoral_file('national_data.csv', 'PRES_2024')
```

### 6. Easy Querying ✅

```python
# List all elections
elections = orchestrator.list_available_elections()
print(elections)

# Load specific election + state
df = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,  # Aguascalientes
    as_geodataframe=True
)

# Compare across states
df_ags = orchestrator.load_election_data('PRES_2024', entidad_id=1)
df_cdmx = orchestrator.load_election_data('PRES_2024', entidad_id=9)
```

## 🔧 Common Use Cases

### Use Case 1: Process New Election Data

```python
orchestrator = CleanVotesOrchestrator()

# Just point it to your new file
orchestrator.process_electoral_file(
    file_path='new_election_2026.csv',
    election_name='LOCAL_2026',
    election_date='2026-06-07',
    include_geometry=True,
    save_to_db=True
)
```

### Use Case 2: Multiple Elections

```python
elections = [
    ('pres_2024.csv', 'PRES_2024', '2024-06-03'),
    ('dip_2021.csv', 'DIP_2021', '2021-06-06'),
    ('pres_2018.csv', 'PRES_2018', '2018-07-01'),
]

for file, name, date in elections:
    orchestrator.process_electoral_file(file, name, election_date=date)
```

### Use Case 3: Export to GeoJSON

```python
orchestrator.process_electoral_file(
    'data.csv',
    'PRES_2024',
    include_geometry=True,
    save_geojson=True,
    geojson_output_path='output.geojson'
)
```

## 📚 Documentation

- **Quick Start**: This file
- **Detailed Docs**: `analytics/src/analytics/clean_votes/README.md`
- **Full Usage Guide**: `CLEAN_VOTES_USAGE.md` (in project root)
- **Demo Notebook**: `analytics/demo_clean_votes.ipynb`
- **Example Script**: `analytics/examples/process_election_example.py`

## 🏃 Next Steps

1. **Try the demo notebook:**
   ```bash
   jupyter notebook analytics/demo_clean_votes.ipynb
   ```

2. **Process your data:**
   ```python
   from analytics.clean_votes import CleanVotesOrchestrator
   orchestrator = CleanVotesOrchestrator()
   result = orchestrator.process_electoral_file('your_file.csv', 'YOUR_ELECTION')
   ```

3. **Check what's in the database:**
   ```python
   elections = orchestrator.list_available_elections()
   print(elections)
   ```

4. **Load and analyze:**
   ```python
   df = orchestrator.load_election_data('YOUR_ELECTION', entidad_id=1)
   ```

## ⚡ Installation

The module requires these packages (already in `analytics/pyproject.toml`):

```bash
cd analytics
uv pip install -e .
```

Or using uv workspace (recommended):

```bash
uv sync
```

## 🎉 Summary

You now have a **production-ready system** that:
- ✅ Reads any electoral data format
- ✅ Cleans data exactly like your notebook
- ✅ Creates per-ENTIDAD tables in SQLite
- ✅ Handles geometry automatically
- ✅ Works with command line or Python
- ✅ Processes multiple elections easily
- ✅ Provides easy querying and comparison

**No more manual notebook steps!** Just point the orchestrator at your files and it handles everything.

## 💬 Questions?

Run the example notebook or check the detailed README:

```bash
jupyter notebook analytics/demo_clean_votes.ipynb
```

Or get help in Python:

```python
from analytics.clean_votes import CleanVotesOrchestrator
help(CleanVotesOrchestrator)
```

---

**Created:** November 22, 2025  
**Location:** `analytics/src/analytics/clean_votes/`  
**Database:** `data/processed/electoral_data.db`

