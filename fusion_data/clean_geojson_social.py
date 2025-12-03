import geopandas as gpd
import pandas as pd

# =========================
# Chemins d’entrée
# =========================
geojson_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_clean.geojson"
csv_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_wgs_with_social.csv"

# =========================
# 1) Charger GeoJSON
# =========================
gdf = gpd.read_file(geojson_path)
gdf["tile_id"] = gdf["tile_id"].astype(str)

# Supprimer anciennes colonnes si présentes
for col in ["Proportion elderly", "Proportion low income"]:
    if col in gdf.columns:
        gdf = gdf.drop(columns=[col])

# =========================
# 2) Charger CSV social
# =========================
df = pd.read_csv(csv_path)
df["tile_id"] = df["tile_id"].astype(str)

# Colonnes sociales
df_social = df[["tile_id", "prop_elderly", "prop_low_income"]].copy()

# Renommer proprement SANS %
df_social = df_social.rename(columns={
    "prop_elderly": "Proportion elderly",
    "prop_low_income": "Proportion low income"
})

# =========================
# 3) Fusion propre
# =========================
merged = gdf.merge(df_social, on="tile_id", how="left")

# Remplacer NaN par 0
merged[["Proportion elderly", "Proportion low income"]] = \
    merged[["Proportion elderly", "Proportion low income"]].fillna(0)

# =========================
# 4) Export GeoJSON mis à jour
# =========================
out_path = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_social.geojson"
merged.to_file(out_path, driver="GeoJSON")

print("✔️ Nouveau GeoJSON créé :", out_path)
print("\nAperçu des colonnes sociales :")
print(merged[["tile_id", "Proportion elderly", "Proportion low income"]].head())
