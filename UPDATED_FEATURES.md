# 🚀 Updated Features - Auto-Inference & Auto-Creation

## ✨ What's New

I've updated the `clean_votes` module with powerful new features that make it even easier to use:

### 1. **Auto-Inference of Election Metadata** 🎯

The system now **automatically extracts** election name and date from file paths!

#### Before (Manual):
```python
orchestrator.process_electoral_file(
    file_path='data/raw/electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',      # ← Had to specify
    election_date='2024-06-03'       # ← Had to specify
)
```

#### After (Automatic):
```python
orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv'  # ← Just the path!
)
# Auto-detects: election_name='PRES_2024', election_date='2024'
```

### 2. **Auto-Creation of SQLite Database** 🗄️

The database is **automatically created** when you first use the system. No manual setup needed!

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Database is created automatically at: data/processed/electoral_data.db
orchestrator = CleanVotesOrchestrator()

# That's it! Database exists and is ready to use
```

### 3. **Full pathlib Support** 📁

Everything now uses `pathlib.Path` for robust cross-platform file handling.

---

## 📋 Supported File Path Patterns

The system automatically detects election metadata from these patterns:

### Presidential Elections
```python
'data/raw/electoral/2024/PRES_2024.csv'
→ election_name='PRES_2024', election_date='2024'

'data/raw/electoral/2024/PRESIDENTE_2024.csv'
→ election_name='PRES_2024', election_date='2024'

'data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv'
→ election_name='PRES_2024', election_date='2024-06-03'  # Full date!
```

### Federal Deputies
```python
'data/raw/electoral/2021/DIP_FED_2021.csv'
→ election_name='DIP_FED_2021', election_date='2021'

'data/raw/electoral/2021/DIPUTADOS_2021.csv'
→ election_name='DIP_FED_2021', election_date='2021'
```

### Senators
```python
'data/raw/electoral/2018/SEN_2018.csv'
→ election_name='SEN_2018', election_date='2018'

'data/raw/electoral/2018/SENADORES_2018.csv'
→ election_name='SEN_2018', election_date='2018'
```

### Governors
```python
'data/raw/electoral/2021/GOB_2021.csv'
→ election_name='GOB_2021', election_date='2021'
```

### Detection Logic

The system looks for:
1. **Year** in path: Searches for `YYYY` pattern (e.g., `/2024/`, `/2021/`)
2. **Full date** in directory name: `YYYYMMDD` pattern (e.g., `20240603_2005_PREP_PRES`)
3. **Election type** in filename:
   - `PRES`, `PRESIDENTE`, `PRESIDENTIAL` → `PRES`
   - `DIP`, `DIPUTADO`, `DIPUTADOS` → `DIP_FED`
   - `SEN`, `SENADOR`, `SENADORES` → `SEN`
   - `GOB`, `GOBERNADOR` → `GOB`
   - `AYU`, `AYUNTAMIENTO` → `AYU`

---

## 🎯 Usage Examples

### Example 1: Simplest Usage (Auto-Everything)

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Just provide the file path - everything else is automatic!
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',
    include_geometry=True,
    save_to_db=True
)

print(f"Processed: {result.shape[0]} rows")
# Database automatically created at: data/processed/electoral_data.db
# Election name automatically set to: PRES_2024
# Election date automatically set to: 2024
```

### Example 2: With Full Date Extraction

```python
# File in path with date: electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv'
)
# Auto-detects: election_name='PRES_2024', election_date='2024-06-03'
```

### Example 3: Override Auto-Inference (If Needed)

```python
# You can still override if the filename is non-standard
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/weird_filename.csv',
    election_name='CUSTOM_2024',    # Explicit override
    election_date='2024-01-15',      # Explicit override
    include_geometry=True
)
```

### Example 4: Process Multiple Elections

```python
from pathlib import Path

orchestrator = CleanVotesOrchestrator()

# Process all elections in a directory
electoral_dir = Path('data/raw/electoral')

for year_dir in electoral_dir.iterdir():
    if year_dir.is_dir():
        for csv_file in year_dir.glob('**/*.csv'):
            print(f"Processing: {csv_file}")
            try:
                result = orchestrator.process_electoral_file(
                    str(csv_file),  # Auto-infers name and date!
                    include_geometry=True,
                    save_to_db=True
                )
                print(f"  ✓ Processed {result.shape[0]} rows")
            except Exception as e:
                print(f"  ✗ Error: {e}")
```

---

## 🔧 Database Initialization

### Automatic Initialization

