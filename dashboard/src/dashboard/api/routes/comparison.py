"""
Comparison Router
=================

API endpoints for cross-state and temporal comparisons.
"""

from fastapi import APIRouter, HTTPException
import logging
from typing import List, Dict, Any

from dashboard.api.models import (
    CrossStateRequest,
    TemporalRequest,
    ComparisonResult
)
from dashboard.api.services import DataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/comparison", tags=["comparison"])

# Initialize service
data_service = DataService()


@router.post("/cross-state", response_model=ComparisonResult)
async def compare_cross_state(request: CrossStateRequest):
    """
    Compare multiple states for a single election.
    
    Useful for understanding regional differences in voting patterns.
    
    Args:
        request: CrossStateRequest with election and list of states
        
    Returns:
        Comparison data with metrics for each state
    """
    try:
        logger.info(f"Cross-state comparison: {request.election_name}, "
                   f"states={request.entidad_ids}")
        
        # Get comparison data
        comparison_data = data_service.compare_states(
            election_name=request.election_name,
            entidad_ids=request.entidad_ids,
            variables=request.variables
        )
        
        if not comparison_data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for election {request.election_name}"
            )
        
        # Compute summary statistics
        total_sections = sum(d.get("sections", 0) for d in comparison_data)
        total_votes = sum(d.get("total_votes", 0) for d in comparison_data)
        
        summary = {
            "total_states": len(comparison_data),
            "total_sections": total_sections,
            "total_votes": total_votes,
            "election_name": request.election_name
        }
        
        result = {
            "comparison_type": "cross_state",
            "data": comparison_data,
            "summary": summary
        }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in cross-state comparison: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/temporal", response_model=ComparisonResult)
async def compare_temporal(request: TemporalRequest):
    """
    Compare same state across multiple elections (temporal analysis).
    
    Useful for understanding voting trends over time.
    
    Args:
        request: TemporalRequest with state and list of elections
        
    Returns:
        Comparison data with metrics for each election
    """
    try:
        logger.info(f"Temporal comparison: entidad={request.entidad_id}, "
                   f"elections={request.election_names}")
        
        # Get comparison data
        comparison_data = data_service.compare_temporal(
            entidad_id=request.entidad_id,
            election_names=request.election_names,
            variables=request.variables
        )
        
        if not comparison_data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for state {request.entidad_id}"
            )
        
        # Compute summary statistics
        total_elections = len(comparison_data)
        state_name = comparison_data[0].get("entidad_name", f"State {request.entidad_id}")
        
        summary = {
            "entidad_id": request.entidad_id,
            "entidad_name": state_name,
            "total_elections": total_elections,
            "elections": [d.get("election_name") for d in comparison_data]
        }
        
        result = {
            "comparison_type": "temporal",
            "data": comparison_data,
            "summary": summary
        }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in temporal comparison: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/party-trends/{entidad_id}/{party}")
async def get_party_trends(
    entidad_id: int,
    party: str,
    elections: List[str] = None
):
    """
    Get voting trends for a specific party across elections.
    
    Args:
        entidad_id: State ID
        party: Party name (e.g., 'MORENA', 'PAN', 'PRI')
        elections: Optional list of elections to include
        
    Returns:
        Time series data for the party
    """
    try:
        # If no elections specified, get all available
        if elections is None:
            all_elections = data_service.get_available_elections()
            state_elections = all_elections[
                all_elections["entidad_id"] == entidad_id
            ]
            elections = sorted(state_elections["election_name"].unique().tolist())
        
        # Get data for each election
        trends = []
        variable = f"{party.upper()}_PCT"
        
        for election in elections:
            try:
                metrics = data_service.get_aggregated_metrics(
                    election_name=election,
                    entidad_id=entidad_id,
                    variables=[variable]
                )
                
                if variable in metrics:
                    trends.append({
                        "election_name": election,
                        "party": party.upper(),
                        "percentage": metrics[variable],
                        "sections": metrics.get("sections", 0),
                        "total_votes": metrics.get("total_votes", 0)
                    })
            except Exception as e:
                logger.warning(f"Could not load {election}: {e}")
                continue
        
        if not trends:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for party {party} in state {entidad_id}"
            )
        
        return {
            "entidad_id": entidad_id,
            "party": party.upper(),
            "trends": trends,
            "elections_analyzed": len(trends)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting party trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state-rankings/{election_name}/{party}")
async def get_state_rankings(election_name: str, party: str):
    """
    Rank all states by party performance for an election.
    
    Args:
        election_name: Election name
        party: Party name
        
    Returns:
        States ranked by party percentage
    """
    try:
        variable = f"{party.upper()}_PCT"
        
        # Get all states for this election
        states = data_service.get_states_for_election(election_name)
        
        if not states:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for election {election_name}"
            )
        
        # Get metrics for each state
        rankings = []
        
        for state_info in states:
            entidad_id = state_info["entidad_id"]
            
            try:
                metrics = data_service.get_aggregated_metrics(
                    election_name=election_name,
                    entidad_id=entidad_id,
                    variables=[variable]
                )
                
                if variable in metrics:
                    rankings.append({
                        "entidad_id": entidad_id,
                        "entidad_name": metrics["entidad_name"],
                        "party": party.upper(),
                        "percentage": metrics[variable],
                        "sections": metrics["sections"],
                        "total_votes": metrics["total_votes"]
                    })
            except Exception as e:
                logger.warning(f"Could not load state {entidad_id}: {e}")
                continue
        
        # Sort by percentage descending
        rankings.sort(key=lambda x: x["percentage"], reverse=True)
        
        # Add rank
        for i, item in enumerate(rankings, 1):
            item["rank"] = i
        
        return {
            "election_name": election_name,
            "party": party.upper(),
            "rankings": rankings,
            "total_states": len(rankings)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting state rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
