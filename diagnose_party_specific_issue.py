"""
Diagnose Party-Specific Geography Issues
=========================================

Check why some parties (MORENA) show wrong geography while others (PRI, PRD, PAN) work correctly.
"""

import sys
from pathlib import Path
import pandas as pd

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator

def diagnose_party_data(entidad_id: int, estado_name: str, parties: list):
    """Check data for different parties."""
    print(f"\n{'=' * 80}")
    print(f"DIAGNOSING: {estado_name} (ENTIDAD = {entidad_id})")
    print(f"{'=' * 80}\n")
    
    # Initialize orchestrator
    db_path = Path(__file__).parent / "data" / "processed" / "electoral_data.db"
    orchestrator = CleanVotesOrchestrator(db_path=str(db_path))
    
    # Load full data with geometry
    print("Loading electoral data with geometry...")
    gdf = orchestrator.load_election_data(
        election_name='PRES_2024',
        entidad_id=entidad_id,
        as_geodataframe=True
    )
    
    print(f"✅ Total rows loaded: {len(gdf)}")
    print(f"📍 ID_ENTIDAD values: {gdf['ID_ENTIDAD'].unique()}")
    print(f"📏 Geometry bounds: {gdf.total_bounds}")
    print(f"🗺️  CRS: {gdf.crs}")
    print(f"📊 Geometries available: {gdf['geometry'].notna().sum()}/{len(gdf)}")
    
    # Check SECCION values
    print(f"\n📋 SECCION range: {gdf['SECCION'].min()} - {gdf['SECCION'].max()}")
    print(f"📋 Unique SECCIONes: {len(gdf['SECCION'].unique())}")
    
    # Now check data for each party
    print(f"\n{'─' * 80}")
    print("PARTY-SPECIFIC DATA CHECK")
    print(f"{'─' * 80}\n")
    
    for party in parties:
        print(f"\n🔍 Checking: {party}")
        
        if party not in gdf.columns:
            print(f"   ❌ Column '{party}' not found!")
            continue
        
        # Get rows with non-zero votes for this party
        party_data = gdf[gdf[party] > 0].copy()
        
        print(f"   📊 Rows with {party} votes: {len(party_data)}")
        
        if len(party_data) == 0:
            print(f"   ⚠️  No votes found for {party}")
            continue
        
        # Check ENTIDAD
        entidad_values = party_data['ID_ENTIDAD'].unique()
        print(f"   📍 ID_ENTIDAD values: {entidad_values}")
        
        # Check SECCION range
        print(f"   📋 SECCION range: {party_data['SECCION'].min()} - {party_data['SECCION'].max()}")
        
        # Check geometry availability
        has_geometry = party_data['geometry'].notna().sum()
        print(f"   🗺️  Has geometry: {has_geometry}/{len(party_data)} rows")
        
        if has_geometry > 0:
            # Check bounds
            bounds = party_data.total_bounds
            print(f"   📏 Bounds: {bounds}")
            
            # Compare with expected CDMX bounds
            cdmx_bounds = [460677, 2106307, 505712, 2166534]
            baja_bounds = [367175, 3100381, 961080, 3622781]
            
            # Check which state this looks like
            cdmx_match = abs(bounds[0] - cdmx_bounds[0]) < 50000
            baja_match = abs(bounds[0] - baja_bounds[0]) < 50000
            
            if cdmx_match:
                print(f"   ✅ Bounds match CDMX!")
            elif baja_match:
                print(f"   ❌ Bounds match BAJA CALIFORNIA! (WRONG)")
            else:
                print(f"   ⚠️  Bounds don't match expected region")
        else:
            print(f"   ❌ NO GEOMETRY AVAILABLE")
    
    return gdf


if __name__ == "__main__":
    print("=" * 80)
    print("PARTY-SPECIFIC GEOGRAPHY DIAGNOSIS")
    print("=" * 80)
    
    # Test parties
    parties = ['PRI', 'PRD', 'PAN', 'MORENA']
    
    print("\n🔍 Testing CDMX with different parties...")
    gdf = diagnose_party_data(9, "Ciudad de México", parties)
    
    print(f"\n{'=' * 80}")
    print("DIAGNOSIS COMPLETE")
    print(f"{'=' * 80}\n")
    
    # Additional analysis
    print("💡 ADDITIONAL ANALYSIS:")
    print(f"   Total unique SECCIONes in data: {len(gdf['SECCION'].unique())}")
    
    for party in parties:
        if party in gdf.columns:
            party_secciones = gdf[gdf[party] > 0]['SECCION'].nunique()
            print(f"   {party}: {party_secciones} unique SECCIONes with votes")
