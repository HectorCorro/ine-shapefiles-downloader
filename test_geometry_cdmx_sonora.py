"""
Test Geometry Loading for CDMX and Sonora
==========================================

Quick test to verify shapefile loading works for problematic states.
"""

import sys
from pathlib import Path

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator

def test_state(entidad_id: int, estado_name: str):
    """Test loading geometry for a state."""
    print(f"\n{'=' * 60}")
    print(f"Testing: {estado_name} (ID: {entidad_id})")
    print(f"{'=' * 60}")
    
    # Initialize orchestrator
    db_path = Path(__file__).parent / "data" / "processed" / "electoral_data.db"
    orchestrator = CleanVotesOrchestrator(db_path=str(db_path))
    
    # Try loading PRES_2024 data with geometry
    try:
        print(f"Loading PRES_2024 for {estado_name}...")
        gdf = orchestrator.load_election_data(
            election_name='PRES_2024',
            entidad_id=entidad_id,
            as_geodataframe=True
        )
        
        print(f"✅ Success!")
        print(f"   Type: {type(gdf)}")
        print(f"   Shape: {gdf.shape}")
        print(f"   Has geometry: {'geometry' in gdf.columns}")
        if 'geometry' in gdf.columns:
            print(f"   Geometry count: {gdf['geometry'].notna().sum()}/{len(gdf)}")
            print(f"   CRS: {gdf.crs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing geometry loading for problematic states...")
    print()
    
    results = []
    
    # Test CDMX
    results.append(("CDMX", test_state(9, "Ciudad de México")))
    
    # Test Sonora
    results.append(("Sonora", test_state(26, "Sonora")))
    
    # Test Aguascalientes (known to work)
    results.append(("Aguascalientes", test_state(1, "Aguascalientes")))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print(f"\n🎉 All tests passed! Geometry loading works correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check errors above.")
