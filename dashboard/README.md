# Electoral Data Dashboard

Interactive dashboard for visualizing and analyzing Mexican electoral data with spatial autocorrelation analysis.

## Architecture

The dashboard consists of two main components:

1. **FastAPI Backend** - REST API for data processing and analysis
2. **Streamlit Frontend** - Interactive web interface

```
┌─────────────────┐
│  Streamlit UI   │
│  (Port 8501)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI API    │
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ CleanVotes      │──────│  SQLite Database │
│ Orchestrator    │      │  electoral_data  │
└─────────────────┘      └──────────────────┘
```

## Features

### 1. Spatial Analysis
- **Moran's I Spatial Autocorrelation**: Measure spatial clustering of electoral patterns
- **Spatial Lag Visualization**: Compare original values with neighborhood averages
- **Side-by-side Maps**: Interactive or static choropleth maps
- **Statistical Interpretation**: Automatic significance testing and interpretation

### 2. Cross-State Comparison
- Compare multiple states for a single election
- Visualize party performance differences across regions
- Export data to CSV for further analysis
- Interactive bar charts

### 3. Temporal Analysis
- Track voting trends over time for a single state
- Compare same party across multiple elections
- Line charts showing temporal evolution
- Identify long-term patterns and shifts

## Installation

### Prerequisites

- Python 3.11 or 3.12
- `uv` package manager (installed in workspace)
- Electoral data processed and stored in database

### Install Dependencies

From the project root:

```bash
# Using uv (recommended)
cd dashboard
uv sync

# Or with pip
pip install -e dashboard/
```

## Usage

### 1. Start the FastAPI Backend

```bash
cd dashboard
uv run uvicorn dashboard.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

### 2. Start the Streamlit Frontend

In a new terminal:

```bash
cd dashboard
uv run streamlit run src/dashboard/app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### 3. Use the Dashboard

1. **Select an Election** from the sidebar (e.g., PRES_2024, DIP_FED_2024)
2. **Choose Visualization Style**: Interactive (Plotly) or Static (Matplotlib)
3. **Navigate between tabs**:
   - **Spatial Analysis**: Select a state and variable to analyze
   - **Cross-State Comparison**: Select multiple states to compare
   - **Temporal Analysis**: Select a state and multiple elections

## API Endpoints

### Data Endpoints

- `GET /api/data/elections` - List all elections
- `GET /api/data/elections/summary` - Get elections summary
- `GET /api/data/states` - List all states
- `GET /api/data/election/{election_name}/states` - States for an election
- `GET /api/data/election/{election_name}/{entidad_id}` - Get election data
- `GET /api/data/election/{election_name}/{entidad_id}/metrics` - Get metrics

### Spatial Analysis Endpoints

- `POST /api/spatial/lag` - Compute spatial lag
- `POST /api/spatial/moran` - Compute Moran's I
- `GET /api/spatial/variables/{election_name}/{entidad_id}` - Available variables

### Comparison Endpoints

- `POST /api/comparison/cross-state` - Compare states
- `POST /api/comparison/temporal` - Compare elections over time
- `GET /api/comparison/party-trends/{entidad_id}/{party}` - Party trends
- `GET /api/comparison/state-rankings/{election_name}/{party}` - State rankings

### Visualization Endpoints

- `POST /api/viz/spatial-lag-map` - Generate spatial lag maps
- `POST /api/viz/choropleth` - Generate choropleth map
- `POST /api/viz/bar-chart` - Generate bar chart
- `POST /api/viz/line-chart` - Generate line chart

## Configuration

Configuration is centralized in `src/dashboard/config.py`:

```python
# API Configuration
API_BASE_URL = "http://localhost:8000"

# Database
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "processed" / "electoral_data.db"

# Political Parties
MAJOR_PARTIES = ["MORENA", "PAN", "PRI", "PRD", "PVEM", "PT", "MC"]

# Cache
CACHE_TTL_SECONDS = 3600  # 1 hour
```

## Development

