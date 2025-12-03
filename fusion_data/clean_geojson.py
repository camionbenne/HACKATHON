import geopandas as gpd

PATH_IN  = "/home/imane/HACKATHON/data/grid_1km_lcz_distances.geojson"
PATH_OUT = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_clean.geojson"

gdf = gpd.read_file(PATH_IN)

# --- Dictionnaire renaming LCZ ---
LCZ_RENAME = {
    "prop_lcz_1":  "Compact high-rise",
    "prop_lcz_2":  "Compact mid-rise",
    "prop_lcz_3":  "Compact low-rise",
    "prop_lcz_4":  "Open high-rise",
    "prop_lcz_5":  "Open mid-rise",
    "prop_lcz_6":  "Open low-rise",
    "prop_lcz_8":  "Large low-rise",
    "prop_lcz_9":  "Sparsely built",
    "prop_lcz_11": "Dense trees",
    "prop_lcz_12": "Scattered trees",
    "prop_lcz_13": "Bush / scrub",
    "prop_lcz_14": "Low plants",
    "prop_lcz_15": "Bare soil or sand",
    "prop_lcz_16": "Bare rock or paved",
    "prop_lcz_17": "Water"
}

# --- Dictionnaire distances ---
DIST_RENAME = {
    "dist_green_m_mean":    "Distance green area (m)",
    "dist_water_m_mean":    "Distance water (m)",
    "dist_hospital_m_mean": "Distance hospital (m)",
    "dist_school_m_mean":   "Distance school (m)",
}

# --- Fusion des deux dictionnaires ---
RENAME = {}
RENAME.update(LCZ_RENAME)
RENAME.update(DIST_RENAME)

# --- Renommer réellement ---
gdf = gdf.rename(columns=RENAME)

# --- Vérification ---
print("\n===== NOUVELLES COLONNES =====")
for col in gdf.columns:
    print(col)

# --- Sauvegarde ---
gdf.to_file(PATH_OUT, driver="GeoJSON")

print("\n✔ Nouveau fichier sauvegardé :")
print(PATH_OUT)

