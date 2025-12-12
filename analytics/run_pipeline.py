#!/usr/bin/env python3
"""
Electoral Data Processing Pipeline
===================================

Scans data/raw/electoral/ for all electoral data files and processes them
into the SQLite database with geometry for spatial analysis.

This script:
1. Finds all electoral files (CSV, Excel, Parquet) in data/raw/electoral/
2. Auto-detects election name and date from file paths
3. Processes each file with cleaning and geometry integration
4. Stores results in SQLite database (one table per election/entidad)
5. Provides detailed progress reporting

The output database is ready for:
- Moran's spatial autocorrelation analysis
- Interactive mapping and visualization
- Statistical analysis across elections and states

Usage:
    # Process all files with geometry (for Moran's analysis)
    uv run python analytics/run_pipeline.py
    
    # Dry-run (show what would be processed)
    uv run python analytics/run_pipeline.py --dry-run
    
    # Process specific years only
    uv run python analytics/run_pipeline.py --years 2024 2021
    
    # Without geometry (faster, but no spatial analysis)
    uv run python analytics/run_pipeline.py --no-geometry
    
    # Custom data directory
    uv run python analytics/run_pipeline.py --data-dir path/to/electoral
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics.clean_votes import CleanVotesOrchestrator, infer_election_metadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


class ElectoralPipeline:
    """
    Pipeline for processing multiple electoral data files.
    """
    
    SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.parquet']
    
    def __init__(
        self,
        data_dir: str = 'data/raw/electoral',
        db_path: str = None,
        include_geometry: bool = True,
        shapefile_type: str = 'peepjf',
        skip_existing: bool = True
    ):
        """
        Initialize the pipeline.
        
        Args:
            data_dir: Base directory containing electoral data
            db_path: Database path (None = auto-detect)
            include_geometry: Whether to merge with shapefiles (needed for Moran's analysis)
            shapefile_type: Type of shapefile ('peepjf' or 'nacional')
            skip_existing: If True, skip elections already in database
        """
        self.data_dir = Path(data_dir).resolve()
        self.include_geometry = include_geometry
        self.shapefile_type = shapefile_type
        self.skip_existing = skip_existing
        
        # Initialize orchestrator
        self.orchestrator = CleanVotesOrchestrator(db_path=db_path)
        
        # Get existing elections
        self.existing_elections = set()
        if skip_existing:
            elections = self.orchestrator.list_available_elections()
            for _, row in elections.iterrows():
                self.existing_elections.add(row['election_name'])
            logger.info(f"Found {len(self.existing_elections)} existing elections in database")
        
        logger.info(f"Pipeline initialized")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Database: {self.orchestrator.db_path}")
        logger.info(f"Include geometry: {include_geometry}")
        logger.info(f"Skip existing: {skip_existing}")
    
    def find_electoral_files(self, years: List[str] = None, specific_folder: str = None) -> List[Tuple[Path, str, str, bool]]:
        """
        Find all electoral data files in the data directory.
        
        Args:
            years: List of years to process (None = all years)
            specific_folder: Process only files in this specific folder (e.g., '2024' or '2024/subfolder')
            
        Returns:
            List of tuples: (file_path, inferred_election_name, inferred_date, already_exists)
        """
        logger.info(f"Scanning for electoral files in: {self.data_dir}")
        
        if not self.data_dir.exists():
            logger.error(f"Data directory does not exist: {self.data_dir}")
            return []
        
        files = []
        
        # If specific folder provided, scan only that folder
        if specific_folder:
            search_dir = self.data_dir / specific_folder
            if not search_dir.exists():
                logger.error(f"Specific folder does not exist: {search_dir}")
                return []
            
            logger.info(f"Scanning specific folder: {specific_folder}")
            files.extend(self._scan_directory(search_dir))
        else:
            # Scan year directories
            for year_dir in sorted(self.data_dir.iterdir()):
                if not year_dir.is_dir():
                    continue
                
                # Filter by years if specified
                if years and year_dir.name not in years:
                    continue
                
                logger.info(f"Scanning year directory: {year_dir.name}")
                files.extend(self._scan_directory(year_dir))
        
        logger.info(f"Found {len(files)} electoral files")
        
        # Filter out existing elections if skip_existing is True
        if self.skip_existing:
            original_count = len(files)
            files = [(fp, en, ed, exists) for fp, en, ed, exists in files if not exists]
            skipped = original_count - len(files)
            if skipped > 0:
                logger.info(f"Skipping {skipped} already processed elections")
        
        return files
    
    def _scan_directory(self, directory: Path) -> List[Tuple[Path, str, str, bool]]:
        """
        Scan a directory for electoral files.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of tuples: (file_path, election_name, election_date, already_exists)
        """
        files = []
        
        for ext in self.SUPPORTED_EXTENSIONS:
            for file_path in directory.rglob(f'*{ext}'):
                # Skip hidden files
                if file_path.name.startswith('.'):
                    continue
                
                # Infer metadata
                election_name, election_date = infer_election_metadata(str(file_path))
                
                if election_name:
                    already_exists = election_name in self.existing_elections
                    files.append((file_path, election_name, election_date, already_exists))
                    
                    status = "EXISTS" if already_exists else "NEW"
                    logger.debug(f"Found [{status}]: {file_path.name} → {election_name} ({election_date})")
        
        return files
    
    def process_file(
        self,
        file_path: Path,
        election_name: str = None,
        election_date: str = None
    ) -> Dict:
        """
        Process a single electoral file.
        
        Args:
            file_path: Path to electoral file
            election_name: Election name (auto-inferred if None)
            election_date: Election date (auto-inferred if None)
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'file': str(file_path),
            'election_name': election_name,
            'election_date': election_date,
            'success': False,
            'rows': 0,
            'entidades': 0,
            'has_geometry': False,
            'error': None
        }
        
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing: {file_path.name}")
            logger.info(f"Election: {election_name} ({election_date})")
            logger.info(f"{'='*70}")
            
            # Process file
            df = self.orchestrator.process_electoral_file(
                file_path=str(file_path),
                election_name=election_name,
                election_date=election_date,
                include_geometry=self.include_geometry,
                shapefile_type=self.shapefile_type,
                save_to_db=True,
                encoding='utf-8'
            )
            
            # Update results
            result['success'] = True
            result['rows'] = len(df)
            result['entidades'] = df['ID_ENTIDAD'].nunique() if 'ID_ENTIDAD' in df.columns else 0
            result['has_geometry'] = 'geometry' in df.columns
            
            logger.info(f"✓ Success!")
            logger.info(f"  Rows: {result['rows']}")
            logger.info(f"  Entidades: {result['entidades']}")
            logger.info(f"  Geometry: {result['has_geometry']}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"✗ Failed: {e}")
            logger.exception("Full error:")
        
        return result
    
    def run(
        self,
        years: List[str] = None,
        specific_folder: str = None,
        dry_run: bool = False,
        continue_on_error: bool = True
    ) -> Dict:
        """
        Run the complete pipeline.
        
        Args:
            years: List of years to process (None = all years)
            specific_folder: Process only files in this specific folder
            dry_run: If True, only show what would be processed
            continue_on_error: If True, continue processing even if a file fails
            
        Returns:
            Dictionary with pipeline results
        """
        start_time = datetime.now()
        
        logger.info("\n" + "="*70)
        logger.info("ELECTORAL DATA PROCESSING PIPELINE")
        logger.info("="*70)
        logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE PROCESSING'}")
        if self.skip_existing:
            logger.info(f"Skip existing: ENABLED")
        
        # Find files
        files = self.find_electoral_files(years=years, specific_folder=specific_folder)
        
        if not files:
            logger.warning("No electoral files found!")
            return {
                'total_files': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        logger.info(f"\n{'='*70}")
        logger.info(f"FOUND {len(files)} FILES TO PROCESS")
        logger.info(f"{'='*70}\n")
        
        # Show what will be processed
        for i, (file_path, election_name, election_date, already_exists) in enumerate(files, 1):
            status = "[SKIP]" if already_exists else "[NEW] "
            logger.info(f"{i}. {status} {file_path.relative_to(self.data_dir)}")
            logger.info(f"   → {election_name} ({election_date})")
        
        if dry_run:
            logger.info(f"\n{'='*70}")
            logger.info("DRY RUN COMPLETE - No files processed")
            logger.info(f"{'='*70}")
            return {
                'total_files': len(files),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }
        
        # Process files
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"\n{'='*70}")
        logger.info("STARTING PROCESSING")
        logger.info(f"{'='*70}\n")
        
        for i, (file_path, election_name, election_date, already_exists) in enumerate(files, 1):
            logger.info(f"\n[{i}/{len(files)}] Processing: {file_path.name}")
            
            result = self.process_file(file_path, election_name, election_date)
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
                if not continue_on_error:
                    logger.error("Stopping pipeline due to error")
                    break
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info(f"\n{'='*70}")
        logger.info("PIPELINE COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration}")
        logger.info(f"\nResults:")
        logger.info(f"  Total files: {len(files)}")
        logger.info(f"  Processed: {len(results)}")
        logger.info(f"  Successful: {successful} ✓")
        logger.info(f"  Failed: {failed} ✗")
        
        if successful > 0:
            total_rows = sum(r['rows'] for r in results if r['success'])
            logger.info(f"  Total rows: {total_rows:,}")
        
        # Show failed files
        if failed > 0:
            logger.info(f"\nFailed files:")
            for r in results:
                if not r['success']:
                    logger.info(f"  ✗ {Path(r['file']).name}: {r['error']}")
        
        # Show database info
        logger.info(f"\nDatabase: {self.orchestrator.db_path}")
        elections = self.orchestrator.list_available_elections()
        logger.info(f"Elections in database: {len(elections)}")
        
        logger.info(f"\n{'='*70}")
        logger.info("✅ PIPELINE READY FOR ANALYSIS!")
        logger.info(f"{'='*70}")
        logger.info("\nNext steps:")
        logger.info("  1. Load data from database")
        logger.info("  2. Perform Moran's spatial autocorrelation analysis")
        logger.info("  3. Create maps and visualizations")
        logger.info(f"\nExample:")
        logger.info(f"  from analytics.clean_votes import CleanVotesOrchestrator")
        logger.info(f"  orchestrator = CleanVotesOrchestrator()")
        logger.info(f"  gdf = orchestrator.load_election_data('PRES_2024', entidad_id=1, as_geodataframe=True)")
        
        return {
            'total_files': len(files),
            'processed': len(results),
            'successful': successful,
            'failed': failed,
            'duration': str(duration),
            'results': results
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process all electoral data files into SQLite database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files with geometry (for Moran's analysis)
  uv run python analytics/run_pipeline.py
  
  # Dry-run to see what would be processed
  uv run python analytics/run_pipeline.py --dry-run
  
  # Process only specific years
  uv run python analytics/run_pipeline.py --years 2024 2021
  
  # Process only a specific folder
  uv run python analytics/run_pipeline.py --folder 2024
  uv run python analytics/run_pipeline.py --folder 2024/subfolder
  
  # Reprocess existing elections (force)
  uv run python analytics/run_pipeline.py --no-skip-existing
  
  # Process without geometry (faster)
  uv run python analytics/run_pipeline.py --no-geometry
  
  # Custom data directory
  uv run python analytics/run_pipeline.py --data-dir path/to/electoral
        """
    )
    
    parser.add_argument(
        '--data-dir',
        default='data/raw/electoral',
        help='Base directory containing electoral data (default: data/raw/electoral)'
    )
    
    parser.add_argument(
        '--db-path',
        help='Database path (default: auto-detect data/processed/electoral_data.db)'
    )
    
    parser.add_argument(
        '--years',
        nargs='+',
        help='Process only specific years (e.g., --years 2024 2021)'
    )
    
    parser.add_argument(
        '--folder',
        help='Process only files in specific folder (e.g., --folder 2024 or --folder 2024/subfolder)'
    )
    
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Reprocess elections already in database (default: skip existing)'
    )
    
    parser.add_argument(
        '--no-geometry',
        action='store_true',
        help='Skip geometry integration (faster, but no spatial analysis)'
    )
    
    parser.add_argument(
        '--shapefile-type',
        choices=['peepjf', 'nacional'],
        default='peepjf',
        help='Type of shapefile to use (default: peepjf)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without actually processing'
    )
    
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop pipeline if any file fails (default: continue)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all elections in database and exit'
    )
    
    args = parser.parse_args()
    
    # List elections if requested
    if args.list:
        from analytics.clean_votes import CleanVotesOrchestrator
        orchestrator = CleanVotesOrchestrator(db_path=args.db_path)
        elections = orchestrator.list_available_elections()
        
        print("\n" + "="*70)
        print("ELECTIONS IN DATABASE")
        print("="*70)
        
        if len(elections) > 0:
            print(elections[['election_name', 'entidad_id', 'entidad_name', 
                            'row_count', 'has_geometry', 'created_at']].to_string(index=False))
        else:
            print("No elections found in database.")
        
        print(f"\nTotal: {len(elections)} election tables")
        print(f"Database: {orchestrator.db_path}\n")
        return
    
    # Run pipeline
    pipeline = ElectoralPipeline(
        data_dir=args.data_dir,
        db_path=args.db_path,
        include_geometry=not args.no_geometry,
        shapefile_type=args.shapefile_type,
        skip_existing=not args.no_skip_existing
    )
    
    results = pipeline.run(
        years=args.years,
        specific_folder=args.folder,
        dry_run=args.dry_run,
        continue_on_error=not args.stop_on_error
    )
    
    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

