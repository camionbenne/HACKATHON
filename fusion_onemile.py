import geopandas as gpd
import pandas as pd
from shapely import wkt
from tqdm import tqdm

tqdm.pandas()   # active progress_apply()

#---------------------------------------------
# 0. Charger données INSEE
#---------------------------------------------
print("\n===== 0) Chargement du carroyage INSEE =====")

insee_csv = "/home/imane/HACKATHON/data/insee/carroyage_insee_metro.csv"
insee = pd.read_csv(insee_csv)

print("Conversion WKT -> géométrie…")
insee["geometry"] = insee["WKT"].progress_apply(
    lambda x: wkt.loads(x)
)

insee = gpd.GeoDataFrame(insee, geometry="geometry", crs="EPSG:4326")
insee = insee.to_crs("EPSG:2154")


# Indicateurs INSEE 200m
insee["elderly"] = insee["ind_age6"].fillna(0) + insee["ind_age7"].fillna(0)

agg_cols = {
    "ind_c": "sum",
    "elderly": "sum",
    "men": "sum",
    "men_basr": "sum"
}

print("\n===== 0c) Agrégation INSEE en grille 1 km =====")
insee_1km = insee.dissolve(by="idk", aggfunc=agg_cols).reset_index()

insee_1km["prop_low_income"] = (
    insee_1km["men_basr"] / insee_1km["men"].replace({0: pd.NA})
)

insee_1km = insee_1km.rename(columns={
    "ind_c": "pop_total",
    "elderly": "pop_elderly",
    "men": "men_total",
    "men_basr": "men_low_income"
})

#---------------------------------------------
# 1. Charger LCZ + OSM
#---------------------------------------------
print("\n===== 1) Chargement LCZ + OSM =====")

lcz = gpd.read_file("/home/imane/HACKATHON/lcz_paris/LCZ_SPOT_2022_Paris.shp")
natural = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_natural_a_free_1.shp")
water = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_water_a_free_1.shp")
landuse = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_landuse_a_free_1.shp")
pois = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_pois_a_free_1.shp")

print("\n===== 2) Reprojection en EPSG:2154 =====")
target_crs = "EPSG:2154"

for name, gdf in zip(
    ["LCZ", "natural", "water", "landuse", "pois"],
    [lcz, natural, water, landuse, pois]
):
    print(f"Reprojection {name}…")
    gdf.to_crs(target_crs, inplace=True)

#---------------------------------------------
# 3. Filtrage OSM (hôpitaux, écoles)
#---------------------------------------------
print("\n===== 3) Filtrage OSM =====")

hospitals = pois[pois["fclass"].isin(["hospital", "clinic"])].copy()
schools = pois[pois["fclass"].isin(["school", "kindergarten", "college"])].copy()

#---------------------------------------------
# 4. Proportion LCZ par carreau 1 km
#---------------------------------------------
print("\n===== 4) Proportion de LCZ par carreau 1 km =====")

grid = insee_1km[["idk", "geometry"]].copy()

print("Intersection grille × LCZ…")
grid_lcz = gpd.overlay(grid, lcz[["lcz_int", "geometry"]], how="intersection")

grid_lcz["area_intersect"] = grid_lcz.geometry.area
cell_area = grid.set_index("idk").geometry.area
grid_lcz["cell_area"] = grid_lcz["idk"].map(cell_area)
grid_lcz["prop_lcz"] = grid_lcz["area_intersect"] / grid_lcz["cell_area"]

print("Pivot large…")
pivot = grid_lcz.pivot_table(
    index="idk",
    columns="lcz_int",
    values="prop_lcz",
    aggfunc="sum",
    fill_value=0.0
)

pivot.columns = [f"prop_lcz_{int(c)}" for c in pivot.columns]
pivot = pivot.reset_index()

grid = grid.merge(pivot, on="idk", how="left")
lcz_cols = [c for c in grid.columns if c.startswith("prop_lcz_")]
grid[lcz_cols] = grid[lcz_cols].fillna(0)

#---------------------------------------------
# 5. Présence binaire (1/0) hôpital / école
#---------------------------------------------
print("\n===== 5) Présence hôpital / école (binaire) =====")

hospitals = hospitals.to_crs("EPSG:2154")
schools = schools.to_crs("EPSG:2154")

# Spatial index for speed
hospitals_sindex = hospitals.sindex
schools_sindex = schools.sindex

print("Jointure spatiale carreaux × hôpitaux…")
join_hosp = gpd.sjoin(grid, hospitals, how="left", predicate="intersects")
grid["has_hospital"] = (join_hosp["index_right"].notna()).astype(int)

print("Jointure spatiale carreaux × écoles…")
join_school = gpd.sjoin(grid, schools, how="left", predicate="intersects")
grid["has_school"] = (join_school["index_right"].notna()).astype(int)

#---------------------------------------------
# 6. Fusion grille 1 km + INSEE
#---------------------------------------------
print("\n===== 6) Fusion grille 1 km + INSEE =====")

grid = grid.merge(
    insee_1km[
        ["idk", "pop_total", "pop_elderly",
         "men_total", "men_low_income", "prop_low_income"]
    ],
    on="idk",
    how="left"
)

#---------------------------------------------
# 7. Export
#---------------------------------------------
print("\n===== 7) Export =====")

# CSV avec centroïde en WGS84
grid_wgs = grid.to_crs("EPSG:4326")
grid_wgs["lon"] = grid_wgs.geometry.centroid.x
grid_wgs["lat"] = grid_wgs.geometry.centroid.y

cols_csv = (
    ["idk", "lon", "lat",
     "has_hospital", "has_school",
     "pop_total", "pop_elderly",
     "men_total", "men_low_income", "prop_low_income"]
    + lcz_cols
)

grid_wgs[cols_csv].to_csv(
    "data/grid_1km_lcz_insee_binary.csv", index=False
)
print("CSV exporté : data/grid_1km_lcz_insee_binary.csv")

grid.to_file(
    "data/grid_1km_lcz_insee_binary.geojson", driver="GeoJSON"
)
print("GeoJSON exporté : data/grid_1km_lcz_insee_binary.geojson")

print("\n FINI ! Grille 1 km binaire générée.")
