"""
Utility functions for clean_votes module
=========================================

Helper functions for parsing election metadata from file paths and names.
"""

import re
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime


def infer_election_metadata(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Infer election name and date from file path and name.
    
    Patterns supported:
    - data/raw/electoral/2024/PRES_2024.csv → ('PRES_2024', '2024')
    - data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv → ('PRES_2024', '2024-06-03')
    - data/raw/electoral/2021/DIP_FED_2021.csv → ('DIP_FED_2021', '2021')
    - data/raw/electoral/2021/diputaciones.csv → ('DIP_FED_2021', '2021')
    - data/raw/electoral/2018/presidencia.csv → ('PRES_2018', '2018')
    - data/raw/electoral/2018/senadurias.csv → ('SEN_2018', '2018')
    
    Args:
        file_path: Path to electoral data file
        
    Returns:
        Tuple of (election_name, election_date)
        - election_name: Inferred name like 'PRES_2024', 'DIP_FED_2021'
        - election_date: Date in YYYY-MM-DD format or just year YYYY
    
    Examples:
        >>> infer_election_metadata('data/raw/electoral/2024/PRES_2024.csv')
        ('PRES_2024', '2024')
        
        >>> infer_election_metadata('electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv')
        ('PRES_2024', '2024-06-03')
        
        >>> infer_election_metadata('data/raw/electoral/2021/diputaciones.csv')
        ('DIP_FED_2021', '2021')
    """
    path = Path(file_path)
    
    # Extract year from path (look for electoral/YYYY pattern)
    year = None
    election_date = None
    
    # Try to find year in path - prioritize parent directory if file is directly in a year folder
    path_parts = list(path.parts)
    for i, part in enumerate(path_parts):
        if part.isdigit() and len(part) == 4 and part.startswith('20'):
            year = part
            # If this is the parent directory of the file, it's the year we want
            if i == len(path_parts) - 2:  # Parent folder
                break
    
    # Try to extract full date from directory name (YYYYMMDD pattern)
    for part in path.parts:
        date_match = re.match(r'(\d{8})_\d+_PREP_', part)
        if date_match:
            date_str = date_match.group(1)
            try:
                parsed_date = datetime.strptime(date_str, '%Y%m%d')
                election_date = parsed_date.strftime('%Y-%m-%d')
                year = str(parsed_date.year)
                break
            except ValueError:
                pass
    
    # If no full date found, use year
    if not election_date and year:
        election_date = year
    
    # Extract election type from filename
    filename = path.stem  # filename without extension
    
    # Common election type patterns
    # Ordered by specificity to match more specific patterns first
    election_types = {
        # Spanish variants (2018, 2021 data)
        'DIPUTACIONES': 'DIP_FED',
        'PRESIDENCIA': 'PRES',
        'SENADURIAS': 'SEN',
        'SENADORES': 'SEN',
        # English/abbreviated variants
        'PRES': 'PRES',
        'PRESIDENTE': 'PRES',
        'PRESIDENTIAL': 'PRES',
        'DIP_FED': 'DIP_FED',
        'DIP_LOC': 'DIP_LOC',
        'DIPUTADO': 'DIP_FED',
        'DIPUTADOS': 'DIP_FED',
        'DIP': 'DIP_FED',  # Generic DIP defaults to federal
        'SEN': 'SEN',
        'SENADOR': 'SEN',
        'GOB': 'GOB',
        'GOBERNADOR': 'GOB',
        'AYU': 'AYU',
        'AYUNTAMIENTO': 'AYU',
    }
    
    election_type = None
    filename_upper = filename.upper()
    
    # Try to detect election type from filename
    # Check exact matches first, then partial matches
    if filename_upper in election_types:
        election_type = election_types[filename_upper]
    else:
        # Try partial matches
        for pattern, etype in election_types.items():
            if pattern in filename_upper:
                election_type = etype
                break
    
    # Build election name
    if election_type and year:
        election_name = f"{election_type}_{year}"
    elif year:
        # Use filename with year
        election_name = f"{filename.upper()}_{year}"
    else:
        # Fall back to filename
        election_name = filename.upper()
    
    return election_name, election_date


def parse_election_name(filename: str) -> Optional[str]:
    """
    Extract election type from filename.
    
    Supports both English and Spanish variants:
    - presidencia/presidente/pres → PRES
    - diputaciones/diputado/dip → DIP_FED
    - senadurias/senadores/sen → SEN
    
    Args:
        filename: Name of the file (with or without extension)
        
    Returns:
        Election type (PRES, DIP_FED, SEN, GOB, etc.) or None
    """
    path = Path(filename)
    filename_upper = path.stem.upper()
    
    # Ordered by specificity - check more specific patterns first
    patterns = [
        (r'PRESIDENCIA', 'PRES'),
        (r'DIPUTACIONES', 'DIP_FED'),
        (r'SENADURIAS', 'SEN'),
        (r'SENADORES', 'SEN'),
        (r'PRES', 'PRES'),
        (r'DIP.*FED', 'DIP_FED'),
        (r'DIP.*LOC', 'DIP_LOC'),
        (r'DIPUTAD', 'DIP_FED'),
        (r'SEN', 'SEN'),
        (r'GOB', 'GOB'),
        (r'AYU', 'AYU'),
    ]
    
    for pattern, election_type in patterns:
        if re.search(pattern, filename_upper):
            return election_type
    
    return None


def ensure_database_directory(db_path: str) -> Path:
    """
    Ensure the database directory exists.
    
    Args:
        db_path: Path to database file
        
    Returns:
        Path object for the database
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_default_db_path() -> Path:
    """
    Get the default database path relative to project root.
    
    Returns:
        Path to default database location
    """
    # Try to find project root (look for pyproject.toml)
    current = Path.cwd()
    
    # Search up to 5 levels up
    for _ in range(5):
        if (current / 'pyproject.toml').exists():
            return current / 'data' / 'processed' / 'electoral_data.db'
        current = current.parent
    
    # Fall back to data/processed/electoral_data.db relative to cwd
    return Path('data') / 'processed' / 'electoral_data.db'


def format_election_table_name(election_name: str, entidad_id: int) -> str:
    """
    Format table name for an election and entidad.
    
    Args:
        election_name: Election name (e.g., 'PRES_2024')
        entidad_id: State ID (1-32)
        
    Returns:
        Table name (e.g., 'election_pres_2024_01')
    """
    # Clean election name (remove special chars, lowercase)
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', election_name).lower()
    return f"election_{clean_name}_{entidad_id:02d}"


def validate_year(year: str) -> bool:
    """
    Validate that year is reasonable for electoral data.
    
    Args:
        year: Year string
        
    Returns:
        True if valid, False otherwise
    """
    try:
        year_int = int(year)
        return 1990 <= year_int <= 2030
    except (ValueError, TypeError):
        return False

