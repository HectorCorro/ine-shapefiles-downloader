"""
Folium Multi-layer Visualization for Electoral Shapefiles
Generates an interactive HTML map with multiple geographic layers
"""
import geopandas as gpd
import folium
from pathlib import Path
import os

# Get project root (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "geo" / "shapefiles_peepjf"

# Diccionario de shapefiles
shapefiles = {
    "Entidades": DATA_DIR / "1_Aguascalientes/01/ENTIDAD.shp",
    "Distrito_Federal": DATA_DIR / "1_Aguascalientes/01/DISTRITO_FEDERAL.shp",
    "Distrito_Local": DATA_DIR / "1_Aguascalientes/01/DISTRITO_LOCAL.shp",
    "Municipios": DATA_DIR / "1_Aguascalientes/01/MUNICIPIO.shp",
    "Secciones": DATA_DIR / "1_Aguascalientes/01/SECCION.shp"
}

# Crear mapa base centrado en Aguascalientes
mapa = folium.Map(
    location=[21.88, -102.30],
    zoom_start=8,
    tiles='OpenStreetMap'
)

# Colores para cada capa
colors = {
    "Entidades": "red",
    "Distrito_Federal": "blue",
    "Distrito_Local": "green",
    "Municipios": "purple",
    "Secciones": "orange"
}

for layer_name, path in shapefiles.items():
    print(f"📥 Leyendo {layer_name} desde {path}")

    try:
        # Verificar si el archivo existe
        if not os.path.exists(path):
            print(f"⚠️  Archivo no encontrado: {path}")
            continue

        # Leer shapefile
        gdf = gpd.read_file(path)

        if gdf.empty or gdf.geometry.notnull().sum() == 0:
            print(f"⚡ {layer_name} vacío o sin geometría, se omite.")
            continue

        # Convertir CRS a WGS84 para Folium
        gdf = gdf.to_crs(epsg=4326)

        # Crear FeatureGroup para control de capas
        feature_group = folium.FeatureGroup(name=layer_name)

        # Agregar GeoJson con estilo y tooltip
        folium.GeoJson(
            gdf,
            name=layer_name,
            style_function=lambda x, color=colors.get(layer_name, "gray"): {
                'fillColor': color,
                'color': color,
                'weight': 2,
                'fillOpacity': 0.1,
                'opacity': 0.6
            },
            highlight_function=lambda x: {
                'weight': 4,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=list(gdf.columns[gdf.columns != 'geometry'])[:5],  # Primeros 5 campos
                aliases=[str(col) for col in gdf.columns[gdf.columns != 'geometry'][:5]],
                localize=True
            )
        ).add_to(feature_group)

        feature_group.add_to(mapa)
        print(f"✅ {layer_name} agregado al mapa con color {colors.get(layer_name, 'gray')}.")
    
    except Exception as e:
        print(f"❌ Error cargando {layer_name}: {e}")

# Agregar control de capas
folium.LayerControl(collapsed=False).add_to(mapa)

# Agregar minimap
from folium.plugins import MiniMap
MiniMap(toggle_display=True).add_to(mapa)

# Guardar como HTML
output_file = PROJECT_ROOT / "folium_multilayer_map.html"
mapa.save(output_file)

print(f"\n✅ Mapa guardado en {output_file}")
print(f"📂 Abre el archivo en tu navegador para ver el resultado interactivo.")