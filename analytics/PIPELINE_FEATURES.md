# Pipeline Features - Quick Reference

## ✨ New Features

### 1. **Skip Already Processed Elections** (Default: ON)

The pipeline automatically checks what's already in the database and skips it.

```bash
# First run - processes all files
uv run python analytics/run_pipeline.py

# Second run - skips already processed files
uv run python analytics/run_pipeline.py
# Output: "Skipping 5 already processed elections"

# Force reprocess everything
uv run python analytics/run_pipeline.py --no-skip-existing
```

### 2. **Process Specific Folder**

You can target a specific folder instead of processing everything.

```bash
# Process only 2024 folder
uv run python analytics/run_pipeline.py --folder 2024

# Process specific subfolder
uv run python analytics/run_pipeline.py --folder 2024/20240603_PREP

# Process multiple folders by running multiple times
uv run python analytics/run_pipeline.py --folder 2025
uv run python analytics/run_pipeline.py --folder 2026
```

## 📋 Complete Usage Examples

### Example 1: First Time Setup

```bash
# See what would be processed
uv run python analytics/run_pipeline.py --dry-run

# Process everything
uv run python analytics/run_pipeline.py

# Verify
uv run python analytics/run_pipeline.py --list
```

### Example 2: Add New Election Data

```bash
# Add new files to data/raw/electoral/2025/

# Process only the new folder (existing elections are skipped automatically)
uv run python analytics/run_pipeline.py --folder 2025

# Or process all but skip existing
uv run python analytics/run_pipeline.py
```

### Example 3: Reprocess Specific Year

```bash
# Force reprocess 2024 data
uv run python analytics/run_pipeline.py --folder 2024 --no-skip-existing
```

### Example 4: Process Multiple New Folders

```bash
# Add 2025 and 2026 folders to data/raw/electoral/

# Process 2025
uv run python analytics/run_pipeline.py --folder 2025

# Process 2026
uv run python analytics/run_pipeline.py --folder 2026

# Both will skip any already existing elections
```

## 🎯 All Command-Line Options

```bash
uv run python analytics/run_pipeline.py [OPTIONS]

Options:
  --data-dir PATH         Base directory (default: data/raw/electoral)
  --db-path PATH          Database path (default: auto-detect)
  --years YEAR [YEAR...]  Process specific years (e.g., --years 2024 2021)
  --folder PATH           Process specific folder (e.g., --folder 2024)
  --no-skip-existing      Reprocess existing elections (force)
  --no-geometry           Skip geometry (faster, no spatial analysis)
  --shapefile-type TYPE   Shapefile type: peepjf or nacional
  --dry-run               Show what would be processed
  --stop-on-error         Stop on first error (default: continue)
  --list                  List elections in database and exit
  -h, --help              Show help message
```

## 🔍 How Skip-Existing Works

```python
# The pipeline checks the database before processing
existing_elections = orchestrator.list_available_elections()

# For each file found:
if election_name in existing_elections:
    print(f"[SKIP] {election_name} - already processed")
else:
    print(f"[NEW]  {election_name} - processing...")
    process_file()
```

### What Gets Checked?

- **Election name** (e.g., "PRES_2024")
- If the election exists in the database, ALL entidades are assumed processed
- To reprocess, use `--no-skip-existing` flag

### When to Use `--no-skip-existing`?

- Data updated at source (new corrections)
- Want to recompute with different settings
- Database was corrupted
- Testing changes

## 📊 Progress Output

```bash
$ uv run python analytics/run_pipeline.py

======================================================================
ELECTORAL DATA PROCESSING PIPELINE
======================================================================
Start time: 2025-11-22 16:00:00
Mode: LIVE PROCESSING
Skip existing: ENABLED

Found 3 existing elections in database

Scanning for electoral files in: data/raw/electoral/
Found 10 electoral files

======================================================================
FOUND 10 FILES TO PROCESS
======================================================================

1. [SKIP] 2024/PRES_2024.csv
   → PRES_2024 (2024-06-03)
2. [SKIP] 2021/DIP_FED_2021.csv
   → DIP_FED_2021 (2021)
3. [NEW]  2025/PRES_2025.csv
   → PRES_2025 (2025-06-01)
...

Skipping 7 already processed elections

======================================================================
STARTING PROCESSING
======================================================================

[1/3] Processing: PRES_2025.csv
...
```

## 💾 Database Querying

See the **`query_database.ipynb`** notebook for examples of:

1. Listing all elections
2. Loading specific election data
3. Loading with geometry (GeoDataFrame)
4. Comparing multiple states
5. Direct SQL queries
6. Time series analysis
7. Exporting to CSV/Parquet/GeoJSON

### Quick Query Examples

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# List what's available
elections = orchestrator.list_available_elections()

# Load specific data
df = orchestrator.load_election_data('PRES_2024', entidad_id=1)

# Load with geometry
gdf = orchestrator.load_election_data('PRES_2024', entidad_id=1, as_geodataframe=True)

# Quick map
gdf.explore(column='MORENA_PCT', cmap='Reds')
```

## 🚨 Important Notes

### About Skip-Existing

- **Default behavior**: ENABLED (skips existing)
- **Check**: By election name (not by file)
- **Override**: Use `--no-skip-existing` flag
- **Safety**: Always backs up database first (recommended)

### About Folders

- `--folder` processes ONLY that folder
- `--years` filters by year directories
- Can't use both `--folder` and `--years` together
- Use `--folder` for more specific control

### About Reprocessing

```bash
# Backup first!
cp data/processed/electoral_data.db data/processed/electoral_data.db.backup

# Then reprocess
uv run python analytics/run_pipeline.py --no-skip-existing
```

## 📚 Related Documentation

- **`PIPELINE_GUIDE.md`** - Complete pipeline workflow
- **`query_database.ipynb`** - How to query the database
- **`QUICK_START_UV.md`** - Quick start guide
- **`README.md`** - Module overview

---

**Updated:** November 22, 2025  
**Features:** Skip-existing + Folder-specific processing


