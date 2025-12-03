import geopandas as gpd
import pandas as pd

# =========================
# Chemins d’entrée
# =========================
geojson_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_clean.geojson"
csv_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs_with_social.csv"

# =========================
# Charger GeoJSON
# =========================
gdf = gpd.read_file(geojson_path)
gdf["tile_id"] = gdf["tile_id"].astype(str)

# =========================
# Charger CSV social
# =========================
df = pd.read_csv(csv_path)
df["tile_id"] = df["tile_id"].astype(str)

# =========================
# Fusion sur tile_id
# =========================
merged = gdf.merge(
    df[["tile_id", "prop_elderly", "prop_low_income"]],
    on="tile_id",
    how="left"
)

# Remplacer NaN par 0
merged = merged.fillna(0)

# =========================
# Export GeoJSON enrichi
# =========================
out_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_social.geojson"
merged.to_file(out_path, driver="GeoJSON")

print("✔️ Nouveau GeoJSON créé :")
print(out_path)

print("Exemple :")
print(merged[["tile_id", "prop_elderly", "prop_low_income"]].head())
