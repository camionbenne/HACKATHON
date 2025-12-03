import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 

def mask(data, lat_min, lat_max, lon_min, lon_max):
    """
    Applique un masque géographique à un DataArray.
    data : xarray.DataArray
    """
    lats = data['lat']
    lons = data['lon']
    mask_bool = (lats >= lat_min) & (lats <= lat_max) & (lons >= lon_min) & (lons <= lon_max)
    
    # where garde les coordonnées et remplace les valeurs hors masque par NaN
    return data.where(mask_bool, drop = True)

#carré lat/lon contenant la region parisienne 
lat_min, lat_max = 47, 49.2 # à recentrer
lon_min, lon_max = 1,4

#liste contenant les numéros des  mois d'été
liste_ete = [4,5,6,7,8,9,10]

#ouverture
tx0 = xr.open_dataset("C:/Users/rober/Downloads/tasmaxAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
tn0 = xr.open_dataset("C:/Users/rober/Downloads/tasminAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
#Zonage
tn = mask(tn0["tasminAdjust"],lat_min, lat_max, lon_min, lon_max)
tx = mask(tx0["tasmaxAdjust"],lat_min, lat_max, lon_min, lon_max)


def occurrence_canicule(tx,tn,seuilx,seuiln):
    """Fonction qui prend 2 DataArray en argument ainsi que 2 seuils de temperature
     elle renvoie un dataset des occurence de canicule en été """
    cond = (tx >= seuilx + 273.15).astype(bool) & (tn >= seuiln+273.15).astype(bool) 

    c0 = cond
    c1 = cond.shift(time=1).fillna(False).astype(bool)
    c2 = cond.shift(time=2).fillna(False).astype(bool)

    occ = (c0 & c1 & c2)
    canicule = xr.Dataset({"occurrence": occ.astype(int)})
    mask_ete = canicule["time"].dt.month.isin(liste_ete)
    return canicule.sel(time=mask_ete) #pour exploiter les occurences faire canicule["occurrence"]

def jour_canicule(occurence_canicule):
    """Fonction qui retourne une liste avec les jours de canicule"""
    ds = occurence_canicule.where(occurence_canicule["occurrence"].sum(dim = ("x","y"))>0,drop = True)
    return ds.time
