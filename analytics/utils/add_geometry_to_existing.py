#!/usr/bin/env python3
"""
Add Geometry to Existing Data
==============================

Script to add geometry to electoral data that's already in the database
but doesn't have spatial information.

This avoids having to reprocess from raw files.
"""

import sys
from pathlib import Path

# Add paths
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator


def add_geometry_to_election(
    election_name: str,
    entidad_id: int,
    shapefile_type: str = 'peepjf'
):
    """
    Add geometry to existing electoral data.
    
    Args:
        election_name: Election name (e.g., 'PRES_2024')
        entidad_id: State ID (1-32)
        shapefile_type: Type of shapefile ('peepjf' or 'nacional')
    """
    orchestrator = CleanVotesOrchestrator()
    
    print(f"\n{'='*70}")
    print(f"Adding geometry to: {election_name}, Entidad {entidad_id}")
    print(f"{'='*70}\n")
    
    try:
        # Load existing data without geometry
        print("[1/3] Loading existing data from database...")
        df = orchestrator.load_election_data(
            election_name=election_name,
            entidad_id=entidad_id,
            as_geodataframe=False
        )
        print(f"  ✓ Loaded {len(df)} rows")
        
        # Merge with geometry
        print("\n[2/3] Merging with shapefile geometry...")
        gdf = orchestrator.geometry_merger.merge_with_shapefile(
            df=df,
            entidad_id=entidad_id,
            shapefile_type=shapefile_type
        )
        print(f"  ✓ Merged geometry for {len(gdf)} rows")
        
        # Get entidad name
        entidad_name = df['ENTIDAD'].iloc[0] if 'ENTIDAD' in df.columns else f"Entidad_{entidad_id}"
        
        # Get election date from existing metadata
        try:
            info = orchestrator.get_election_info(election_name, entidad_id)
            election_date = info.get('election_date')
        except:
            election_date = None
        
        # Save back to database
        print("\n[3/3] Saving updated data to database...")
        table_name = orchestrator.database.save_electoral_data(
            df=gdf,
            election_name=election_name,
            entidad_id=entidad_id,
            entidad_name=entidad_name,
            election_date=election_date,
            if_exists='replace'  # Replace existing data
        )
        print(f"  ✓ Saved to table: {table_name}")
        
        print(f"\n{'='*70}")
        print("✅ SUCCESS! Geometry added successfully")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def add_geometry_to_all_states(election_name: str, shapefile_type: str = 'peepjf'):
    """
    Add geometry to all states for an election.
    
    Args:
        election_name: Election name
        shapefile_type: Type of shapefile
    """
    orchestrator = CleanVotesOrchestrator()
    
    print(f"\n{'='*70}")
    print(f"Adding geometry to ALL states for: {election_name}")
    print(f"{'='*70}\n")
    
    # Get all states for this election
    elections = orchestrator.list_available_elections()
    election_data = elections[elections['election_name'] == election_name]
    
    print(f"Found {len(election_data)} states\n")
    
    success_count = 0
    error_count = 0
    
    for _, row in election_data.iterrows():
        entidad_id = int(row['entidad_id'])
        entidad_name = row['entidad_name']
        has_geometry = row['has_geometry']
        
        if has_geometry:
            print(f"⏭️  Skipping {entidad_name} (ID: {entidad_id}) - already has geometry")
            continue
        
        print(f"\n📍 Processing: {entidad_name} (ID: {entidad_id})")
        print("-" * 70)
        
        try:
            add_geometry_to_election(election_name, entidad_id, shapefile_type)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed: {e}")
            error_count += 1
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Add geometry to existing electoral data in database'
    )
    
    parser.add_argument(
        '--election',
        required=True,
        help='Election name (e.g., PRES_2024)'
    )
    
    parser.add_argument(
        '--entidad',
        type=int,
        help='Specific entidad ID (1-32). If not provided, processes all states.'
    )
    
    parser.add_argument(
        '--shapefile-type',
        choices=['peepjf', 'nacional'],
        default='peepjf',
        help='Type of shapefile to use'
    )
    
    args = parser.parse_args()
    
    if args.entidad:
        # Process single state
        add_geometry_to_election(
            election_name=args.election,
            entidad_id=args.entidad,
            shapefile_type=args.shapefile_type
        )
    else:
        # Process all states
        add_geometry_to_all_states(
            election_name=args.election,
            shapefile_type=args.shapefile_type
        )


if __name__ == '__main__':
    main()
