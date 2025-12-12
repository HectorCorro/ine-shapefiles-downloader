# 🚀 Complete Pipeline Guide - From Raw Data to Moran's Analysis

## Overview

This guide shows you how to process multiple electoral data files and prepare them for Moran's spatial autocorrelation analysis.

## 📁 Your Directory Structure

```
data/
├── raw/
│   └── electoral/
│       ├── 2024/
│       │   ├── PRES_2024.csv
│       │   ├── 20240603_2005_PREP_PRES/
│       │   │   └── PRES_2024.csv
│       │   └── other_files.xlsx
│       ├── 2021/
│       │   ├── DIP_FED_2021.csv
│       │   └── SEN_2021.csv
│       ├── 2018/
│       │   └── PRES_2018.csv
│       └── ... (more years)
│
├── processed/
│   └── electoral_data.db         ← Auto-created by pipeline
│
├── insights/
│   └── moran_plots/               ← Created by analysis
│       ├── moran_morena_pct_aguascalientes.png
│       ├── moran_morena_pct_cdmx.png
│       └── moran_summary_pres_2024.csv
│
└── geo/
    ├── shapefiles_peepjf/         ← Needed for geometry
    └── productos_ine_nacional/
```

## 🔄 Complete Workflow

### Step 1: Run the Pipeline

The pipeline scans `data/raw/electoral/` for all electoral files and processes them into the database.

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

# Process ALL electoral files with geometry (for Moran's analysis)
uv run python analytics/run_pipeline.py

# Or dry-run to see what would be processed
uv run python analytics/run_pipeline.py --dry-run
```

**What the pipeline does:**
1. ✅ Scans `data/raw/electoral/` for CSV, Excel, and Parquet files
2. ✅ Auto-detects election name and date from file paths
3. ✅ Processes each file (cleaning + aggregation)
4. ✅ Merges with shapefile geometries (needed for Moran's)
5. ✅ Stores in SQLite database (one table per election/entidad)
6. ✅ Provides detailed progress and error reporting

### Step 2: Verify Data

```bash
# List all elections in database
uv run python analytics/run_pipeline.py --list

# Or from Python
python -c "
from analytics.clean_votes import CleanVotesOrchestrator
orchestrator = CleanVotesOrchestrator()
print(orchestrator.list_available_elections())
"
```

### Step 3: Run Moran's Analysis

```bash
# Analyze all entidades for an election
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024

# Or analyze specific entidad
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024 --entidad 1

# Analyze different variable
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024 --variable PAN_PCT
```

## 📋 Pipeline Options

### Basic Usage

```bash
# Process all files with geometry (default)
uv run python analytics/run_pipeline.py
```

### Advanced Options

```bash
# Process only specific years
uv run python analytics/run_pipeline.py --years 2024 2021

# Process without geometry (faster, but no Moran's analysis)
uv run python analytics/run_pipeline.py --no-geometry

# Use different shapefile type
uv run python analytics/run_pipeline.py --shapefile-type nacional

# Custom data directory
uv run python analytics/run_pipeline.py --data-dir path/to/electoral

# Stop on first error (default: continue on error)
uv run python analytics/run_pipeline.py --stop-on-error

# Dry run (show what would be processed)
uv run python analytics/run_pipeline.py --dry-run
```

## 🎓 Example: Complete Workflow

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

# 1. Check what files exist
ls -R data/raw/electoral/

# 2. Dry-run to see what would be processed
uv run python analytics/run_pipeline.py --dry-run

# 3. Run the pipeline
uv run python analytics/run_pipeline.py

# 4. Check what was created
uv run python analytics/run_pipeline.py --list

# 5. Run Moran's analysis
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024

# 6. Check results
ls data/insights/moran_plots/
```

## 🐍 Python API Usage

### Process Multiple Folders

