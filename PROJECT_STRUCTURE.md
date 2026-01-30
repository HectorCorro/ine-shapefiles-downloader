# Project Structure - INE Electoral Data Analysis

## 📋 Overview

This project follows a clean **3-layer architecture** for Mexican electoral data analysis:

1. **Ingestion** - Data acquisition from INE/PEEPJF
2. **Analytics** - Data cleaning, homologation, and storage in database
3. **Dashboard** - Visualization from database only

## 🏗️ Current Structure

```
ine-shapefiles-downloader/
│
├── README.md                    # Main project documentation
├── pyproject.toml               # Workspace configuration (uv)
├── uv.lock                      # Dependency lock file
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── Dockerfile                   # Container configuration
├── validate_setup.py            # Setup validation script
│
├── ingestion/                   # 📥 Layer 1: Data Acquisition
│   ├── README.md                # Module documentation
│   ├── pyproject.toml           # Module dependencies
│   └── src/ingestion/
│       ├── __init__.py
│       ├── download_nacional.py # Download INE shapefiles
│       ├── download_peepjf.py   # Download PEEPJF shapefiles
│       └── utils/
│           ├── __init__.py
│           └── s3_utils.py      # S3 upload utilities
│
├── analytics/                   # 📊 Layer 2: Processing & Storage
│   ├── README.md                # Module documentation
│   ├── pyproject.toml           # Module dependencies
│   ├── init_database.py         # Database initialization
│   ├── run_pipeline.py          # Batch processing script
│   ├── demo_clean_votes.ipynb   # Demo notebook
│   ├── query_database.ipynb     # Query examples
│   ├── src/analytics/
│   │   ├── __init__.py
│   │   └── clean_votes/         # Main processing package
│   │       ├── __init__.py
│   │       ├── reader.py        # File reading
│   │       ├── cleaner.py       # Data cleaning
│   │       ├── column_mapper.py # Column homologation
│   │       ├── geometry.py      # Geometry processing
│   │       ├── database.py      # Database operations
│   │       ├── orchestrator.py  # Main coordinator
│   │       └── utils.py         # Helper functions
│   ├── examples/                # Usage examples
│   │   ├── auto_infer_example.py
│   │   ├── moran_analysis_example.py
│   │   └── process_election_example.py
│   └── utils/                   # Utility scripts
│       ├── add_geometry_to_existing.py
│       └── check_geometry.py
│
├── dashboard/                   # 📈 Layer 3: Visualization
│   ├── README.md                # Module documentation
│   ├── pyproject.toml           # Module dependencies
│   ├── .streamlit/
│   │   └── config.toml          # Streamlit configuration
│   ├── src/dashboard/
│   │   ├── __init__.py
│   │   ├── app.py               # Streamlit UI
│   │   ├── config.py            # Dashboard configuration
│   │   ├── theme.py             # UI theme
│   │   ├── kepler_visualization.py  # Kepler.gl integration
│   │   ├── api/                 # FastAPI backend
│   │   │   ├── __init__.py
│   │   │   ├── main.py          # API entry point
│   │   │   ├── models/          # Pydantic models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── requests.py
│   │   │   │   └── responses.py
│   │   │   ├── routes/          # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data.py
│   │   │   │   ├── spatial.py
│   │   │   │   ├── comparison.py
│   │   │   │   └── visualization.py
│   │   │   └── services/        # Business logic
│   │   │       ├── __init__.py
│   │   │       ├── data_service.py
│   │   │       ├── spatial_service.py
│   │   │       └── visualization_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── api_client.py    # API client for Streamlit
│   └── tests/                   # Dashboard tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api_endpoints.py
│       └── test_spatial_service.py
│
└── shared/                      # 🔧 Shared Configuration
    └── config/
        ├── __init__.py
        └── estados.py           # State codes and names
```

## 🔄 Data Flow

```
┌──────────────────┐
│   data/geo/      │  ← Shapefiles (from ingestion)
│   (Shapefiles)   │
└────────┬─────────┘
         │
         │ Read shapefiles
         ▼
┌──────────────────┐
│   INGESTION      │  ← Layer 1: Download raw data
│   Module         │
└────────┬─────────┘
         │
         │ Save raw files
         ▼
┌──────────────────┐
│   data/raw/      │  ← Raw electoral data (CSV, Excel)
└────────┬─────────┘
         │
         │ Read & process
         ▼
┌──────────────────┐
│   ANALYTICS      │  ← Layer 2: Clean, homologate, merge geometry
│   Module         │
└────────┬─────────┘
         │
         │ Store in database
         ▼
┌──────────────────┐
│ electoral_data.db│  ← SQLite database with cleaned data + geometry
│ (data/processed/)│
└────────┬─────────┘
         │
         │ Query database ONLY
         ▼
┌──────────────────┐
│   DASHBOARD      │  ← Layer 3: Visualize from database
│   Module         │
└──────────────────┘
```

## 📁 Data Directories

