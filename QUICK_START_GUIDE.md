# Quick Start Guide - How to Run Everything

## 📋 Overview

This guide shows you how to execute the complete pipeline from data ingestion to visualization.

---

## 🔄 Step 1: Run the Data Processing Pipeline

The pipeline processes electoral data files and stores them in the database with geometry.

### Process All Files

```bash
# From project root
cd analytics
uv run python run_pipeline.py
```

This will:
- Scan `data/raw/electoral/` for all CSV/Excel/Parquet files
- Auto-detect election names and dates
- Clean and homologate columns
- Merge with shapefiles (geometry)
- Store in `data/processed/electoral_data.db`

### Process Specific Years Only

```bash
# Process only 2024 and 2021 elections
uv run python run_pipeline.py --years 2024 2021
```

### Process Specific Folder

```bash
# Process only files in data/raw/electoral/2024/
uv run python run_pipeline.py --folder 2024

# Process subfolder
uv run python run_pipeline.py --folder 2024/presidencial
```

### Dry-Run (Preview What Will Be Processed)

```bash
# See what would be processed without actually processing
uv run python run_pipeline.py --dry-run
```

### Process Without Geometry (Faster, No Maps)

```bash
# Skip geometry merging (can't do spatial analysis later)
uv run python run_pipeline.py --no-geometry
```

### Force Reprocess Existing Data

```bash
# Reprocess elections already in database
uv run python run_pipeline.py --no-skip-existing
```

### List Elections in Database

```bash
# See what's already in the database
uv run python run_pipeline.py --list
```

### Advanced Options

```bash
# Custom data directory
uv run python run_pipeline.py --data-dir /path/to/electoral

# Stop on first error (default: continue)
uv run python run_pipeline.py --stop-on-error

# Use nacional shapefiles instead of peepjf
uv run python run_pipeline.py --shapefile-type nacional
```

---

## 🗺️ Step 2: Run the Dashboard

The dashboard has two components that run together:

### Option A: Run Both (Recommended)

Open **two terminal windows**:

**Terminal 1 - Start the API:**
```bash
cd dashboard
uv run uvicorn dashboard.api.main:app --reload --port 8000
```

**Terminal 2 - Start the Streamlit UI:**
```bash
cd dashboard
uv run streamlit run src/dashboard/app.py
```

### Option B: Quick Single Command (Using &)

```bash
cd dashboard
uv run uvicorn dashboard.api.main:app --port 8000 &
uv run streamlit run src/dashboard/app.py
```

### Access the Dashboard

- **Streamlit UI**: http://localhost:8501 (opens automatically)
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/health

---

## 📊 Step 3: Use the Dashboard

### Available Tabs

1. **🗺️ Spatial Analysis**
   - Select state and variable (party)
   - Compute Moran's I spatial autocorrelation
   - View spatial lag maps

2. **🌍 Interactive Map Explorer**
   - Explore data with interactive Folium maps
   - See original values and spatial lag side-by-side
   - Click regions for details

3. **🔄 Cross-State Comparison**
   - Compare multiple states for same election
   - Select parties to analyze
   - Download results as CSV

4. **📈 Temporal Analysis**
   - Track trends over time for one state
   - Compare same party across multiple elections
   - Line charts showing evolution

---

## 🔧 Utility Scripts

### Check Geometry Availability

```bash
cd analytics
uv run python utils/check_geometry.py
```

Shows which elections have geometry data available.

### Add Geometry to Existing Data

```bash
cd analytics

# Add geometry to specific election/state
uv run python utils/add_geometry_to_existing.py \
  --election PRES_2024 \
  --entidad 9

# Add geometry to all states for an election
uv run python utils/add_geometry_to_existing.py \
  --election PRES_2024
```

### Initialize/Reset Database

```bash
cd analytics
uv run python init_database.py
```

---

## 📁 Complete Workflow Example

### 1. Download Shapefiles (if needed)

```bash
cd ingestion
uv run python -m ingestion.download_peepjf
```

Output: `data/geo/peepjf/`

### 2. Add Electoral Data Files

