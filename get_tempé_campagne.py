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

def mask(data, lat_min, lat_max, lon_min, lon_max):
    lats = data['lat'].values
    lons = data['lon'].values
    # Création du masque : True pour les points à garder, False ailleurs
    mask = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)

    masked_data = np.where(mask[None, :, :], data, np.nan)
    # Application du masque : on remplace les valeurs hors zone par np.nan
    return np.where(mask, data, np.nan)


lat_min, lat_max = 48.0, 49.2
lon_min, lon_max = 1.8, 3.6
T_data_IDF = mask(T_data, lat_min, lat_max, lon_min, lon_max)


moy_data = ds_data[parametre[i_param]].mean(dim='time', skipna=True).values - 273.15



#lats_data = ds_data['lat'].values
#lons_data = ds_data['lon'].values

