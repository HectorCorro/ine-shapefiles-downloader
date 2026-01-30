# Analytics Module

Electoral data processing and spatial analysis for Mexican elections.

## Features

### 1. Clean Votes Module (`clean_votes/`)

Complete pipeline for cleaning and processing electoral data:

- **Flexible file reading** - CSV, Excel, Parquet with auto header detection
- **Data cleaning** - Standardization, type conversion, aggregation
- **Geometry integration** - Automatic shapefile merging
- **Database storage** - SQLite with metadata tracking
- **Auto-inference** - Election name and date from file paths

### 2. Pipeline Script (`run_pipeline.py`)

Batch process multiple electoral files:

```bash
# Process all files in data/raw/electoral/
uv run python analytics/run_pipeline.py

# Dry-run to see what would be processed
uv run python analytics/run_pipeline.py --dry-run

# Process specific years
uv run python analytics/run_pipeline.py --years 2024 2021
```

### 3. Moran's Analysis (`examples/moran_analysis_example.py`)

Spatial autocorrelation analysis:

```bash
# Analyze all states for an election
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024

# Analyze specific state
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024 --entidad 1
```

## Quick Start

```bash
# 1. Sync workspace
uv sync

# 2. Run pipeline (processes all files in data/raw/electoral/)
uv run python analytics/run_pipeline.py

# 3. Run Moran's analysis
uv run python analytics/examples/moran_analysis_example.py
```

## Python API

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Initialize
orchestrator = CleanVotesOrchestrator()

# Process a file (auto-infers election name and date)
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',
    include_geometry=True,
    save_to_db=True
)

# Load from database
gdf = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,
    as_geodataframe=True
)

# Perform Moran's analysis
from libpysal.weights import Queen
from esda.moran import Moran

w = Queen.from_dataframe(gdf)
moran = Moran(gdf['MORENA_PCT'], w)
print(f"Moran's I: {moran.I:.4f}, p-value: {moran.p_sim:.4f}")
```

## Documentation

- **`QUICK_START_UV.md`** - Quick start with uv
- **`src/analytics/clean_votes/README.md`** - Detailed module documentation
- **`PIPELINE_GUIDE.md`** (in project root) - Complete pipeline guide
- **`UPDATED_FEATURES.md`** (in project root) - Auto-inference features

## Dependencies

Core:
- `pandas` - Data manipulation
- `geopandas` - Geospatial operations
- `numpy` - Numerical operations
- `shapely` - Geometric objects

File formats:
- `openpyxl` - Excel files
- `pyarrow` - Parquet files

Spatial analysis:
- `libpysal` - Spatial weights
- `esda` - Moran's I and other spatial statistics
- `splot` - Spatial visualization
- `matplotlib` - Plotting

Machine learning:
- `scikit-learn` - Statistical analysis

## Project Structure

```
analytics/
├── src/analytics/
│   └── clean_votes/
│       ├── __init__.py
│       ├── reader.py           # File reading
│       ├── cleaner.py          # Data cleaning
│       ├── geometry.py         # Shapefile integration
│       ├── database.py         # SQLite storage
│       ├── orchestrator.py     # Main coordinator
│       ├── utils.py            # Helper functions
│       └── README.md
│
├── examples/
│   ├── auto_infer_example.py
│   ├── moran_analysis_example.py
│   └── process_election_example.py
│
├── run_pipeline.py             # Batch processing script
├── init_database.py            # Database initialization
├── demo_clean_votes.ipynb      # Demo notebook
├── QUICK_START_UV.md
└── README.md                   # This file
```

## Installation

```bash
# Add dependencies to analytics package
uv add libpysal esda splot matplotlib --package analytics

# Or sync entire workspace
uv sync
```

## Usage Examples

### Process Multiple Elections

```python
from pathlib import Path
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Process all files in a directory
for csv_file in Path('data/raw/electoral').rglob('*.csv'):
    result = orchestrator.process_electoral_file(
        str(csv_file),
        include_geometry=True,
        save_to_db=True
    )
```

### Compare Across States

```python
import pandas as pd

results = []
for entidad_id in range(1, 33):  # All 32 states
    try:
        gdf = orchestrator.load_election_data('PRES_2024', entidad_id)
        results.append({
            'Entidad ID': entidad_id,
            'MORENA %': gdf['MORENA_PCT'].mean(),
            'Sections': len(gdf)
        })
    except:
        pass

comparison = pd.DataFrame(results)
```

### Batch Moran's Analysis

```bash
# Analyze all states for an election
uv run python analytics/examples/moran_analysis_example.py --election PRES_2024

# Output: plots and CSV summary in data/insights/moran_plots/
```

## Output

### Database Structure

```
data/processed/electoral_data.db
├── election_pres_2024_01    (Aguascalientes)
├── election_pres_2024_02    (Baja California)
├── ...
└── election_metadata        (Tracks all elections)
```

### Analysis Outputs

```
data/insights/moran_plots/
├── moran_morena_pct_aguascalientes.png
├── moran_morena_pct_cdmx.png
└── moran_summary_pres_2024.csv
```

## Contributing

When adding new features:
1. Follow the existing code structure
2. Use `pathlib` for file operations
3. Add type hints
4. Include docstrings
5. Test with `uv run pytest`

## License

Part of the INE Shapefiles Downloader project.