```python
from pathlib import Path
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Process all electoral files
electoral_dir = Path('data/raw/electoral')

for year_dir in electoral_dir.iterdir():
    if year_dir.is_dir():
        print(f"Processing year: {year_dir.name}")
        
        for csv_file in year_dir.glob('**/*.csv'):
            try:
                result = orchestrator.process_electoral_file(
                    str(csv_file),  # Auto-infers name & date!
                    include_geometry=True,
                    save_to_db=True
                )
                print(f"  ✓ {csv_file.name}: {result.shape[0]} rows")
            except Exception as e:
                print(f"  ✗ {csv_file.name}: {e}")
```

### Load and Analyze

```python
from analytics.clean_votes import CleanVotesOrchestrator
from libpysal.weights import Queen
from esda.moran import Moran

# Load data with geometry
orchestrator = CleanVotesOrchestrator()
gdf = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,  # Aguascalientes
    as_geodataframe=True
)

# Perform Moran's analysis
w = Queen.from_dataframe(gdf)
moran = Moran(gdf['MORENA_PCT'], w)

print(f"Moran's I: {moran.I:.4f}")
print(f"P-value: {moran.p_sim:.4f}")

# Visualize
gdf.explore(column='MORENA_PCT', cmap='Reds')
```

## 📊 Output Structure

### Database Tables

```
electoral_data.db
├── election_pres_2024_01    (Presidential 2024, Aguascalientes)
├── election_pres_2024_02    (Presidential 2024, Baja California)
├── ...
├── election_dip_fed_2021_01 (Diputados 2021, Aguascalientes)
├── ...
└── election_metadata        (Tracks all elections)
```

### Each Table Contains:

| Column Type | Examples |
|-------------|----------|
| **IDs** | `ID_ENTIDAD`, `SECCION`, `ID_DISTRITO_FEDERAL` |
| **Names** | `ENTIDAD`, `DISTRITO_FEDERAL` |
| **Vote Counts** | `PAN`, `PRI`, `MORENA`, `NULOS` |
| **Percentages** | `PAN_PCT`, `PRI_PCT`, `MORENA_PCT` |
| **Totals** | `TOTAL_VOTOS_SUM`, `LISTA_NOMINAL` |
| **Geometry** | `geometry` (WKT), `crs` |

### Analysis Outputs

```
data/insights/moran_plots/
├── moran_morena_pct_aguascalientes.png
├── moran_morena_pct_baja_california.png
├── moran_morena_pct_cdmx.png
├── ...
└── moran_summary_pres_2024.csv
```

## 🔍 What Gets Auto-Detected

From file path: `data/raw/electoral/2024/PRES_2024.csv`

✅ **Election Type:** `PRES` (Presidential)  
✅ **Year:** `2024`  
✅ **Election Name:** `PRES_2024`  
✅ **Election Date:** `2024`

From path: `data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv`

✅ **Election Type:** `PRES`  
✅ **Full Date:** `2024-06-03` (extracted from `20240603`)  
✅ **Election Name:** `PRES_2024`

## 📈 Pipeline Progress Output

```
======================================================================
ELECTORAL DATA PROCESSING PIPELINE
======================================================================
Start time: 2025-11-22 15:30:00
Mode: LIVE PROCESSING

Found 5 electoral files to process
======================================================================

1. 2024/PRES_2024.csv
   → PRES_2024 (2024-06-03)
2. 2021/DIP_FED_2021.csv
   → DIP_FED_2021 (2021)
3. 2021/SEN_2021.csv
   → SEN_2021 (2021)
4. 2018/PRES_2018.csv
   → PRES_2018 (2018)
5. 2018/GOB_2018.csv
   → GOB_2018 (2018)

======================================================================
STARTING PROCESSING
======================================================================

[1/5] Processing: PRES_2024.csv
======================================================================
Processing electoral file: data/raw/electoral/2024/PRES_2024.csv
Election: PRES_2024
Date: 2024-06-03
======================================================================

[1/5] Reading data...
✓ Read 171410 rows, 54 columns

[2/5] Cleaning data...
✓ Cleaned data: 70544 rows, 44 columns

[3/5] Processing by entidad...

--- Processing ENTIDAD 01 ---
Entidad: AGUASCALIENTES, Rows: 685

[4/5] Merging with geometry...
✓ Merged with geometry: 659 rows

[5/5] Saving to database...
✓ Saved to table: election_pres_2024_01
✓ ENTIDAD 01 completed successfully

... (continues for all entidades)

======================================================================
PIPELINE COMPLETE
======================================================================
End time: 2025-11-22 15:45:00
Duration: 0:15:00

Results:
  Total files: 5
  Processed: 5
  Successful: 5 ✓
  Failed: 0 ✗
  Total rows: 250,000

Database: /path/to/electoral_data.db
Elections in database: 120

======================================================================
✅ PIPELINE READY FOR ANALYSIS!
======================================================================

Next steps:
  1. Load data from database
  2. Perform Moran's spatial autocorrelation analysis
  3. Create maps and visualizations
```

