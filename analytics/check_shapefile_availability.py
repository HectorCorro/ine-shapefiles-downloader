"""
Shapefile Availability Checker
===============================

Check which states have valid SECCION.shp files in nacional and peepjf directories.
"""

from pathlib import Path
import sys

# State mapping
ESTADOS = {
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas"
}

def find_seccion_shp(base_path: Path) -> Path:
    """Recursively find SECCION.shp in directory."""
    if not base_path.exists():
        return None
    
    # Try direct path
    direct_path = base_path / 'SECCION.shp'
    if direct_path.exists():
        return direct_path
    
    # Search in subdirectories (max 2 levels deep)
    for subdir in base_path.rglob('SECCION.shp'):
        # Only go 2 levels deep
        if len(subdir.relative_to(base_path).parts) <= 3:
            return subdir
    
    return None


def check_shapefile_availability():
    """Check shapefile availability for all states."""
    
    project_root = Path(__file__).parent.parent
    geo_path = project_root / 'data' / 'geo'
    
    if not geo_path.exists():
        print(f"❌ Geo data directory not found: {geo_path}")
        return
    
    nacional_base = geo_path / 'productos_ine_nacional'
    peepjf_base = geo_path / 'shapefiles_peepjf'
    
    print("=" * 80)
    print("SHAPEFILE AVAILABILITY CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    for entidad_id in range(1, 33):
        estado_name = ESTADOS.get(entidad_id, f"Estado {entidad_id}")
        
        # Check nacional
        nacional_folder_patterns = [
            f"{entidad_id}_" + estado_name.replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u"),
            f"{entidad_id}_{estado_name}",
        ]
        
        nacional_found = False
        nacional_path = None
        
        if nacional_base.exists():
            for folder in nacional_base.iterdir():
                if folder.is_dir() and folder.name.startswith(f"{entidad_id}_"):
                    shapefile = find_seccion_shp(folder / 'Shapefile')
                    if shapefile:
                        nacional_found = True
                        nacional_path = shapefile
                        break
        
        # Check peepjf
        peepjf_found = False
        peepjf_path = None
        
        if peepjf_base.exists():
            for folder in peepjf_base.iterdir():
                if folder.is_dir() and folder.name.startswith(f"{entidad_id}_"):
                    shapefile = find_seccion_shp(folder)
                    if shapefile:
                        peepjf_found = True
                        peepjf_path = shapefile
                        break
        
        # Status
        status = ""
        if nacional_found and peepjf_found:
            status = "✅✅ Both"
        elif nacional_found:
            status = "✅ Nacional only"
        elif peepjf_found:
            status = "✅ PEEPJF only"
        else:
            status = "❌ Neither"
        
        results.append({
            'id': entidad_id,
            'name': estado_name,
            'status': status,
            'nacional': nacional_found,
            'peepjf': peepjf_found,
            'nacional_path': nacional_path,
            'peepjf_path': peepjf_path
        })
        
        # Print detailed info
        print(f"{entidad_id:2d}. {estado_name:25s} {status}")
        if nacional_found and nacional_path:
            print(f"    📍 Nacional: {nacional_path.relative_to(geo_path)}")
        if peepjf_found and peepjf_path:
            print(f"    📍 PEEPJF:   {peepjf_path.relative_to(geo_path)}")
        if not nacional_found and not peepjf_found:
            print(f"    ⚠️  No SECCION.shp found for this state")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    both = sum(1 for r in results if r['nacional'] and r['peepjf'])
    nacional_only = sum(1 for r in results if r['nacional'] and not r['peepjf'])
    peepjf_only = sum(1 for r in results if not r['nacional'] and r['peepjf'])
    neither = sum(1 for r in results if not r['nacional'] and not r['peepjf'])
    
    print(f"✅ Both available:      {both}/32")
    print(f"📊 Nacional only:       {nacional_only}/32")
    print(f"📊 PEEPJF only:         {peepjf_only}/32")
    print(f"❌ Neither available:   {neither}/32")
    print()
    
    if neither > 0:
        print("⚠️  States with NO shapefiles:")
        for r in results:
            if not r['nacional'] and not r['peepjf']:
                print(f"   - {r['name']} (ID: {r['id']})")
        print()
        print("💡 To fix: Download shapefiles for these states")
    
    print("=" * 80)


if __name__ == "__main__":
    check_shapefile_availability()
