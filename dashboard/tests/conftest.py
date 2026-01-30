"""
Pytest Configuration and Fixtures
==================================

Shared fixtures for testing the Electoral Dashboard.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add dashboard to path
dashboard_path = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(dashboard_path))

from dashboard.api.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_election_name():
    """Sample election name for testing."""
    return "PRES_2024"


@pytest.fixture
def sample_entidad_id():
    """Sample state ID for testing."""
    return 9  # CDMX


@pytest.fixture
def sample_variable():
    """Sample variable for spatial analysis."""
    return "MORENA_PCT"


@pytest.fixture
def sample_entidad_ids():
    """Sample state IDs for comparison."""
    return [1, 9, 15, 19]  # Aguascalientes, CDMX, Estado de México, Nuevo León
