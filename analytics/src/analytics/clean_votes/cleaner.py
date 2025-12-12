"""
Electoral Data Cleaner
======================

Data transformation and cleaning functions for electoral data.
Based on the clean_votes.ipynb workflow.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ElectoralDataCleaner:
    """
    Cleans and transforms electoral data.
    """
    
    # Columns to exclude from processing
    COLUMNS_TO_EXCLUDE = [
        'REPRESENTANTES_PP_CI',
        'OBSERVACIONES',
        'CONTABILIZADA',
        'MECANISMOS_TRASLADO',
        'CODIGO_INTEGRIDAD',
        'FECHA_HORA_ACOPIO',
        'FECHA_HORA_CAPTURA',
        'FECHA_HORA_VERIFICACION',
        'ORIGEN',
        'DIGITALIZACION',
        'TIPO_DOCUMENTO',
        'COTEJADA'
    ]
    
    # Standard numeric vote columns (will be detected dynamically as well)
    STANDARD_VOTE_COLUMNS = [
        'TOTAL_VOTOS_ASENTADO', 'TOTAL_VOTOS_CALCULADO', 'TOTAL_VOTOS_SACADOS',
        'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA',
        'PAN-PRI-PRD', 'PAN-PRI', 'PAN-PRD', 'PRI-PRD',
        'PVEM_PT_MORENA', 'PVEM_PT', 'PVEM_MORENA', 'PT_MORENA',
        'NO_REGISTRADAS', 'NULOS'
    ]
    
    def __init__(self, columns_to_exclude: Optional[List[str]] = None):
        """
        Initialize the cleaner.
        
        Args:
            columns_to_exclude: Custom list of columns to exclude.
                              If None, uses COLUMNS_TO_EXCLUDE.
        """
        self.columns_to_exclude = columns_to_exclude or self.COLUMNS_TO_EXCLUDE
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main cleaning pipeline.
        
        Args:
            df: Raw electoral DataFrame
            
        Returns:
            Cleaned and aggregated DataFrame by ENTIDAD and SECCION
        """
        logger.info(f"Starting cleaning process. Input shape: {df.shape}")
        
        # Step 1: Remove unwanted columns
        df = self._remove_unwanted_columns(df)
        logger.info(f"After removing unwanted columns: {df.shape}")
        
        # Step 2: Identify and convert numeric columns
        df = self._convert_numeric_columns(df)
        logger.info("Converted numeric columns")
        
        # Step 3: Calculate totals and percentages
        df = self._calculate_totals_and_percentages(df)
        logger.info("Calculated totals and percentages")
        
        # Step 4: Homogenize ID columns with zfill
        df = self._homogenize_id_columns(df)
        logger.info("Homogenized ID columns")
        
        # Step 5: Clean and aggregate LISTA_NOMINAL
        df_lista = self._clean_and_aggregate_lista_nominal(df)
        logger.info(f"Aggregated LISTA_NOMINAL: {df_lista.shape}")
        
        # Step 6: Aggregate votes by section
        df_voto = self._aggregate_votes_by_section(df)
        logger.info(f"Aggregated votes by section: {df_voto.shape}")
        
        # Step 7: Merge votes and lista nominal
        df_final = self._merge_votes_and_lista(df_voto, df_lista, df)
        logger.info(f"Final merged dataset: {df_final.shape}")
        
        # Step 8: Remove rows with null key columns
        df_final = self._remove_null_rows(df_final)
        logger.info(f"After removing nulls: {df_final.shape}")
        
        return df_final
    
    def _remove_unwanted_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove columns that are not needed for analysis."""
        df = df.copy()
        cols_to_keep = [col for col in df.columns if col not in self.columns_to_exclude]
        return df[cols_to_keep]
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify and convert numeric vote columns."""
        df = df.copy()
        
        # Detect vote columns (existing standard columns + any that look like parties/coalitions)
        numeric_cols = []
        for col in df.columns:
            if col in self.STANDARD_VOTE_COLUMNS:
                numeric_cols.append(col)
            # Also detect columns with vote-like patterns (all caps, underscores/hyphens)
            elif col.isupper() and any(char in col for char in ['_', '-']) and col not in ['ID_ENTIDAD', 'ID_DISTRITO_FEDERAL']:
                # Check if it looks like a party/coalition column
                if not any(keyword in col for keyword in ['FECHA', 'HORA', 'CODIGO', 'CLAVE', 'TIPO', 'ID_']):
                    numeric_cols.append(col)
        
        logger.info(f"Converting {len(numeric_cols)} numeric columns")
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _calculate_totals_and_percentages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate TOTAL_VOTOS_SUM and percentage for each party."""
        df = df.copy()
        
        # Identify vote columns (excluding TOTAL_* columns)
        vote_columns = [col for col in df.columns 
                       if pd.api.types.is_numeric_dtype(df[col]) 
                       and not col.startswith('TOTAL_')
                       and not col.startswith('ID_')
                       and not col.startswith('LISTA_')
                       and col not in ['SECCION', 'CASILLA']]
        
        logger.info(f"Calculating totals for {len(vote_columns)} vote columns")
        
        # Clean values
        df[vote_columns] = df[vote_columns].replace({'-': pd.NA, '': pd.NA, ' ': pd.NA})
        df[vote_columns] = df[vote_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Calculate total
        df['TOTAL_VOTOS_SUM'] = df[vote_columns].sum(axis=1)
        
        # Calculate percentages
        for col in vote_columns:
            df[f'{col}_PCT'] = df.apply(
                lambda row: (row[col] / row['TOTAL_VOTOS_SUM']) * 100 if row['TOTAL_VOTOS_SUM'] > 0 else 0,
                axis=1
            )
        
        return df
    
    def _homogenize_id_columns(self, df: pd.DataFrame, width: int = 3) -> pd.DataFrame:
        """
        Homogenize ID columns (convert to Int64 and create string version with zfill).
        """
        df = df.copy()
        
        id_columns = ['ID_DISTRITO_FEDERAL', 'ID_ENTIDAD', 'SECCION']
        
        for col in id_columns:
            if col not in df.columns:
                continue
            
            # Convert to string, strip, and handle NaN
            col_temp = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({'nan': pd.NA, 'None': pd.NA, '<NA>': pd.NA})
            )
            
            # Convert to Int64
            df[col] = col_temp.apply(
                lambda x: int(x) if pd.notna(x) and str(x).replace('.', '').replace('-', '').isdigit() else pd.NA
            ).astype("Int64")
            
            # Create string version with zfill
            str_col_name = f"{col}_STR"
            df[str_col_name] = df[col].astype(str).str.zfill(width)
        
        return df
    
    def _clean_and_aggregate_lista_nominal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean LISTA_NOMINAL column and aggregate by section."""
        df = df.copy()
        
        if 'LISTA_NOMINAL' not in df.columns:
            logger.warning("LISTA_NOMINAL column not found, skipping")
            # Return empty dataframe with expected structure
            return pd.DataFrame(columns=['ID_ENTIDAD', 'SECCION', 'LISTA_NOMINAL'])
        
        # Clean LISTA_NOMINAL
        lista_nominal_limpia = (
            df['LISTA_NOMINAL']
            .astype(str)
            .str.replace(r'\D', '', regex=True)
            .replace('', np.nan)
            .astype(float)
        )
        
        df['LISTA_NOMINAL'] = lista_nominal_limpia.fillna(0)
        
        # Aggregate by section
        df_lista = df.groupby(['ID_ENTIDAD', 'SECCION'], dropna=False)['LISTA_NOMINAL'].sum().reset_index()
        
        return df_lista
    
    def _aggregate_votes_by_section(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate vote counts by ENTIDAD and SECCION."""
        df = df.copy()
        
        # Identify vote columns
        vote_columns = [col for col in df.columns 
                       if pd.api.types.is_numeric_dtype(df[col]) 
                       and not col.startswith('TOTAL_')
                       and not col.startswith('ID_')
                       and not col.startswith('LISTA_')
                       and not col.endswith('_PCT')
                       and col not in ['SECCION', 'CASILLA']]
        
        claves = ['ID_ENTIDAD', 'SECCION']
        
        # Ensure clean numeric data
        df[vote_columns] = df[vote_columns].replace({'-': pd.NA, '': pd.NA, ' ': pd.NA})
        df[vote_columns] = df[vote_columns].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Aggregate
        df_agrupado = df.groupby(claves, dropna=False)[vote_columns].sum().reset_index()
        
        # Recalculate total and percentages
        df_agrupado['TOTAL_VOTOS_SUM'] = df_agrupado[vote_columns].sum(axis=1)
        
        for col in vote_columns:
            df_agrupado[f'{col}_PCT'] = df_agrupado.apply(
                lambda row: (row[col] / row['TOTAL_VOTOS_SUM']) * 100 if row['TOTAL_VOTOS_SUM'] > 0 else 0,
                axis=1
            )
        
        return df_agrupado
    
    def _merge_votes_and_lista(
        self,
        df_voto: pd.DataFrame,
        df_lista: pd.DataFrame,
        df_original: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge vote aggregations with lista nominal and descriptive info."""
        claves = ['ID_ENTIDAD', 'SECCION']
        
        # Merge lista and votes
        df_base = df_lista.merge(df_voto, how='left', on=claves)
        
        # Extract descriptive columns from original data
        descriptive_cols = []
        for col in ['ENTIDAD', 'DISTRITO_FEDERAL', 'ID_DISTRITO_FEDERAL', 
                    'ID_DISTRITO_FEDERAL_STR', 'ID_ENTIDAD_STR', 'SECCION_STR']:
            if col in df_original.columns:
                descriptive_cols.append(col)
        
        if descriptive_cols:
            df_info_extra = (
                df_original[claves + descriptive_cols]
                .drop_duplicates(subset=claves)
                .groupby(claves, dropna=False)
                .first()
                .reset_index()
            )
            
            df_final = df_base.merge(df_info_extra, how='left', on=claves)
        else:
            df_final = df_base
        
        return df_final
    
    def _remove_null_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with null values in key columns."""
        df = df.copy()
        
        # Define key columns to check (only check if they exist)
        cols_to_check = []
        for col in ['ID_DISTRITO_FEDERAL', 'DISTRITO_FEDERAL', 'SECCION']:
            if col in df.columns:
                cols_to_check.append(col)
        
        if cols_to_check:
            logger.info(f"Checking for nulls in: {cols_to_check}")
            df = df.dropna(subset=cols_to_check)
        
        return df
    
    def get_final_schema(self, df: pd.DataFrame) -> List[str]:
        """
        Get the final schema in the expected order.
        
        Args:
            df: DataFrame to extract schema from
            
        Returns:
            List of column names in expected order
        """
        # Base columns
        base_cols = ['ENTIDAD', 'ID_ENTIDAD', 'ID_ENTIDAD_STR', 'DISTRITO_FEDERAL', 
                     'ID_DISTRITO_FEDERAL', 'ID_DISTRITO_FEDERAL_STR', 'SECCION', 'SECCION_STR', 
                     'LISTA_NOMINAL']
        
        # Vote columns (parties and coalitions)
        vote_cols = [col for col in df.columns 
                    if col not in base_cols 
                    and not col.endswith('_PCT') 
                    and not col.startswith('TOTAL_')
                    and pd.api.types.is_numeric_dtype(df[col])]
        
        # Total
        total_cols = ['TOTAL_VOTOS_SUM']
        
        # Percentage columns
        pct_cols = [col for col in df.columns if col.endswith('_PCT')]
        
        # Build final schema with only existing columns
        schema = []
        for col in base_cols + vote_cols + total_cols + pct_cols:
            if col in df.columns:
                schema.append(col)
        
        return schema

