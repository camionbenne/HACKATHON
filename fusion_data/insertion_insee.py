import pandas as pd
import geopandas as gpd
from shapely import wkt

# ================================
# 1) Charger LCZ + distances
# ================================
grid_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs.csv"
grid = pd.read_csv(grid_path)
grid["tile_id"] = grid["tile_id"].astype(str)

# ================================
# 2) Charger INSEE avec WKT
# ================================
insee_path = "/home/imane/HACKATHON/data/insee/carroyage_insee_metro.csv"
insee = pd.read_csv(insee_path)

# Convertir WKT -> géométrie
insee["geometry"] = insee["WKT"].apply(wkt.loads)
insee = gpd.GeoDataFrame(insee, geometry="geometry", crs=4326)

# Passer en Lambert 93 (EPSG:2154), comme ton LCZ
insee = insee.to_crs(2154)

# ================================
# 3) Calcul tile_id INSEE à 1 km
# ================================
insee["centroid"] = insee.geometry.centroid
insee["x"] = insee["centroid"].x
insee["y"] = insee["centroid"].y

insee["x_km"] = (insee["x"] // 1000).astype(int)
insee["y_km"] = (insee["y"] // 1000).astype(int)

insee["tile_id"] = insee["x_km"].astype(str) + "_" + insee["y_km"].astype(str)

# ================================
# 4) Indicateurs sociaux
# ================================
insee["elderly"] = insee["ind_age6"].fillna(0) + insee["ind_age7"].fillna(0)

agg = (
    insee.groupby("tile_id")
    .agg({
        "ind_c": "sum",
        "elderly": "sum",
        "men": "sum",
        "men_basr": "sum"
    })
    .reset_index()
)

agg["prop_elderly"] = agg["elderly"] / agg["ind_c"].replace({0: pd.NA})
agg["prop_low_income"] = agg["men_basr"] / agg["men"].replace({0: pd.NA})
agg = agg.fillna(0)

# ================================
# 5) Merge avec fichiers LCZ
# ================================
merged = grid.merge(
    agg[["tile_id", "prop_elderly", "prop_low_income"]],
    on="tile_id",
    how="left"
).fillna(0)

# ================================
# 6) Export
# ================================
out = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs_with_social.csv"
merged.to_csv(out, index=False)

print("\n✔ Social enrichment done!")
print("Fichier exporté :", out)
print(merged[["tile_id", "prop_elderly", "prop_low_income"]].head())
