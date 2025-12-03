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
periode = ["20150101-20191231","20200101-20291231","20300101-20391231","20400101-20491231",
           "20500101-20591231","20600101-20691231","20700101-20791231","20800101-20891231",
           "20900101-20991231"]
periode_bis = ["2015-2019","2020-2029","2030,2039","2040-2049","2050-2059","2060-2069","2070-2079","2080-2089","2090-2099"]

i_param = 0
i_periode = 6

chemin_file = f"../CPRCM/ssp370/{parametre[i_param]}/"
nom_fichier = (
    f"{parametre[i_param]}_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_"
    f"CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_"
    f"{periode[i_periode]}.nc"
)

T_data = xr.open_dataset(chemin_file + nom_fichier)


###########################################
#   Masque rectangle
###########################################
def mask_rectangle(data, lat_min, lat_max, lon_min, lon_max):
    """
    Applique un masque géographique à un DataArray.
    data : xarray.DataArray
    """
    lats = data['lat']
    lons = data['lon']

    # Construction du masque 2D correct via broadcasting
    mask = (
        (lats >= lat_min) & (lats <= lat_max)
    ) & (
        (lons >= lon_min) & (lons <= lon_max)
    )

    return data.where(mask, drop = True)


###########################################
#   Extraction Melun
###########################################
def get_melun_tempe(data):
    lat_Melun = 48.572551
    lon_Melun = 2.672507

    lats = data['lat'].values   
    lons = data['lon'].values

    # distance brute
    dist = np.sqrt((lats - lat_Melun)**2 + (lons - lon_Melun)**2)

    # indices du point le plus proche
    j, i = np.unravel_index(np.argmin(dist), dist.shape)

    return data[:, j, i]



###########################################
#   Zone géographique
###########################################
lat_min, lat_max = 48.0, 49.2
lon_min, lon_max = 1.8, 3.6

T_data_IDF = mask_rectangle(T_data[parametre[i_param]], lat_min, lat_max, lon_min, lon_max)

T_data_Melun = get_melun_tempe(T_data[parametre[i_param]])


###########################################
#   Moyennes temporelles
###########################################
moy_data = T_data_IDF.mean(dim="time", skipna=True).values - 273.15
moy_T_melun = T_data_Melun.mean(dim="time", skipna=True).values - 273.15

anomalie_par_melun = moy_data - moy_T_melun

###########################################
#   AFFICHAGE
###########################################
lats_data = T_data_IDF['lat'].values
lons_data = T_data_IDF['lon'].values

lat_lim_idf = [lat_min, lat_max]
lon_lim_idf = [lon_min, lon_max]

# Création figure avec deux sous-graphes
fig, axs = plt.subplots(
    1, 2, figsize=(16, 6),
    subplot_kw={'projection': ccrs.LambertConformal(central_longitude=3, central_latitude=48.6)}
)

# --- Température moyenne ---
ax = axs[0]
ax.set_extent([lon_lim_idf[0], lon_lim_idf[1], lat_lim_idf[0], lat_lim_idf[1]], crs=ccrs.PlateCarree())
ax.coastlines('10m', color='black', linewidth=0.8)

# Grille
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linestyle='--', alpha=0.3)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LONGITUDE_FORMATTER
gl.xlocator = mticker.FixedLocator(np.arange(lon_lim_idf[0], lon_lim_idf[1]+0.1, 0.2))
gl.ylocator = mticker.FixedLocator(np.arange(lat_lim_idf[0], lat_lim_idf[1]+0.1, 0.2))

mm0 = ax.pcolormesh(
    lons_data, lats_data, moy_data,
    vmin=np.nanmin(moy_data), vmax=np.nanmax(moy_data),
    cmap=mpl.cm.viridis, shading='auto',
    transform=ccrs.PlateCarree()
)
cbar0 = plt.colorbar(mm0, ax=ax, orientation='vertical', shrink=0.7)
cbar0.set_label('Température moyenne (°C)', fontsize=12)
ax.set_title(f"Température moyenne {periode_bis[i_periode]}", fontsize=14)

# --- Anomalie par rapport à Melun ---
ax = axs[1]
ax.set_extent([lon_lim_idf[0], lon_lim_idf[1], lat_lim_idf[0], lat_lim_idf[1]], crs=ccrs.PlateCarree())
ax.coastlines('10m', color='black', linewidth=0.8)

# Grille
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linestyle='--', alpha=0.3)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LONGITUDE_FORMATTER
gl.xlocator = mticker.FixedLocator(np.arange(lon_lim_idf[0], lon_lim_idf[1]+0.1, 0.2))
gl.ylocator = mticker.FixedLocator(np.arange(lat_lim_idf[0], lat_lim_idf[1]+0.1, 0.2))


mm1 = ax.pcolormesh(
    lons_data, lats_data, anomalie_par_melun,
    vmin=-np.nanmax(abs(anomalie_par_melun)),
    vmax=np.nanmax(abs(anomalie_par_melun)),
    cmap='coolwarm', shading='auto',
    transform=ccrs.PlateCarree()
)
cbar1 = plt.colorbar(mm1, ax=ax, orientation='vertical', shrink=0.7)
cbar1.set_label('Anomalie par rapport à Melun (°C)', fontsize=12)
ax.set_title(f"Anomalie par rapport à Melun {periode_bis[i_periode]}", fontsize=14)

# Sauvegarde
chemin_fig = "Cartes/"
os.makedirs(chemin_fig, exist_ok=True)
plt.savefig(chemin_fig + f"carte_{parametre[i_param]}_IDF_{periode_bis[i_periode]}_double.png", dpi=200)
plt.close()
