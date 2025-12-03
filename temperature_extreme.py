import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 
from id_canicule import *
import datetime
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
#liste mois été
liste_ete = [4,5,6,7,8,9,10]
#ouverture
tx0 = xr.open_dataset("C:/Users/rober/Downloads/tasmaxAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
tn0 = xr.open_dataset("C:/Users/rober/Downloads/tasminAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
#tmean0 =xr.open_dataset()
#Zonage / création de DataArray
tn = mask(tn0["tasminAdjust"],lat_min, lat_max, lon_min, lon_max)
tx = mask(tx0["tasmaxAdjust"],lat_min, lat_max, lon_min, lon_max)
#tmean = mask(tmean0["tasAdjust"],lat_min, lat_max, lon_min, lon_max)
#jour de canicule 
jours_canicule = jour_canicule(occurrence_canicule(tx,tn,seuilx,seuiln))# pour un jeu de données

def enleverzero_datetime(liste):
    """Fonction qui créée une liste sans les 0 d'un datetime"""
    liste_new = []
    for i in liste:
        if i!=np.datetime64('1970-01-01T00:00:00.000000000'):
            liste_new.append(i-273)
    return liste_new


def diff_days(date1,date2):
    # convertir en objet datetime
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")

    # différence en jours
    diff_jours = (d2 - d1).days
    return diff_jours

def intensite_canicule(temp_max,duree):
    """Indicateur d'intensité de canicule"""
    return temp_max*duree

def traitement(tx,ds_jours_canicule):
    """Fonction qui retourne une liste intensité de la canicule et sa date"""
    jours_canicule = ds_jours_canicule.values.copy()
    intensite_can=[]
    prec_j = 0 
    streak = 0
    for j in range(0,len(jours_canicule)):
        if diff_days(str(jours_canicule[prec_j])[:10],str(jours_canicule[j])[:10]) > 1:
            intensite_can.append(intensite_canicule(tx.where(tx.time == jours_canicule[j]).max(),streak+1))
            streak = 0
        else:
            streak += 1 
            jours_canicule[prec_j] = 0
        prec_j = j

    return (intensite_can,enleverzero_datetime(jours_canicule))



a = traitement(tx,jours_canicule)
plt.scatter(a[1],a[0])
plt.show()



