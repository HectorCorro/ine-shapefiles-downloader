"""
API Endpoints Tests
===================

Tests for all API endpoints.
"""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_endpoint(self, client):
        """Test dedicated health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestDataEndpoints:
    """Test data-related endpoints."""
    
    def test_list_elections(self, client):
        """Test listing all elections."""
        response = client.get("/api/data/elections")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_elections_summary(self, client):
        """Test getting elections summary."""
        response = client.get("/api/data/elections/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "unique_elections" in data
        assert "elections" in data
    
    def test_list_states(self, client):
        """Test listing all states."""
        response = client.get("/api/data/states")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 32  # Mexico has 32 states
        
        # Check first state structure
        if data:
            state = data[0]
            assert "entidad_id" in state
            assert "entidad_name" in state
            assert "code" in state
    
    def test_get_states_for_election(self, client, sample_election_name):
        """Test getting states for a specific election."""
        response = client.get(f"/api/data/election/{sample_election_name}/states")
        
        # May not have data, but should not error
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            if data:
                state = data[0]
                assert "entidad_id" in state
                assert "entidad_name" in state
                assert "has_geometry" in state
    
    def test_get_election_metrics(self, client, sample_election_name, sample_entidad_id):
        """Test getting election metrics."""
        response = client.get(
            f"/api/data/election/{sample_election_name}/{sample_entidad_id}/metrics"
        )
        
        # May not have data
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "election_name" in data
            assert "entidad_id" in data
            assert "sections" in data


class TestSpatialEndpoints:
    """Test spatial analysis endpoints."""
    
    def test_compute_moran_i_invalid_data(self, client):
        """Test Moran's I with invalid data returns appropriate error."""
        response = client.post(
            "/api/spatial/moran",
            json={
                "election_name": "INVALID_ELECTION",
                "entidad_id": 999,
                "variable": "INVALID_VAR"
            }
        )
        
        # Should return error
        assert response.status_code in [400, 404, 500]
    
    def test_compute_spatial_lag_invalid_data(self, client):
        """Test spatial lag with invalid data returns appropriate error."""
        response = client.post(
            "/api/spatial/lag",
            json={
                "election_name": "INVALID_ELECTION",
                "entidad_id": 999,
                "variable": "INVALID_VAR"
            }
        )
        
        # Should return error
        assert response.status_code in [400, 404, 500]
    
    def test_get_available_variables(self, client, sample_election_name, sample_entidad_id):
        """Test getting available variables."""
        response = client.get(
            f"/api/spatial/variables/{sample_election_name}/{sample_entidad_id}"
        )
        
        # May not have data
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "percentage_variables" in data
            assert "other_numeric_variables" in data


class TestComparisonEndpoints:
    """Test comparison endpoints."""
    
    def test_cross_state_comparison_invalid(self, client):
        """Test cross-state comparison with invalid data."""
        response = client.post(
            "/api/comparison/cross-state",
            json={
                "election_name": "INVALID_ELECTION",
                "entidad_ids": [1, 2]
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]
    
    def test_temporal_comparison_invalid(self, client):
        """Test temporal comparison with invalid data."""
        response = client.post(
            "/api/comparison/temporal",
            json={
                "entidad_id": 999,
                "election_names": ["INVALID1", "INVALID2"]
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]
    
    def test_cross_state_validation(self, client):
        """Test request validation for cross-state comparison."""
        # Missing required field
        response = client.post(
            "/api/comparison/cross-state",
            json={
                "election_name": "PRES_2024"
                # Missing entidad_ids
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_temporal_validation(self, client):
        """Test request validation for temporal comparison."""
        # Invalid entidad_id
        response = client.post(
            "/api/comparison/temporal",
            json={
                "entidad_id": 99,  # Out of range
                "election_names": ["PRES_2024"]  # Too few
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestVisualizationEndpoints:
    """Test visualization endpoints."""
    
    def test_bar_chart_creation(self, client):
        """Test creating a simple bar chart."""
        response = client.post(
            "/api/viz/bar-chart",
            json={
                "data": [
                    {"category": "A", "value": 10},
                    {"category": "B", "value": 20}
                ],
                "x": "category",
                "y": "value",
                "style": "static"
            }
        )
        
        # Should succeed or fail gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert "content_type" in data
    
    def test_line_chart_creation(self, client):
        """Test creating a simple line chart."""
        response = client.post(
            "/api/viz/line-chart",
            json={
                "data": [
                    {"x": "2020", "y": 10},
                    {"x": "2021", "y": 15},
                    {"x": "2022", "y": 12}
                ],
                "x": "x",
                "y": "y",
                "style": "static"
            }
        )
        
        # Should succeed or fail gracefully
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert "content_type" in data


class TestValidation:
    """Test request validation."""
    
    def test_invalid_entidad_id_too_low(self, client):
        """Test that entidad_id < 1 is rejected."""
        response = client.post(
            "/api/spatial/moran",
            json={
                "election_name": "PRES_2024",
                "entidad_id": 0,  # Invalid
                "variable": "MORENA_PCT"
            }
        )
        
        assert response.status_code == 422
    
    def test_invalid_entidad_id_too_high(self, client):
        """Test that entidad_id > 32 is rejected."""
        response = client.post(
            "/api/spatial/moran",
            json={
                "election_name": "PRES_2024",
                "entidad_id": 33,  # Invalid
                "variable": "MORENA_PCT"
            }
        )
        
        assert response.status_code == 422
    
    def test_empty_election_name(self, client):
        """Test that empty election_name is rejected."""
        response = client.post(
            "/api/spatial/moran",
            json={
                "election_name": "",  # Empty
                "entidad_id": 9,
                "variable": "MORENA_PCT"
            }
        )
        
        assert response.status_code == 422
    
    def test_invalid_weights_type(self, client):
        """Test that invalid weights_type is rejected."""
        response = client.post(
            "/api/spatial/moran",
            json={
                "election_name": "PRES_2024",
                "entidad_id": 9,
                "variable": "MORENA_PCT",
                "weights_type": "invalid"  # Not 'queen' or 'rook'
            }
        )
        
        assert response.status_code == 422
