# Clean Votes Module

A comprehensive system for cleaning, processing, and storing Mexican electoral data.

## Features

- **Flexible File Reading**: Supports CSV, Excel, and Parquet formats with automatic header detection
- **Data Cleaning**: Standardizes columns, converts numeric values, and aggregates by section
- **Geometry Integration**: Merges electoral data with shapefiles for geospatial analysis
- **Database Storage**: Stores processed data in SQLite with metadata tracking
- **Multi-Entidad Support**: Processes data for all states in a single run

## Quick Start

### Basic Usage (Python API)

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Initialize orchestrator
orchestrator = CleanVotesOrchestrator(
    db_path='data/processed/electoral_data.db'
)

# Process an electoral file
df = orchestrator.process_electoral_file(
    file_path='data/raw/electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,  # Merge with shapefiles
    save_to_db=True
)

# List available elections
elections = orchestrator.list_available_elections()
print(elections)

# Load specific election data
df = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,  # Aguascalientes
    as_geodataframe=True
)
```

### Command-Line Usage

```bash
# Process a file
python -m analytics.clean_votes.orchestrator \
    data/raw/electoral/2024/PRES_2024.csv \
    PRES_2024 \
    --election-date 2024-06-03 \
    --geometry \
    --geojson data/insights/pres_2024.geojson

# List all elections in database
python -m analytics.clean_votes.orchestrator --list-elections

# Process without geometry
python -m analytics.clean_votes.orchestrator \
    data/raw/electoral/2024/PRES_2024.csv \
    PRES_2024 \
    --election-date 2024-06-03

# Custom database path
python -m analytics.clean_votes.orchestrator \
    mydata.csv \
    LOCAL_2023 \
    --db-path custom/path/elections.db
```

## Architecture

### Modules

1. **`reader.py`**: Flexible file reader with automatic header detection
   - Searches for key columns like `CLAVE_CASILLA`, `ID_ENTIDAD`
   - Handles CSV files with metadata rows before headers
   - Supports multiple encodings

2. **`cleaner.py`**: Data transformation pipeline
   - Removes unnecessary columns
   - Converts vote columns to numeric
   - Calculates totals and percentages
   - Aggregates by ENTIDAD and SECCION
   - Merges vote data with lista nominal

3. **`geometry.py`**: Shapefile integration
   - Auto-detects shapefile paths by ENTIDAD
   - Supports 'peepjf' and 'nacional' shapefile types
   - Handles geometry reprojection
   - Exports to GeoJSON

4. **`database.py`**: SQLite storage with metadata
   - Creates separate tables per election and entidad
   - Stores geometry as WKT
   - Tracks data lineage and timestamps
   - Provides query interface

5. **`orchestrator.py`**: Main workflow coordinator
   - Chains all modules together
   - Handles multi-entidad processing
   - Provides CLI and Python API

## Workflow

```
Raw Data (CSV/Excel/Parquet)
    ↓
[1] Read & Detect Headers
    ↓
[2] Clean & Transform
    ↓
[3] Aggregate by ENTIDAD, SECCION
    ↓
[4] Merge with Geometry (optional)
    ↓
[5] Save to SQLite
    ↓
Clean Electoral Data (by ENTIDAD)
```

## Database Schema

### Election Tables

Each election and entidad gets its own table: `election_{name}_{id:02d}`

Example: `election_pres_2024_01` (Presidential 2024, Aguascalientes)

**Columns**:
- Descriptive: `ENTIDAD`, `ID_ENTIDAD`, `DISTRITO_FEDERAL`, `SECCION`
- Vote counts: `PAN`, `PRI`, `MORENA`, etc.
- Percentages: `PAN_PCT`, `PRI_PCT`, `MORENA_PCT`, etc.
- Totals: `TOTAL_VOTOS_SUM`, `LISTA_NOMINAL`
- Geometry (optional): `geometry` (as WKT), `crs`

### Metadata Table

`election_metadata` tracks all processed elections:

- `election_name`: Election identifier
- `election_date`: Date of election
- `entidad_id`: State ID (1-32)
- `table_name`: Database table name
- `has_geometry`: Whether geometry is included
- `row_count`: Number of rows
- `source_file`: Original data file
- `shapefile_path`: Shapefile used (if any)
- `created_at`, `updated_at`: Timestamps

## Advanced Usage

### Custom Column Exclusion

```python
from analytics.clean_votes import ElectoralDataCleaner

cleaner = ElectoralDataCleaner(
    columns_to_exclude=['CUSTOM_COL_1', 'CUSTOM_COL_2']
)
```

### Custom Header Detection

```python
from analytics.clean_votes import ElectoralDataReader

reader = ElectoralDataReader(
    header_indicators=['SECCION', 'MY_CUSTOM_KEY']
)
```

### Multiple Elections

```python
orchestrator = CleanVotesOrchestrator()

# Process multiple elections
for election in ['PRES_2024', 'DIP_2021', 'GOB_2018']:
    orchestrator.process_electoral_file(
        file_path=f'data/raw/{election}.csv',
        election_name=election,
        include_geometry=True,
        save_to_db=True
    )

# Compare across elections
df_2024 = orchestrator.load_election_data('PRES_2024', entidad_id=9)
df_2021 = orchestrator.load_election_data('DIP_2021', entidad_id=9)
```

## Data Quality

The cleaner automatically:
- Converts numeric columns with error handling
- Imputes missing values as 0
- Removes duplicate rows per section
- Validates key columns exist
- Standardizes ID formats with zero-padding

## Error Handling

- Continues processing even if one entidad fails
- Logs all errors with full tracebacks
- Skips geometry merge if shapefiles not found
- Falls back to alternative encodings for CSV

## Best Practices

1. **Organize by Election**: Use consistent naming like `PRES_2024`, `DIP_2021`
2. **Include Dates**: Always provide `election_date` for temporal analysis
3. **Use Geometry**: Enable `include_geometry` for spatial analysis
4. **Backup Database**: The SQLite file contains all processed data
5. **Check Metadata**: Use `list_available_elections()` to verify what's stored

## Troubleshooting

### "Header not found"
- Check that file contains key columns like `CLAVE_CASILLA`
- Try different encoding: `encoding='latin-1'`

### "Shapefile not found"
- Verify shapefile_base_dir points to `data/geo`
- Check that shapefiles are organized by state folders
- Use explicit `shapefile_path` parameter

### "No matching geometries"
- Verify ENTIDAD and SECCION values match shapefile
- Check data types (should be Int64)
- Some secciones may not have geometries in shapefiles

## Example: Reproduce Notebook Workflow

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Same as clean_votes.ipynb
orchestrator = CleanVotesOrchestrator()

df = orchestrator.process_electoral_file(
    file_path='electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,
    shapefile_type='peepjf',
    save_to_db=True,
    save_geojson=True,
    geojson_output_path='data/insights/pres_2024_aguascalientes.geojson'
)

# Result: Same as gdf_final in the notebook
print(f"Shape: {df.shape}")
print(f"Has geometry: {'geometry' in df.columns}")
```

## Future Enhancements

- [ ] Support for coalition vote splitting
- [ ] Automatic detection of party columns
- [ ] Multi-level aggregations (Municipio, Distrito)
- [ ] Integration with PREP real-time data
- [ ] PostGIS support for large datasets
- [ ] Parallel processing for multiple files

## Questions?

See the module docstrings or run:
```python
help(CleanVotesOrchestrator)
```


