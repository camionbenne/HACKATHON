import geopandas as gpd
import pandas as pd
from shapely import wkt
from tqdm import tqdm

tqdm.pandas()

#---------------------------------------------
# 0. Charger données INSEE (200 m) puis aggréger 1 km
#---------------------------------------------
print("\n===== 0) Chargement du carroyage INSEE =====")

insee_csv = "/home/imane/HACKATHON/data/insee/carroyage_insee_metro.csv"
insee = pd.read_csv(insee_csv)

print("Conversion WKT -> géométrie…")
insee["geometry"] = insee["WKT"].progress_apply(wkt.loads)
insee = gpd.GeoDataFrame(insee, geometry="geometry", crs="EPSG:4326")
insee = insee.to_crs("EPSG:2154")

# Indicateurs INSEE par carreau 200 m
insee["elderly"] = insee["ind_age6"].fillna(0) + insee["ind_age7"].fillna(0)

agg_cols = {
    "ind_c": "sum",
    "elderly": "sum",
    "men": "sum",
    "men_basr": "sum"
}

print("\n===== 0c) Agrégation INSEE en grille 1 km via idk =====")
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

print(f"Carreaux 1 km générés : {len(insee_1km)}")

#---------------------------------------------
# 1. Charger LCZ + OSM
#---------------------------------------------
print("\n===== 1) Chargement LCZ + OSM =====")

lcz = gpd.read_file("/home/imane/HACKATHON/lcz_paris/LCZ_SPOT_2022_Paris.shp").to_crs("EPSG:2154")
pois = gpd.read_file("/home/imane/HACKATHON/data/gis_osm_pois_a_free_1.shp").to_crs("EPSG:2154")

#---------------------------------------------
# 3. Filtrage OSM (hôpital / école)
#---------------------------------------------
print("\n===== 3) Filtrage OSM =====")

hospitals = pois[pois["fclass"].isin(["hospital", "clinic"])]
schools   = pois[pois["fclass"].isin(["school", "kindergarten", "college", "university"])]

#---------------------------------------------
# 4. Proportion LCZ par carreau 1 km
#---------------------------------------------
print("\n===== 4) Intersection grille 1 km × LCZ =====")

grid = insee_1km[["idk", "geometry"]].copy()

grid_lcz = gpd.overlay(
    grid,
    lcz[["lcz_int", "geometry"]],
    how="intersection"
)

print("Calcul des surfaces…")
grid_lcz["area_intersect"] = grid_lcz.geometry.area
cell_area = grid.set_index("idk").geometry.area
grid_lcz["cell_area"] = grid_lcz["idk"].map(cell_area)
grid_lcz["prop_lcz"] = grid_lcz["area_intersect"] / grid_lcz["cell_area"]

print("Pivot table LCZ → colonnes prop_lcz_X…")
pivot = (
    grid_lcz.pivot_table(
        index="idk",
        columns="lcz_int",
        values="prop_lcz",
        aggfunc="sum",
        fill_value=0.0
    )
).reset_index()

pivot.columns = ["idk"] + [f"prop_lcz_{int(c)}" for c in pivot.columns[1:]]

grid = grid.merge(pivot, on="idk", how="left").fillna(0)
lcz_cols = [c for c in grid.columns if c.startswith("prop_lcz_")]

#---------------------------------------------
# 5. Présence binaire hôpital / école
#---------------------------------------------
print("\n===== 5) Présence hôpital / école =====")

print("Jointure hôpitaux…")
join_hosp = gpd.sjoin(grid, hospitals, how="left", predicate="intersects")
grid["has_hospital"] = (join_hosp["index_right"].notna()).astype(int)

print("Jointure écoles…")
join_school = gpd.sjoin(grid, schools, how="left", predicate="intersects")
grid["has_school"] = (join_school["index_right"].notna()).astype(int)

#---------------------------------------------
# 6. Fusion grille 1 km + INSEE
#---------------------------------------------
print("\n===== 6) Fusion avec INSEE =====")

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

grid_wgs = grid.to_crs("EPSG:4326")
grid_wgs["lon"] = grid_wgs.geometry.centroid.x
grid_wgs["lat"] = grid_wgs.geometry.centroid.y

cols_csv = [
    "idk", "lon", "lat",
    "has_hospital", "has_school",
    "pop_total", "pop_elderly",
    "men_total", "men_low_income", "prop_low_income"
] + lcz_cols

grid_wgs[cols_csv].to_csv(
    "/home/imane/HACKATHON/data/grid_1km_lcz_insee_binary.csv",
    index=False
)

print("CSV exporté.")

grid.to_file(
    "/home/imane/HACKATHON/data/grid_1km_lcz_insee_binary.geojson",
    driver="GeoJSON"
)

print("GeoJSON exporté.")
print("\n FINI ! Grille 1 km complète générée.")
