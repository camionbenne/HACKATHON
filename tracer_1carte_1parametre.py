#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

"""
Trace la carte moyenne d'une variable sur tous les pas de temps d'un fichier NetCDF
avec une échelle de couleur continue et une colormap.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import os

### Chemins des données
chemin_file = "../CPRCM/ssp370/tasAdjust/"
nom_fichier = "tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc"
ds_data = xr.open_dataset(chemin_file + nom_fichier)

### Lecture de la variable
variable = 'tasAdjust'
moy_data = ds_data[variable].mean(dim='time', skipna=True).values - 273.15

# Coordonnées 2D
lats_data = ds_data['lat'].values
lons_data = ds_data['lon'].values



#############################################################
##################### Figure ###############################
#############################################################

# Paramètres d'affichage
fig_width_cm = 52
fig_height_cm = 32
inches_per_cm = 1 / 2.54
fig_size = [fig_width_cm * inches_per_cm, fig_height_cm * inches_per_cm]

plt.rcParams.update({'figure.titlesize': 25})

fig = plt.figure(figsize=fig_size)

### Zone et projection (France métropolitaine)
lat_lim = [41.0, 51.5]
lon_lim = [-5.5, 9.8]


map_proj = ccrs.LambertConformal(central_longitude=3, central_latitude=46)

ax = plt.subplot(1, 1, 1, projection=map_proj)
ax.set_extent([lon_lim[0], lon_lim[1], lat_lim[0], lat_lim[1]], crs=ccrs.PlateCarree())
ax.coastlines('10m', color='black', linewidth=0.8)

# Grille compatible Lambert
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linestyle='--', linewidth=1, color='grey', alpha=0.3)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlocator = mticker.FixedLocator(np.arange(lon_lim[0], lon_lim[1]+1, 2))
gl.ylocator = mticker.FixedLocator(np.arange(lat_lim[0], lat_lim[1]+1, 2))
gl.xlabel_style = {"size": 10, "color": "gray"}
gl.ylabel_style = {"size": 10, "color": "gray"}

# Colormap continue
colormap = mpl.cm.viridis  # tu peux changer : plasma, inferno, coolwarm...

valmin = np.nanmin(moy_data)
valmax = np.nanmax(moy_data)

# Tracé avec contourf et échelle continue
mm = ax.pcolormesh(lons_data, lats_data, moy_data,
                   vmin=valmin, vmax=valmax,
                   cmap=colormap,
                   shading='auto',
                   transform=ccrs.PlateCarree())


# Colorbar
cbar = plt.colorbar(mm, orientation='vertical', shrink=0.7, drawedges=False)
cbar.set_label('Température moyenne (°C)', fontsize=17)

# Titres
plt.title('Température moyenne 2015–2019', fontsize=25)
plt.suptitle('CNRM-AROME / SSP370', fontsize=18)

# Sauvegarde
chemin_fig = 'Cartes/'
os.makedirs(chemin_fig, exist_ok=True)
figname = chemin_fig + f'carte_tasAdjust_2015_2019.png'
plt.savefig(figname, dpi=200)
plt.close()




# Zone Île-de-France
lat_lim_idf = [48.0, 49.2]
lon_lim_idf = [1.8, 3.6]

# Création figure
fig, ax = plt.subplots(1, 1, figsize=(8, 6), subplot_kw={'projection': ccrs.LambertConformal(central_longitude=3, central_latitude=48.6)})

ax.set_extent([lon_lim_idf[0], lon_lim_idf[1], lat_lim_idf[0], lat_lim_idf[1]], crs=ccrs.PlateCarree())
ax.coastlines('10m', color='black', linewidth=0.8)

# Grille
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linestyle='--', alpha=0.3)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlocator = mticker.FixedLocator(np.arange(lon_lim_idf[0], lon_lim_idf[1]+0.1, 0.2))
gl.ylocator = mticker.FixedLocator(np.arange(lat_lim_idf[0], lat_lim_idf[1]+0.1, 0.2))
gl.xlabel_style = {"size": 10, "color": "gray"}
gl.ylabel_style = {"size": 10, "color": "gray"}

# Tracé lisse
mm = ax.pcolormesh(lons_data, lats_data, moy_data,
                   vmin=np.nanmin(moy_data), vmax=np.nanmax(moy_data),
                   cmap=mpl.cm.viridis, shading='auto',
                   transform=ccrs.PlateCarree())

# Colorbar
cbar = plt.colorbar(mm, orientation='vertical', shrink=0.7)
cbar.set_label('Température moyenne (°C)', fontsize=12)

plt.title("Température moyenne 2015-2019 - Île-de-France", fontsize=14)

# Sauvegarde
chemin_fig = 'Cartes/'
os.makedirs(chemin_fig, exist_ok=True)
figname = chemin_fig + f'carte_tasAdjust_IDF_2015_2019.png'
plt.savefig(figname, dpi=200)
plt.close()
