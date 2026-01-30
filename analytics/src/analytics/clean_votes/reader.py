"""
Electoral Data Reader
=====================

Flexible reader for electoral data files with automatic header detection.
Supports CSV, Excel, and Parquet formats.
"""

import pandas as pd
from io import StringIO
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class ElectoralDataReader:
    """
    Reads electoral data from various file formats with flexible header detection.
    """
    
    # Key columns that indicate electoral data headers
    HEADER_INDICATORS = [
        'CLAVE_CASILLA',
        'ID_ESTADO',
        'ID_ENTIDAD',
        'SECCION',
        'CASILLA',
        'TIPO_CASILLA'
    ]
    
    def __init__(self, header_indicators: Optional[List[str]] = None):
        """
        Initialize the reader.
        
        Args:
            header_indicators: List of column names that indicate the header row.
                             If None, uses default HEADER_INDICATORS.
        """
        self.header_indicators = header_indicators or self.HEADER_INDICATORS
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        Read electoral data from a file with automatic format detection.
        
        Args:
            file_path: Path to the data file
            encoding: File encoding (default: utf-8)
            
        Returns:
            DataFrame with electoral data
            
        Raises:
            ValueError: If file format is not supported or header cannot be found
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        logger.info(f"Reading file: {file_path}")
        
        if suffix == '.csv':
            return self._read_csv(file_path, encoding)
        elif suffix in ['.xlsx', '.xls']:
            return self._read_excel(file_path)
        elif suffix == '.parquet':
            return self._read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _read_csv(self, file_path: str, encoding: str) -> pd.DataFrame:
        """
        Read CSV file with flexible header detection and delimiter detection.
        
        Handles both comma-separated (2024) and pipe-separated (2018, 2021) files.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            
        Returns:
            DataFrame with electoral data
        """
        try:
            # First, try reading the file to find the header row
            # Handle different line terminators (\n, \r\n, \r) by using pandas' lineterminator param
            # Read sample to find header and delimiter
            with open(file_path, encoding=encoding, newline='') as f:
                # Read first 1MB to find header (much faster for large files)
                sample = f.read(1024 * 1024)  # 1MB sample
                # Split on any line terminator type
                sample_lines = sample.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            
            header_row = self._find_header_row(sample_lines)
            
            if header_row is None:
                logger.warning(
                    f"Could not find header row with indicators {self.header_indicators}. "
                    "Assuming data starts from first row."
                )
                # Try reading with pandas (it handles \r automatically)
                return pd.read_csv(file_path, encoding=encoding, dtype=str, lineterminator='\r')
            
            logger.info(f"Found header at line {header_row}")
            
            # Detect delimiter from header line
            delimiter = self._detect_delimiter(sample_lines[header_row])
            logger.info(f"Detected delimiter: {repr(delimiter)}")
            
            # Use pandas to read directly with lineterminator='\r' for CR-only files
            # This is MUCH faster than reading entire file into memory
            df = pd.read_csv(
                file_path, 
                sep=delimiter, 
                dtype=str, 
                encoding=encoding,
                skiprows=header_row,
                lineterminator='\r',  # Handle CR line terminators
                on_bad_lines='skip'  # Skip any malformed lines
            )
            
            # Clean up empty columns (sometimes pipe-delimited files have trailing pipes)
            empty_cols = [col for col in df.columns if str(col).strip() == '']
            if empty_cols:
                df = df.drop(columns=empty_cols)
                logger.info(f"Removed {len(empty_cols)} empty columns")
            
            logger.info(f"Successfully read {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except UnicodeDecodeError:
            logger.warning(f"Failed with encoding {encoding}, trying latin-1")
            return self._read_csv(file_path, encoding='latin-1')
    
    def _read_excel(self, file_path: str) -> pd.DataFrame:
        """
        Read Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            DataFrame with electoral data
        """
        # Read entire file first to find header
        df_temp = pd.read_excel(file_path, header=None, dtype=str)
        
        header_row = None
        for idx, row in df_temp.iterrows():
            row_values = row.astype(str).str.upper()
            if any(indicator.upper() in ' '.join(row_values) for indicator in self.header_indicators):
                header_row = idx
                break
        
        if header_row is None:
            logger.warning("Could not find header row, assuming first row is header")
            return pd.read_excel(file_path, dtype=str)
        
        logger.info(f"Found header at row {header_row}")
        df = pd.read_excel(file_path, header=header_row, dtype=str)
        
        logger.info(f"Successfully read {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def _read_parquet(self, file_path: str) -> pd.DataFrame:
        """
        Read Parquet file.
        
        Args:
            file_path: Path to Parquet file
            
        Returns:
            DataFrame with electoral data
        """
        df = pd.read_parquet(file_path)
        logger.info(f"Successfully read {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def _find_header_row(self, lines: List[str]) -> Optional[int]:
        """
        Find the row index that contains the header.
        
        Args:
            lines: List of file lines
            
        Returns:
            Index of header row, or None if not found
        """
        for idx, line in enumerate(lines):
            line_upper = line.upper()
            if any(indicator.upper() in line_upper for indicator in self.header_indicators):
                return idx
        
        return None
    
    def _detect_delimiter(self, line: str) -> str:
        """
        Detect the delimiter used in a CSV line.
        
        Checks for pipe (|) first, then defaults to comma (,).
        
        Args:
            line: Header line from CSV
            
        Returns:
            Delimiter character
        """
        # Check for pipe delimiter (2018, 2021)
        if '|' in line:
            return '|'
        
        # Default to comma (2024)
        return ','

