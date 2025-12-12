"""
Clean Votes Module
==================

This module provides functionality to clean and process electoral data from various sources
(CSV, Excel, Parquet) and optionally merge with geospatial data.

Main Components:
- reader: Flexible file reading with automatic header detection
- cleaner: Data transformation and aggregation functions
- geometry: Shapefile integration
- database: SQLite storage for processed data (auto-created)
- orchestrator: Main workflow coordinator
- utils: Helper functions for metadata inference

Key Features:
- Automatically infers election name and date from file paths
- Creates SQLite database automatically if it doesn't exist
- Processes all entidades in a single call
- Supports CSV, Excel, and Parquet formats
"""

from .reader import ElectoralDataReader
from .cleaner import ElectoralDataCleaner
from .geometry import GeometryMerger
from .database import ElectoralDatabase
from .orchestrator import CleanVotesOrchestrator
from .utils import infer_election_metadata, get_default_db_path
from .column_mapper import ColumnMapper, homologate_dataframe

__all__ = [
    "ElectoralDataReader",
    "ElectoralDataCleaner",
    "GeometryMerger",
    "ElectoralDatabase",
    "CleanVotesOrchestrator",
    "ColumnMapper",
    "homologate_dataframe",
    "infer_election_metadata",
    "get_default_db_path",
]

