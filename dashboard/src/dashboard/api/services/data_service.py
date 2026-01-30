"""
Data Service
============

Service layer for data access using CleanVotesOrchestrator.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache
import pandas as pd
import geopandas as gpd
import logging

# Add analytics to path
analytics_path = Path(__file__).parents[5] / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator
from dashboard.config import DEFAULT_DB_PATH, MAJOR_PARTIES

logger = logging.getLogger(__name__)


class DataService:
    """
    Service for accessing electoral data from the database.
    
    Provides caching and convenient methods for data retrieval.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the data service.
        
        Args:
            db_path: Path to the SQLite database. If None, uses default.
        """
        if db_path is None:
            db_path = str(DEFAULT_DB_PATH)
        
        self.db_path = db_path
        self.orchestrator = CleanVotesOrchestrator(db_path=db_path)
        logger.info(f"DataService initialized with database: {db_path}")
    
    def get_available_elections(self) -> pd.DataFrame:
        """
        Get list of all available elections.
        
        Returns:
            DataFrame with election metadata
        """
        try:
            elections = self.orchestrator.list_available_elections()
            logger.info(f"Found {len(elections)} election records")
            return elections
        except Exception as e:
            logger.error(f"Error fetching elections: {e}")
            raise
    
    def get_elections_summary(self) -> Dict[str, Any]:
        """
        Get summary of available elections.
        
        Returns:
            Dictionary with election counts and metadata
        """
        elections = self.get_available_elections()
        
        summary = {
            "total_records": len(elections),
            "unique_elections": elections["election_name"].nunique(),
            "elections": []
        }
        
        for election_name in elections["election_name"].unique():
            election_data = elections[elections["election_name"] == election_name]
            summary["elections"].append({
                "election_name": election_name,
                "entidades_count": len(election_data),
                "with_geometry": int(election_data["has_geometry"].sum()),
                "election_date": election_data["election_date"].iloc[0] if "election_date" in election_data.columns else None
            })
        
        return summary
    
    def get_states_for_election(self, election_name: str) -> List[Dict[str, Any]]:
        """
        Get list of states available for a specific election.
        
        Args:
            election_name: Name of the election
            
        Returns:
            List of state information dictionaries
        """
        elections = self.get_available_elections()
        election_data = elections[elections["election_name"] == election_name.upper()]
        
        if len(election_data) == 0:
            return []
        
        states = []
        for _, row in election_data.iterrows():
            states.append({
                "entidad_id": int(row["entidad_id"]),
                "entidad_name": row["entidad_name"],
                "has_geometry": bool(row["has_geometry"]),
                "row_count": int(row["row_count"])
            })
        
        return sorted(states, key=lambda x: x["entidad_id"])
    
    def load_election_data(
        self,
        election_name: str,
        entidad_id: int,
        as_geodataframe: bool = False
    ) -> pd.DataFrame:
        """
        Load election data for a specific state.
        
        Args:
            election_name: Name of the election
            entidad_id: State ID (1-32)
            as_geodataframe: Whether to return as GeoDataFrame
            
        Returns:
            DataFrame or GeoDataFrame with election data
        """
        try:
            logger.info(f"Loading data: {election_name}, entidad_id={entidad_id}, geodf={as_geodataframe}")
            
            df = self.orchestrator.load_election_data(
                election_name=election_name.upper(),
                entidad_id=entidad_id,
                as_geodataframe=as_geodataframe
            )
            
            logger.info(f"Loaded {len(df)} rows")
            logger.info(f"Type: {type(df)}")
            logger.info(f"Total columns: {len(df.columns)}")
            logger.info(f"First 10 columns: {list(df.columns)[:10]}")
            logger.info(f"Last 10 columns: {list(df.columns)[-10:]}")
            
            # Check for critical geometry columns
            logger.info(f"Has 'geometry' column: {'geometry' in df.columns}")
            logger.info(f"Has 'crs' column: {'crs' in df.columns}")
            
            if as_geodataframe:
                logger.info(f"Is GeoDataFrame: {isinstance(df, gpd.GeoDataFrame)}")
                if isinstance(df, gpd.GeoDataFrame):
                    logger.info(f"Has geometry column: {'geometry' in df.columns}")
                    if 'geometry' in df.columns:
                        logger.info(f"Geometry count: {df['geometry'].notna().sum()}/{len(df)}")
                        logger.info(f"CRS: {df.crs}")
                else:
                    logger.warning("as_geodataframe=True but result is not a GeoDataFrame!")
                    if 'geometry' not in df.columns:
                        logger.warning("Missing 'geometry' column")
                    if 'crs' not in df.columns:
                        logger.warning("Missing 'crs' column - this is required for GeoDataFrame conversion!")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading election data: {e}")
            raise ValueError(f"Failed to load election data: {str(e)}")
    
    def get_aggregated_metrics(
        self,
        election_name: str,
        entidad_id: int,
        variables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for an election and state.
        
        Args:
            election_name: Name of the election
            entidad_id: State ID
            variables: List of variables to include (default: major parties)
            
        Returns:
            Dictionary with aggregated metrics
        """
        df = self.load_election_data(election_name, entidad_id, as_geodataframe=False)
        
        if variables is None:
            variables = [f"{party}_PCT" for party in MAJOR_PARTIES if f"{party}_PCT" in df.columns]
        
        metrics = {
            "election_name": election_name.upper(),
            "entidad_id": entidad_id,
            "entidad_name": df["ENTIDAD"].iloc[0] if "ENTIDAD" in df.columns else f"State {entidad_id}",
            "sections": len(df),
            "total_votes": float(df["TOTAL_VOTOS_SUM"].sum()) if "TOTAL_VOTOS_SUM" in df.columns else 0,
        }
        
        # Add party percentages
        for var in variables:
            if var in df.columns:
                metrics[var] = float(df[var].mean())
        
        return metrics
    
    def compare_states(
        self,
        election_name: str,
        entidad_ids: List[int],
        variables: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Compare multiple states for a single election.
        
        Args:
            election_name: Name of the election
            entidad_ids: List of state IDs to compare
            variables: Variables to include
            
        Returns:
            List of metrics dictionaries for each state
        """
        results = []
        
        for entidad_id in entidad_ids:
            try:
                metrics = self.get_aggregated_metrics(election_name, entidad_id, variables)
                results.append(metrics)
            except Exception as e:
                logger.warning(f"Failed to load data for state {entidad_id}: {e}")
                continue
        
        return results
    
    def compare_temporal(
        self,
        entidad_id: int,
        election_names: List[str],
        variables: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Compare same state across multiple elections (temporal analysis).
        
        Args:
            entidad_id: State ID
            election_names: List of elections to compare
            variables: Variables to include
            
        Returns:
            List of metrics dictionaries for each election
        """
        results = []
        
        for election_name in election_names:
            try:
                metrics = self.get_aggregated_metrics(election_name, entidad_id, variables)
                results.append(metrics)
            except Exception as e:
                logger.warning(f"Failed to load data for election {election_name}: {e}")
                continue
        
        return results


# Singleton instance
_data_service_instance: Optional[DataService] = None


def get_data_service(db_path: Optional[str] = None) -> DataService:
    """
    Get or create the DataService singleton instance.
    
    Args:
        db_path: Path to the database (only used on first call)
        
    Returns:
        DataService instance
    """
    global _data_service_instance
    
    if _data_service_instance is None:
        _data_service_instance = DataService(db_path)
    
    return _data_service_instance
