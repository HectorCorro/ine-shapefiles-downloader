"""
Electoral Database Handler
===========================

SQLite database handler for storing cleaned electoral data.
"""

import sqlite3
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class ElectoralDatabase:
    """
    Handles storage of electoral data in SQLite database.
    
    The database is automatically created on first use if it doesn't exist.
    """
    
    def __init__(self, db_path: str = "data/processed/electoral_data.db"):
        """
        Initialize the database handler.
        
        The database file and all parent directories are created automatically
        if they don't exist.
        
        Args:
            db_path: Path to SQLite database file (relative or absolute)
        """
        self.db_path = Path(db_path).resolve()
        
        # Ensure parent directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_metadata_table()
        
        logger.info(f"Database initialized at: {self.db_path}")
        logger.info(f"Database exists: {self.db_path.exists()}")
    
    def _init_metadata_table(self):
        """
        Create metadata table if it doesn't exist.
        
        This ensures the database structure is ready even on first run.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS election_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        election_name TEXT NOT NULL,
                        election_date TEXT,
                        entidad_id INTEGER NOT NULL,
                        entidad_name TEXT NOT NULL,
                        table_name TEXT NOT NULL UNIQUE,
                        has_geometry BOOLEAN NOT NULL,
                        row_count INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source_file TEXT,
                        shapefile_path TEXT,
                        metadata_json TEXT
                    )
                """)
                conn.commit()
                logger.info("Metadata table initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize metadata table: {e}")
            raise
    
    def save_electoral_data(
        self,
        df: pd.DataFrame,
        election_name: str,
        entidad_id: int,
        entidad_name: str,
        election_date: Optional[str] = None,
        source_file: Optional[str] = None,
        shapefile_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        if_exists: str = 'replace'
    ) -> str:
        """
        Save electoral data to database.
        
        Args:
            df: Electoral DataFrame (can be GeoDataFrame)
            election_name: Name of the election (e.g., 'PRES_2024', 'DIP_2021')
            entidad_id: State ID (1-32)
            entidad_name: State name
            election_date: Election date (YYYY-MM-DD format)
            source_file: Source file path
            shapefile_path: Shapefile path if geometry was merged
            metadata: Additional metadata dictionary
            if_exists: What to do if table exists ('replace', 'append', 'fail')
            
        Returns:
            Table name where data was saved
        """
        # Generate table name: election_entidad_{election_name}_{entidad_id}
        table_name = f"election_{election_name.lower()}_{entidad_id:02d}"
        
        # Check if it's a GeoDataFrame
        has_geometry = isinstance(df, gpd.GeoDataFrame) and 'geometry' in df.columns
        
        logger.info(f"Saving data to table: {table_name}")
        logger.info(f"Rows: {len(df)}, Has geometry: {has_geometry}")
        
        with sqlite3.connect(self.db_path) as conn:
            if has_geometry:
                # For GeoDataFrame, convert geometry to WKT
                df_to_save = df.copy()
                df_to_save['geometry'] = df_to_save['geometry'].apply(lambda x: x.wkt if x is not None else None)
                df_to_save['crs'] = str(df.crs) if df.crs else None
            else:
                df_to_save = df
            
            # Save data
            df_to_save.to_sql(table_name, conn, if_exists=if_exists, index=False)
            
            # Update metadata
            self._update_metadata(
                conn=conn,
                table_name=table_name,
                election_name=election_name,
                election_date=election_date,
                entidad_id=entidad_id,
                entidad_name=entidad_name,
                has_geometry=has_geometry,
                row_count=len(df),
                source_file=source_file,
                shapefile_path=shapefile_path,
                metadata=metadata
            )
        
        logger.info(f"Data saved successfully to table: {table_name}")
        return table_name
    
    def _update_metadata(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        election_name: str,
        entidad_id: int,
        entidad_name: str,
        has_geometry: bool,
        row_count: int,
        election_date: Optional[str] = None,
        source_file: Optional[str] = None,
        shapefile_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update metadata table."""
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Check if record exists
        cursor = conn.execute(
            "SELECT id FROM election_metadata WHERE table_name = ?",
            (table_name,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            conn.execute("""
                UPDATE election_metadata
                SET election_name = ?,
                    election_date = ?,
                    entidad_id = ?,
                    entidad_name = ?,
                    has_geometry = ?,
                    row_count = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    source_file = ?,
                    shapefile_path = ?,
                    metadata_json = ?
                WHERE table_name = ?
            """, (
                election_name, election_date, entidad_id, entidad_name,
                has_geometry, row_count, source_file, shapefile_path,
                metadata_json, table_name
            ))
        else:
            # Insert new record
            conn.execute("""
                INSERT INTO election_metadata (
                    election_name, election_date, entidad_id, entidad_name,
                    table_name, has_geometry, row_count, source_file,
                    shapefile_path, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                election_name, election_date, entidad_id, entidad_name,
                table_name, has_geometry, row_count, source_file,
                shapefile_path, metadata_json
            ))
        
        conn.commit()
    
    def load_electoral_data(
        self,
        table_name: Optional[str] = None,
        election_name: Optional[str] = None,
        entidad_id: Optional[int] = None,
        as_geodataframe: bool = False
    ) -> pd.DataFrame:
        """
        Load electoral data from database.
        
        Args:
            table_name: Explicit table name. If None, will construct from election_name and entidad_id.
            election_name: Election name (if table_name not provided)
            entidad_id: State ID (if table_name not provided)
            as_geodataframe: Whether to return as GeoDataFrame (if geometry available)
            
        Returns:
            DataFrame or GeoDataFrame with electoral data
            
        Raises:
            ValueError: If insufficient parameters provided or table not found
        """
        if table_name is None:
            if election_name is None or entidad_id is None:
                raise ValueError("Must provide either table_name or both election_name and entidad_id")
            table_name = f"election_{election_name.lower()}_{entidad_id:02d}"
        
        logger.info(f"Loading data from table: {table_name}")
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not cursor.fetchone():
                raise ValueError(f"Table not found: {table_name}")
            
            # Load data
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            
            logger.info(f"Loaded {len(df)} rows")
            
            # Convert to GeoDataFrame if requested and geometry available
            if as_geodataframe and 'geometry' in df.columns:
                from shapely import wkt
                
                logger.info(f"Converting to GeoDataFrame (has_crs_column: {'crs' in df.columns})")
                
                # Convert WKT to geometry objects
                df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x) if pd.notna(x) else None)
                
                # Get CRS from column or use default
                if 'crs' in df.columns:
                    crs = df['crs'].iloc[0] if not df['crs'].isna().all() else 'EPSG:4326'
                    df = df.drop(columns=['crs'])
                else:
                    crs = 'EPSG:4326'  # Default to WGS84 if no CRS column
                    logger.info("No 'crs' column found, using default EPSG:4326")
                
                # Create GeoDataFrame
                df = gpd.GeoDataFrame(df, geometry='geometry', crs=crs)
                logger.info(f"Converted to GeoDataFrame with CRS: {crs}")
        
        return df
    
    def list_elections(self) -> pd.DataFrame:
        """
        List all elections in the database.
        
        Returns:
            DataFrame with election metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                "SELECT * FROM election_metadata ORDER BY election_date DESC, entidad_id",
                conn
            )
        return df
    
    def get_election_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific election table.
        
        Args:
            table_name: Name of the election table
            
        Returns:
            Dictionary with election metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM election_metadata WHERE table_name = ?",
                (table_name,)
            )
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"No metadata found for table: {table_name}")
            
            columns = [desc[0] for desc in cursor.description]
            info = dict(zip(columns, row))
            
            # Parse JSON metadata if present
            if info.get('metadata_json'):
                info['metadata'] = json.loads(info['metadata_json'])
                del info['metadata_json']
            
            return info
    
    def delete_election(self, table_name: str):
        """
        Delete an election table and its metadata.
        
        Args:
            table_name: Name of the table to delete
        """
        logger.warning(f"Deleting table: {table_name}")
        
        with sqlite3.connect(self.db_path) as conn:
            # Delete table
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            # Delete metadata
            conn.execute("DELETE FROM election_metadata WHERE table_name = ?", (table_name,))
            conn.commit()
        
        logger.info(f"Table deleted: {table_name}")

