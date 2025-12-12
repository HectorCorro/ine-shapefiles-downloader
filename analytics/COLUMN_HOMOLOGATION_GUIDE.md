# Column Homologation Guide

## Overview

The electoral data from different years (2018, 2021, 2024) uses different column naming conventions and file formats. The **Column Homologation System** automatically standardizes these differences, allowing you to process all electoral data with a unified pipeline.

## File Format Differences

### 2024 Format
- **Delimiter**: Comma (`,`)
- **Encoding**: UTF-8
- **Header Line**: Line 6
- **Key Columns**:
  - `ID_ENTIDAD` (not ID_ESTADO)
  - `ENTIDAD` (not NOMBRE_ESTADO)
  - `ID_DISTRITO_FEDERAL` (not ID_DISTRITO)
  - `DISTRITO_FEDERAL` (not NOMBRE_DISTRITO)
  - `LISTA_NOMINAL` (not LISTA_NOMINAL_CASILLA)
  - `NO_REGISTRADAS` (not CNR)
  - `NULOS` (not VN)
  - `TOTAL_VOTOS_CALCULADO` (singular, not plural)

### 2021 Format
- **Delimiter**: Pipe (`|`)
- **Encoding**: Latin-1 (usually)
- **Header Line**: Line 6
- **Key Columns**:
  - `ID_ESTADO` → maps to `ID_ENTIDAD`
  - `NOMBRE_ESTADO` → maps to `ENTIDAD`
  - `ID_DISTRITO` → maps to `ID_DISTRITO_FEDERAL`
  - `NOMBRE_DISTRITO` → maps to `DISTRITO_FEDERAL`
  - `LISTA_NOMINAL_CASILLA` → maps to `LISTA_NOMINAL`
  - `CANDIDATO/A NO REGISTRADO/A` → maps to `NO_REGISTRADAS`
  - `VOTOS NULOS` → maps to `NULOS`
  - `TOTAL_VOTOS_CALCULADOS` (plural) → maps to `TOTAL_VOTOS_CALCULADO`

### 2018 Format
- **Delimiter**: Pipe (`|`)
- **Encoding**: Latin-1 (usually)
- **Header Line**: Line 6
- **Key Columns**: Similar to 2021, plus:
  - `MOVIMIENTO CIUDADANO` → maps to `MC`
  - `NUEVA ALIANZA` → maps to `NA`
  - `ENCUENTRO SOCIAL` → maps to `PES`
  - `CNR` → maps to `NO_REGISTRADAS`
  - `VN` → maps to `NULOS`
  - Coalition names use underscores (`PAN_PRD_MC`) → maps to hyphens (`PAN-PRD-MC`)

## Automatic Homologation

The system **automatically handles** all these differences:

### 1. File Reading with Delimiter Detection

The `ElectoralDataReader` automatically:
- Detects pipe (`|`) or comma (`,`) delimiters
- Handles UTF-8 or Latin-1 encoding
- Finds the header row (even with preamble text)
- Removes empty trailing columns

```python
from analytics.clean_votes import ElectoralDataReader

reader = ElectoralDataReader()

# Works with any format!
df_2024 = reader.read_file('data/raw/electoral/2024/PRES_2024.csv')
df_2021 = reader.read_file('data/raw/electoral/2021/diputaciones.csv')
df_2018 = reader.read_file('data/raw/electoral/2018/presidencia.csv')
```

### 2. Column Name Homologation

The `ColumnMapper` automatically:
- Detects the data format year (2018/2021/2024)
- Renames columns to the standard 2024 schema
- Standardizes party names and coalition formats

```python
from analytics.clean_votes import ColumnMapper

mapper = ColumnMapper()

# Auto-detect and homologate
detected_year = mapper.detect_format_year(df)
df_standard = mapper.homologate_columns(df)

# Now df_standard has: ID_ENTIDAD, ENTIDAD, etc. regardless of source year
```

### 3. Integrated in Orchestrator

The `CleanVotesOrchestrator` **automatically applies homologation** in the pipeline:

```python
from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Works seamlessly with any year!
df_2024 = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',
    save_to_db=True
)

df_2021 = orchestrator.process_electoral_file(
    'data/raw/electoral/2021/diputaciones.csv',
    save_to_db=True
)

df_2018 = orchestrator.process_electoral_file(
    'data/raw/electoral/2018/presidencia.csv',
    save_to_db=True
)
```

## Column Mapping Reference

### Core Identification Columns

| 2018/2021 Format | 2024 Format (Standard) |
|------------------|------------------------|
| `ID_ESTADO` | `ID_ENTIDAD` |
| `NOMBRE_ESTADO` | `ENTIDAD` |
| `ID_DISTRITO` | `ID_DISTRITO_FEDERAL` |
| `NOMBRE_DISTRITO` | `DISTRITO_FEDERAL` |

### Vote Count Columns

| 2018/2021 Format | 2024 Format (Standard) |
|------------------|------------------------|
| `LISTA_NOMINAL_CASILLA` | `LISTA_NOMINAL` |
| `TOTAL_VOTOS_CALCULADOS` | `TOTAL_VOTOS_CALCULADO` |
| `CNR` (2018) | `NO_REGISTRADAS` |
| `CANDIDATO/A NO REGISTRADO/A` (2021) | `NO_REGISTRADAS` |
| `VN` (2018) | `NULOS` |
| `VOTOS NULOS` (2021) | `NULOS` |

### Party Names