```
data/
├── geo/                         # Shapefiles (manually placed or from ingestion)
│   ├── peepjf/                  # PEEPJF shapefiles
│   └── nacional/                # INE national shapefiles
│
├── raw/                         # Raw electoral data files
│   └── electoral/
│       ├── 2024/
│       ├── 2021/
│       └── ...
│
├── processed/                   # Processed data
│   └── electoral_data.db        # Main SQLite database
│
└── insights/                    # Analysis outputs
    └── moran_plots/             # Spatial analysis plots
```

## 🎯 Key Principles

### 1. Separation of Concerns

- **Ingestion**: Only downloads and basic file management
- **Analytics**: All data transformation, cleaning, and database storage
- **Dashboard**: Only reads from database, no data processing

### 2. Database-Centric Architecture

- All cleaned data stored in `data/processed/electoral_data.db`
- Dashboard **ONLY** queries the database
- No direct file reading in dashboard
- Ensures data consistency and reproducibility

### 3. Reproducible Pipeline

```bash
# Step 1: Download shapefiles (if needed)
cd ingestion
uv run python -m ingestion.download_peepjf

# Step 2: Process electoral data → database
cd ../analytics
uv run python run_pipeline.py

# Step 3: Visualize from database
cd ../dashboard
uv run uvicorn dashboard.api.main:app --port 8000 &
uv run streamlit run src/dashboard/app.py
```

### 4. Environment Management with uv

```bash
# Install all dependencies
uv sync

# Add dependency to specific module
uv add <package> --package <module_name>

# Examples:
uv add requests --package ingestion
uv add geopandas --package analytics
uv add streamlit --package dashboard
```

## 📝 Documentation Files

**Kept:**
- `README.md` (root) - Main project documentation
- `ingestion/README.md` - Ingestion module docs
- `analytics/README.md` - Analytics module docs
- `dashboard/README.md` - Dashboard module docs

**Removed (22 files):**
- All summary/changelog files
- All quickstart guides (info now in module READMEs)
- All troubleshooting docs (info now in module READMEs)
- Duplicate/temporary files

## 🗂️ Files Removed in Cleanup

### Documentation (22 .md files):
- `CLEAN_VOTES_SUMMARY.md`
- `CLEAN_VOTES_USAGE.md`
- `CR_LINE_TERMINATOR_FIX.md`
- `HOMOLOGATION_IMPLEMENTATION_SUMMARY.md`
- `PIPELINE_UPDATE_SUMMARY.md`
- `SECURITY_IMPROVEMENTS.md`
- `UPDATED_FEATURES.md`
- `PIPELINE_GUIDE.md`
- `PROJECT_README.md`
- `SETUP_COMPLETE.md`
- `QUICKSTART.md`
- `MIGRATION_GUIDE.md`
- `ENV_SETUP.md`
- `analytics/CLEAN_VOTES_QUICKSTART.md`
- `analytics/COLUMN_HOMOLOGATION_GUIDE.md`
- `analytics/PIPELINE_FEATURES.md`
- `analytics/QUICK_REFERENCE_HOMOLOGATION.md`
- `analytics/QUICK_START_UV.md`
- `analytics/src/analytics/clean_votes/README.md`
- `dashboard/API_AND_DESIGN_FIXES_SUMMARY.md`
- `dashboard/LABEXANDRIA_DESIGN_SYSTEM.md`
- `dashboard/UI_IMPROVEMENTS_SUMMARY.md`
- `dashboard/FIXES_SUMMARY.md`
- `dashboard/TROUBLESHOOTING.md`
- `dashboard/QUICKSTART.md`
- `ingestion/SECURITY_CHANGELOG.md`

### Notebooks (4 .ipynb files):
- `clean_votes.ipynb` (root - duplicate)
- `test_data.ipynb` (root)
- `analytics/test_data.ipynb`
- `analytics/clean_votes.ipynb` (duplicate)

### Scripts:
- `dashboard/quick_fix.sh` (temporary fix script)

### Dependencies:
- `requirements.txt` (replaced by uv/pyproject.toml)

## ✅ Files Reorganized

**Moved to `analytics/utils/`:**
- `add_geometry_to_existing.py` (was in dashboard/)
- `check_geometry.py` (was in dashboard/)

**Reason:** These scripts process data and interact with the database, so they belong in analytics, not dashboard.

## 🛠️ Utility Files (Kept)

- `validate_setup.py` - Useful for verifying workspace setup
- `Dockerfile` - For containerized deployments
- `analytics/init_database.py` - Database initialization
- `analytics/demo_clean_votes.ipynb` - Demo notebook
- `analytics/query_database.ipynb` - Query examples

## 📊 Current State

**Total remaining .md files:** 4 (essential documentation only)
**Total remaining .ipynb files:** 2 (demo and query examples)
**Python packages:** 3 (ingestion, analytics, dashboard)
**Architecture:** Clean 3-layer separation
**Data flow:** Unidirectional (Ingestion → Analytics → Database → Dashboard)

## 🚀 Next Steps

1. **Add more elections**: Place CSV/Excel files in `data/raw/electoral/`
2. **Run pipeline**: `cd analytics && uv run python run_pipeline.py`
3. **Visualize**: Dashboard automatically shows new data from database

## 📞 Support

- Main README: `README.md`
- Module docs: `<module>/README.md`
- Workspace rules: `.cursorrules`
- Setup validation: `python validate_setup.py`
