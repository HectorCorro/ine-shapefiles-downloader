#!/usr/bin/env python3
"""
Check Geometry Availability
============================

Quick script to check which elections have geometry data available.
This helps diagnose "No geometry available" errors in the dashboard.
"""

import sys
from pathlib import Path

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator


def main():
    """Check which elections have geometry."""
    orchestrator = CleanVotesOrchestrator()
    
    print("\n" + "="*70)
    print("GEOMETRY AVAILABILITY CHECK")
    print("="*70)
    
    # Get all elections
    elections = orchestrator.list_available_elections()
    
    # Group by election name
    election_names = elections['election_name'].unique()
    
    for election_name in sorted(election_names):
        print(f"\n{election_name}:")
        print("-" * 70)
        
        election_data = elections[elections['election_name'] == election_name]
        
        with_geom = election_data[election_data['has_geometry'] == True]
        without_geom = election_data[election_data['has_geometry'] == False]
        
        print(f"  ✅ With geometry: {len(with_geom)} states")
        print(f"  ❌ Without geometry: {len(without_geom)} states")
        
        if len(without_geom) > 0:
            print(f"\n  States missing geometry:")
            for _, row in without_geom.iterrows():
                print(f"    - {row['entidad_name']} (ID: {row['entidad_id']})")
    
    print("\n" + "="*70)
    print("HOW TO ADD GEOMETRY TO EXISTING DATA")
    print("="*70)
    print("""
If your data doesn't have geometry, you need to reprocess it with geometry enabled.

Example:

from analytics.clean_votes import CleanVotesOrchestrator

orchestrator = CleanVotesOrchestrator()

# Process with geometry
orchestrator.process_electoral_file(
    file_path='path/to/your/data.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,  # ← Important!
    shapefile_type='peepjf',  # or 'nacional'
    save_to_db=True
)

This will merge the electoral data with shapefiles from data/geo/ directory.
""")
    
    print("\n" + "="*70)


if __name__ == '__main__':
    main()
