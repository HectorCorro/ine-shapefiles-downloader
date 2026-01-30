"""
Column Homologation Mapper
===========================

Maps column names from different election years (2018, 2021, 2024) to a standardized schema.
Handles differences in column naming conventions across different INE/PREP datasets.
"""

from typing import Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Homologates column names from different electoral data formats to a standard schema.
    """
    
    # Standard column names (2024 format)
    STANDARD_SCHEMA = {
        # Identification columns
        'CLAVE_CASILLA': 'CLAVE_CASILLA',
        'CLAVE_ACTA': 'CLAVE_ACTA',
        'ID_ENTIDAD': 'ID_ENTIDAD',
        'ENTIDAD': 'ENTIDAD',
        'ID_DISTRITO_FEDERAL': 'ID_DISTRITO_FEDERAL',
        'DISTRITO_FEDERAL': 'DISTRITO_FEDERAL',
        'SECCION': 'SECCION',
        'ID_CASILLA': 'ID_CASILLA',
        'TIPO_CASILLA': 'TIPO_CASILLA',
        'EXT_CONTIGUA': 'EXT_CONTIGUA',
        'UBICACION_CASILLA': 'UBICACION_CASILLA',
        'CASILLA': 'CASILLA',
        
        # Vote totals
        'LISTA_NOMINAL': 'LISTA_NOMINAL',
        'TOTAL_VOTOS_CALCULADO': 'TOTAL_VOTOS_CALCULADO',
        'TOTAL_VOTOS_ASENTADO': 'TOTAL_VOTOS_ASENTADO',
        'TOTAL_VOTOS_SACADOS': 'TOTAL_VOTOS_SACADOS',
        'NO_REGISTRADAS': 'NO_REGISTRADAS',
        'NULOS': 'NULOS',
        
        # Metadata
        'OBSERVACIONES': 'OBSERVACIONES',
        'MECANISMOS_TRASLADO': 'MECANISMOS_TRASLADO',
        'FECHA_HORA': 'FECHA_HORA',
    }
    
    # Mappings from old names to standard names
    # 2018 and 2021 formats
    COLUMN_MAPPINGS = {
        # State/Entity columns
        'ID_ESTADO': 'ID_ENTIDAD',
        'NOMBRE_ESTADO': 'ENTIDAD',
        
        # District columns
        'ID_DISTRITO': 'ID_DISTRITO_FEDERAL',
        'NOMBRE_DISTRITO': 'DISTRITO_FEDERAL',
        
        # Lista nominal
        'LISTA_NOMINAL_CASILLA': 'LISTA_NOMINAL',
        
        # Vote counts
        'TOTAL_VOTOS_CALCULADOS': 'TOTAL_VOTOS_CALCULADO',  # 2018/2021 uses plural
        
        # Non-registered votes (different names in different years)
        'CNR': 'NO_REGISTRADAS',  # 2018 - Candidatos No Registrados
        'CANDIDATO/A NO REGISTRADO/A': 'NO_REGISTRADAS',  # 2021
        
        # Null votes
        'VN': 'NULOS',  # 2018 - Votos Nulos
        'VOTOS NULOS': 'NULOS',  # 2021
        
        # Other metadata
        'NUM_ACTA_IMPRESO': 'NUM_ACTA_IMPRESO',  # Keep as is
        'TIPO_ACTA': 'TIPO_ACTA',  # Keep as is
    }
    
    # Party name standardization (for older formats with different party names)
    PARTY_NAME_MAPPINGS = {
        # 2018 uses full name for MC
        'MOVIMIENTO CIUDADANO': 'MC',
        
        # 2018 uses different coalition separators
        'PAN_PRD_MC': 'PAN-PRD-MC',
        'PAN_PRD': 'PAN-PRD',
        'PAN_MC': 'PAN-MC',
        'PRD_MC': 'PRD-MC',
        'PRI_PVEM_NA': 'PRI-PVEM-NA',
        'PRI_PVEM': 'PRI-PVEM',
        'PRI_NA': 'PRI-NA',
        'PVEM_NA': 'PVEM-NA',
        'PT_MORENA_PES': 'PT-MORENA-PES',
        'PT_MORENA': 'PT-MORENA',
        'PT_PES': 'PT-PES',
        'MORENA_PES': 'MORENA-PES',
        
        # 2021 uses underscores
        'PVEM_PT_MORENA': 'PVEM-PT-MORENA',
        'PVEM_PT': 'PVEM-PT',
        'PVEM_MORENA': 'PVEM-MORENA',
        
        # Parties that no longer exist or have changed
        'NUEVA ALIANZA': 'NA',
        'ENCUENTRO SOCIAL': 'PES',
        
        # Independent candidates
        'CAND_IND_01': 'CAND_IND_01',
        'CAND_IND_02': 'CAND_IND_02',
        
        # Other parties from 2021
        'FXM': 'FXM',  # Fuerza por México
        'RSP': 'RSP',  # Redes Sociales Progresistas
        'CI': 'CI',    # Candidatura Independiente
    }
    
    def __init__(self):
        """Initialize the column mapper."""
        pass
    
    def homologate_columns(self, df: pd.DataFrame, year: Optional[int] = None) -> pd.DataFrame:
        """
        Homologate column names to standard schema.
        
        Args:
            df: DataFrame with original column names
            year: Optional year to apply specific mappings (2018, 2021, 2024)
            
        Returns:
            DataFrame with standardized column names
        """
        df = df.copy()
        original_columns = df.columns.tolist()
        
        # Create column rename mapping
        rename_map = {}
        
        # First, apply standard column mappings
        for old_name, new_name in self.COLUMN_MAPPINGS.items():
            if old_name in df.columns:
                rename_map[old_name] = new_name
                logger.debug(f"Mapping: {old_name} → {new_name}")
        
        # Then, apply party name standardization
        for old_name, new_name in self.PARTY_NAME_MAPPINGS.items():
            if old_name in df.columns:
                rename_map[old_name] = new_name
                logger.debug(f"Party mapping: {old_name} → {new_name}")
        
        # Rename columns
        if rename_map:
            df = df.rename(columns=rename_map)
            logger.info(f"Homologated {len(rename_map)} column names")
            logger.debug(f"Renamed columns: {list(rename_map.keys())}")
        else:
            logger.info("No column mappings needed (already in standard format)")
        
        return df
    
    def get_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Get the mapping dictionary for a given DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping old column names to new names
        """
        rename_map = {}
        
        # Apply standard column mappings
        for old_name, new_name in self.COLUMN_MAPPINGS.items():
            if old_name in df.columns:
                rename_map[old_name] = new_name
        
        # Apply party name standardization
        for old_name, new_name in self.PARTY_NAME_MAPPINGS.items():
            if old_name in df.columns:
                rename_map[old_name] = new_name
        
        return rename_map
    
    def detect_format_year(self, df: pd.DataFrame) -> Optional[int]:
        """
        Detect which year/format the data is from based on column names.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Detected year (2018, 2021, 2024) or None if cannot determine
        """
        columns = set(df.columns)
        
        # 2024 indicators
        if 'ID_ENTIDAD' in columns and 'ENTIDAD' in columns:
            return 2024
        
        # 2018 indicators (has specific parties that don't exist in 2021)
        if 'NUEVA ALIANZA' in columns or 'ENCUENTRO SOCIAL' in columns:
            return 2018
        
        # 2021 indicators (has specific parties)
        if 'ID_ESTADO' in columns and any(p in columns for p in ['FXM', 'RSP', 'PES']):
            return 2021
        
        # General old format (2018 or 2021)
        if 'ID_ESTADO' in columns and 'NOMBRE_ESTADO' in columns:
            # Could be either, default to 2021
            return 2021
        
        return None
    
    def validate_required_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that required columns exist after homologation.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all required columns exist
        """
        required = ['ID_ENTIDAD', 'SECCION']
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            logger.warning(f"Missing required columns after homologation: {missing}")
            return False
        
        return True


def homologate_dataframe(df: pd.DataFrame, year: Optional[int] = None) -> pd.DataFrame:
    """
    Convenience function to homologate a DataFrame's columns.
    
    Args:
        df: DataFrame with original column names
        year: Optional year to apply specific mappings
        
    Returns:
        DataFrame with standardized column names
    """
    mapper = ColumnMapper()
    
    # Auto-detect year if not provided
    if year is None:
        detected_year = mapper.detect_format_year(df)
        if detected_year:
            logger.info(f"Auto-detected data format: {detected_year}")
            year = detected_year
    
    # Homologate columns
    df_homologated = mapper.homologate_columns(df, year=year)
    
    # Validate
    if not mapper.validate_required_columns(df_homologated):
        logger.warning("Homologation may be incomplete")
    
    return df_homologated




