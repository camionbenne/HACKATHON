import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import Point
from shapely import speedups
import math

# Activer les optimisations Shapely (si disponibles)
if speedups.available:
    speedups.enable()

# 1. Charger le shapefile LCZ
path = "/home/imane/HACKATHON/lcz_paris/LCZ_SPOT_2022_Paris.shp"
gdf = gpd.read_file(path)

# 2. Fusionner toutes les géométries en une seule (Paris entier)
merged = unary_union(gdf.geometry)

# 3. Calculer le centre géométrique (centroid)
center = merged.centroid
center_coords = (center.x, center.y)
print(" Centre géométrique de Paris (fichier LCZ) :", center_coords)

# 4. Calculer le rayon maximal : distance du centre au point le plus éloigné
max_radius = 0

for geom in gdf.geometry:
    # distance centre → géométrie
    dist = center.distance(geom)
    if dist > max_radius:
        max_radius = dist

print(f" Rayon maximal : {max_radius:.2f} mètres")

# 5. Exporter pour ton équipe (facultatif)
with open("paris_center_and_radius.txt", "w") as f:
    f.write(f"Center (X,Y): {center_coords}\n")
    f.write(f"Max radius (meters): {max_radius:.2f}\n")

print("\n Fichier exporté : paris_center_and_radius.txt")