### Project Structure

```
dashboard/
├── src/dashboard/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Main FastAPI app
│   │   ├── models/            # Pydantic models
│   │   │   ├── requests.py    # Request models
│   │   │   └── responses.py   # Response models
│   │   ├── routes/            # API endpoints
│   │   │   ├── data.py        # Data endpoints
│   │   │   ├── spatial.py     # Spatial analysis
│   │   │   ├── comparison.py  # Comparisons
│   │   │   └── visualization.py # Visualizations
│   │   └── services/          # Business logic
│   │       ├── data_service.py
│   │       ├── spatial_service.py
│   │       └── visualization_service.py
│   ├── app.py                 # Streamlit frontend
│   ├── config.py              # Configuration
│   └── utils/                 # Utilities
│       └── api_client.py      # API client for Streamlit
├── tests/                      # Tests
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

### Running Tests

```bash
cd dashboard
uv run pytest tests/
```

### Adding New Features

1. **New API Endpoint**:
   - Add Pydantic models in `api/models/`
   - Implement service logic in `api/services/`
   - Create router in `api/routes/`
   - Mount router in `api/main.py`

2. **New Frontend Feature**:
   - Add API client method in `utils/api_client.py`
   - Update relevant tab function in `app.py`

## Troubleshooting

### API Connection Failed

**Issue**: Streamlit shows "API Connection Failed"

**Solutions**:
1. Ensure FastAPI server is running: `lsof -i :8000`
2. Check database exists: `ls -la ../data/processed/electoral_data.db`
3. Verify API health: `curl http://localhost:8000/health`

### No Data Available

**Issue**: "No data found for election"

**Solutions**:
1. Process electoral data first using the analytics pipeline
2. Check database has data: Run `analytics/query_database.ipynb`
3. Ensure geometry was included when processing

### Spatial Analysis Fails

**Issue**: "No geometry available for this election/state"

**Solutions**:
1. Reprocess data with `include_geometry=True`
2. Check shapefile availability in `data/geo/`
3. Verify `has_geometry` column in database metadata

### Slow Performance

**Solutions**:
1. Reduce number of permutations for Moran's I (default: 999)
2. Use static visualizations instead of interactive
3. Clear Streamlit cache: Settings → Clear cache
4. Restart both API and Streamlit servers

## Examples

### Example 1: Spatial Analysis for MORENA in CDMX

1. Select Election: `PRES_2024`
2. Go to "Spatial Analysis" tab
3. Select State: `CIUDAD DE MEXICO`
4. Select Variable: `MORENA_PCT`
5. Click "Analyze"

**Expected Result**: Moran's I showing positive spatial autocorrelation, indicating MORENA support clusters geographically.

### Example 2: Compare States

1. Select Election: `PRES_2024`
2. Go to "Cross-State Comparison" tab
3. Select States: `Aguascalientes`, `CDMX`, `Estado de México`, `Nuevo León`
4. Select Parties: `MORENA`, `PAN`, `PRI`
5. Click "Compare"

**Expected Result**: Bar chart showing party performance varies significantly across states.

### Example 3: Temporal Trends

1. Go to "Temporal Analysis" tab
2. Select State: `CDMX`
3. Select Elections: `PRES_2024`, `PRES_2018`, `DIP_FED_2021`
4. Select Parties: `MORENA`, `PAN`, `PRI`
5. Click "Analyze Trends"

**Expected Result**: Line chart showing how party support changed over time in CDMX.

## Technologies Used

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Data Processing**: Pandas, GeoPandas
- **Spatial Analysis**: libpysal, esda, splot
- **Visualization**: Matplotlib, Plotly, Folium
- **Database**: SQLite
- **Validation**: Pydantic

## Contributing

1. Follow the workspace rules in `.cursorrules`
2. Use `uv` for dependency management
3. Add tests for new features
4. Update documentation

## License

Part of the INE Electoral Data Analysis project.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/api/docs`
3. Check logs in terminal where API/Streamlit are running