Place your CSV/Excel files in `data/raw/electoral/`:

```
data/raw/electoral/
├── 2024/
│   ├── PRES_2024.csv
│   ├── DIP_FED_2024.csv
│   └── SEN_2024.csv
├── 2021/
│   └── DIP_FED_2021.csv
└── 2018/
    └── PRES_2018.csv
```

### 3. Process All Files

```bash
cd analytics
uv run python run_pipeline.py
```

Expected output:
```
==================================================
ELECTORAL DATA PROCESSING PIPELINE
==================================================
Found 5 files to process
...
Processing: PRES_2024.csv
✓ Success!
  Rows: 156,890
  Entidades: 32
  Geometry: True
...
✅ PIPELINE READY FOR ANALYSIS!
Database: data/processed/electoral_data.db
Elections in database: 5
```

### 4. Verify Data

```bash
# List elections in database
uv run python run_pipeline.py --list
```

### 5. Start Dashboard

**Terminal 1:**
```bash
cd dashboard
uv run uvicorn dashboard.api.main:app --reload --port 8000
```

**Terminal 2:**
```bash
cd dashboard
uv run streamlit run src/dashboard/app.py
```

### 6. Analyze in Browser

Open http://localhost:8501 and:
- Select election (e.g., PRES_2024)
- Go to "Spatial Analysis" tab
- Select state (e.g., CIUDAD DE MEXICO)
- Select variable (e.g., MORENA_PCT)
- Click "Analyze"

---

## 🐛 Troubleshooting

### Pipeline Issues

**Error: "No electoral files found"**
```bash
# Check your data directory structure
ls -la data/raw/electoral/

# Specify custom directory
uv run python run_pipeline.py --data-dir path/to/data
```

**Error: "No geometry available"**
```bash
# Download shapefiles first
cd ingestion
uv run python -m ingestion.download_peepjf

# Or skip geometry temporarily
cd analytics
uv run python run_pipeline.py --no-geometry
```

**Error: "Election already exists"**
```bash
# Force reprocess
uv run python run_pipeline.py --no-skip-existing
```

### Dashboard Issues

**Error: "API Connection Failed"**
```bash
# Check if API is running
lsof -i :8000

# If not, start it:
cd dashboard
uv run uvicorn dashboard.api.main:app --port 8000
```

**Error: "No data available"**
```bash
# Verify database has data
cd analytics
uv run python run_pipeline.py --list

# If empty, run pipeline first
uv run python run_pipeline.py
```

**Streamlit Port Already in Use**
```bash
# Use different port
uv run streamlit run src/dashboard/app.py --server.port 8502
```

---

## ⚡ Quick Commands Reference

```bash
# Process all electoral data
cd analytics && uv run python run_pipeline.py

# Dry-run (preview)
cd analytics && uv run python run_pipeline.py --dry-run

# List database contents
cd analytics && uv run python run_pipeline.py --list

# Start API
cd dashboard && uv run uvicorn dashboard.api.main:app --port 8000

# Start Streamlit
cd dashboard && uv run streamlit run src/dashboard/app.py

# Check geometry
cd analytics && uv run python utils/check_geometry.py

# Download shapefiles
cd ingestion && uv run python -m ingestion.download_peepjf
```

---

## 📚 Additional Resources

- **Full Documentation**: `README.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Module READMEs**: 
  - `ingestion/README.md`
  - `analytics/README.md`
  - `dashboard/README.md`
- **Examples**: `analytics/examples/`
- **Query Examples**: `analytics/query_database.ipynb`

---

## 💡 Pro Tips

1. **Always run the pipeline first** before starting the dashboard
2. **Use dry-run** to preview what will be processed
3. **Check geometry availability** with `check_geometry.py` before spatial analysis
4. **Use --folder** option to process specific subsets of data
5. **Monitor logs** in `pipeline.log` for detailed processing info
6. **API docs** at http://localhost:8000/api/docs are interactive - try endpoints there
7. **Download CSV** from dashboard for further analysis in Excel/Python

---

**Last Updated**: January 2026
**Version**: 2.0
