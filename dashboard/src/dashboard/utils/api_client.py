"""
API Client
==========

Client for making requests to the FastAPI backend.
"""

import requests
import logging
from typing import Optional, List, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)


class APIClient:
    """
    Client for the Electoral Dashboard API.
    
    Provides methods for calling all API endpoints with caching support.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip("/")
        logger.info(f"APIClient initialized with base_url: {self.base_url}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method ('GET', 'POST', etc.)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            raise Exception(f"API request failed: {str(e)}")
    
    # Data endpoints
    
    @st.cache_data(ttl=3600)
    def get_elections(_self) -> List[Dict[str, Any]]:
        """Get list of all available elections."""
        return _self._make_request("GET", "/api/data/elections")
    
    @st.cache_data(ttl=3600)
    def get_elections_summary(_self) -> Dict[str, Any]:
        """Get summary of available elections."""
        return _self._make_request("GET", "/api/data/elections/summary")
    
    @st.cache_data(ttl=3600)
    def get_states(_self) -> List[Dict[str, Any]]:
        """Get list of all states."""
        return _self._make_request("GET", "/api/data/states")
    
    @st.cache_data(ttl=3600)
    def get_states_for_election(_self, election_name: str) -> List[Dict[str, Any]]:
        """Get states available for an election."""
        return _self._make_request("GET", f"/api/data/election/{election_name}/states")
    
    @st.cache_data(ttl=3600)
    def get_election_metrics(_self, election_name: str, entidad_id: int) -> Dict[str, Any]:
        """Get aggregated metrics for an election and state."""
        return _self._make_request(
            "GET",
            f"/api/data/election/{election_name}/{entidad_id}/metrics"
        )
    
    # Spatial endpoints
    
    @st.cache_data(ttl=300, show_spinner=False)  # 5 minutes for faster refresh
    def compute_spatial_lag(
        _self,
        election_name: str,
        entidad_id: int,
        variable: str,
        weights_type: str = "queen"
    ) -> Dict[str, Any]:
        """Compute spatial lag for a variable."""
        return _self._make_request(
            "POST",
            "/api/spatial/lag",
            json={
                "election_name": election_name,
                "entidad_id": entidad_id,
                "variable": variable,
                "weights_type": weights_type
            }
        )
    
    @st.cache_data(ttl=300, show_spinner=False)  # 5 minutes for faster refresh
    def compute_moran_i(
        _self,
        election_name: str,
        entidad_id: int,
        variable: str,
        weights_type: str = "queen",
        permutations: int = 999
    ) -> Dict[str, Any]:
        """Compute Moran's I statistic."""
        return _self._make_request(
            "POST",
            "/api/spatial/moran",
            json={
                "election_name": election_name,
                "entidad_id": entidad_id,
                "variable": variable,
                "weights_type": weights_type,
                "permutations": permutations
            }
        )
    
    @st.cache_data(ttl=3600)
    def get_available_variables(_self, election_name: str, entidad_id: int) -> Dict[str, Any]:
        """Get available variables for spatial analysis."""
        return _self._make_request(
            "GET",
            f"/api/spatial/variables/{election_name}/{entidad_id}"
        )
    
    # Comparison endpoints
    
    @st.cache_data(ttl=3600)
    def compare_cross_state(
        _self,
        election_name: str,
        entidad_ids: List[int],
        variables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare multiple states for one election."""
        return _self._make_request(
            "POST",
            "/api/comparison/cross-state",
            json={
                "election_name": election_name,
                "entidad_ids": entidad_ids,
                "variables": variables
            }
        )
    
    @st.cache_data(ttl=3600)
    def compare_temporal(
        _self,
        entidad_id: int,
        election_names: List[str],
        variables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare same state across multiple elections."""
        return _self._make_request(
            "POST",
            "/api/comparison/temporal",
            json={
                "entidad_id": entidad_id,
                "election_names": election_names,
                "variables": variables
            }
        )
    
    @st.cache_data(ttl=3600)
    def get_party_trends(
        _self,
        entidad_id: int,
        party: str,
        elections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get voting trends for a specific party."""
        params = {"elections": elections} if elections else {}
        return _self._make_request(
            "GET",
            f"/api/comparison/party-trends/{entidad_id}/{party}",
            params=params
        )
    
    # Visualization endpoints
    
    @st.cache_data(ttl=300, show_spinner=False)  # 5 minutes, faster refresh for development
    def create_spatial_lag_map(
        _self,
        election_name: str,
        entidad_id: int,
        variable: str,
        style: str = "interactive"
    ) -> Dict[str, Any]:
        """Generate spatial lag comparison map."""
        return _self._make_request(
            "POST",
            "/api/viz/spatial-lag-map",
            json={
                "election_name": election_name,
                "entidad_id": entidad_id,
                "variable": variable,
                "style": style,
                "include_spatial_lag": True
            }
        )
    
    @st.cache_data(ttl=3600)
    def create_bar_chart(
        _self,
        data: List[Dict[str, Any]],
        x: str,
        y: str,
        style: str = "interactive",
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate bar chart."""
        return _self._make_request(
            "POST",
            "/api/viz/bar-chart",
            json={
                "data": data,
                "x": x,
                "y": y,
                "style": style,
                "title": title,
                "color": color
            }
        )
    
    @st.cache_data(ttl=3600)
    def create_line_chart(
        _self,
        data: List[Dict[str, Any]],
        x: str,
        y: str,
        style: str = "interactive",
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate line chart."""
        return _self._make_request(
            "POST",
            "/api/viz/line-chart",
            json={
                "data": data,
                "x": x,
                "y": y,
                "style": style,
                "title": title,
                "color": color
            }
        )
