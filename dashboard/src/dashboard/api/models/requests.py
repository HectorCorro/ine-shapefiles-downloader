"""
Request Models
==============

Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional


class SpatialLagRequest(BaseModel):
    """Request for computing spatial lag."""
    
    election_name: str = Field(..., description="Election name (e.g., 'PRES_2024')")
    entidad_id: int = Field(..., ge=1, le=32, description="State ID (1-32)")
    variable: str = Field(..., description="Variable to analyze (e.g., 'MORENA_PCT')")
    weights_type: Literal["queen", "rook"] = Field(default="queen", description="Spatial weights type")
    
    @field_validator("election_name")
    @classmethod
    def validate_election_name(cls, v: str) -> str:
        """Validate election name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Election name cannot be empty")
        return v.strip().upper()
    
    @field_validator("variable")
    @classmethod
    def validate_variable(cls, v: str) -> str:
        """Validate variable name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Variable name cannot be empty")
        return v.strip()


class MoranRequest(BaseModel):
    """Request for computing Moran's I statistic."""
    
    election_name: str = Field(..., description="Election name (e.g., 'PRES_2024')")
    entidad_id: int = Field(..., ge=1, le=32, description="State ID (1-32)")
    variable: str = Field(..., description="Variable to analyze (e.g., 'MORENA_PCT')")
    weights_type: Literal["queen", "rook"] = Field(default="queen", description="Spatial weights type")
    permutations: int = Field(default=999, ge=99, le=9999, description="Number of permutations for significance test")
    
    @field_validator("election_name")
    @classmethod
    def validate_election_name(cls, v: str) -> str:
        """Validate election name format."""
        return v.strip().upper()
    
    @field_validator("variable")
    @classmethod
    def validate_variable(cls, v: str) -> str:
        """Validate variable name."""
        return v.strip()


class CrossStateRequest(BaseModel):
    """Request for cross-state comparison."""
    
    election_name: str = Field(..., description="Election name (e.g., 'PRES_2024')")
    entidad_ids: List[int] = Field(..., min_length=2, max_length=32, description="List of state IDs to compare")
    variables: Optional[List[str]] = Field(default=None, description="Variables to include (default: all major parties)")
    
    @field_validator("entidad_ids")
    @classmethod
    def validate_entidad_ids(cls, v: List[int]) -> List[int]:
        """Validate state IDs."""
        if not v:
            raise ValueError("At least one state ID is required")
        
        for state_id in v:
            if state_id < 1 or state_id > 32:
                raise ValueError(f"Invalid state ID: {state_id}. Must be between 1 and 32.")
        
        # Remove duplicates
        return list(set(v))
    
    @field_validator("election_name")
    @classmethod
    def validate_election_name(cls, v: str) -> str:
        """Validate election name format."""
        return v.strip().upper()


class TemporalRequest(BaseModel):
    """Request for temporal analysis (same state, multiple elections)."""
    
    entidad_id: int = Field(..., ge=1, le=32, description="State ID (1-32)")
    election_names: List[str] = Field(..., min_length=2, description="List of elections to compare")
    variables: Optional[List[str]] = Field(default=None, description="Variables to include (default: major parties)")
    
    @field_validator("election_names")
    @classmethod
    def validate_election_names(cls, v: List[str]) -> List[str]:
        """Validate and normalize election names."""
        if not v or len(v) < 2:
            raise ValueError("At least two elections are required for temporal comparison")
        
        # Normalize to uppercase and remove duplicates
        normalized = [name.strip().upper() for name in v if name.strip()]
        return list(dict.fromkeys(normalized))  # Preserve order while removing duplicates


class VisualizationRequest(BaseModel):
    """Request for generating visualizations."""
    
    election_name: str = Field(..., description="Election name")
    entidad_id: int = Field(..., ge=1, le=32, description="State ID (1-32)")
    variable: str = Field(..., description="Variable to visualize")
    style: Literal["static", "interactive"] = Field(default="interactive", description="Visualization style")
    chart_type: Optional[Literal["map", "bar", "line", "scatter"]] = Field(default="map", description="Type of chart")
    include_spatial_lag: bool = Field(default=False, description="Include spatial lag visualization")
    
    @field_validator("election_name")
    @classmethod
    def validate_election_name(cls, v: str) -> str:
        """Validate election name format."""
        return v.strip().upper()
    
    @field_validator("variable")
    @classmethod
    def validate_variable(cls, v: str) -> str:
        """Validate variable name."""
        return v.strip()
