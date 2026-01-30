"""
Response Models
===============

Pydantic models for API response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    version: str = Field(..., description="API version")


class StateInfo(BaseModel):
    """State information."""
    
    entidad_id: int = Field(..., description="State ID")
    entidad_name: str = Field(..., description="State name")
    code: str = Field(..., description="State code (e.g., '01', '09')")


class ElectionMetadata(BaseModel):
    """Election metadata information."""
    
    id: int = Field(..., description="Record ID")
    election_name: str = Field(..., description="Election name")
    election_date: Optional[str] = Field(None, description="Election date")
    entidad_id: int = Field(..., description="State ID")
    entidad_name: str = Field(..., description="State name")
    table_name: str = Field(..., description="Database table name")
    has_geometry: bool = Field(..., description="Whether data includes geometry")
    row_count: int = Field(..., description="Number of rows")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")


class MoranResult(BaseModel):
    """Moran's I spatial autocorrelation result."""
    
    election_name: str = Field(..., description="Election name")
    entidad_id: int = Field(..., description="State ID")
    entidad_name: str = Field(..., description="State name")
    variable: str = Field(..., description="Variable analyzed")
    moran_i: float = Field(..., description="Moran's I statistic")
    expected_i: float = Field(..., description="Expected I value under null hypothesis")
    variance: Optional[float] = Field(None, description="Variance of I")
    z_score: float = Field(..., description="Z-score (standardized statistic)")
    p_value: float = Field(..., description="P-value from permutation test")
    significant: bool = Field(..., description="Whether result is statistically significant (p < 0.05)")
    interpretation: str = Field(..., description="Human-readable interpretation")
    n_observations: int = Field(..., description="Number of observations")
    mean_neighbors: float = Field(..., description="Average number of neighbors")
    islands: int = Field(default=0, description="Number of observations with no neighbors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "election_name": "PRES_2024",
                "entidad_id": 9,
                "entidad_name": "CDMX",
                "variable": "MORENA_PCT",
                "moran_i": 0.6234,
                "expected_i": -0.0005,
                "z_score": 12.45,
                "p_value": 0.001,
                "significant": True,
                "interpretation": "Strong positive spatial autocorrelation: similar values cluster together",
                "n_observations": 2149,
                "mean_neighbors": 5.2,
                "islands": 0
            }
        }


class SpatialLagResult(BaseModel):
    """Spatial lag computation result."""
    
    election_name: str = Field(..., description="Election name")
    entidad_id: int = Field(..., description="State ID")
    entidad_name: str = Field(..., description="State name")
    variable: str = Field(..., description="Variable analyzed")
    geojson: Dict[str, Any] = Field(..., description="GeoJSON with original and lag values")
    statistics: Dict[str, float] = Field(..., description="Summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "election_name": "PRES_2024",
                "entidad_id": 9,
                "entidad_name": "CDMX",
                "variable": "MORENA_PCT",
                "geojson": {
                    "type": "FeatureCollection",
                    "features": []
                },
                "statistics": {
                    "mean_original": 42.5,
                    "mean_lag": 42.3,
                    "correlation": 0.65
                }
            }
        }


class ComparisonResult(BaseModel):
    """Comparison analysis result."""
    
    comparison_type: str = Field(..., description="Type of comparison ('cross_state' or 'temporal')")
    data: List[Dict[str, Any]] = Field(..., description="Comparison data")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "comparison_type": "cross_state",
                "data": [
                    {
                        "entidad_name": "CDMX",
                        "sections": 2149,
                        "total_votes": 1923711,
                        "MORENA_PCT": 42.04
                    }
                ],
                "summary": {
                    "total_states": 4,
                    "total_sections": 8432,
                    "total_votes": 7654321
                }
            }
        }


class VisualizationResponse(BaseModel):
    """Visualization generation response."""
    
    visualization_type: str = Field(..., description="Type of visualization")
    style: str = Field(..., description="Style (static or interactive)")
    content: str = Field(..., description="Base64 encoded image or HTML content")
    content_type: str = Field(..., description="Content MIME type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
