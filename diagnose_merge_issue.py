"""
Diagnose Merge Issues
=====================

Check why CDMX and Sonora shapefiles don't merge with electoral data.
"""

import sys
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Add analytics to path
analytics_path = Path(__file__).parent / "analytics" / "src"
sys.path.insert(0, str(analytics_path))

from analytics.clean_votes import CleanVotesOrchestrator

def diagnose_merge(entidad_id: int, estado_name: str):
    """Diagnose merge issues for a state."""
    print(f"\n{'=' * 70}")
    print(f"DIAGNOSING: {estado_name} (ID: {entidad_id})")
    print(f"{'=' * 70}\n")
    
    # Initialize orchestrator
    db_path = Path(__file__).parent / "data" / "processed" / "electoral_data.db"
    orchestrator = CleanVotesOrchestrator(db_path=str(db_path))
    
    # Load electoral data WITHOUT geometry
    print("1. Loading electoral data from database...")
    df = orchestrator.load_election_data(
        election_name='PRES_2024',
        entidad_id=entidad_id,
        as_geodataframe=False
    )
    print(f"   Rows: {len(df)}")
    print(f"   ID_ENTIDAD values: {df['ID_ENTIDAD'].unique()}")
    print(f"   SECCION range: {df['SECCION'].min()} - {df['SECCION'].max()}")
    print(f"   Sample SECCIONes: {sorted(df['SECCION'].unique())[:10]}")
    
    # Load shapefile
    print(f"\n2. Loading shapefile...")
    geo_path = Path(__file__).parent / "data" / "geo" / "shapefiles_peepjf" / f"{entidad_id}_{estado_name.replace(' ', '_')}"
    
    # Find SECCION.shp
    shp_file = None
    for subdir in geo_path.rglob('SECCION.shp'):
        shp_file = subdir
        break
    
    if not shp_file:
        print(f"   ❌ No SECCION.shp found in {geo_path}")
        return
    
    print(f"   Found: {shp_file}")
    gdf = gpd.read_file(shp_file)
    print(f"   Rows: {len(gdf)}")
    print(f"   Columns: {list(gdf.columns)}")
    
    # Check ENTIDAD column
    if 'ENTIDAD' in gdf.columns:
        print(f"   ENTIDAD values: {gdf['ENTIDAD'].unique()}")
    else:
        print(f"   ⚠️  No ENTIDAD column!")
    
    # Check SECCION column
    if 'SECCION' in gdf.columns:
        print(f"   SECCION range: {gdf['SECCION'].min()} - {gdf['SECCION'].max()}")
        print(f"   Sample SECCIONes: {sorted(gdf['SECCION'].unique())[:10]}")
    else:
        print(f"   ⚠️  No SECCION column!")
    
    # Try manual merge to see what happens
    print(f"\n3. Attempting merge...")
    
    # Prepare keys
    df_prep = df.copy()
    gdf_prep = gdf.copy()
    
    # Ensure proper types
    if 'ID_ENTIDAD' in df_prep.columns:
        df_prep['ID_ENTIDAD'] = pd.to_numeric(df_prep['ID_ENTIDAD'], errors='coerce').astype('Int64')
    if 'SECCION' in df_prep.columns:
        df_prep['SECCION'] = pd.to_numeric(df_prep['SECCION'], errors='coerce').astype('Int64')
    
    if 'ENTIDAD' in gdf_prep.columns:
        gdf_prep['ENTIDAD'] = pd.to_numeric(gdf_prep['ENTIDAD'], errors='coerce').astype('Int64')
    if 'SECCION' in gdf_prep.columns:
        gdf_prep['SECCION'] = pd.to_numeric(gdf_prep['SECCION'], errors='coerce').astype('Int64')
    
    # Check for matching values
    if 'ENTIDAD' in gdf_prep.columns and 'ID_ENTIDAD' in df_prep.columns:
        shapefile_entidades = set(gdf_prep['ENTIDAD'].dropna().astype(int))
        electoral_entidades = set(df_prep['ID_ENTIDAD'].dropna().astype(int))
        print(f"   Shapefile ENTIDAD values: {sorted(shapefile_entidades)}")
        print(f"   Electoral ID_ENTIDAD values: {sorted(electoral_entidades)}")
        print(f"   Match: {shapefile_entidades & electoral_entidades}")
        
        if not (shapefile_entidades & electoral_entidades):
            print(f"   ❌ NO MATCHING ENTIDAD VALUES!")
            print(f"   💡 Expected: {sorted(electoral_entidades)}")
            print(f"   💡 Got: {sorted(shapefile_entidades)}")
    
    if 'SECCION' in gdf_prep.columns and 'SECCION' in df_prep.columns:
        shapefile_secciones = set(gdf_prep['SECCION'].dropna().astype(int))
        electoral_secciones = set(df_prep['SECCION'].dropna().astype(int))
        common_secciones = shapefile_entidades & electoral_secciones if 'shapefile_entidades' in locals() else electoral_secciones & shapefile_secciones
        print(f"   Common SECCIONes: {len(common_secciones)}/{len(electoral_secciones)}")
        
        if len(common_secciones) == 0:
            print(f"   ❌ NO MATCHING SECCION VALUES!")
            print(f"   Electoral SECCIONes (sample): {sorted(electoral_secciones)[:10]}")
            print(f"   Shapefile SECCIONes (sample): {sorted(shapefile_secciones)[:10]}")


if __name__ == "__main__":
    print("Diagnosing merge issues for CDMX and Sonora...")
    
    # Test CDMX
    diagnose_merge(9, "CDMX")
    
    # Test Sonora
    diagnose_merge(26, "Sonora")
    
    print(f"\n{'=' * 70}")
    print("DIAGNOSIS COMPLETE")
    print(f"{'=' * 70}")
