"""
Visualization Router
====================

API endpoints for generating visualizations.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import logging
import geopandas as gpd
import pandas as pd

from dashboard.api.models import VisualizationRequest
from dashboard.api.services import DataService, SpatialService, VisualizationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/viz", tags=["visualization"])

# Initialize services
data_service = DataService()
spatial_service = SpatialService()
viz_service = VisualizationService()


@router.post("/spatial-lag-map")
async def create_spatial_lag_map(request: VisualizationRequest):
    """
    Generate side-by-side maps comparing original values and spatial lag.
    
    Args:
        request: VisualizationRequest with election, state, and variable info
        
    Returns:
        Base64 encoded image (static) or HTML (interactive)
    """
    try:
        logger.info(f"Creating spatial lag map: {request.election_name}, "
                   f"entidad={request.entidad_id}, style={request.style}")
        
        # Load data with geometry
        gdf = data_service.load_election_data(
            election_name=request.election_name,
            entidad_id=request.entidad_id,
            as_geodataframe=True
        )
        
        logger.info(f"Got data type: {type(gdf)}")
        
        # Compute spatial lag
        gdf_lag = spatial_service.compute_spatial_lag(
            gdf=gdf,
            variable=request.variable,
            weights_type="queen"
        )
        
        lag_variable = f"{request.variable}_lag"
        
        # Get entidad name for title
        entidad_name = gdf["ENTIDAD"].iloc[0] if "ENTIDAD" in gdf.columns else f"State {request.entidad_id}"
        title = f"{request.election_name} - {entidad_name}"
        
        # Create visualization
        content = viz_service.create_spatial_lag_comparison(
            gdf=gdf_lag,
            variable=request.variable,
            lag_variable=lag_variable,
            style=request.style,
            title=title
        )
        
        if request.style == "static":
            # Return as image
            return {
                "content": content,
                "content_type": "image/png",
                "encoding": "base64"
            }
        else:
            # Return as HTML
            return {
                "content": content,
                "content_type": "text/html",
                "encoding": "utf-8"
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating spatial lag map: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/choropleth")
async def create_choropleth(request: VisualizationRequest):
    """
    Generate a choropleth map for a variable.
    
    Args:
        request: VisualizationRequest with election, state, and variable info
        
    Returns:
        Base64 encoded image (static) or HTML (interactive)
    """
    try:
        logger.info(f"Creating choropleth: {request.election_name}, "
                   f"entidad={request.entidad_id}, var={request.variable}")
        
        # Load data with geometry
        gdf = data_service.load_election_data(
            election_name=request.election_name,
            entidad_id=request.entidad_id,
            as_geodataframe=True
        )
        
        logger.info(f"Got data type: {type(gdf)}")
        
        # Get entidad name for title
        entidad_name = gdf["ENTIDAD"].iloc[0] if "ENTIDAD" in gdf.columns else f"State {request.entidad_id}"
        title = f"{request.variable} - {request.election_name} - {entidad_name}"
        
        # Create visualization
        content = viz_service.create_choropleth_map(
            gdf=gdf,
            variable=request.variable,
            style=request.style,
            title=title
        )
        
        if request.style == "static":
            return {
                "content": content,
                "content_type": "image/png",
                "encoding": "base64"
            }
        else:
            return {
                "content": content,
                "content_type": "text/html",
                "encoding": "utf-8"
            }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating choropleth: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class ChartRequest(BaseModel):
    """Request model for chart generation."""
    data: list
    x: str
    y: str
    style: str = "interactive"
    title: Optional[str] = None
    color: Optional[str] = None


@router.post("/bar-chart")
async def create_bar_chart(request: ChartRequest):
    """
    Generate a bar chart from data.
    
    Args:
        request: ChartRequest with data and chart configuration
        
    Returns:
        Base64 encoded image (static) or HTML (interactive)
    """
    try:
        logger.info(f"Creating bar chart: x={request.x}, y={request.y}, style={request.style}")
        
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Create visualization
        content = viz_service.create_bar_chart(
            df=df,
            x=request.x,
            y=request.y,
            style=request.style,
            title=request.title,
            color=request.color
        )
        
        if request.style == "static":
            return {
                "content": content,
                "content_type": "image/png",
                "encoding": "base64"
            }
        else:
            return {
                "content": content,
                "content_type": "text/html",
                "encoding": "utf-8"
            }
    
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/line-chart")
async def create_line_chart(request: ChartRequest):
    """
    Generate a line chart for temporal analysis.
    
    Args:
        request: ChartRequest with data and chart configuration
        
    Returns:
        Base64 encoded image (static) or HTML (interactive)
    """
    try:
        logger.info(f"Creating line chart: x={request.x}, y={request.y}, style={request.style}")
        
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Create visualization
        content = viz_service.create_line_chart(
            df=df,
            x=request.x,
            y=request.y,
            style=request.style,
            title=request.title,
            color=request.color
        )
        
        if request.style == "static":
            return {
                "content": content,
                "content_type": "image/png",
                "encoding": "base64"
            }
        else:
            return {
                "content": content,
                "content_type": "text/html",
                "encoding": "utf-8"
            }
    
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
