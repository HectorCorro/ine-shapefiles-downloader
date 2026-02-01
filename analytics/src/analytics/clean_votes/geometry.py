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
        
        # First try: Use the constructed/provided path
        if shapefile_path.exists():
            logger.info(f"Reading shapefile: {shapefile_path}")
            gdf = gpd.read_file(shapefile_path)
            logger.info(f"Loaded {len(gdf)} geometries")
            
            # Check if this shapefile has the correct ENTIDAD
            if 'ENTIDAD' in gdf.columns and entidad_id is not None:
                entidad_values = gdf['ENTIDAD'].unique()
                if len(entidad_values) == 1 and int(entidad_values[0]) != entidad_id:
                    logger.warning(f"Shapefile has wrong ENTIDAD ({entidad_values[0]}), expected {entidad_id}")
                    logger.info("Searching for correct shapefile...")
                    
                    # Use smart search to find the correct file
                    try:
                        shapefile_path = self._find_shapefile_by_entidad(entidad_id, shapefile_type)
                        gdf = gpd.read_file(shapefile_path)
                        logger.info(f"Loaded {len(gdf)} geometries from correct file")
                    except FileNotFoundError as e:
                        logger.error(f"Could not find correct shapefile: {e}")
                        # Continue with wrong data as fallback
        else:
            # File doesn't exist at expected path, use smart search
            logger.warning(f"Shapefile not found at expected path: {shapefile_path}")
            logger.info("Searching for correct shapefile...")
            shapefile_path = self._find_shapefile_by_entidad(entidad_id, shapefile_type)
            logger.info(f"Reading shapefile: {shapefile_path}")
            gdf = gpd.read_file(shapefile_path)
            logger.info(f"Loaded {len(gdf)} geometries")
        
        # Prepare merge keys (no need to override ENTIDAD anymore since we find the correct file)
        gdf_prepared = self._prepare_geodataframe(gdf, expected_entidad=None)
        df_prepared = self._prepare_dataframe(df)
        
        # Perform merge
        gdf_merged = self._perform_merge(gdf_prepared, df_prepared)
        
        logger.info(f"Merge completed. Final shape: {gdf_merged.shape}")
        logger.info(f"Rows with geometry: {gdf_merged['geometry'].notna().sum()}")
        
        return gdf_merged
    
    def _find_shapefile_by_entidad(
        self,
        entidad_id: int,
        shapefile_type: str = 'nacional'
    ) -> Path:
        """
        Search for shapefile with matching ENTIDAD value across all folders.
        
        This handles cases where shapefiles are in the wrong folders.
        
        Args:
            entidad_id: State ID to find
            shapefile_type: Type of shapefile ('nacional' or 'peepjf')
            
        Returns:
            Path to the correct shapefile
            
        Raises:
            FileNotFoundError: If no shapefile with matching ENTIDAD is found
        """
        import geopandas as gpd
        
        base_dir = self.shapefile_base_dir / ('productos_ine_nacional' if shapefile_type == 'nacional' else 'shapefiles_peepjf')
        
        if not base_dir.exists():
            raise FileNotFoundError(f"Base directory not found: {base_dir}")
        
        logger.info(f"Searching for ENTIDAD={entidad_id} in {base_dir.name}...")
        
        # Search all SECCION.shp files
        for shp_file in base_dir.rglob('SECCION.shp'):
            try:
                # Quick check: read just the ENTIDAD column
                gdf = gpd.read_file(shp_file, rows=1)
                
                if 'ENTIDAD' in gdf.columns:
                    # Read full file to check all ENTIDAD values
                    gdf_full = gpd.read_file(shp_file)
                    entidad_values = gdf_full['ENTIDAD'].unique()
                    
                    if len(entidad_values) == 1 and int(entidad_values[0]) == entidad_id:
                        logger.info(f"✅ Found correct shapefile at: {shp_file.relative_to(self.shapefile_base_dir)}")
                        return shp_file
            except Exception as e:
                # Skip files that can't be read
                logger.debug(f"Skipping {shp_file}: {e}")
                continue
        
        raise FileNotFoundError(
            f"No shapefile found with ENTIDAD={entidad_id} in {shapefile_type} directory. "
            f"You may need to re-download the correct shapefile."
        )
    
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
            
            # Try expected path first (entidad_id as folder name)
            entidad_str = str(entidad_id).zfill(2)
            shapefile_path = base_path / entidad_str / 'SECCION.shp'
            
            # If not found, search dynamically for any SECCION.shp in subdirectories
            if not shapefile_path.exists() and base_path.exists():
                logger.info(f"Standard peepjf path not found, searching for SECCION.shp in {base_path}")
                for subdir in base_path.iterdir():
                    if subdir.is_dir():
                        potential_path = subdir / 'SECCION.shp'
                        if potential_path.exists():
                            logger.info(f"Found SECCION.shp at: {potential_path}")
                            shapefile_path = potential_path
                            break
                            
        elif shapefile_type == 'nacional':
            base_path = self.shapefile_base_dir / 'productos_ine_nacional' / folder_name / 'Shapefile'
            
            # The nacional shapefiles have an extra subfolder with pattern: "01 AGUASCALIENTES"
            # We need to find it dynamically since the state names vary
            if base_path.exists():
                # Look for the state subfolder (should be the only directory inside Shapefile/)
                subdirs = [d for d in base_path.iterdir() if d.is_dir()]
                if subdirs:
                    # Search in each subdirectory for SECCION.shp
                    for subdir in subdirs:
                        potential_path = subdir / 'SECCION.shp'
                        if potential_path.exists():
                            shapefile_path = potential_path
                            break
                    else:
                        # No SECCION.shp found in subdirectories, try first subdir as fallback
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
    
    def _prepare_geodataframe(self, gdf: gpd.GeoDataFrame, expected_entidad: int = None) -> gpd.GeoDataFrame:
        """
        Prepare GeoDataFrame for merging (standardize column types).
        
        Args:
            gdf: Original GeoDataFrame
            expected_entidad: Expected ENTIDAD value to override if shapefile has wrong value
            
        Returns:
            Prepared GeoDataFrame
        """
        gdf = gdf.copy()
        
        # Convert ENTIDAD to Int64 if it exists
        if 'ENTIDAD' in gdf.columns:
            if gdf['ENTIDAD'].dtype == 'object':
                gdf['ENTIDAD'] = pd.to_numeric(gdf['ENTIDAD'], errors='coerce')
            gdf['ENTIDAD'] = gdf['ENTIDAD'].astype('Int64')
            
            # Check if ENTIDAD is wrong (common issue with PEEPJF shapefiles)
            if expected_entidad is not None:
                unique_entidades = gdf['ENTIDAD'].dropna().unique()
                if len(unique_entidades) == 1 and unique_entidades[0] != expected_entidad:
                    logger.warning(f"Shapefile has wrong ENTIDAD value ({unique_entidades[0]}), "
                                  f"overriding to {expected_entidad}")
                    gdf['ENTIDAD'] = expected_entidad
        
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

