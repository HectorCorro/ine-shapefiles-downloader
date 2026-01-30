"""
Dashboard Configuration
=======================

Central configuration for the electoral dashboard application.
"""

from pathlib import Path
from typing import Dict, List
import os

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_VERSION = "v1"

# Database Configuration
PROJECT_ROOT = Path(__file__).parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "processed" / "electoral_data.db"

# Shapefile Configuration
SHAPEFILE_BASE_DIR = PROJECT_ROOT / "data" / "geo"

# Cache Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_CACHE_SIZE = 100  # Maximum number of cached items

# Political Parties
MAJOR_PARTIES: List[str] = [
    "MORENA",
    "PAN", 
    "PRI",
    "PRD",
    "PVEM",
    "PT",
    "MC"
]

# Election Type Mappings
ELECTION_TYPE_DISPLAY: Dict[str, str] = {
    "PRES": "Presidential",
    "DIP_FED": "Federal Deputies",
    "SEN": "Senators",
    "GOB": "Gubernatorial",
    "DIP_LOC": "Local Deputies"
}

# Color schemes for parties (for visualizations)
PARTY_COLORS: Dict[str, str] = {
    "MORENA": "#8B4513",  # Brown
    "PAN": "#0066CC",     # Blue
    "PRI": "#ED1C24",     # Red
    "PRD": "#FFD700",     # Yellow
    "PVEM": "#00A651",    # Green
    "PT": "#DC143C",      # Crimson
    "MC": "#FF6600"       # Orange
}

# Visualization Styles
VISUALIZATION_STYLES: List[str] = ["static", "interactive"]

# Map Configuration
DEFAULT_MAP_CRS = "EPSG:4326"  # WGS84 for web maps
PLOT_CRS = "EPSG:3857"  # Web Mercator for better visualization

# Default States for Comparison
DEFAULT_COMPARISON_STATES: List[int] = [
    1,   # Aguascalientes
    9,   # CDMX
    15,  # Estado de México
    19   # Nuevo León
]

# API Pagination
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CORS Configuration (for FastAPI)
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit default port
    "http://localhost:8000",
]

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "Electoral Data Dashboard"
STREAMLIT_PAGE_ICON = "📊"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_INITIAL_SIDEBAR_STATE = "expanded"
