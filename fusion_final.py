import geopandas as gpd
import pandas as pd
from shapely import wkt
from tqdm import tqdm

tqdm.pandas()   # permet d'utiliser progress_apply

print("\n===== 0) Chargement du carroyage INSEE =====")
#---------------------------------------------
# 0. Charger les données population INSEE (carroyage)
#---------------------------------------------
insee_csv = "/home/imane/HACKATHON/data/insee/carroyage_insee_metro.csv"

insee = pd.read_csv(insee_csv)
insee["geometry"] = tqdm(insee["WKT"], desc="Conversion WKT -> géométrie").progress_apply(wkt.loads)
insee = gpd.GeoDataFrame(insee, geometry="geometry", crs="EPSG:4326")

print("Reprojection du carroyage INSEE…")
insee = insee.to_crs("EPSG:2154")

print("\n===== 1) Chargement LCZ + OSM =====")
#---------------------------------------------
# 1. Charger les couches LCZ + OSM
#---------------------------------------------
lcz = gpd.read_file("/home/imane/HACKATHON/lcz_paris/LCZ_SPOT_2022_Paris.shp")
natural = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_natural_a_free_1.shp")
water = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_water_a_free_1.shp")
landuse = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_landuse_a_free_1.shp")
pois = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_pois_a_free_1.shp")

print("\n===== 2) Reprojection des couches =====")
#---------------------------------------------
# 2. Reprojection en mètres (Lambert 93)
#---------------------------------------------
target_crs = "EPSG:2154"

for name, gdf in zip(
    ["LCZ", "natural", "water", "landuse", "pois"],
    [lcz, natural, water, landuse, pois]
):
    print(f"Reprojection {name}…")
    gdf.to_crs(target_crs, inplace=True)

print("\n===== 3) Filtrage OSM =====")
#---------------------------------------------
# 3. Filtrer les couches OSM utiles
#---------------------------------------------
print("Filtrage espaces verts…")
green = landuse[landuse["fclass"].isin([
    "park", "forest", "grass", "meadow", "scrub",
    "recreation_ground", "nature_reserve", "allotments"
])]

print("Filtrage natural green…")
natural_green = natural[natural["fclass"].isin([
    "tree", "wood", "forest", "grassland", "scrub", "beach"
])]

print("Fusion des zones vertes…")
all_green = gpd.GeoDataFrame(
    pd.concat([green, natural_green], ignore_index=True),
    crs=target_crs
)

print("Filtrage eau, hôpitaux, écoles…")
all_water = water
hospitals = pois[pois["fclass"].isin(["hospital", "clinic"])]
schools = pois[pois["fclass"].isin(["school", "kindergarten", "college", "university"])]

print("\n===== 4) Calcul centroïdes LCZ =====")
#---------------------------------------------
# 4. Centroïdes LCZ
#---------------------------------------------
lcz_centroids = lcz.copy()
lcz_centroids["geometry"] = lcz.geometry.centroid

print("\n===== 5) Distances =====")
#---------------------------------------------
# 5. Distances
#---------------------------------------------
def safe_union(gdf):
    return gdf.geometry.unary_union if len(gdf) > 0 else None

print("Fusion espaces verts…")
green_union = safe_union(all_green)
print("Fusion eau…")
water_union = safe_union(all_water)
print("Fusion hôpitaux…")
hospital_union = safe_union(hospitals)
print("Fusion écoles…")
school_union = safe_union(schools)

print("Calcul distance espace vert…")
lcz["dist_green_m"] = lcz_centroids.geometry.progress_apply(lambda g: g.distance(green_union))

print("Calcul distance eau…")
lcz["dist_water_m"] = lcz_centroids.geometry.progress_apply(lambda g: g.distance(water_union))

print("Calcul distance hôpital…")
lcz["dist_hospital_m"] = lcz_centroids.geometry.progress_apply(lambda g: g.distance(hospital_union))

print("Calcul distance école…")
lcz["dist_school_m"] = lcz_centroids.geometry.progress_apply(lambda g: g.distance(school_union))

print("\n===== 6) Intersection LCZ × INSEE =====")
#--------------------------------------------------------
# 6. Intersection LCZ × population INSEE
#--------------------------------------------------------
print("Intersection spatiale… (peut être long)")
lcz_pop = gpd.overlay(lcz, insee, how="intersection")

print("Calcul des ratios de surface…")
lcz_pop["area_ratio"] = lcz_pop.area / lcz_pop.geometry.area

print("\n===== 7) Calcul indicateurs population =====")
#--------------------------------------------------------
# 7. Calcul indicateurs démographiques
#--------------------------------------------------------

print("Calcul population âgée…")
lcz_pop["elderly"] = (
    lcz_pop["ind_age6"].fillna(0) +
    lcz_pop["ind_age7"].fillna(0)
) * lcz_pop["area_ratio"]

print("Calcul ménages bas revenus…")
lcz_pop["men_basr_weight"] = lcz_pop["men_basr"].fillna(0) * lcz_pop["area_ratio"]
lcz_pop["men_total_weight"] = lcz_pop["men"].fillna(0) * lcz_pop["area_ratio"]

print("\n===== 8) Agrégation par LCZ =====")
#---------------------------------------------
pop_stats = lcz_pop.groupby("lcz_int").agg({
    "elderly": "sum",
    "men_basr_weight": "sum",
    "men_total_weight": "sum"
}).reset_index()

pop_stats["prop_low_income"] = (
    pop_stats["men_basr_weight"] / pop_stats["men_total_weight"]
)

print("Fusion statistiques dans LCZ…")
lcz = lcz.merge(pop_stats, on="lcz_int", how="left")

print("\n===== 9) Export CSV WGS84 =====")
#---------------------------------------------
lcz_wgs = lcz.to_crs("EPSG:4326")
lcz_wgs["lon"] = lcz_wgs.geometry.centroid.x
lcz_wgs["lat"] = lcz_wgs.geometry.centroid.y

cols = [
    "lcz_int", "lon", "lat",
    "dist_green_m", "dist_water_m",
    "dist_hospital_m", "dist_school_m",
    "elderly", "prop_low_income"
]

lcz_wgs[cols].to_csv("data/LCZ_distance_population_metrics.csv", index=False)
print("CSV exporté")

print("\n===== 10) Export GeoJSON =====")
#---------------------------------------------
lcz.to_file("data/LCZ_distance_population_metrics.geojson", driver="GeoJSON")
print("GeoJSON exporté")

print("\n FINI ! Tout est exporté avec succès.")
