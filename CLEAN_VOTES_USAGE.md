# Clean Votes Module - Usage Guide

## Overview

The **Clean Votes** module is a comprehensive system for processing Mexican electoral data. It automates the workflow from raw electoral files (CSV/Excel/Parquet) to clean, standardized datasets stored in SQLite with optional geospatial integration.

## 🎯 What It Does

1. **Reads** electoral files with flexible header detection
2. **Cleans** and standardizes data (removes unwanted columns, converts types)
3. **Aggregates** votes by ENTIDAD (state) and SECCION (electoral section)
4. **Merges** with shapefiles for geospatial analysis (optional)
5. **Stores** in SQLite database with metadata tracking

## 📁 Location

```
analytics/src/analytics/clean_votes/
├── __init__.py           # Module exports
├── reader.py             # File reading with header detection
├── cleaner.py            # Data transformation pipeline
├── geometry.py           # Shapefile integration
├── database.py           # SQLite storage
├── orchestrator.py       # Main workflow coordinator
└── README.md             # Detailed documentation
```

## 🚀 Quick Start

### Method 1: Python API (Recommended)

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Initialize
orchestrator = CleanVotesOrchestrator(
    db_path='data/processed/electoral_data.db'
)

# Process a file (reproduces your notebook workflow)
df = orchestrator.process_electoral_file(
    file_path='electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,  # Merge with shapefiles
    save_to_db=True
)

print(f"Processed {df.shape[0]} rows across {df['ID_ENTIDAD'].nunique()} states")
```

### Method 2: Command Line

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

# Process electoral file
python -m analytics.clean_votes.orchestrator \
    electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv \
    PRES_2024 \
    --election-date 2024-06-03 \
    --geometry \
    --shapefile-type peepjf

# List all processed elections
python -m analytics.clean_votes.orchestrator --list-elections
```

## 📊 Workflow Details

### Step 1: Read Data

The reader automatically:
- Searches for header row (looks for columns like `CLAVE_CASILLA`, `ID_ENTIDAD`)
- Handles metadata rows before the actual data
- Supports multiple encodings (UTF-8, Latin-1)

```python
from analytics.clean_votes import ElectoralDataReader

reader = ElectoralDataReader()
df = reader.read_file('path/to/electoral_data.csv')
```

### Step 2: Clean & Transform

The cleaner:
- Removes administrative columns (timestamps, codes, etc.)
- Converts vote columns to numeric
- Calculates `TOTAL_VOTOS_SUM` and percentages for each party
- Homogenizes ID columns (creates both Int64 and zero-padded string versions)
- Aggregates by ENTIDAD and SECCION

```python
from analytics.clean_votes import ElectoralDataCleaner

cleaner = ElectoralDataCleaner()
df_clean = cleaner.clean(df_raw)
```

### Step 3: Merge with Geometry (Optional)

```python
from analytics.clean_votes import GeometryMerger

merger = GeometryMerger(shapefile_base_dir='data/geo')
gdf = merger.merge_with_shapefile(
    df=df_clean,
    entidad_id=1,  # Aguascalientes
    shapefile_type='peepjf'  # or 'nacional'
)

# Save as GeoJSON
merger.save_geojson(gdf, 'output.geojson')
```

### Step 4: Store in Database

```python
from analytics.clean_votes import ElectoralDatabase

db = ElectoralDatabase('data/processed/electoral_data.db')

# Save
db.save_electoral_data(
    df=df_clean,
    election_name='PRES_2024',
    entidad_id=1,
    entidad_name='AGUASCALIENTES',
    election_date='2024-06-03',
    source_file='PRES_2024.csv'
)

# Load
df_loaded = db.load_electoral_data(
    election_name='PRES_2024',
    entidad_id=1,
    as_geodataframe=True
)

# List all
elections = db.list_elections()
```

## 🗄️ Database Schema

### Election Tables

Tables are created per election and state: `election_{name}_{id}`

Example: `election_pres_2024_01` (Presidential 2024, Aguascalientes)

