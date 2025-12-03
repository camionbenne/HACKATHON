import geopandas as gpd
import matplotlib.pyplot as plt

# ------------------------------------------
# 1) Charger ton GeoJSON avec vulnérabilité
# ------------------------------------------
geojson = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_vuln.geojson"
gdf = gpd.read_file(geojson)

if "vulnerability_index" not in gdf.columns:
    raise ValueError(" La colonne 'vulnerability_index' n'existe pas dans le GeoJSON !")

# ------------------------------------------
# 2) Carte rouge → vert
# ------------------------------------------
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

gdf.plot(
    column="vulnerability_index",
    cmap="RdYlGn_r",     
    linewidth=0,
    edgecolor="none",
    legend=True,
    ax=ax
)

ax.set_title("Vulnerability Index (Rouge → Vert)", fontsize=15)
ax.axis("off")

# ------------------------------------------
# 3) Sauvegarde
# ------------------------------------------
output_path = "/home/imane/HACKATHON/indicator/vulnerability_map.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print("✔ Carte enregistrée :", output_path)
