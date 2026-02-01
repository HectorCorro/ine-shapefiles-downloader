"""
Find Correct Shapefiles
========================

Search all shapefiles to find which folders actually contain
the correct geometry for CDMX and Sonora.
"""

import geopandas as gpd
from pathlib import Path

def scan_all_shapefiles(target_entidad: int, estado_name: str):
    """Scan all SECCION.shp files to find the correct one."""
    print(f"\n{'=' * 70}")
    print(f"SEARCHING FOR: {estado_name} (ENTIDAD = {target_entidad})")
    print(f"{'=' * 70}\n")
    
    geo_path = Path("data/geo")
    
    found_files = []
    
    # Search all SECCION.shp files
    for shp_file in geo_path.rglob("SECCION.shp"):
        try:
            gdf = gpd.read_file(shp_file)
            
            if 'ENTIDAD' in gdf.columns:
                entidad_values = gdf['ENTIDAD'].unique()
                
                if len(entidad_values) == 1 and int(entidad_values[0]) == target_entidad:
                    found_files.append({
                        'path': shp_file,
                        'features': len(gdf),
                        'bounds': gdf.total_bounds
                    })
                    print(f"✅ FOUND at: {shp_file.relative_to(geo_path)}")
                    print(f"   Features: {len(gdf)}")
                    print(f"   Bounds: {gdf.total_bounds}")
                    print()
        except Exception as e:
            # Skip files that can't be read
            pass
    
    if not found_files:
        print(f"❌ No shapefile found with ENTIDAD = {target_entidad}")
        print(f"💡 You may need to re-download the correct shapefile for {estado_name}")
    
    return found_files


if __name__ == "__main__":
    print("=" * 70)
    print("SEARCHING FOR CORRECT SHAPEFILES")
    print("=" * 70)
    
    # Search for CDMX (9)
    cdmx_files = scan_all_shapefiles(9, "Ciudad de México")
    
    # Search for Sonora (26)
    sonora_files = scan_all_shapefiles(26, "Sonora")
    
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE")
    print("=" * 70)
    
    if not cdmx_files:
        print("\n⚠️  CDMX: No correct shapefile found - needs re-download")
    
    if not sonora_files:
        print("⚠️  Sonora: No correct shapefile found - needs re-download")
