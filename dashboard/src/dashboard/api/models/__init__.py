"""
Pydantic Models for API
========================

Request and response models for API validation.
"""

from .requests import (
    SpatialLagRequest,
    MoranRequest,
    CrossStateRequest,
    TemporalRequest,
    VisualizationRequest
)

from .responses import (
    ElectionMetadata,
    StateInfo,
    MoranResult,
    SpatialLagResult,
    ComparisonResult,
    HealthCheckResponse
)

__all__ = [
    # Requests
    "SpatialLagRequest",
    "MoranRequest",
    "CrossStateRequest",
    "TemporalRequest",
    "VisualizationRequest",
    # Responses
    "ElectionMetadata",
    "StateInfo",
    "MoranResult",
    "SpatialLagResult",
    "ComparisonResult",
    "HealthCheckResponse"
]
