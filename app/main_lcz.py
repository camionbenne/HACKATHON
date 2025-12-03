import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import leafmap.foliumap as leafmap
import matplotlib.cm as cm
import matplotlib.colors as colors

st.set_page_config(layout="wide")
st.title("🌍 Carte LCZ & distances")

DATA_CSV = "/home/imane/HACKATHON/data/LCZ_distance_all_metrics_wgs.csv"


# ----------------------------------------------------------
# Viridis color for numeric attributes
# ----------------------------------------------------------

def viridis_color(value, vmin, vmax):
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("viridis")
    rgba = cmap(norm(value))
    return colors.to_hex(rgba)


# ----------------------------------------------------------
# Load CSV as points GeoDataFrame
# ----------------------------------------------------------

@st.cache_resource
def load_data():
    df = pd.read_csv(DATA_CSV)
    geometry = [Point(xy) for xy in zip(df["lon"], df["lat"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf

gdf = load_data()


# ----------------------------------------------------------
# Select column
# ----------------------------------------------------------

cols = [c for c in gdf.columns if c not in ["lon", "lat"]]
selected_col = st.sidebar.selectbox("Choisir la colonne :", cols)


# ----------------------------------------------------------
# Create map
# ----------------------------------------------------------

m = leafmap.Map(center=[48.8566, 2.3522], zoom=10)

# LCZ palette
LCZ_COLORS = {
    1: "#8b0000", 2: "#b22222", 3: "#dc143c", 4: "#ff4500",
    5: "#ff8c00", 6: "#ffa500", 7: "#deb887", 8: "#808080",
    9: "#d3d3d3", 10: "#696969", 11: "#006400", 12: "#228b22",
    13: "#7cfc00", 14: "#adff2f", 15: "#f5deb3", 16: "#c0c0c0",
    17: "#1e90ff"
}


# ----------------------------------------------------------
# Add points with correct color
# ----------------------------------------------------------

# We build a temporary gdf with style information
plot_gdf = gdf.copy()

if selected_col == "lcz_int":
    plot_gdf["color"] = plot_gdf["lcz_int"].map(LCZ_COLORS)
else:
    vmin = plot_gdf[selected_col].min()
    vmax = plot_gdf[selected_col].max()
    plot_gdf["color"] = plot_gdf[selected_col].apply(lambda v: viridis_color(v, vmin, vmax))


# add_points_from_xy expects a color column for marker and popup text
m.add_points_from_xy(
    plot_gdf,
    x="lon",
    y="lat",
    color="color",
    popup=[selected_col]   # <-- IMPORTANT !!
)



# ----------------------------------------------------------
# Display map
# ----------------------------------------------------------

m.to_streamlit(height=720)
