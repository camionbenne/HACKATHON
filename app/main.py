import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

# ----------------------------------------------------------
# 1. Configuration de l'app
# ----------------------------------------------------------

st.set_page_config(layout="wide")
st.title("🌍 Carte dynamique – Grille 1 km LCZ / INSEE / OSM")


# ----------------------------------------------------------
# 2. Charger les données
# ----------------------------------------------------------

@st.cache_resource
def load_data():
    path = "/home/imane/HACKATHON/data/grid_1km_lcz_insee_binary.geojson"
    gdf = gpd.read_file(path)
    return gdf

gdf = load_data()


# ----------------------------------------------------------
# 3. Liste des colonnes quantitatives ou binaires
# ----------------------------------------------------------

numeric_cols = [
    col for col in gdf.columns
    if gdf[col].dtype in ["int64", "float64"]
    and col not in ["lon", "lat"]
]

st.sidebar.header("Options")
selected_col = st.sidebar.selectbox("Choisir la colonne à afficher :", numeric_cols)


# ----------------------------------------------------------
# 4. Création de la carte Leafmap
# ----------------------------------------------------------

st.sidebar.write(f"Colonne sélectionnée : **{selected_col}**")

m = leafmap.Map(center=[48.8566, 2.3522], zoom=10)


# ----------------------------------------------------------
# 5. Ajout du GeoJSON coloré selon la colonne
# ----------------------------------------------------------

m.add_geojson(
    data=gdf,
    layer_name=selected_col,
    style_function=lambda feature: {
        "fillColor": leafmap.legend_colormap(
            value=feature["properties"][selected_col],
            vmin=gdf[selected_col].min(),
            vmax=gdf[selected_col].max(),
            cmap="viridis"
        ),
        "color": "black",
        "weight": 0.2,
        "fillOpacity": 0.8,
    },
)


# ----------------------------------------------------------
# 6. Affichage
# ----------------------------------------------------------

m.to_streamlit(height=700)

st.sidebar.success("Carte chargée ")
