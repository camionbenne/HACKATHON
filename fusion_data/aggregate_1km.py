import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
import numpy as np

# ----------------------------------------------------------
# 1) Charger le CSV de points
# ----------------------------------------------------------

csv_path = "/home/imane/HACKATHON/data/LCZ_distance_all_metrics_wgs.csv"

df = pd.read_csv(csv_path)

# Construire géométrie en WGS84
gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df["lon"], df["lat"])],
    crs="EPSG:4326"
)

# Passer en Lambert 93 pour un carroyage 1 km réel
gdf = gdf.to_crs("EPSG:2154")

# Extraire les coordonnées projetées
gdf["x"] = gdf.geometry.x
gdf["y"] = gdf.geometry.y


# ----------------------------------------------------------
# 2) Construire identifiant de carreau 1 km
# ----------------------------------------------------------
# Exemple : carreau 1km = plancher(x/1000)*1000

gdf["x_km"] = (gdf["x"] // 1000).astype(int)
gdf["y_km"] = (gdf["y"] // 1000).astype(int)

gdf["tile_id"] = gdf["x_km"].astype(str) + "_" + gdf["y_km"].astype(str)


# ----------------------------------------------------------
# 3) Agrégation LCZ : compter puis normaliser en proportion
# ----------------------------------------------------------

# Comptage LCZ par carreau
lcz_counts = (
    gdf.pivot_table(
        index="tile_id",
        columns="lcz_int",
        values="lon",  # n'importe quelle colonne non nulle
        aggfunc="count",
        fill_value=0
    )
)

# Renommer les colonnes : prop_lcz_1, prop_lcz_2, ...
lcz_counts.columns = [f"count_lcz_{int(c)}" for c in lcz_counts.columns]

# Calculer proportions
lcz_prop = lcz_counts.div(lcz_counts.sum(axis=1), axis=0)
lcz_prop.columns = [c.replace("count_", "prop_") for c in lcz_prop.columns]


# ----------------------------------------------------------
# 4) Moyennes des distances par carreau
# ----------------------------------------------------------

dist_cols = ["dist_green_m", "dist_water_m", "dist_hospital_m", "dist_school_m"]

dist_means = (
    gdf.groupby("tile_id")[dist_cols]
    .mean()
    .rename(columns=lambda c: c + "_mean")
)


# ----------------------------------------------------------
# 5) Calcul bounding box du carreau 1 km
# ----------------------------------------------------------

bbox_df = (
    gdf.groupby("tile_id")[["x_km", "y_km"]]
    .first()
    .reset_index()
)

bbox_df["x_min"] = bbox_df["x_km"] * 1000
bbox_df["x_max"] = bbox_df["x_min"] + 1000
bbox_df["y_min"] = bbox_df["y_km"] * 1000
bbox_df["y_max"] = bbox_df["y_min"] + 1000

# Construire la géométrie du carreau
bbox_df["geometry"] = bbox_df.apply(
    lambda r: box(r["x_min"], r["y_min"], r["x_max"], r["y_max"]),
    axis=1
)
bbox_gdf = gpd.GeoDataFrame(bbox_df, geometry="geometry", crs="EPSG:2154")


# ----------------------------------------------------------
# 6) Fusion finale : bbox + LCZ proportions + distances moyennes
# ----------------------------------------------------------

final = (
    bbox_gdf
    .set_index("tile_id")
    .join(lcz_prop, how="left")
    .join(dist_means, how="left")
)

# Remplir NaN par 0 pour proportions
for col in final.columns:
    if col.startswith("prop_lcz_"):
        final[col] = final[col].fillna(0)


# ----------------------------------------------------------
# 7) Export : GeoJSON + CSV WGS84 + CSV Lambert
# ----------------------------------------------------------

# Lambert 93
final.to_file(
    "/home/imane/HACKATHON/data/grid_1km_lcz_distances.geojson",
    driver="GeoJSON"
)

# Version CSV Lambert
final.to_csv(
    "/home/imane/HACKATHON/data/grid_1km_lcz_distances_lambert.csv"
)

# Version CSV WGS84 (centroïdes)
final_wgs = final.to_crs("EPSG:4326")
final_wgs["lon"] = final_wgs.geometry.centroid.x
final_wgs["lat"] = final_wgs.geometry.centroid.y

final_wgs.drop(columns="geometry").to_csv(
    "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs.csv"
)


print(" Grille 1 km générée !")
print(final.head())
