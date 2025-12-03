import geopandas as gpd
import pandas as pd

geojson = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_social.geojson"
csv     = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_with_vuln.csv"

gdf = gpd.read_file(geojson)
df  = pd.read_csv(csv)

gdf = gdf.merge(df[["tile_id", "vulnerability_index"]], on="tile_id", how="left")

out = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_vuln.geojson"
gdf.to_file(out, driver="GeoJSON")

print("✔ Fusion OK :", out)
