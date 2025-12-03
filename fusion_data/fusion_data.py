import geopandas as gpd
import pandas as pd
#---------------------------------------------
# 1. Charger les couches
#---------------------------------------------
lcz = gpd.read_file("/home/imane/HACKATHON/lcz_paris/LCZ_SPOT_2022_Paris.shp")
natural = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_natural_a_free_1.shp")
water = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_water_a_free_1.shp")
landuse = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_landuse_a_free_1.shp")
pois = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_pois_a_free_1.shp")

#---------------------------------------------
# 2. Reprojection en mètres (Lambert 93)
#---------------------------------------------
target_crs = "EPSG:2154"

lcz = lcz.to_crs(target_crs)
natural = natural.to_crs(target_crs)
water = water.to_crs(target_crs)
landuse = landuse.to_crs(target_crs)
pois = pois.to_crs(target_crs)

#---------------------------------------------
# 3. Filtrer les couches OSM utiles
#---------------------------------------------

# Zones de verdure : parc, forêt, gazon, nature
green = landuse[landuse["fclass"].isin([
    "park", "forest", "grass", "meadow", "scrub",
    "recreation_ground", "nature_reserve", "allotments"
])]

# alternative : natural_a contient aussi bois/beach/peak/etc.
# tu peux garder les arbres isolés aussi :
natural_green = natural[natural["fclass"].isin([
    "tree", "wood", "forest", "grassland", "scrub", "beach"
])]

# On fusionne toute la verdure potentielle
all_green = gpd.GeoDataFrame(
    pd.concat([green, natural_green], ignore_index=True),
    crs=target_crs
)

# Eau
all_water = water 

# Hôpitaux
hospitals = pois[pois["fclass"].isin(["hospital", "clinic"])]

# Écoles
schools = pois[pois["fclass"].isin(["school", "kindergarten", "college", "university"])]

#---------------------------------------------
# 4. Préparer centroïdes LCZ
#---------------------------------------------
lcz_centroids = lcz.copy()
lcz_centroids["geometry"] = lcz.geometry.centroid

#---------------------------------------------
# 5. Calcul des distances
#---------------------------------------------

# Si une couche est vide, éviter erreurs
def safe_union(gdf):
    return gdf.geometry.unary_union if len(gdf) > 0 else None

green_union = safe_union(all_green)
water_union = safe_union(all_water)
hospital_union = safe_union(hospitals)
school_union = safe_union(schools)

# Distance aux espaces verts
lcz["dist_green_m"] = (
    lcz_centroids.distance(green_union) if green_union else None
)

# Distance à l’eau
lcz["dist_water_m"] = (
    lcz_centroids.distance(water_union) if water_union else None
)

# Distance au centre médical le plus proche
lcz["dist_hospital_m"] = (
    lcz_centroids.distance(hospital_union) if hospital_union else None
)

# Distance à une école
lcz["dist_school_m"] = (
    lcz_centroids.distance(school_union) if school_union else None
)

#---------------------------------------------
# 6. Export CSV avec latitude/longitude
#---------------------------------------------
lcz_wgs = lcz.to_crs("EPSG:4326")
lcz_wgs["lon"] = lcz_wgs.geometry.centroid.x
lcz_wgs["lat"] = lcz_wgs.geometry.centroid.y

cols = [
    "lcz_int", "lon", "lat",
    "dist_green_m", "dist_water_m",
    "dist_hospital_m", "dist_school_m"
]

lcz_wgs[cols].to_csv("data/LCZ_distance_all_metrics_wgs.csv", index=False)

print("CSV exporté : data/LCZ_distance_all_metrics_wgs.csv")

#---------------------------------------------
# 7. Export GeoJSON complet avec géométrie
#---------------------------------------------
lcz.to_file("data/LCZ_distance_all_metrics.geojson", driver="GeoJSON")

print("GeoJSON exporté : data/LCZ_distance_all_metrics.geojson")
