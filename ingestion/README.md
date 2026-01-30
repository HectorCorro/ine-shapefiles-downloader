# Ingestion Module

Data acquisition and initial processing for Mexican electoral shapefiles and data files.

## Purpose

The ingestion module handles:
- **Downloading** shapefiles from INE and PEEPJF sources
- **Basic validation** of downloaded files
- **Storage** of raw data in standardized locations
- **Optional S3 upload** for backup and distribution

## Features

### 1. Nacional Shapefiles (`download_nacional.py`)

Downloads official INE shapefiles for all 32 states in three formats:
- Geomedia Profesional
- Geomedia Viewer
- Shapefile

```bash
cd ingestion
uv run python -m ingestion.download_nacional
```

**Output**: `data/raw/productos_ine_nacional/`

### 2. PEEPJF Shapefiles (`download_peepjf.py`)

Downloads electoral section shapefiles from PEEPJF (Proceso Electoral de las Entidades Públicas de los Juzgados Federales).

```bash
cd ingestion
uv run python -m ingestion.download_peepjf
```

**Output**: `data/raw/shapefiles_peepjf/`

### 3. S3 Upload Utilities (`utils/s3_utils.py`)

Utility functions for uploading downloaded files to Amazon S3 for backup and distribution.

## Installation

From the project root:

```bash
# Install ingestion dependencies
uv sync

# Or add specific packages
uv add requests selenium boto3 --package ingestion
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```bash
# AWS S3 Configuration (optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### States Configuration

State codes are defined in `shared/config/estados.py`:

```python
ESTADOS = {
    "01": "Aguascalientes",
    "02": "Baja California",
    # ... etc
    "32": "Zacatecas"
}
```

## Usage Examples

### Download All Nacional Shapefiles

```python
from ingestion.download_nacional import download_all_states

download_all_states(
    output_dir="data/raw/productos_ine_nacional",
    upload_to_s3=False
)
```

### Download PEEPJF Shapefiles

```python
from ingestion.download_peepjf import download_peepjf_shapefiles

download_peepjf_shapefiles(
    output_dir="data/raw/shapefiles_peepjf"
)
```

### Upload to S3

```python
from ingestion.utils.s3_utils import upload_to_s3

upload_to_s3(
    local_path="data/raw/productos_ine_nacional/01_aguascalientes.zip",
    s3_key="shapefiles/nacional/01_aguascalientes.zip"
)
```

## Output Structure

```
data/raw/
├── productos_ine_nacional/
│   ├── 01_aguascalientes/
│   │   ├── GEOMEDIA_PRO/
│   │   ├── GEOMEDIA_VIEWER/
│   │   └── SHAPEFILE/
│   ├── 02_baja_california/
│   └── ...
│
└── shapefiles_peepjf/
    ├── 01_aguascalientes.zip
    ├── 02_baja_california.zip
    └── ...
```

## Dependencies

Core:
- `requests` - HTTP requests
- `selenium` - Web automation
- `webdriver-manager` - Chrome driver management

Optional:
- `boto3` - AWS S3 integration
- `python-dotenv` - Environment variable loading

## Data Flow

```
┌─────────────────┐
│  INE / PEEPJF   │
│    Websites     │
└────────┬────────┘
         │ Download
         ▼
┌─────────────────┐
│   Ingestion     │
│    Module       │
└────────┬────────┘
         │ Save
         ▼
┌─────────────────┐      ┌──────────────┐
│  data/raw/      │──────│  S3 Backup   │
│  (Local)        │      │  (Optional)  │
└────────┬────────┘      └──────────────┘
         │ Read
         ▼
┌─────────────────┐
│   Analytics     │
│    Module       │
└─────────────────┘
```

## Troubleshooting

### Chrome Driver Not Found

```bash
# Reinstall webdriver-manager
uv add webdriver-manager --package ingestion --force
```

### Download Fails

1. Check internet connection
2. Verify website URLs are still valid
3. Check for rate limiting or blocking
4. Review logs for specific errors

### S3 Upload Fails

1. Verify AWS credentials are configured
2. Check S3 bucket exists and is accessible
3. Verify IAM permissions for S3 write
4. Check AWS region configuration

## Best Practices

1. **Run downloads during off-peak hours** - Large files may take time
2. **Verify checksums** - If provided by source
3. **Store raw data unchanged** - Keep original files for reproducibility
4. **Use S3 backup** - For disaster recovery
5. **Document data sources** - Keep track of download dates and URLs

## Contributing

When adding new data sources:
1. Create a new script in `ingestion/src/ingestion/`
2. Follow existing naming conventions
3. Output to `data/raw/<source_name>/`
4. Add documentation to this README

## License

Part of the INE Electoral Data Analysis project.