**Columns:**
- **Identifiers**: `ID_ENTIDAD`, `SECCION`, `ID_DISTRITO_FEDERAL`
- **Names**: `ENTIDAD`, `DISTRITO_FEDERAL`
- **Strings**: `ID_ENTIDAD_STR`, `SECCION_STR` (zero-padded)
- **Lista Nominal**: `LISTA_NOMINAL`
- **Vote Counts**: `PAN`, `PRI`, `PRD`, `PVEM`, `PT`, `MC`, `MORENA`, coalitions, `NULOS`
- **Percentages**: `PAN_PCT`, `PRI_PCT`, etc.
- **Total**: `TOTAL_VOTOS_SUM`
- **Geometry** (if included): `geometry` (WKT format), `crs`

### Metadata Table

`election_metadata` tracks all processed elections:

| Column | Description |
|--------|-------------|
| `election_name` | Election identifier (e.g., 'PRES_2024') |
| `entidad_id` | State ID (1-32) |
| `entidad_name` | State name |
| `table_name` | Database table name |
| `election_date` | Date of election |
| `has_geometry` | Boolean: includes geometry? |
| `row_count` | Number of rows |
| `source_file` | Original data file path |
| `shapefile_path` | Shapefile used (if any) |
| `created_at` | Timestamp |
| `updated_at` | Last update timestamp |

## 🎓 Usage Examples

### Example 1: Reproduce Your Notebook

This replaces your entire notebook workflow:

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Same as your notebook, but automated
gdf_final = orchestrator.process_electoral_file(
    file_path='electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,
    save_to_db=True
)

# Now you have the same gdf_final as in the notebook!
print(gdf_final.columns)
print(gdf_final[['ENTIDAD', 'SECCION', 'MORENA_PCT', 'geometry']].head())
```

### Example 2: Process Multiple Elections

```python
orchestrator = CleanVotesOrchestrator()

elections = [
    ('electoral/2024/PRES_2024.csv', 'PRES_2024', '2024-06-03'),
    ('electoral/2021/DIP_2021.csv', 'DIP_2021', '2021-06-06'),
    ('electoral/2018/PRES_2018.csv', 'PRES_2018', '2018-07-01'),
]

for file_path, name, date in elections:
    print(f"\nProcessing {name}...")
    orchestrator.process_electoral_file(
        file_path=file_path,
        election_name=name,
        election_date=date,
        include_geometry=True,
        save_to_db=True
    )

# Now compare across elections
df_2024 = orchestrator.load_election_data('PRES_2024', entidad_id=9)  # CDMX
df_2018 = orchestrator.load_election_data('PRES_2018', entidad_id=9)

print(f"MORENA 2024: {df_2024['MORENA_PCT'].mean():.2f}%")
print(f"MORENA 2018: {df_2018['MORENA_PCT'].mean():.2f}%")
```

### Example 3: Query Specific States

```python
orchestrator = CleanVotesOrchestrator()

# Load Aguascalientes
df_ags = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,  # Aguascalientes
    as_geodataframe=True
)

# Load CDMX
df_cdmx = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=9,  # CDMX
    as_geodataframe=True
)

# Compare
print(f"Aguascalientes - MORENA: {df_ags['MORENA_PCT'].mean():.2f}%")
print(f"CDMX - MORENA: {df_cdmx['MORENA_PCT'].mean():.2f}%")
```

### Example 4: Export to GeoJSON

```python
orchestrator = CleanVotesOrchestrator()

# Process and save as GeoJSON
orchestrator.process_electoral_file(
    file_path='electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',
    include_geometry=True,
    save_geojson=True,
    geojson_output_path='data/insights/pres_2024_all_states.geojson'
)

# Or load and export later
gdf = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,
    as_geodataframe=True
)

from analytics.clean_votes import GeometryMerger
merger = GeometryMerger()
merger.save_geojson(gdf, 'aguascalientes_pres_2024.geojson')
```

## 🔧 Advanced Configuration

### Custom Column Exclusion

```python
from analytics.clean_votes import ElectoralDataCleaner