## 🚨 Error Handling

The pipeline is designed to be robust:

✅ **Continues on error** (by default) - processes all files even if one fails  
✅ **Detailed logging** - saved to `pipeline.log`  
✅ **Progress reporting** - shows what's being processed  
✅ **Error summary** - lists all failed files at the end

```bash
# Stop on first error (if you prefer)
uv run python analytics/run_pipeline.py --stop-on-error
```

## 💡 Pro Tips

1. **Always dry-run first** to see what will be processed
   ```bash
   uv run python analytics/run_pipeline.py --dry-run
   ```

2. **Process year by year** for large datasets
   ```bash
   uv run python analytics/run_pipeline.py --years 2024
   uv run python analytics/run_pipeline.py --years 2021
   ```

3. **Check logs** if something fails
   ```bash
   tail -f pipeline.log
   ```

4. **Use without geometry** for quick testing
   ```bash
   uv run python analytics/run_pipeline.py --no-geometry
   ```

5. **Verify database contents** before analysis
   ```bash
   uv run python analytics/run_pipeline.py --list
   ```

## 🎯 Common Workflows

### Workflow 1: First Time Setup

```bash
# 1. Check directory structure
ls -R data/raw/electoral/

# 2. Run pipeline
uv run python analytics/run_pipeline.py

# 3. Verify
uv run python analytics/run_pipeline.py --list

# 4. Analyze
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024
```

### Workflow 2: Add New Data

```bash
# 1. Add new files to data/raw/electoral/2025/

# 2. Process only new year
uv run python analytics/run_pipeline.py --years 2025

# 3. Analyze new data
uv run python analytics/examples/moran_analysis_example.py --election PRES_2025
```

### Workflow 3: Reprocess Everything

```bash
# Note: This will replace existing data in database

# 1. Backup database
cp data/processed/electoral_data.db data/processed/electoral_data.db.backup

# 2. Reprocess
uv run python analytics/run_pipeline.py

# 3. Verify
uv run python analytics/run_pipeline.py --list
```

## 📚 Next Steps After Pipeline

1. **Load Data:**
   ```python
   from analytics.clean_votes import CleanVotesOrchestrator
   orchestrator = CleanVotesOrchestrator()
   gdf = orchestrator.load_election_data('PRES_2024', entidad_id=1, as_geodataframe=True)
   ```

2. **Moran's Analysis:**
   ```bash
   uv run python analytics/examples/moran_analysis_example.py
   ```

3. **Custom Analysis:**
   - Use the data for any spatial analysis
   - Create custom visualizations
   - Compare across elections
   - Build dashboard

## 🔧 Dependencies

Required packages (already in `analytics/pyproject.toml`):
- `pandas` - Data manipulation
- `geopandas` - Geospatial data
- `openpyxl` - Excel files
- `pyarrow` - Parquet files
- `libpysal` - Spatial weights
- `esda` - Moran's I calculation
- `splot` - Spatial plots
- `matplotlib` - Visualization

Install with:
```bash
uv sync
```

---

**Created:** November 22, 2025  
**Purpose:** Process multiple electoral files and prepare for Moran's analysis  
**Scripts:** `analytics/run_pipeline.py`, `analytics/examples/moran_analysis_example.py`


