# 🚀 Quick Start with uv

## Installation

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

# Sync workspace (installs all dependencies)
uv sync

# Add Excel support if not already added
uv add openpyxl --package analytics
```

## Instant Usage

### Option 1: Python (Simplest)

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Database is auto-created, election name/date auto-detected!
orchestrator = CleanVotesOrchestrator()

# Just provide the file path
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',
    include_geometry=True,  # Optional: merge with shapefiles
    save_to_db=True         # Optional: save to SQLite
)

print(f"✓ Processed {result.shape[0]} rows!")
```

### Option 2: Command Line

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader

# Process any electoral file
uv run python -m analytics.clean_votes.orchestrator \
    data/raw/electoral/2024/PRES_2024.csv \
    --geometry

# List what's in database
uv run python -m analytics.clean_votes.orchestrator --list-elections
```

## Your Directory Structure

```
/Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader/
├── data/
│   ├── raw/
│   │   └── electoral/
│   │       ├── 2024/
│   │       │   └── PRES_2024.csv              ← Your input files
│   │       ├── 2021/
│   │       └── 2018/
│   │
│   ├── processed/
│   │   └── electoral_data.db                  ← Auto-created database
│   │
│   ├── insights/                               ← GeoJSON outputs (optional)
│   └── geo/                                    ← Shapefiles (for geometry)
│       ├── shapefiles_peepjf/
│       └── productos_ine_nacional/
│
└── analytics/
    ├── src/analytics/clean_votes/              ← The module
    ├── init_database.py                        ← Initialize DB
    └── examples/
        └── auto_infer_example.py               ← Demo script
```

## File Path Patterns (Auto-Detected)

The system automatically extracts election info from your file paths:

```python
# Pattern: data/raw/electoral/YEAR/TYPE_YEAR.csv
'data/raw/electoral/2024/PRES_2024.csv'
→ election_name='PRES_2024', date='2024'

'data/raw/electoral/2021/DIP_FED_2021.csv'
→ election_name='DIP_FED_2021', date='2021'

'data/raw/electoral/2018/SEN_2018.csv'
→ election_name='SEN_2018', date='2018'

# With full date in directory name
'data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv'
→ election_name='PRES_2024', date='2024-06-03'
```

**Supported election types:**
- `PRES`, `PRESIDENTE` → Presidential
- `DIP`, `DIPUTADOS` → Federal Deputies
- `SEN`, `SENADORES` → Senators
- `GOB`, `GOBERNADOR` → Governor
- `AYU`, `AYUNTAMIENTO` → Municipal

## Complete Example

```python
from analytics.clean_votes import CleanVotesOrchestrator
from pathlib import Path

# Initialize (database auto-created)
orchestrator = CleanVotesOrchestrator()

# Process 2024 Presidential election
# (election name and date auto-detected from path!)
result_2024 = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',
    include_geometry=True,
    save_to_db=True
)

# Process 2021 Deputies election
result_2021 = orchestrator.process_electoral_file(
    'data/raw/electoral/2021/DIP_FED_2021.csv',
    include_geometry=True,
    save_to_db=True
)

# List all elections in database
elections = orchestrator.list_available_elections()
print(elections)

# Load specific election + state
df_aguascalientes = orchestrator.load_election_data(
    election_name='PRES_2024',
    entidad_id=1,  # Aguascalientes
    as_geodataframe=True
)

# Compare states
df_cdmx = orchestrator.load_election_data('PRES_2024', entidad_id=9)
print(f"Aguascalientes MORENA: {df_aguascalientes['MORENA_PCT'].mean():.2f}%")
print(f"CDMX MORENA: {df_cdmx['MORENA_PCT'].mean():.2f}%")
```

## Database Info

**Location:** `data/processed/electoral_data.db` (auto-created)

**Structure:**
- One table per (election, entidad): `election_pres_2024_01`, `election_pres_2024_09`, etc.
- Metadata table: `election_metadata` (tracks all elections)

**Each table contains:**
- Identifiers: `ID_ENTIDAD`, `SECCION`, `ID_DISTRITO_FEDERAL`
- Vote counts: `PAN`, `PRI`, `MORENA`, coalitions, `NULOS`
- Percentages: `PAN_PCT`, `PRI_PCT`, `MORENA_PCT`, etc.
- Totals: `TOTAL_VOTOS_SUM`, `LISTA_NOMINAL`
- Geometry (optional): `geometry`, `crs`

## Demo Scripts

```bash
# See how auto-inference works
uv run python analytics/examples/auto_infer_example.py

# Initialize database (optional - it's auto-created anyway)
uv run python analytics/init_database.py

# Check default database path
uv run python analytics/init_database.py --show-path
```

## Tips

1. **Organize by Year:** `data/raw/electoral/YYYY/`
2. **Standard Names:** `PRES_2024.csv`, `DIP_FED_2021.csv`, `SEN_2018.csv`
3. **Full Dates:** Put in directory: `20240603_PRES/` for date extraction
4. **Override When Needed:** Can still provide explicit `election_name` and `election_date`

## Troubleshooting

**"Module not found"**
```bash
uv sync  # Sync workspace first
```

**"Database path doesn't exist"**
→ It's auto-created! Just run your code.

**"Can't infer election name"**
→ Provide explicit parameters:
```python
orchestrator.process_electoral_file(
    'weird_filename.csv',
    election_name='CUSTOM_2024',
    election_date='2024-01-15'
)
```

## Summary

**✅ What's Auto-Detected:**
- Election name (from filename: `PRES_2024`, `DIP_FED_2021`, etc.)
- Election date (from path: year or full date)
- Database creation (on first use)
- Entidades in data (processes all automatically)

**✅ What You Provide:**
- File path
- Whether to include geometry
- Whether to save to database

**Result: 1-line data processing!**

```python
orchestrator.process_electoral_file('data/raw/electoral/2024/PRES_2024.csv')
```

---

**Updated:** November 22, 2025  
**For:** uv workspace environments  
**Location:** `/Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader/`

