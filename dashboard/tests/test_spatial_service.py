"""
Spatial Service Tests
=====================

Tests for spatial analysis service logic.
"""

import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import sys
from pathlib import Path

# Add dashboard to path
dashboard_path = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(dashboard_path))

from dashboard.api.services.spatial_service import SpatialService


@pytest.fixture
def sample_gdf():
    """Create a sample GeoDataFrame for testing."""
    # Create a simple grid of polygons
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)])
    ]
    
    data = {
        'ID': [1, 2, 3, 4],
        'VALUE': [10.0, 20.0, 15.0, 25.0],
        'ENTIDAD': ['Test State'] * 4,
        'geometry': polygons
    }
    
    gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
    return gdf


class TestSpatialWeights:
    """Test spatial weights creation."""
    
    def test_create_queen_weights(self, sample_gdf):
        """Test creating Queen contiguity weights."""
        w = SpatialService.create_spatial_weights(sample_gdf, weights_type="queen")
        
        assert w is not None
        assert w.n == len(sample_gdf)
        assert w.mean_neighbors > 0
    
    def test_create_rook_weights(self, sample_gdf):
        """Test creating Rook contiguity weights."""
        w = SpatialService.create_spatial_weights(sample_gdf, weights_type="rook")
        
        assert w is not None
        assert w.n == len(sample_gdf)
    
    def test_invalid_weights_type(self, sample_gdf):
        """Test that invalid weights type raises error."""
        with pytest.raises(ValueError):
            SpatialService.create_spatial_weights(sample_gdf, weights_type="invalid")


class TestSpatialLag:
    """Test spatial lag computation."""
    
    def test_compute_spatial_lag(self, sample_gdf):
        """Test computing spatial lag."""
        gdf_lag = SpatialService.compute_spatial_lag(
            sample_gdf,
            variable="VALUE",
            weights_type="queen"
        )
        
        assert 'VALUE_lag' in gdf_lag.columns
        assert len(gdf_lag) == len(sample_gdf)
        assert not gdf_lag['VALUE_lag'].isna().all()
    
    def test_spatial_lag_with_missing_values(self, sample_gdf):
        """Test spatial lag handles missing values."""
        # Add missing value
        sample_gdf.loc[0, 'VALUE'] = None
        
        gdf_lag = SpatialService.compute_spatial_lag(
            sample_gdf,
            variable="VALUE",
            weights_type="queen"
        )
        
        # Should remove missing values
        assert len(gdf_lag) < len(sample_gdf)
        assert not gdf_lag['VALUE'].isna().any()
    
    def test_spatial_lag_invalid_variable(self, sample_gdf):
        """Test spatial lag with invalid variable."""
        with pytest.raises(ValueError):
            SpatialService.compute_spatial_lag(
                sample_gdf,
                variable="NONEXISTENT",
                weights_type="queen"
            )


class TestMoranI:
    """Test Moran's I computation."""
    
    def test_compute_moran_i(self, sample_gdf):
        """Test computing Moran's I."""
        result = SpatialService.compute_moran_i(
            sample_gdf,
            variable="VALUE",
            weights_type="queen",
            permutations=99  # Use fewer permutations for speed
        )
        
        assert 'moran_i' in result
        assert 'p_value' in result
        assert 'z_score' in result
        assert 'interpretation' in result
        assert 'significant' in result
        
        # Check types
        assert isinstance(result['moran_i'], float)
        assert isinstance(result['p_value'], float)
        assert isinstance(result['significant'], bool)
    
    def test_moran_i_with_missing_values(self, sample_gdf):
        """Test Moran's I handles missing values."""
        sample_gdf.loc[0, 'VALUE'] = None
        
        result = SpatialService.compute_moran_i(
            sample_gdf,
            variable="VALUE",
            weights_type="queen",
            permutations=99
        )
        
        assert result['n_observations'] < len(sample_gdf)
    
    def test_moran_i_insufficient_observations(self, sample_gdf):
        """Test Moran's I with too few observations."""
        # Keep only 2 observations
        gdf_small = sample_gdf.head(2)
        
        with pytest.raises(ValueError):
            SpatialService.compute_moran_i(
                gdf_small,
                variable="VALUE",
                weights_type="queen"
            )


class TestSpatialStatistics:
    """Test spatial statistics computation."""
    
    def test_get_spatial_statistics(self, sample_gdf):
        """Test computing spatial statistics."""
        stats = SpatialService.get_spatial_statistics(sample_gdf, "VALUE")
        
        assert 'count' in stats
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        
        # Verify values
        assert stats['count'] == len(sample_gdf)
        assert stats['mean'] == sample_gdf['VALUE'].mean()
        assert stats['min'] == sample_gdf['VALUE'].min()
        assert stats['max'] == sample_gdf['VALUE'].max()
    
    def test_spatial_statistics_invalid_variable(self, sample_gdf):
        """Test statistics with invalid variable."""
        with pytest.raises(ValueError):
            SpatialService.get_spatial_statistics(sample_gdf, "NONEXISTENT")


class TestSpatialLagWithStatistics:
    """Test combined spatial lag and statistics."""
    
    def test_compute_lag_with_statistics(self, sample_gdf):
        """Test computing spatial lag with statistics."""
        gdf_lag, stats = SpatialService.compute_spatial_lag_with_statistics(
            sample_gdf,
            variable="VALUE",
            weights_type="queen"
        )
        
        assert 'VALUE_lag' in gdf_lag.columns
        assert 'original' in stats
        assert 'lag' in stats
        assert 'correlation' in stats
        
        # Check statistics structure
        assert 'mean' in stats['original']
        assert 'mean' in stats['lag']
        assert isinstance(stats['correlation'], float)
