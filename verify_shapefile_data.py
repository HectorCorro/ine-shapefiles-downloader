"""
Verify Shapefile Data Integrity
================================

Check if shapefiles actually contain the correct state's geometry.
"""

import geopandas as gpd
from pathlib import Path

def check_shapefile_data(entidad_id: int, estado_name: str):
    """Check what data a shapefile actually contains."""
    print(f"\n{'=' * 70}")
    print(f"CHECKING: {estado_name} (Expected ENTIDAD: {entidad_id})")
    print(f"{'=' * 70}")
    
    geo_path = Path("data/geo")
    
    # Check PEEPJF
    peepjf_folders = list((geo_path / "shapefiles_peepjf").glob(f"{entidad_id}_*"))
    if peepjf_folders:
        folder = peepjf_folders[0]
        print(f"\n📁 PEEPJF Folder: {folder.name}")
        
        # Find SECCION.shp
        shp_files = list(folder.rglob("SECCION.shp"))
        if shp_files:
            shp_file = shp_files[0]
            print(f"   📍 File: {shp_file.relative_to(geo_path)}")
            
            gdf = gpd.read_file(shp_file)
            
            # Check ENTIDAD values
            if 'ENTIDAD' in gdf.columns:
                entidad_values = gdf['ENTIDAD'].unique()
                print(f"   🏷️  ENTIDAD in file: {entidad_values}")
                if len(entidad_values) == 1:
                    actual_entidad = int(entidad_values[0])
                    if actual_entidad == entidad_id:
                        print(f"   ✅ Correct! Data matches expected state")
                    else:
                        print(f"   ❌ WRONG! This is actually state {actual_entidad}'s data")
                        
                        # Map ID to name
                        estado_map = {
                            1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
                            9: "Ciudad de México", 26: "Sonora"
                        }
                        wrong_state = estado_map.get(actual_entidad, f"Estado {actual_entidad}")
                        print(f"   💡 This shapefile contains {wrong_state} geometry!")
            
            # Check geometry bounds
            bounds = gdf.total_bounds
            print(f"   📏 Bounds: {bounds}")
            print(f"   📊 Features: {len(gdf)}")
        else:
            print(f"   ❌ No SECCION.shp found")
    else:
        print(f"\n❌ No PEEPJF folder found")
    
    # Check Nacional
    nacional_folders = list((geo_path / "productos_ine_nacional").glob(f"{entidad_id}_*"))
    if nacional_folders:
        folder = nacional_folders[0]
        print(f"\n📁 Nacional Folder: {folder.name}")
        
        shp_files = list(folder.rglob("SECCION.shp"))
        if shp_files:
            shp_file = shp_files[0]
            print(f"   📍 File: {shp_file.relative_to(geo_path)}")
            
            gdf = gpd.read_file(shp_file)
            
            if 'ENTIDAD' in gdf.columns:
                entidad_values = gdf['ENTIDAD'].unique()
                print(f"   🏷️  ENTIDAD in file: {entidad_values}")
            
            bounds = gdf.total_bounds
            print(f"   📏 Bounds: {bounds}")
            print(f"   📊 Features: {len(gdf)}")
        else:
            print(f"   ❌ No SECCION.shp found")
    else:
        print(f"\n⚠️  No Nacional folder found")


if __name__ == "__main__":
    print("VERIFYING SHAPEFILE DATA INTEGRITY")
    print("=" * 70)
    
    # Check the problematic states
    check_shapefile_data(2, "Baja California")
    check_shapefile_data(9, "Ciudad de México")
    check_shapefile_data(26, "Sonora")
    
    print(f"\n{'=' * 70}")
    print("VERIFICATION COMPLETE")
    print(f"{'=' * 70}")
