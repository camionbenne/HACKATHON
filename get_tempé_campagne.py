import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import os


### Chemins des données
parametre = ["tasAdjust", "tasmaxAdjust", "tasminAdjust"]
periode = ["20150101-20191231","20200101-20291231","20300101-20391231","20400101-20491231","20500101-20591231","20600101-20691231","20700101-20791231","20800101-20891231","20900101-20991231"]

i_param = 0 #indice du parametre choisi
i_periode = 0 #indice pour la periode
chemin_file = f"../CPRCM/ssp370/{parametre[i_param]}/"
nom_fichier = f"{parametre[i_param]}_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_{periode[i_periode]}.nc"

T_data = xr.open_dataset(chemin_file + nom_fichier)


def mask_rectangle(data, lat_min, lat_max, lon_min, lon_max):
    """
    Applique un masque géographique à un DataArray.
    data : xarray.DataArray
    """
    lats = data['lat']
    lons = data['lon']
    mask_bool = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)
    
    # where garde les coordonnées et remplace les valeurs hors masque par NaN
    return data.where(mask_bool)

def get_melun_tempe(data):
    """
    Donne la tempé de Melun
    data : xarray.DataArray
    """
    lat_Melun = 48.572551
    lon_Melun = 2.672507
    data_Melun = data.sel(lat=lat_Melun, lon=lon_Melun, method="nearest")

    return data_Melun




# Zone Île-de-France
lat_min, lat_max = 48.0, 49.2
lon_min, lon_max = 1.8, 3.6

T_data_IDF = mask_rectangle(T_data[f"{parametre[i_param]}"], lat_min, lat_max, lon_min, lon_max)
T_data_Melun = get_melun_tempe(T_data_IDF)


# Moyenne temporelle sur la zone masquée
moy_data = T_data_IDF.mean(dim='time', skipna=True).values - 273.15
moy_T_melun = T_data_Melun.mean(dim='time', skipna=True).values - 273.15









###################################################################
#######################  AFFICHAGE  ###############################
###################################################################
lats_data = T_data_IDF['lat'].values
lons_data = T_data_IDF['lon'].values

lat_lim_idf = [lat_min, lat_max]
lon_lim_idf = [lon_min, lon_max]

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
mm = ax.pcolormesh(lons_data, lats_data, moy_data-moy_T_melun,
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
