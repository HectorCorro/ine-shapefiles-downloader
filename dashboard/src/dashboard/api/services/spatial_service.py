"""
Spatial Analysis Service
=========================

Service for spatial autocorrelation analysis using libpysal and esda.
"""

import logging
from typing import Dict, Any, Literal, Tuple
import geopandas as gpd
import pandas as pd
from libpysal.weights import Queen, Rook
from esda.moran import Moran
from functools import lru_cache

logger = logging.getLogger(__name__)


class SpatialService:
    """
    Service for spatial analysis operations.
    
    Provides methods for computing spatial weights, spatial lag,
    and Moran's I spatial autocorrelation.
    """
    
    @staticmethod
    def create_spatial_weights(
        gdf: gpd.GeoDataFrame,
        weights_type: Literal["queen", "rook"] = "queen"
    ) -> Any:
        """
        Create spatial weights matrix from GeoDataFrame.
        
        Args:
            gdf: GeoDataFrame with geometries
            weights_type: Type of contiguity weights ('queen' or 'rook')
            
        Returns:
            Spatial weights object
        """
        # Check if it's actually a GeoDataFrame
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError(
                f"Expected GeoDataFrame but got {type(gdf).__name__}. "
                f"Data must be loaded with as_geodataframe=True and must have geometry in the database."
            )
        
        if 'geometry' not in gdf.columns:
            raise ValueError(
                f"GeoDataFrame is missing 'geometry' column. Available columns: {list(gdf.columns)}"
            )
        
        logger.info(f"Creating {weights_type} spatial weights for {len(gdf)} observations")
        
        if weights_type == "queen":
            w = Queen.from_dataframe(gdf)
        elif weights_type == "rook":
            w = Rook.from_dataframe(gdf)
        else:
            raise ValueError(f"Invalid weights_type: {weights_type}. Must be 'queen' or 'rook'")
        
        logger.info(f"Weights created: {w.n} observations, {w.nonzero} connections, "
                   f"avg neighbors: {w.mean_neighbors:.2f}")
        
        return w
    
    @staticmethod
    def compute_spatial_lag(
        gdf: gpd.GeoDataFrame,
        variable: str,
        weights_type: Literal["queen", "rook"] = "queen"
    ) -> gpd.GeoDataFrame:
        """
        Compute spatial lag for a variable.
        
        Spatial lag is the weighted average of neighboring values.
        
        Args:
            gdf: GeoDataFrame with data
            variable: Variable to compute lag for
            weights_type: Type of spatial weights
            
        Returns:
            GeoDataFrame with original data plus spatial lag column
        """
        logger.info(f"Computing spatial lag for variable: {variable}")
        
        # Check if variable exists
        if variable not in gdf.columns:
            raise ValueError(f"Variable '{variable}' not found in data. "
                           f"Available columns: {list(gdf.columns)}")
        
        # Remove missing values
        gdf_clean = gdf.dropna(subset=[variable]).copy()
        n_missing = len(gdf) - len(gdf_clean)
        
        if n_missing > 0:
            logger.warning(f"Removed {n_missing} observations with missing values in {variable}")
        
        if len(gdf_clean) == 0:
            raise ValueError(f"No valid observations for variable {variable}")
        
        # Create spatial weights
        w = SpatialService.create_spatial_weights(gdf_clean, weights_type)
        
        # Compute spatial lag
        lag_variable = f"{variable}_lag"
        gdf_clean[lag_variable] = w.sparse.dot(gdf_clean[variable].values)
        
        logger.info(f"Spatial lag computed: {lag_variable}")
        
        # Add correlation
        correlation = gdf_clean[variable].corr(gdf_clean[lag_variable])
        logger.info(f"Correlation between {variable} and {lag_variable}: {correlation:.4f}")
        
        return gdf_clean
    
    @staticmethod
    def compute_moran_i(
        gdf: gpd.GeoDataFrame,
        variable: str,
        weights_type: Literal["queen", "rook"] = "queen",
        permutations: int = 999
    ) -> Dict[str, Any]:
        """
        Compute Moran's I spatial autocorrelation statistic.
        
        Args:
            gdf: GeoDataFrame with data
            variable: Variable to analyze
            weights_type: Type of spatial weights
            permutations: Number of permutations for significance test
            
        Returns:
            Dictionary with Moran's I results and interpretation
        """
        logger.info(f"Computing Moran's I for variable: {variable}")
        
        # Check if variable exists
        if variable not in gdf.columns:
            raise ValueError(f"Variable '{variable}' not found in data")
        
        # Remove missing values
        gdf_clean = gdf.dropna(subset=[variable]).copy()
        n_missing = len(gdf) - len(gdf_clean)
        
        if n_missing > 0:
            logger.warning(f"Removed {n_missing} observations with missing values")
        
        if len(gdf_clean) < 3:
            raise ValueError(f"Insufficient observations for Moran's I (need at least 3, got {len(gdf_clean)})")
        
        # Create spatial weights
        w = SpatialService.create_spatial_weights(gdf_clean, weights_type)
        
        # Check for islands
        islands = w.islands
        n_islands = len(islands)
        
        # Compute Moran's I
        moran = Moran(gdf_clean[variable].values, w, permutations=permutations)
        
        # Interpret results
        interpretation = SpatialService._interpret_moran(moran)
        
        # Get entidad name
        entidad_name = gdf_clean["ENTIDAD"].iloc[0] if "ENTIDAD" in gdf_clean.columns else "Unknown"
        
        result = {
            "entidad_name": entidad_name,
            "variable": variable,
            "moran_i": float(moran.I),
            "expected_i": float(moran.EI),
            "variance": float(moran.VI_norm) if hasattr(moran, "VI_norm") else None,
            "z_score": float(moran.z_norm),
            "p_value": float(moran.p_sim),
            "significant": moran.p_sim < 0.05,
            "interpretation": interpretation,
            "n_observations": len(gdf_clean),
            "mean_neighbors": float(w.mean_neighbors),
            "islands": n_islands
        }
        
        logger.info(f"Moran's I = {moran.I:.4f}, p-value = {moran.p_sim:.4f}, significant = {result['significant']}")
        
        return result
    
    @staticmethod
    def _interpret_moran(moran: Moran) -> str:
        """
        Generate human-readable interpretation of Moran's I result.
        
        Args:
            moran: Moran object with results
            
        Returns:
            Interpretation string
        """
        is_significant = moran.p_sim < 0.05
        is_positive = moran.I > moran.EI
        
        if not is_significant:
            return "No significant spatial autocorrelation detected (p >= 0.05). The spatial pattern could be random."
        
        if is_positive:
            strength = SpatialService._get_strength_label(abs(moran.I))
            return (f"{strength} positive spatial autocorrelation detected (p < 0.05). "
                   f"Similar values cluster together spatially.")
        else:
            strength = SpatialService._get_strength_label(abs(moran.I))
            return (f"{strength} negative spatial autocorrelation detected (p < 0.05). "
                   f"Dissimilar values are neighbors.")
    
    @staticmethod
    def _get_strength_label(abs_i: float) -> str:
        """Get strength label for Moran's I value."""
        if abs_i < 0.2:
            return "Weak"
        elif abs_i < 0.4:
            return "Moderate"
        elif abs_i < 0.6:
            return "Strong"
        else:
            return "Very strong"
    
    @staticmethod
    def get_spatial_statistics(
        gdf: gpd.GeoDataFrame,
        variable: str
    ) -> Dict[str, float]:
        """
        Get summary statistics for a spatial variable.
        
        Args:
            gdf: GeoDataFrame with data
            variable: Variable to summarize
            
        Returns:
            Dictionary with statistics
        """
        if variable not in gdf.columns:
            raise ValueError(f"Variable '{variable}' not found")
        
        series = gdf[variable].dropna()
        
        return {
            "count": int(len(series)),
            "mean": float(series.mean()),
            "median": float(series.median()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
            "q25": float(series.quantile(0.25)),
            "q75": float(series.quantile(0.75))
        }
    
    @staticmethod
    def compute_spatial_lag_with_statistics(
        gdf: gpd.GeoDataFrame,
        variable: str,
        weights_type: Literal["queen", "rook"] = "queen"
    ) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
        """
        Compute spatial lag with summary statistics.
        
        Args:
            gdf: GeoDataFrame with data
            variable: Variable to analyze
            weights_type: Type of spatial weights
            
        Returns:
            Tuple of (GeoDataFrame with lag, statistics dictionary)
        """
        # Compute spatial lag
        gdf_lag = SpatialService.compute_spatial_lag(gdf, variable, weights_type)
        
        lag_variable = f"{variable}_lag"
        
        # Compute statistics
        stats = {
            "original": SpatialService.get_spatial_statistics(gdf_lag, variable),
            "lag": SpatialService.get_spatial_statistics(gdf_lag, lag_variable),
            "correlation": float(gdf_lag[variable].corr(gdf_lag[lag_variable]))
        }
        
        return gdf_lag, stats