| 2018/2021 Format | 2024 Format (Standard) |
|------------------|------------------------|
| `MOVIMIENTO CIUDADANO` | `MC` |
| `NUEVA ALIANZA` | `NA` |
| `ENCUENTRO SOCIAL` | `PES` |

### Coalition Names (Underscores → Hyphens)

| 2018 Format | Standard Format |
|-------------|-----------------|
| `PAN_PRD_MC` | `PAN-PRD-MC` |
| `PAN_PRD` | `PAN-PRD` |
| `PRI_PVEM_NA` | `PRI-PVEM-NA` |
| `PT_MORENA_PES` | `PT-MORENA-PES` |

## Standardized Output Schema

After homologation, all data has these standard columns (when present):

### Identification
- `CLAVE_CASILLA`
- `CLAVE_ACTA`
- `ID_ENTIDAD` ✓ (always present)
- `ENTIDAD` ✓ (state name)
- `ID_DISTRITO_FEDERAL`
- `DISTRITO_FEDERAL`
- `SECCION` ✓ (always present)
- `ID_CASILLA`
- `TIPO_CASILLA`

### Vote Counts
- `LISTA_NOMINAL`
- `TOTAL_VOTOS_CALCULADO`
- `NO_REGISTRADAS`
- `NULOS`

### Parties (standardized names)
- `PAN`, `PRI`, `PRD`, `PVEM`, `PT`, `MC`, `MORENA`
- `NA` (Nueva Alianza, 2018)
- `PES` (Encuentro Social, 2018-2021)
- `FXM` (Fuerza por México, 2021)
- `RSP` (Redes Sociales Progresistas, 2021)

### Coalitions (standardized with hyphens)
- `PAN-PRI-PRD`, `PAN-PRI`, `PAN-PRD`, etc.
- `PVEM-PT-MORENA`, `PVEM-PT`, `PT-MORENA`, etc.

## Usage Examples

### Basic Usage

```python
from analytics.clean_votes import CleanVotesOrchestrator

# Initialize orchestrator (uses default database path)
orchestrator = CleanVotesOrchestrator()

# Process any year's data - homologation is automatic!
df = orchestrator.process_electoral_file(
    'data/raw/electoral/2021/diputaciones.csv',
    save_to_db=True
)

# df now has standardized columns: ID_ENTIDAD, ENTIDAD, etc.
print(df[['ID_ENTIDAD', 'ENTIDAD', 'SECCION', 'LISTA_NOMINAL']].head())
```

### Processing Multiple Years

```python
# Process elections from different years
files = [
    'data/raw/electoral/2024/PRES_2024.csv',
    'data/raw/electoral/2021/diputaciones.csv',
    'data/raw/electoral/2018/presidencia.csv'
]

for file_path in files:
    df = orchestrator.process_electoral_file(file_path, save_to_db=True)
    print(f"Processed {file_path}: {len(df)} sections")
```

### Manual Homologation

```python
from analytics.clean_votes import ElectoralDataReader, homologate_dataframe

# Read file
reader = ElectoralDataReader()
df_raw = reader.read_file('data/raw/electoral/2018/presidencia.csv')

# Homologate
df_standard = homologate_dataframe(df_raw)

# Now you can work with standardized column names
print(df_standard['ID_ENTIDAD'].unique())
```

## Database Storage

Data is stored in the SQLite database with standardized table names:

```
election_{type}_{year}_{entidad_id}
```

Examples:
- `election_pres_2024_09` (CDMX Presidential 2024)
- `election_dip_fed_2021_15` (Estado de México Diputaciones 2021)
- `election_pres_2018_01` (Aguascalientes Presidential 2018)

All tables share the same standardized schema, making queries consistent across years.

## Querying Across Years

```python
import sqlite3

conn = sqlite3.connect('data/processed/electoral_data.db')

# Query 2024 presidential data
df_2024 = pd.read_sql(
    "SELECT ID_ENTIDAD, SECCION, MORENA, PAN, PRI FROM election_pres_2024_09",
    conn
)

# Query 2018 presidential data (same column names!)
df_2018 = pd.read_sql(
    "SELECT ID_ENTIDAD, SECCION, MORENA, PAN, PRI FROM election_pres_2018_09",
    conn
)

# Compare across years
comparison = df_2024.merge(df_2018, on=['ID_ENTIDAD', 'SECCION'], suffixes=('_2024', '_2018'))
```

## Benefits

1. **Unified Pipeline**: Process any year's data with the same code
2. **Automatic Detection**: No need to specify file format manually
3. **Consistent Output**: All data uses the same column names
4. **Easy Comparison**: Query and compare data across years
5. **Future-Proof**: Add new mappings for future election formats

## Validation

The system validates that required columns exist after homologation:
- `ID_ENTIDAD` (required)
- `SECCION` (required)

If these are missing, warnings are logged but processing continues.

## Extension

To add support for new column mappings, edit:
- `analytics/src/analytics/clean_votes/column_mapper.py`
- Add entries to `COLUMN_MAPPINGS` or `PARTY_NAME_MAPPINGS`

## Troubleshooting

### Missing Columns After Homologation

Check the mapper's detection:
```python
mapper = ColumnMapper()
detected_year = mapper.detect_format_year(df)
print(f"Detected format: {detected_year}")

mapping = mapper.get_column_mapping(df)
print(f"Mappings to apply: {mapping}")
```

### Encoding Issues

The reader automatically falls back to latin-1 if UTF-8 fails. Check logs for:
```
WARNING - Failed with encoding utf-8, trying latin-1
```

### Custom Delimiters

If you have files with other delimiters, modify `_detect_delimiter()` in `reader.py`.


