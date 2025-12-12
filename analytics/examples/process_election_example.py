"""
Example: Process Electoral Data
================================

This script demonstrates how to use the clean_votes module to process
electoral data files and store them in a SQLite database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from analytics.clean_votes import CleanVotesOrchestrator


def main():
    """Example workflow for processing electoral data."""
    
    print("="*60)
    print("ELECTORAL DATA PROCESSING EXAMPLE")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = CleanVotesOrchestrator(
        db_path='data/processed/electoral_data.db'
    )
    
    # Example 1: Process 2024 Presidential data
    print("\n[Example 1] Processing 2024 Presidential Election Data")
    print("-" * 60)
    
    try:
        df = orchestrator.process_electoral_file(
            file_path='electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv',
            election_name='PRES_2024',
            election_date='2024-06-03',
            include_geometry=True,  # Merge with shapefiles
            shapefile_type='peepjf',
            save_to_db=True,
            encoding='utf-8'
        )
        
        print(f"\n✓ Success!")
        print(f"  - Shape: {df.shape}")
        print(f"  - Has geometry: {'geometry' in df.columns}")
        print(f"  - Entidades processed: {df['ID_ENTIDAD'].nunique()}")
        
    except FileNotFoundError as e:
        print(f"\n⚠️  File not found: {e}")
        print("   Please check the file path and try again.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    # Example 2: List all available elections
    print("\n[Example 2] List Available Elections")
    print("-" * 60)
    
    elections = orchestrator.list_available_elections()
    if len(elections) > 0:
        print("\nAvailable elections in database:")
        print(elections[['election_name', 'entidad_name', 'row_count', 'has_geometry', 'created_at']].to_string(index=False))
    else:
        print("No elections found in database yet.")
    
    # Example 3: Load specific election data
    if len(elections) > 0:
        print("\n[Example 3] Load Specific Election Data")
        print("-" * 60)
        
        # Get first election from list
        first_election = elections.iloc[0]
        election_name = first_election['election_name']
        entidad_id = first_election['entidad_id']
        
        print(f"\nLoading: {election_name} - ENTIDAD {entidad_id}")
        
        df_loaded = orchestrator.load_election_data(
            election_name=election_name,
            entidad_id=entidad_id,
            as_geodataframe=first_election['has_geometry']
        )
        
        print(f"✓ Loaded {len(df_loaded)} rows")
        print(f"  Columns: {', '.join(df_loaded.columns[:10])}...")
        
        # Show some statistics
        if 'MORENA_PCT' in df_loaded.columns:
            print(f"\nMORENA vote percentage statistics:")
            print(f"  Mean: {df_loaded['MORENA_PCT'].mean():.2f}%")
            print(f"  Median: {df_loaded['MORENA_PCT'].median():.2f}%")
            print(f"  Min: {df_loaded['MORENA_PCT'].min():.2f}%")
            print(f"  Max: {df_loaded['MORENA_PCT'].max():.2f}%")
    
    print("\n" + "="*60)
    print("Example completed!")
    print("="*60)


if __name__ == '__main__':
    main()


