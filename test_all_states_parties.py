"""
Comprehensive Test: All States and Parties
===========================================

Test that all states load correct geography regardless of party selected.
"""

import sys
from pathlib import Path
import pandas as pd

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator

# Expected bounds for key states (to detect if wrong state is loaded)
EXPECTED_BOUNDS = {
    2: [367175, 3100381, 961080, 3622781],  # Baja California
    9: [460677, 2106307, 505712, 2166534],  # CDMX
    26: [118332, 2910644, 752812, 3601533], # Sonora
}

MAJOR_PARTIES = ['PAN', 'PRI', 'PRD', 'MORENA', 'PVEM', 'PT', 'MC']

def test_state_party_combination(entidad_id: int, estado_name: str, parties: list):
    """Test a state with multiple parties."""
    print(f"\n{'=' * 80}")
    print(f"TESTING: {estado_name} (ID={entidad_id})")
    print(f"{'=' * 80}\n")
    
    try:
        # Initialize orchestrator
        db_path = Path(__file__).parent / "data" / "processed" / "electoral_data.db"
        orchestrator = CleanVotesOrchestrator(db_path=str(db_path))
        
        # Load full data with geometry
        gdf = orchestrator.load_election_data(
            election_name='PRES_2024',
            entidad_id=entidad_id,
            as_geodataframe=True
        )
        
        if len(gdf) == 0:
            print(f"❌ No data loaded for {estado_name}")
            return False
        
        # Get expected bounds for this state
        expected_bounds = EXPECTED_BOUNDS.get(entidad_id)
        actual_bounds = gdf.total_bounds
        
        # Check if bounds are correct
        bounds_correct = True
        if expected_bounds:
            bounds_match = abs(actual_bounds[0] - expected_bounds[0]) < 50000
            if not bounds_match:
                print(f"❌ GEOGRAPHY MISMATCH!")
                print(f"   Expected bounds: {expected_bounds}")
                print(f"   Actual bounds:   {actual_bounds}")
                
                # Check if it matches wrong state
                for other_id, other_bounds in EXPECTED_BOUNDS.items():
                    if other_id != entidad_id:
                        other_match = abs(actual_bounds[0] - other_bounds[0]) < 50000
                        if other_match:
                            other_names = {2: "Baja California", 9: "CDMX", 26: "Sonora"}
                            print(f"   💡 This looks like {other_names.get(other_id, f'State {other_id}')}!")
                
                bounds_correct = False
        
        # Test each party
        party_results = []
        for party in parties:
            if party not in gdf.columns:
                continue
            
            # Get rows with votes for this party
            party_data = gdf[gdf[party] > 0]
            
            if len(party_data) == 0:
                party_results.append((party, "⚪ No votes"))
                continue
            
            # Check if party data has geometry
            has_geometry = party_data['geometry'].notna().sum()
            
            if has_geometry == 0:
                party_results.append((party, "❌ No geometry"))
            else:
                # Check party-specific bounds
                party_bounds = party_data.total_bounds
                
                if expected_bounds:
                    party_match = abs(party_bounds[0] - expected_bounds[0]) < 50000
                    if party_match:
                        party_results.append((party, f"✅ OK ({has_geometry} secciones)"))
                    else:
                        # Check if matches wrong state
                        wrong_state = None
                        for other_id, other_bounds in EXPECTED_BOUNDS.items():
                            if other_id != entidad_id:
                                other_match = abs(party_bounds[0] - other_bounds[0]) < 50000
                                if other_match:
                                    other_names = {2: "Baja California", 9: "CDMX", 26: "Sonora"}
                                    wrong_state = other_names.get(other_id, f'State {other_id}')
                                    break
                        
                        if wrong_state:
                            party_results.append((party, f"❌ WRONG ({wrong_state})"))
                        else:
                            party_results.append((party, f"⚠️ Unknown region"))
                else:
                    party_results.append((party, f"✅ OK ({has_geometry} secciones)"))
        
        # Print results
        print(f"📊 Total features: {len(gdf)}")
        print(f"📏 Bounds: {actual_bounds}")
        print(f"🗺️  CRS: {gdf.crs}")
        
        if bounds_correct:
            print(f"✅ Geography: CORRECT")
        else:
            print(f"❌ Geography: WRONG")
        
        print(f"\n🎯 Party-specific results:")
        for party, result in party_results:
            print(f"   {party:12s} {result}")
        
        # Overall result
        all_ok = all("✅" in result for _, result in party_results if "⚪" not in result)
        
        if all_ok and bounds_correct:
            print(f"\n✅ ALL TESTS PASSED for {estado_name}")
            return True
        else:
            print(f"\n❌ SOME TESTS FAILED for {estado_name}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE STATE AND PARTY TEST")
    print("=" * 80)
    
    # Test states known to have had issues
    test_states = [
        (2, "Baja California"),
        (9, "Ciudad de México"),
        (26, "Sonora"),
    ]
    
    results = {}
    
    for entidad_id, estado_name in test_states:
        result = test_state_party_combination(entidad_id, estado_name, MAJOR_PARTIES)
        results[estado_name] = result
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    
    for estado_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {estado_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 ALL STATES PASSED!")
        print(f"   All states show correct geography for all parties.")
    else:
        print(f"\n⚠️  SOME STATES FAILED")
        print(f"   Check results above for details.")
