"""
API Routes
==========

FastAPI routers for the electoral dashboard API.
"""

from .data import router as data_router
from .spatial import router as spatial_router
from .comparison import router as comparison_router
from .visualization import router as visualization_router

__all__ = [
    "data_router",
    "spatial_router",
    "comparison_router",
    "visualization_router"
]
