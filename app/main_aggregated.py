import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import pandas as pd


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(layout="wide")
st.title(" T'ICU social")

DATA_GEOJSON = "/home/imane/HACKATHON/data/grid_1km_lcz_distances_social.geojson"


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_resource
def load_data():
    return gpd.read_file(DATA_GEOJSON)

gdf = load_data()


# =========================================================
# LCZ RENAMED COLUMNS
# =========================================================
BUILT_COLS = [
    "Compact high-rise",
    "Compact mid-rise",
    "Compact low-rise",
    "Open high-rise",
    "Open mid-rise",
    "Open low-rise",
    "Large low-rise",
    "Sparsely built"
]

LAND_COLS = [
    "Dense trees",
    "Scattered trees",
    "Bush / scrub",
    "Low plants",
    "Bare soil or sand",
    "Bare rock or paved",
    "Water"
]

# =========================================================
# LCZ PALETTES
# =========================================================
BUILT_COLORS = {
    "Compact high-rise":  "#D7191C",
    "Compact mid-rise":   "#EF6548",
    "Compact low-rise":   "#FB9A99",
    "Open high-rise":     "#FDBF6F",
    "Open mid-rise":      "#FF7F00",
    "Open low-rise":      "#F6E8C3",
    "Large low-rise":     "#B2B2B2",
    "Sparsely built":     "#CCCCCC"
}

LAND_COLORS = {
    "Dense trees":       "#1A9850",
    "Scattered trees":   "#66BD63",
    "Bush / scrub":      "#A6D96A",
    "Low plants":        "#DDFF33",
    "Bare soil or sand": "#FEE08B",
    "Bare rock or paved":"#F6C65C",
    "Water":             "#3E8AC0"
}


# =========================================================
# SOCIAL COLUMNS (RENAMED)
# =========================================================
SOCIAL_COLS = [
    "Proportion elderly",
    "Proportion low income"
]


# =========================================================
# DISTANCE COLUMNS
# =========================================================
DISTANCE_COLS = [
    "Distance green area (m)",
    "Distance water (m)",
    "Distance school (m)",
    "Distance hospital (m)"
]


# =========================================================
# SIDEBAR (must be BEFORE any map)
# =========================================================
choice_lcz = st.sidebar.selectbox("Carte LCZ → Afficher :", ["Built type", "Land cover type"])
choice_dist = st.sidebar.selectbox("Carte distances → Afficher :", DISTANCE_COLS)
choice_social = st.sidebar.selectbox("Carte sociale → Afficher :", SOCIAL_COLS)


# =========================================================
# COLOR TOOLS
# =========================================================
def mix_colors(weighted_colors):
    rgb_sum = np.array([0.0, 0.0, 0.0])
    for w, hex_color in weighted_colors:
        rgb = np.array(mcolors.to_rgb(hex_color))
        rgb_sum += w * rgb
    return mcolors.to_hex(np.clip(rgb_sum, 0, 1))


def viridis_color(val, vmin, vmax):
    if vmin == vmax:
        return "#FFFFFF"
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("viridis")
    return mcolors.to_hex(cmap(norm(val)))


# =========================================================
# MAP 1 : LCZ
# =========================================================
m_lcz = leafmap.Map(center=[48.8566, 2.3522], zoom=10)

def style_lcz(feature):
    props = feature["properties"]

    if choice_lcz == "Built type":
        data_cols = BUILT_COLS
        colors = BUILT_COLORS
    else:
        data_cols = LAND_COLS
        colors = LAND_COLORS

    values = {name: props.get(name, 0) for name in data_cols}
    total = sum(values.values())

    if total == 0:
        return {"fillColor": "#FFFFFF", "color": "black", "weight": 0.2}

    weighted = [(v / total, colors[name]) for name, v in values.items() if v > 0]
    color = mix_colors(weighted)

    return {"fillColor": color, "color": "black", "weight": 0.2, "fillOpacity": 0.9}

m_lcz.add_geojson(gdf, layer_name="LCZ", style_function=style_lcz)


# =========================================================
# MAP 2 : Distance
# =========================================================
m_dist = leafmap.Map(center=[48.8566, 2.3522], zoom=10)

GREEN_THRESHOLD = 1000

if choice_dist == "Distance green area (m)":
    vmin = gdf[choice_dist].clip(upper=GREEN_THRESHOLD).min()
    vmax = gdf[choice_dist].clip(upper=GREEN_THRESHOLD).max()
else:
    vmin = gdf[choice_dist].min()
    vmax = gdf[choice_dist].max()

def style_distance(feature):
    val = feature["properties"].get(choice_dist, 0)

    if choice_dist == "Distance green area (m)" and val > GREEN_THRESHOLD:
        return {
            "fillColor": "#FFFFFF",
            "color": "black",
            "weight": 0.2,
            "fillOpacity": 0.8,
        }

    color = viridis_color(val, vmin, vmax)
    return {"fillColor": color, "color": "black", "weight": 0.2, "fillOpacity": 0.8}

m_dist.add_geojson(gdf, layer_name=choice_dist, style_function=style_distance)


# =========================================================
# MAP 3 : Social
# =========================================================
m_social = leafmap.Map(center=[48.8566, 2.3522], zoom=10)

vmin_s = gdf[choice_social].min()
vmax_s = gdf[choice_social].max()

def style_social(feature):
    val = feature["properties"].get(choice_social, 0)
    color = viridis_color(val, vmin_s, vmax_s)
    return {"fillColor": color, "color": "black", "weight": 0.2, "fillOpacity": 0.85}

m_social.add_geojson(gdf, layer_name=choice_social, style_function=style_social)


# =========================================================
# LAYOUT 3 MAPS
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🟥 Carte LCZ (built / land)")
    m_lcz.to_streamlit(height=700)

with col2:
    st.subheader(f"🟦 Carte Distance : {choice_dist}")
    m_dist.to_streamlit(height=700)

with col3:
    st.subheader(f"🟩 Carte Sociale : {choice_social}")
    m_social.to_streamlit(height=700)
