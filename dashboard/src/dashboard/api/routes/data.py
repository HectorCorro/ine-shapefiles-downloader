"""
Data Router
===========

API endpoints for accessing electoral data.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging
import sys
from pathlib import Path

# Add shared config to path
shared_path = Path(__file__).parents[5] / "shared"
sys.path.insert(0, str(shared_path))

from config.estados import ENTIDADES
from dashboard.api.models import ElectionMetadata, StateInfo
from dashboard.api.services import DataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])

# Initialize service
data_service = DataService()


@router.get("/elections", response_model=List[ElectionMetadata])
async def list_elections():
    """
    List all available elections in the database.
    
    Returns:
        List of election metadata records
    """
    try:
        elections_df = data_service.get_available_elections()
        
        # Convert to list of dicts
        records = elections_df.to_dict('records')
        
        return records
    
    except Exception as e:
        logger.error(f"Error listing elections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/elections/summary")
async def get_elections_summary():
    """
    Get summary of available elections.
    
    Returns:
        Summary with election counts and metadata
    """
    try:
        summary = data_service.get_elections_summary()
        return summary
    
    except Exception as e:
        logger.error(f"Error getting elections summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/states", response_model=List[StateInfo])
async def list_states():
    """
    List all Mexican states.
    
    Returns:
        List of state information
    """
    states = []
    
    for code, name in ENTIDADES.items():
        states.append({
            "entidad_id": int(code),
            "entidad_name": name.replace("_", " ").upper(),
            "code": code
        })
    
    return sorted(states, key=lambda x: x["entidad_id"])


@router.get("/election/{election_name}/states")
async def get_states_for_election(election_name: str):
    """
    Get list of states available for a specific election.
    
    Args:
        election_name: Name of the election (e.g., 'PRES_2024')
        
    Returns:
        List of available states with metadata
    """
    try:
        states = data_service.get_states_for_election(election_name)
        
        if not states:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for election: {election_name}"
            )
        
        return states
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting states for election {election_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/election/{election_name}/{entidad_id}")
async def get_election_data(
    election_name: str,
    entidad_id: int,
    as_geodataframe: bool = Query(False, description="Return with geometry")
):
    """
    Get election data for a specific state.
    
    Args:
        election_name: Name of the election
        entidad_id: State ID (1-32)
        as_geodataframe: Whether to include geometry
        
    Returns:
        Election data as JSON
    """
    try:
        if entidad_id < 1 or entidad_id > 32:
            raise HTTPException(
                status_code=400,
                detail="entidad_id must be between 1 and 32"
            )
        
        df = data_service.load_election_data(
            election_name=election_name,
            entidad_id=entidad_id,
            as_geodataframe=as_geodataframe
        )
        
        # Convert to dict
        if as_geodataframe:
            # Convert geometry to GeoJSON
            import geopandas as gpd
            if isinstance(df, gpd.GeoDataFrame):
                geojson = df.to_json()
                import json
                return json.loads(geojson)
        
        # Regular DataFrame
        return df.to_dict('records')
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error loading election data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/election/{election_name}/{entidad_id}/metrics")
async def get_election_metrics(
    election_name: str,
    entidad_id: int,
    variables: List[str] = Query(None, description="Variables to include")
):
    """
    Get aggregated metrics for an election and state.
    
    Args:
        election_name: Name of the election
        entidad_id: State ID (1-32)
        variables: Optional list of variables to include
        
    Returns:
        Aggregated metrics dictionary
    """
    try:
        if entidad_id < 1 or entidad_id > 32:
            raise HTTPException(
                status_code=400,
                detail="entidad_id must be between 1 and 32"
            )
        
        metrics = data_service.get_aggregated_metrics(
            election_name=election_name,
            entidad_id=entidad_id,
            variables=variables
        )
        
        return metrics
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
