"""
FastAPI Main Application
=========================

Main entry point for the Electoral Dashboard API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from dashboard.config import CORS_ORIGINS, API_VERSION, LOG_LEVEL, LOG_FORMAT
from dashboard.api.routes import (
    data_router,
    spatial_router,
    comparison_router,
    visualization_router
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Electoral Data Dashboard API",
    description="REST API for Mexican electoral data analysis and visualization",
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("Electoral Dashboard API Starting")
    logger.info("=" * 60)
    logger.info(f"Version: {API_VERSION}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info("API Documentation: http://localhost:8000/api/docs")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Electoral Dashboard API Shutting Down")


# Health check endpoint
@app.get("/", tags=["health"])
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "service": "Electoral Dashboard API",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat()
    }


# Mount routers
app.include_router(data_router)
app.include_router(spatial_router)
app.include_router(comparison_router)
app.include_router(visualization_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    import traceback
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )


# Entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "dashboard.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