The database is created automatically when you first use the orchestrator:

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Database created automatically on first use
orchestrator = CleanVotesOrchestrator()
# → Creates data/processed/electoral_data.db
```

### Manual Initialization (Optional)

If you want to pre-create the database:

```bash
# Using uv
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader
uv run python analytics/init_database.py

# Or with custom path
uv run python analytics/init_database.py --db-path custom/path/elections.db

# Check default database path
uv run python analytics/init_database.py --show-path
```

### Custom Database Location

```python
# Specify custom database path
orchestrator = CleanVotesOrchestrator(
    db_path='custom/path/my_elections.db'
)
# Database will be created at specified location
```

---

## 📁 Expected Directory Structure

```
data/
├── raw/
│   └── electoral/
│       ├── 2024/
│       │   ├── PRES_2024.csv                          # ← Your raw data
│       │   └── 20240603_2005_PREP_PRES/
│       │       └── PRES_2024.csv
│       ├── 2021/
│       │   ├── DIP_FED_2021.csv
│       │   └── SEN_2021.csv
│       └── 2018/
│           └── PRES_2018.csv
│
├── processed/
│   └── electoral_data.db                              # ← Auto-created database
│
├── insights/                                           # ← Optional GeoJSON outputs
└── geo/                                                # ← Shapefiles (if using geometry)
    ├── shapefiles_peepjf/
    └── productos_ine_nacional/
```

---

## 🚀 Complete Workflow (uv)

### Step 1: Ensure Workspace is Synced

```bash
cd /Users/hectorcorro/Documents/Labex/ine-shapefiles-downloader
uv sync
```

### Step 2: Process Your Data

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Process 2024 Presidential election
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',  # Auto-infers everything!
    include_geometry=True,
    save_to_db=True
)

print(f"✓ Processed {result.shape[0]} rows")
```

### Step 3: Query Results

```python
# List all elections in database
elections = orchestrator.list_available_elections()
print(elections)

# Load specific election
df = orchestrator.load_election_data('PRES_2024', entidad_id=1)
```

---

## 🎓 Demo Scripts

### 1. Test Auto-Inference

```bash
uv run python analytics/examples/auto_infer_example.py
```

This shows how the system automatically extracts election metadata from various file path patterns.

### 2. Initialize Database

```bash
uv run python analytics/init_database.py
```

This pre-creates the database (though it's created automatically anyway).

---

## 📊 Quick Reference Table

| Feature | Before | After |
|---------|--------|-------|
| **Election Name** | Manual: `election_name='PRES_2024'` | Auto-detected from path |
| **Election Date** | Manual: `election_date='2024-06-03'` | Auto-detected from path |
| **Database Creation** | Manual setup required | Auto-created on first use |
| **Path Handling** | String-based | Full `pathlib` support |
| **Minimum Code** | 3 required parameters | 1 parameter (file path) |

---

## 💡 Tips

1. **Organize by Year**: Keep files in `data/raw/electoral/YYYY/` structure
2. **Standard Naming**: Use patterns like `PRES_2024.csv`, `DIP_FED_2021.csv`
3. **Full Dates**: Put date in directory name: `20240603_PRES/` for full date extraction
4. **Override When Needed**: You can still provide explicit parameters if filenames are non-standard

---

## 🔍 How It Works

```python
# When you call this:
orchestrator.process_electoral_file('data/raw/electoral/2024/PRES_2024.csv')

# The system does this internally:
# 1. Parse file path: Path('data/raw/electoral/2024/PRES_2024.csv')
# 2. Extract year from path: '2024'
# 3. Extract election type from filename: 'PRES'
# 4. Build election_name: 'PRES_2024'
# 5. Set election_date: '2024'
# 6. Create database if doesn't exist
# 7. Process and store data
```

---

## ✅ Summary

**What Changed:**
- ✅ Auto-inference of election name from file path/name
- ✅ Auto-inference of election date (year or full date)
- ✅ Auto-creation of SQLite database
- ✅ Full pathlib support throughout
- ✅ Smart detection of election types (PRES, DIP_FED, SEN, GOB, AYU)

**What Stayed the Same:**
- ✅ All existing functionality still works
- ✅ You can still provide explicit parameters
- ✅ Same output format and database structure
- ✅ Same API and method signatures

**Result:**
```python
# Old way: 5 parameters
orchestrator.process_electoral_file(
    file_path='data/raw/electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,
    save_to_db=True
)

# New way: 1 parameter!
orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv'
)
```

---

**Updated:** November 22, 2025  
**Features:** Auto-inference + Auto-creation + pathlib  
**Status:** ✅ Ready to use with `uv`


