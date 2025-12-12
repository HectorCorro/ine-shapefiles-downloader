"""
Clean Votes Orchestrator
=========================

Main workflow coordinator for cleaning electoral data.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging

from .reader import ElectoralDataReader
from .cleaner import ElectoralDataCleaner
from .geometry import GeometryMerger
from .database import ElectoralDatabase
from .utils import infer_election_metadata, get_default_db_path
from .column_mapper import ColumnMapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CleanVotesOrchestrator:
    """
    Orchestrates the complete workflow for cleaning electoral data.
    
    The orchestrator automatically:
    - Creates the database if it doesn't exist
    - Infers election name and date from file paths
    - Processes all entidades in the data
    """
    
    def __init__(
        self,
        db_path: Optional[str] = None,
        shapefile_base_dir: Optional[str] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            db_path: Path to SQLite database (auto-created if doesn't exist).
                    If None, uses default location: data/processed/electoral_data.db
            shapefile_base_dir: Base directory for shapefiles.
                              If None, auto-detects from data/geo/
        """
        # Use default database path if not provided
        if db_path is None:
            db_path = str(get_default_db_path())
        
        self.db_path = Path(db_path)
        
        # Initialize components
        self.reader = ElectoralDataReader()
        self.column_mapper = ColumnMapper()
        self.cleaner = ElectoralDataCleaner()
        self.geometry_merger = GeometryMerger(shapefile_base_dir)
        self.database = ElectoralDatabase(str(db_path))
        
        logger.info(f"Orchestrator initialized with database: {self.db_path}")
    
    def process_electoral_file(
        self,
        file_path: str,
        election_name: Optional[str] = None,
        election_date: Optional[str] = None,
        include_geometry: bool = False,
        shapefile_path: Optional[str] = None,
        shapefile_type: str = 'peepjf',
        save_to_db: bool = True,
        save_geojson: bool = False,
        geojson_output_path: Optional[str] = None,
        encoding: str = 'utf-8',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Complete workflow: read, clean, optionally merge geometry, and save.
        
        If election_name or election_date are not provided, they will be
        automatically inferred from the file path.
        
        Args:
            file_path: Path to electoral data file (CSV, Excel, or Parquet)
            election_name: Name of election (e.g., 'PRES_2024', 'DIP_FED_2021').
                          If None, inferred from file path/name.
            election_date: Date of election (YYYY-MM-DD or YYYY).
                          If None, inferred from file path.
            include_geometry: Whether to merge with shapefile geometries
            shapefile_path: Explicit shapefile path (if not using auto-detection)
            shapefile_type: Type of shapefile ('peepjf' or 'nacional')
            save_to_db: Whether to save to database
            save_geojson: Whether to save as GeoJSON (only if include_geometry=True)
            geojson_output_path: Path for GeoJSON output
            encoding: File encoding
            metadata: Additional metadata to store
            
        Returns:
            Cleaned DataFrame or GeoDataFrame
            
        Examples:
            >>> # Explicit parameters
            >>> orchestrator = CleanVotesOrchestrator()
            >>> df = orchestrator.process_electoral_file(
            ...     file_path='data/raw/electoral/2024/PRES_2024.csv',
            ...     election_name='PRES_2024',
            ...     election_date='2024-06-03',
            ...     include_geometry=True
            ... )
            
            >>> # Auto-infer from path
            >>> df = orchestrator.process_electoral_file(
            ...     'data/raw/electoral/2024/PRES_2024.csv',  # Auto-detects PRES_2024, 2024
            ...     include_geometry=True
            ... )
        """
        # Auto-infer election metadata if not provided
        if election_name is None or election_date is None:
            inferred_name, inferred_date = infer_election_metadata(file_path)
            
            if election_name is None:
                election_name = inferred_name
                logger.info(f"Auto-inferred election name: {election_name}")
            
            if election_date is None:
                election_date = inferred_date
                logger.info(f"Auto-inferred election date: {election_date}")
        
        if election_name is None:
            raise ValueError(
                "Could not determine election_name. Please provide it explicitly or "
                "ensure file path follows pattern: data/raw/electoral/YYYY/TYPE_YYYY.csv"
            )
        
        logger.info("="*60)
        logger.info(f"Processing electoral file: {file_path}")
        logger.info(f"Election: {election_name}")
        logger.info(f"Date: {election_date}")
        logger.info("="*60)
        
        # Step 1: Read data
        logger.info("\n[1/6] Reading data...")
        df_raw = self.reader.read_file(file_path, encoding=encoding)
        logger.info(f"✓ Read {len(df_raw)} rows, {len(df_raw.columns)} columns")
        
        # Step 2: Homologate column names (standardize 2018/2021/2024 formats)
        logger.info("\n[2/6] Homologating column names...")
        detected_year = self.column_mapper.detect_format_year(df_raw)
        if detected_year:
            logger.info(f"✓ Detected data format: {detected_year}")
        df_homologated = self.column_mapper.homologate_columns(df_raw)
        logger.info(f"✓ Homologated columns: {len(df_homologated.columns)} columns")
        
        # Step 3: Clean data
        logger.info("\n[3/6] Cleaning data...")
        df_clean = self.cleaner.clean(df_homologated)
        logger.info(f"✓ Cleaned data: {len(df_clean)} rows, {len(df_clean.columns)} columns")
        
        # Step 4: Get entidades in the data
        if 'ID_ENTIDAD' not in df_clean.columns:
            raise ValueError("ID_ENTIDAD column not found in cleaned data")
        
        entidades = df_clean['ID_ENTIDAD'].dropna().unique()
        logger.info(f"✓ Found {len(entidades)} entidades: {sorted(entidades)}")
        
        # Step 5: Process each entidad separately
        logger.info("\n[4/6] Processing by entidad...")
        results = {}
        
        for entidad_id in sorted(entidades):
            try:
                entidad_id = int(entidad_id)
                logger.info(f"\n--- Processing ENTIDAD {entidad_id:02d} ---")
                
                # Filter data for this entidad
                df_entidad = df_clean[df_clean['ID_ENTIDAD'] == entidad_id].copy()
                
                # Get entidad name
                entidad_name = df_entidad['ENTIDAD'].iloc[0] if 'ENTIDAD' in df_entidad.columns else f"ENTIDAD_{entidad_id:02d}"
                
                logger.info(f"Entidad: {entidad_name}, Rows: {len(df_entidad)}")
                
                # Step 5: Merge with geometry if requested
                if include_geometry:
                    logger.info("\n[5/6] Merging with geometry...")
                    try:
                        gdf_entidad = self.geometry_merger.merge_with_shapefile(
                            df_entidad,
                            shapefile_path=shapefile_path,
                            entidad_id=entidad_id,
                            shapefile_type=shapefile_type
                        )
                        logger.info(f"✓ Merged with geometry: {len(gdf_entidad)} rows")
                        
                        # Save GeoJSON if requested
                        if save_geojson:
                            if geojson_output_path is None:
                                geojson_output_path = f"data/insights/{election_name.lower()}_{entidad_id:02d}.geojson"
                            self.geometry_merger.save_geojson(gdf_entidad, geojson_output_path)
                        
                        df_final = gdf_entidad
                    except Exception as e:
                        logger.error(f"Failed to merge geometry: {e}")
                        logger.warning("Continuing without geometry")
                        df_final = df_entidad
                else:
                    df_final = df_entidad
                
                # Step 6: Save to database
                if save_to_db:
                    logger.info("\n[6/6] Saving to database...")
                    table_name = self.database.save_electoral_data(
                        df=df_final,
                        election_name=election_name,
                        entidad_id=entidad_id,
                        entidad_name=entidad_name,
                        election_date=election_date,
                        source_file=file_path,
                        shapefile_path=str(shapefile_path) if shapefile_path else None,
                        metadata=metadata
                    )
                    logger.info(f"✓ Saved to table: {table_name}")
                
                results[entidad_id] = df_final
                logger.info(f"✓ ENTIDAD {entidad_id:02d} completed successfully")
                
            except Exception as e:
                logger.error(f"✗ Failed to process ENTIDAD {entidad_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        logger.info("\n" + "="*60)
        logger.info(f"Processing complete! Processed {len(results)}/{len(entidades)} entidades")
        logger.info("="*60)
        
        # Return combined results if multiple entidades, otherwise return single result
        if len(results) == 1:
            return list(results.values())[0]
        else:
            # Concatenate all results
            all_dfs = list(results.values())
            if isinstance(all_dfs[0], gpd.GeoDataFrame):
                return gpd.GeoDataFrame(pd.concat(all_dfs, ignore_index=True))
            else:
                return pd.concat(all_dfs, ignore_index=True)
    
    def load_election_data(
        self,
        election_name: str,
        entidad_id: int,
        as_geodataframe: bool = False
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        Load processed election data from database.
        
        Args:
            election_name: Name of election (e.g., 'PRES_2024')
            entidad_id: State ID (1-32)
            as_geodataframe: Whether to return as GeoDataFrame
            
        Returns:
            DataFrame or GeoDataFrame with election data
        """
        return self.database.load_electoral_data(
            election_name=election_name,
            entidad_id=entidad_id,
            as_geodataframe=as_geodataframe
        )
    
    def list_available_elections(self) -> pd.DataFrame:
        """
        List all available elections in the database.
        
        Returns:
            DataFrame with election metadata
        """
        return self.database.list_elections()
    
    def get_election_info(self, election_name: str, entidad_id: int) -> Dict[str, Any]:
        """
        Get metadata for a specific election and entidad.
        
        Args:
            election_name: Name of election
            entidad_id: State ID
            
        Returns:
            Dictionary with election metadata
        """
        table_name = f"election_{election_name.lower()}_{entidad_id:02d}"
        return self.database.get_election_info(table_name)


def main():
    """
    Command-line interface for the orchestrator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean and process electoral data files'
    )
    
    parser.add_argument(
        'file_path',
        help='Path to electoral data file (CSV, Excel, or Parquet)'
    )
    
    parser.add_argument(
        'election_name',
        help='Name of election (e.g., PRES_2024, DIP_2021)'
    )
    
    parser.add_argument(
        '--election-date',
        help='Election date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--geometry',
        action='store_true',
        help='Include geometry from shapefiles'
    )
    
    parser.add_argument(
        '--shapefile-path',
        help='Explicit path to shapefile (optional)'
    )
    
    parser.add_argument(
        '--shapefile-type',
        choices=['peepjf', 'nacional'],
        default='peepjf',
        help='Type of shapefile to use'
    )
    
    parser.add_argument(
        '--no-db',
        action='store_true',
        help='Skip saving to database'
    )
    
    parser.add_argument(
        '--geojson',
        help='Save as GeoJSON to specified path'
    )
    
    parser.add_argument(
        '--db-path',
        default='data/processed/electoral_data.db',
        help='Path to SQLite database'
    )
    
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='File encoding'
    )
    
    parser.add_argument(
        '--list-elections',
        action='store_true',
        help='List all elections in database and exit'
    )
    
    args = parser.parse_args()
    
    orchestrator = CleanVotesOrchestrator(db_path=args.db_path)
    
    if args.list_elections:
        elections = orchestrator.list_available_elections()
        print("\n" + "="*60)
        print("AVAILABLE ELECTIONS")
        print("="*60)
        print(elections.to_string(index=False))
        return
    
    # Process file
    result = orchestrator.process_electoral_file(
        file_path=args.file_path,
        election_name=args.election_name,
        election_date=args.election_date,
        include_geometry=args.geometry,
        shapefile_path=args.shapefile_path,
        shapefile_type=args.shapefile_type,
        save_to_db=not args.no_db,
        save_geojson=bool(args.geojson),
        geojson_output_path=args.geojson,
        encoding=args.encoding
    )
    
    print(f"\n✓ Processing complete! Final shape: {result.shape}")


if __name__ == '__main__':
    main()

