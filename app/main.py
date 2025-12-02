import streamlit as st
import leafmap.foliumap as leafmap

m = leafmap.Map(center=[48.85, 2.35], zoom=12)
m.add_geojson("lcz.geojson", layer_name="LCZ")
m.add_shp("parks.shp", layer_name="Parcs")
m.add_shp("water.shp", layer_name="Eau")

m.to_streamlit()
