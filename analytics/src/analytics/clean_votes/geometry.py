"""
Geometry Merger
===============

Merges cleaned electoral data with shapefile geometries.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


class GeometryMerger:
    """
    Merges electoral data with shapefile geometries.
    """
    
    def __init__(self, shapefile_base_dir: Optional[str] = None):
        """
        Initialize the geometry merger.
        
        Args:
            shapefile_base_dir: Base directory containing shapefiles organized by state.
                              If None, will need to be provided per merge operation.
        """
        self.shapefile_base_dir = Path(shapefile_base_dir) if shapefile_base_dir else None
    
    def merge_with_shapefile(
        self,
        df: pd.DataFrame,
        shapefile_path: Optional[str] = None,
        entidad_id: Optional[int] = None,
        shapefile_type: str = 'peepjf'
    ) -> gpd.GeoDataFrame:
        """
        Merge electoral data with shapefile geometries.
        
        Args:
            df: Cleaned electoral DataFrame
            shapefile_path: Explicit path to shapefile. If None, will construct from entidad_id.
            entidad_id: ENTIDAD ID for automatic shapefile path construction
            shapefile_type: Type of shapefile ('peepjf' or 'nacional')
            
        Returns:
            GeoDataFrame with merged data and geometries
            
        Raises:
            ValueError: If neither shapefile_path nor entidad_id is provided
            FileNotFoundError: If shapefile cannot be found
        """
        if shapefile_path is None and entidad_id is None:
            raise ValueError("Must provide either shapefile_path or entidad_id")
        
        # Construct shapefile path if not provided
        if shapefile_path is None:
            shapefile_path = self._construct_shapefile_path(entidad_id, shapefile_type)
        
        shapefile_path = Path(shapefile_path)
        
        if not shapefile_path.exists():
            raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
        
        logger.info(f"Reading shapefile: {shapefile_path}")
        gdf = gpd.read_file(shapefile_path)
        logger.info(f"Loaded {len(gdf)} geometries")
        
        # Prepare merge keys
        gdf_prepared = self._prepare_geodataframe(gdf)
        df_prepared = self._prepare_dataframe(df)
        
        # Perform merge
        gdf_merged = self._perform_merge(gdf_prepared, df_prepared)
        
        logger.info(f"Merge completed. Final shape: {gdf_merged.shape}")
        logger.info(f"Rows with geometry: {gdf_merged['geometry'].notna().sum()}")
        
        return gdf_merged
    
    def _construct_shapefile_path(self, entidad_id: int, shapefile_type: str) -> Path:
        """
        Construct shapefile path from entidad_id.
        
        Args:
            entidad_id: State ID (1-32)
            shapefile_type: 'peepjf' or 'nacional'
            
        Returns:
            Path to SECCION.shp file
        """
        if self.shapefile_base_dir is None:
            # Use default data/geo directory
            self.shapefile_base_dir = Path(__file__).parents[4] / 'data' / 'geo'
        
        # Map entidad_id to folder name
        entidad_folders = {
            1: "1_Aguascalientes",
            2: "2_Baja_California",
            3: "3_Baja_California_Sur",
            4: "4_Campeche",
            5: "5_Coahuila",
            6: "6_Colima",
            7: "7_Chiapas",
            8: "8_Chihuahua",
            9: "9_CDMX",
            10: "10_Durango",
            11: "11_Guanajuato",
            12: "12_Guerrero",
            13: "13_Hidalgo",
            14: "14_Jalisco",
            15: "15_Mexico",
            16: "16_Michoacan",
            17: "17_Morelos",
            18: "18_Nayarit",
            19: "19_Nuevo_Leon",
            20: "20_Oaxaca",
            21: "21_Puebla",
            22: "22_Queretaro",
            23: "23_Quintana_Roo",
            24: "24_San_Luis_Potosi",
            25: "25_Sinaloa",
            26: "26_Sonora",
            27: "27_Tabasco",
            28: "28_Tamaulipas",
            29: "29_Tlaxcala",
            30: "30_Veracruz",
            31: "31_Yucatan",
            32: "32_Zacatecas"
        }
        
        folder_name = entidad_folders.get(entidad_id)
        if folder_name is None:
            raise ValueError(f"Invalid entidad_id: {entidad_id}. Must be 1-32.")
        
        # Construct path based on shapefile type
        if shapefile_type == 'peepjf':
            base_path = self.shapefile_base_dir / 'shapefiles_peepjf' / folder_name
            # Format: 01, 02, ..., 32
            entidad_str = str(entidad_id).zfill(2)
            shapefile_path = base_path / entidad_str / 'SECCION.shp'
        elif shapefile_type == 'nacional':
            base_path = self.shapefile_base_dir / 'productos_ine_nacional' / folder_name / 'Shapefile'
            
            # The nacional shapefiles have an extra subfolder with pattern: "01 AGUASCALIENTES"
            # We need to find it dynamically since the state names vary
            if base_path.exists():
                # Look for the state subfolder (should be the only directory inside Shapefile/)
                subdirs = [d for d in base_path.iterdir() if d.is_dir()]
                if subdirs:
                    shapefile_path = subdirs[0] / 'SECCION.shp'
                else:
                    # Fallback: try direct path
                    shapefile_path = base_path / 'SECCION.shp'
            else:
                # Fallback: try direct path
                shapefile_path = base_path / 'SECCION.shp'
        else:
            raise ValueError(f"Invalid shapefile_type: {shapefile_type}. Must be 'peepjf' or 'nacional'.")
        
        return shapefile_path
    
    def _prepare_geodataframe(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Prepare GeoDataFrame for merging (standardize column types).
        
        Args:
            gdf: Original GeoDataFrame
            
        Returns:
            Prepared GeoDataFrame
        """
        gdf = gdf.copy()
        
        # Convert ENTIDAD to Int64 if it exists
        if 'ENTIDAD' in gdf.columns:
            if gdf['ENTIDAD'].dtype == 'object':
                gdf['ENTIDAD'] = pd.to_numeric(gdf['ENTIDAD'], errors='coerce')
            gdf['ENTIDAD'] = gdf['ENTIDAD'].astype('Int64')
        
        # Convert SECCION to Int64 if it exists
        if 'SECCION' in gdf.columns:
            if gdf['SECCION'].dtype == 'object':
                gdf['SECCION'] = pd.to_numeric(gdf['SECCION'], errors='coerce')
            gdf['SECCION'] = gdf['SECCION'].astype('Int64')
        
        return gdf
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare electoral DataFrame for merging (ensure proper types).
        
        Args:
            df: Electoral DataFrame
            
        Returns:
            Prepared DataFrame
        """
        df = df.copy()
        
        # Ensure ID_ENTIDAD and SECCION are Int64
        for col in ['ID_ENTIDAD', 'SECCION']:
            if col in df.columns:
                if df[col].dtype != 'Int64':
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        
        return df
    
    def _perform_merge(
        self,
        gdf: gpd.GeoDataFrame,
        df: pd.DataFrame
    ) -> gpd.GeoDataFrame:
        """
        Perform the actual merge operation.
        
        Args:
            gdf: Prepared GeoDataFrame
            df: Prepared electoral DataFrame
            
        Returns:
            Merged GeoDataFrame
        """
        # Merge on ENTIDAD and SECCION
        gdf_merged = gdf.merge(
            df,
            left_on=['ENTIDAD', 'SECCION'],
            right_on=['ID_ENTIDAD', 'SECCION'],
            how='inner',  # Only keep matching records
            suffixes=('_gdf', '')
        )
        
        # Ensure it's still a GeoDataFrame
        if not isinstance(gdf_merged, gpd.GeoDataFrame):
            gdf_merged = gpd.GeoDataFrame(gdf_merged, geometry='geometry', crs=gdf.crs)
        
        # Check for missing geometries
        missing_geom = gdf_merged['geometry'].isna().sum()
        if missing_geom > 0:
            logger.warning(f"Found {missing_geom} rows without geometry")
        
        return gdf_merged
    
    def save_geojson(
        self,
        gdf: gpd.GeoDataFrame,
        output_path: str,
        reproject: bool = True,
        target_crs: str = 'EPSG:4326'
    ):
        """
        Save GeoDataFrame to GeoJSON.
        
        Args:
            gdf: GeoDataFrame to save
            output_path: Output file path
            reproject: Whether to reproject to target_crs
            target_crs: Target CRS (default: WGS84)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if reproject and gdf.crs != target_crs:
            logger.info(f"Reprojecting from {gdf.crs} to {target_crs}")
            gdf = gdf.to_crs(target_crs)
        
        logger.info(f"Saving GeoJSON to: {output_path}")
        gdf.to_file(output_path, driver='GeoJSON')
        logger.info("GeoJSON saved successfully")

