# 🎉 Pipeline Updates - Summary

## ✅ Your Requirements - Implemented!

### **1. Skip Already Processed Files** ✅

The pipeline now checks the database before processing and **automatically skips** elections that already exist.

```bash
# First run - processes everything
uv run python analytics/run_pipeline.py

# Second run - skips what's already there
uv run python analytics/run_pipeline.py
# Output: "Skipping 5 already processed elections"
```

**How it works:**
- Checks database on startup
- Compares each file's inferred election name
- Skips if already in database
- Can be disabled with `--no-skip-existing`

### **2. Process Specific Folder** ✅

You can now pass a specific folder to process only those files.

```bash
# Process only 2024 folder
uv run python analytics/run_pipeline.py --folder 2024

# Process specific subfolder
uv run python analytics/run_pipeline.py --folder 2024/20240603_PREP

# Add new 2025 data and process only that
uv run python analytics/run_pipeline.py --folder 2025
```

### **3. Query Database from Notebook** ✅

Created `query_database.ipynb` with complete examples of:

- Listing all elections
- Loading specific election data
- Loading with geometry (GeoDataFrame)
- Comparing multiple states
- Direct SQL queries
- Time series analysis
- Exporting to other formats

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# List what's available
elections = orchestrator.list_available_elections()

# Load as DataFrame
df = orchestrator.load_election_data('PRES_2024', entidad_id=1)

# Load as GeoDataFrame (with geometry)
gdf = orchestrator.load_election_data('PRES_2024', entidad_id=1, as_geodataframe=True)
```

---

## 📋 Complete Usage

### Process New Folders (Recommended Workflow)

```bash
# Step 1: Add new folders to data/raw/electoral/2025/

# Step 2: Process only the new folder
uv run python analytics/run_pipeline.py --folder 2025

# Step 3: Verify
uv run python analytics/run_pipeline.py --list
```

### All Command Options

```bash
# Basic - processes all, skips existing
uv run python analytics/run_pipeline.py

# Dry-run - see what would be processed
uv run python analytics/run_pipeline.py --dry-run

# Specific folder - process only this folder
uv run python analytics/run_pipeline.py --folder 2024

# Specific years - process multiple years
uv run python analytics/run_pipeline.py --years 2024 2025

# Force reprocess - ignore what's in database
uv run python analytics/run_pipeline.py --no-skip-existing

# List database contents
uv run python analytics/run_pipeline.py --list
```

---

## 🎯 Use Cases

### Use Case 1: Add New Election Data

```bash
# 1. Add files to data/raw/electoral/2025/

# 2. Process only new folder (existing data is preserved)
uv run python analytics/run_pipeline.py --folder 2025

# Done! Old data is untouched, new data is added
```

### Use Case 2: Periodic Updates

```bash
# Run periodically - only processes new files
uv run python analytics/run_pipeline.py

# Automatically skips what's already processed
```

### Use Case 3: Reprocess Specific Election

```bash
# Force reprocess 2024 data
uv run python analytics/run_pipeline.py --folder 2024 --no-skip-existing
```

### Use Case 4: Query from Notebook

```python
# In Jupyter/notebook
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Get all available elections
elections = orchestrator.list_available_elections()

# Load and analyze
gdf = orchestrator.load_election_data('PRES_2024', entidad_id=9, as_geodataframe=True)

# Quick map
gdf.explore(column='MORENA_PCT', cmap='Reds')
```

---

## 📊 What You Get

### Database Structure

```
data/processed/electoral_data.db
├── election_pres_2024_01    (Presidential 2024, Aguascalientes)
├── election_pres_2024_02    (Baja California)
├── election_pres_2025_01    (Presidential 2025, Aguascalientes) ← New!
├── ...
└── election_metadata        (Tracks everything)
```

### Each Table Contains

- **Geographic IDs**: `ID_ENTIDAD`, `SECCION`, `ID_DISTRITO_FEDERAL`
- **Vote counts**: `PAN`, `PRI`, `MORENA`, coalitions, `NULOS`
- **Percentages**: `PAN_PCT`, `PRI_PCT`, `MORENA_PCT`, etc.
- **Totals**: `TOTAL_VOTOS_SUM`, `LISTA_NOMINAL`
- **Geometry**: `geometry` (WKT), `crs` (if included)

---

## 🔍 How Skip-Existing Works

```python
# Pseudocode
existing_elections = load_from_database()  # {'PRES_2024', 'DIP_2021', ...}

for file in found_files:
    election_name = infer_from_path(file)  # 'PRES_2024'
    
    if election_name in existing_elections:
        print(f"[SKIP] {election_name} - already processed")
        continue
    else:
        print(f"[NEW]  {election_name} - processing...")
        process(file)
```

**Important:** 
- Checks by **election name** (e.g., "PRES_2024")
- If election exists, assumes ALL entidades are processed
- Use `--no-skip-existing` to reprocess

---

## 📚 Documentation

### New Files Created

1. **`analytics/query_database.ipynb`** - Complete query examples
2. **`analytics/PIPELINE_FEATURES.md`** - Feature reference
3. **`PIPELINE_UPDATE_SUMMARY.md`** - This file

### Existing Files Updated

1. **`analytics/run_pipeline.py`** - Added skip-existing and folder options

### How to Learn More

- **Quick start**: `analytics/PIPELINE_FEATURES.md`
- **Full guide**: `PIPELINE_GUIDE.md`
- **Query examples**: `analytics/query_database.ipynb`
- **Module docs**: `analytics/README.md`

---

## 🎓 Quick Examples

### Example 1: Process New 2025 Data

```bash
# Add files to data/raw/electoral/2025/

# Process (skips existing 2024, 2021, etc.)
uv run python analytics/run_pipeline.py --folder 2025

# Or process all (auto-skips existing)
uv run python analytics/run_pipeline.py
```

### Example 2: Query in Python

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# List all
elections = orchestrator.list_available_elections()
print(f"Total: {len(elections)} elections")

# Load specific
df = orchestrator.load_election_data('PRES_2025', entidad_id=1)
print(f"Loaded {len(df)} rows")
```

### Example 3: Compare Elections

```python
# Load 2024 and 2025 for comparison
df_2024 = orchestrator.load_election_data('PRES_2024', entidad_id=9)
df_2025 = orchestrator.load_election_data('PRES_2025', entidad_id=9)

print(f"MORENA 2024: {df_2024['MORENA_PCT'].mean():.2f}%")
print(f"MORENA 2025: {df_2025['MORENA_PCT'].mean():.2f}%")
```

---

## ✨ Key Benefits

1. **No Reprocessing** - Skips what's already done (saves time!)
2. **Folder Targeting** - Process only what you need
3. **Easy Querying** - Simple Python API for data retrieval
4. **Incremental Updates** - Add new data without touching old
5. **Flexible** - Can force reprocess if needed

---

## 🚀 Next Steps

1. **Process your data:**
   ```bash
   uv run python analytics/run_pipeline.py --folder 2024
   ```

2. **Query in notebook:**
   ```bash
   jupyter notebook analytics/query_database.ipynb
   ```

3. **Run Moran's analysis:**
   ```bash
   uv run python analytics/examples/moran_analysis_example.py
   ```

---

**Summary:** The pipeline now intelligently skips processed data, lets you target specific folders, and provides easy database querying! 🎉

**Linter warnings:** The import warnings in `run_pipeline.py` are expected (runtime path manipulation) and don't affect functionality.


