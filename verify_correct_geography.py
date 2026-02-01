"""
Verify Correct Geography
=========================

Check that CDMX and Sonora now return the correct geography, not Baja California.
"""

import sys
from pathlib import Path
import pandas as pd

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator

def verify_geography(entidad_id: int, estado_name: str, expected_bounds: tuple = None):
    """Verify a state loads the correct geography."""
    print(f"\n{'=' * 70}")
    print(f"VERIFYING: {estado_name} (ENTIDAD = {entidad_id})")
    print(f"{'=' * 70}\n")
    
    # Initialize orchestrator
    db_path = Path(__file__).parent / "data" / "processed" / "electoral_data.db"
    orchestrator = CleanVotesOrchestrator(db_path=str(db_path))
    
    # Load with geometry
    gdf = orchestrator.load_election_data(
        election_name='PRES_2024',
        entidad_id=entidad_id,
        as_geodataframe=True
    )
    
    print(f"✅ Loaded: {len(gdf)} features")
    
    # Check ENTIDAD values
    if 'ID_ENTIDAD' in gdf.columns:
        entidad_values = gdf['ID_ENTIDAD'].unique()
        print(f"📍 ID_ENTIDAD values: {entidad_values}")
        
        if len(entidad_values) == 1 and int(entidad_values[0]) == entidad_id:
            print(f"✅ Correct ENTIDAD!")
        else:
            print(f"❌ Wrong ENTIDAD! Expected {entidad_id}")
    
    # Check geometry bounds
    bounds = gdf.total_bounds
    print(f"📏 Bounds: {bounds}")
    
    # Check CRS
    print(f"🗺️  CRS: {gdf.crs}")
    
    # Rough checks for known states
    if expected_bounds:
        print(f"\n📋 Expected bounds: {expected_bounds}")
        
        # Check if bounds are close (within reasonable tolerance)
        bounds_match = all(
            abs(actual - expected) < 50000  # 50km tolerance
            for actual, expected in zip(bounds, expected_bounds)
        )
        
        if bounds_match:
            print(f"✅ Geography bounds match expected region!")
        else:
            print(f"⚠️  Geography bounds don't match - might be wrong state")
    
    return gdf


if __name__ == "__main__":
    print("=" * 70)
    print("VERIFYING CORRECT GEOGRAPHY")
    print("=" * 70)
    
    # Known approximate bounds for these states (from our earlier scans)
    # Format: [minx, miny, maxx, maxy]
    
    # Baja California bounds (this is what we DON'T want)
    baja_bounds = [367175, 3100381, 961080, 3622781]
    
    # CDMX should be around: [460677, 2106307, 505712, 2166534]
    cdmx_bounds = [460677, 2106307, 505712, 2166534]
    
    # Sonora should be around: [118332, 2910644, 752812, 3601533]
    sonora_bounds = [118332, 2910644, 752812, 3601533]
    
    print("\n🔍 Testing CDMX (should NOT be Baja California)...")
    gdf_cdmx = verify_geography(9, "Ciudad de México", cdmx_bounds)
    
    print("\n🔍 Testing Sonora (should NOT be Baja California)...")
    gdf_sonora = verify_geography(26, "Sonora", sonora_bounds)
    
    print("\n🔍 Testing Baja California (for reference)...")
    gdf_baja = verify_geography(2, "Baja California", baja_bounds)
    
    print(f"\n{'=' * 70}")
    print("VERIFICATION COMPLETE")
    print(f"{'=' * 70}\n")
    
    # Final check
    cdmx_correct = abs(gdf_cdmx.total_bounds[0] - cdmx_bounds[0]) < 50000
    sonora_correct = abs(gdf_sonora.total_bounds[0] - sonora_bounds[0]) < 50000
    
    if cdmx_correct and sonora_correct:
        print("🎉 SUCCESS! All states now return correct geography!")
    else:
        print("⚠️  WARNING: Some states may still have incorrect geography")
