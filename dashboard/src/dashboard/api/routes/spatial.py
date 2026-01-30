"""
Spatial Analysis Router
========================

API endpoints for spatial autocorrelation analysis.
"""

from fastapi import APIRouter, HTTPException
import logging
import geopandas as gpd

from dashboard.api.models import (
    SpatialLagRequest,
    MoranRequest,
    MoranResult,
    SpatialLagResult
)
from dashboard.api.services import DataService, SpatialService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/spatial", tags=["spatial"])

# Initialize services
data_service = DataService()
spatial_service = SpatialService()


@router.post("/lag", response_model=SpatialLagResult)
async def compute_spatial_lag(request: SpatialLagRequest):
    """
    Compute spatial lag for a variable.
    
    Spatial lag is the weighted average of neighboring values.
    
    Args:
        request: SpatialLagRequest with election, state, and variable info
        
    Returns:
        GeoJSON with original values and spatial lag
    """
    try:
        logger.info(f"Computing spatial lag: {request.election_name}, "
                   f"entidad={request.entidad_id}, var={request.variable}")
        
        # Load data with geometry
        gdf = data_service.load_election_data(
            election_name=request.election_name,
            entidad_id=request.entidad_id,
            as_geodataframe=True
        )
        
        logger.info(f"Got data type: {type(gdf)}, is GeoDataFrame: {isinstance(gdf, gpd.GeoDataFrame)}")
        
        # Let the spatial service handle validation
        # Compute spatial lag
        gdf_lag, stats = spatial_service.compute_spatial_lag_with_statistics(
            gdf=gdf,
            variable=request.variable,
            weights_type=request.weights_type
        )
        
        # Convert to GeoJSON
        gdf_wgs84 = gdf_lag.to_crs(epsg=4326) if gdf_lag.crs else gdf_lag
        geojson = gdf_wgs84.to_json()
        
        import json
        geojson_dict = json.loads(geojson)
        
        # Get entidad name
        entidad_name = gdf["ENTIDAD"].iloc[0] if "ENTIDAD" in gdf.columns else f"State {request.entidad_id}"
        
        result = {
            "election_name": request.election_name,
            "entidad_id": request.entidad_id,
            "entidad_name": entidad_name,
            "variable": request.variable,
            "geojson": geojson_dict,
            "statistics": {
                "mean_original": stats["original"]["mean"],
                "mean_lag": stats["lag"]["mean"],
                "correlation": stats["correlation"],
                "std_original": stats["original"]["std"],
                "std_lag": stats["lag"]["std"],
                "n_observations": stats["original"]["count"]
            }
        }
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing spatial lag: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moran", response_model=MoranResult)
async def compute_moran_i(request: MoranRequest):
    """
    Compute Moran's I spatial autocorrelation statistic.
    
    Moran's I measures the degree of spatial clustering in the data.
    - Values near +1 indicate positive spatial autocorrelation (similar values cluster)
    - Values near -1 indicate negative spatial autocorrelation (dissimilar values are neighbors)
    - Values near 0 indicate random spatial pattern
    
    Args:
        request: MoranRequest with election, state, and variable info
        
    Returns:
        Moran's I statistic with interpretation
    """
    try:
        logger.info(f"Computing Moran's I: {request.election_name}, "
                   f"entidad={request.entidad_id}, var={request.variable}")
        
        # Load data with geometry
        gdf = data_service.load_election_data(
            election_name=request.election_name,
            entidad_id=request.entidad_id,
            as_geodataframe=True
        )
        
        logger.info(f"Got data type: {type(gdf)}, is GeoDataFrame: {isinstance(gdf, gpd.GeoDataFrame)}")
        
        # Let the spatial service handle validation - it will raise better errors
        # Compute Moran's I
        moran_result = spatial_service.compute_moran_i(
            gdf=gdf,
            variable=request.variable,
            weights_type=request.weights_type,
            permutations=request.permutations
        )
        
        # Add request info
        moran_result["election_name"] = request.election_name
        moran_result["entidad_id"] = request.entidad_id
        
        return moran_result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing Moran's I: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/variables/{election_name}/{entidad_id}")
async def get_available_variables(election_name: str, entidad_id: int):
    """
    Get list of variables available for spatial analysis.
    
    Args:
        election_name: Name of the election
        entidad_id: State ID
        
    Returns:
        List of variable names that can be used for spatial analysis
    """
    try:
        # Load data (without geometry for faster query)
        df = data_service.load_election_data(
            election_name=election_name,
            entidad_id=entidad_id,
            as_geodataframe=False
        )
        
        # Filter for numeric columns that are likely percentages or counts
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        # Prioritize percentage columns
        pct_cols = [col for col in numeric_cols if 'PCT' in col.upper()]
        
        # Filter out non-party variables (administrative data)
        excluded_patterns = ['DISTRITO_FEDERAL', 'EXT_CONTIGUA', 'UBICACION_CASILLA', 
                            'DISTRITO', 'SECCION', 'CASILLA', 'ID_']
        
        pct_cols = [col for col in pct_cols 
                   if not any(pattern in col.upper() for pattern in excluded_patterns)]
        
        other_numeric = [col for col in numeric_cols if 'PCT' not in col.upper()]
        
        return {
            "percentage_variables": pct_cols,
            "other_numeric_variables": other_numeric[:20],  # Limit to first 20
            "total_numeric_columns": len(numeric_cols)
        }
    
    except Exception as e:
        logger.error(f"Error getting available variables: {e}")
        raise HTTPException(status_code=500, detail=str(e))