cleaner = ElectoralDataCleaner(
    columns_to_exclude=[
        'MY_CUSTOM_COL',
        'ANOTHER_COL_TO_REMOVE'
    ]
)
```

### Custom Header Detection

```python
from analytics.clean_votes import ElectoralDataReader

reader = ElectoralDataReader(
    header_indicators=['SECCION', 'MY_CUSTOM_KEY_COLUMN']
)
```

### Using Different Shapefiles

```python
from analytics.clean_votes import GeometryMerger

# Option 1: Explicit path
merger = GeometryMerger()
gdf = merger.merge_with_shapefile(
    df,
    shapefile_path='/path/to/custom/SECCION.shp'
)

# Option 2: Use different shapefile type
gdf = merger.merge_with_shapefile(
    df,
    entidad_id=1,
    shapefile_type='nacional'  # Instead of 'peepjf'
)
```

## ⚠️ Important Notes

### About Multiple Elections Per ENTIDAD

**Question:** Should I create one table per election, or combine multiple elections?

**Answer:** The current implementation creates **one table per (election, entidad) pair**:
- `election_pres_2024_01` (Presidential 2024, Aguascalientes)
- `election_pres_2024_09` (Presidential 2024, CDMX)
- `election_dip_2021_01` (Diputados 2021, Aguascalientes)

This approach:
✅ Keeps elections separate for easy comparison
✅ Allows different schemas per election type
✅ Maintains data integrity
✅ Easy to query specific elections

If you want to combine elections, you can load and merge them:

```python
import pandas as pd

df_2024 = orchestrator.load_election_data('PRES_2024', entidad_id=1)
df_2021 = orchestrator.load_election_data('DIP_2021', entidad_id=1)

df_2024['election_year'] = 2024
df_2021['election_year'] = 2021

df_combined = pd.concat([df_2024, df_2021], ignore_index=True)
```

### Encoding Issues

If you get encoding errors:

```python
# Try latin-1
orchestrator.process_electoral_file(
    file_path='problematic.csv',
    election_name='TEST',
    encoding='latin-1'
)
```

### Missing Shapefiles

If shapefiles are not found:

```python
# Process without geometry first
df = orchestrator.process_electoral_file(
    file_path='data.csv',
    election_name='TEST',
    include_geometry=False,  # Skip geometry
    save_to_db=True
)

# Add geometry later
from analytics.clean_votes import GeometryMerger
merger = GeometryMerger()
gdf = merger.merge_with_shapefile(df, entidad_id=1)
```

## 🐛 Troubleshooting

### "Header not found"
- Verify file contains columns like `CLAVE_CASILLA`, `ID_ENTIDAD`
- Try viewing the raw file to check structure
- Use custom header indicators

### "Table already exists"
- Use `if_exists='replace'` in `save_electoral_data()` (default)
- Or delete the table first: `db.delete_election(table_name)`

### "No matching geometries"
- Check that ENTIDAD and SECCION values match shapefile
- Some secciones may not exist in shapefiles
- Use `how='left'` in merge to keep all electoral data

## 📈 Next Steps

After processing data with this module, you can:

1. **Visualize** in the dashboard module
2. **Analyze** spatial patterns (Moran's I, hotspots)
3. **Compare** across elections and states
4. **Export** to various formats (GeoJSON, CSV, Parquet)
5. **Join** with other datasets (socioeconomic, demographic)

## 📚 References

- Main module: `analytics/src/analytics/clean_votes/`
- Example script: `analytics/examples/process_election_example.py`
- Detailed docs: `analytics/src/analytics/clean_votes/README.md`

## 💡 Tips

- Always provide `election_date` for temporal analysis
- Use consistent naming conventions for elections
- Back up the SQLite database regularly
- Enable geometry for spatial analysis
- Check `list_elections()` to see what's in the database

---

**Created:** November 22, 2025  
**Version:** 1.0  
**Module:** analytics/clean_votes


