import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import os

def El_Allocator(i_param,i_periode):
    return f"../CPRCM/ssp370/{parametre[i_param]}/{parametre[i_param]}_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_{periode[i_periode]}.nc"

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
#   OCCURRENCE DE CANICULE
###########################################
def occurrence_canicule(tx,tn,seuilx,seuiln):
    """Fonction qui prend 2 DataArray en argument ainsi que 2 seuils de temperature
     elle renvoie un dataset des occurrence de canicule en été """
    liste_ete = [4,5,6,7,8,9,10]
    cond = (tx >= seuilx + 273.15).astype(bool) & (tn >= seuiln+273.15).astype(bool) 

    c0 = cond
    c1 = cond.shift(time=1).fillna(False).astype(bool)
    c2 = cond.shift(time=2).fillna(False).astype(bool)

    occ = (c0 & c1 & c2)
    canicule = xr.Dataset({"occurrence": occ.astype(int)})
    mask_ete = canicule["time"].dt.month.isin(liste_ete)
    return canicule.sel(time=mask_ete) #pour exploiter les occurrences faire canicule["occurrence"]

def jour_canicule(occurrence_canicule):
    """Fonction qui retourne une liste avec les jours de canicule"""
    ds = occurrence_canicule.where(occurrence_canicule["occurrence"].sum(dim = ("x","y"))>0,drop = True)
    return ds.time

###########################################
#   AFFICHAGE
###########################################
def AFFICHAGE(moy_T, anomalie_par_melun, i_param, i_periode, lat_min, lat_max, lon_min, lon_max):
    lats_data = moy_T['lat'].values
    lons_data = moy_T['lon'].values

    periode_bis = ["2015-2019","2020-2029","2030,2039","2040-2049","2050-2059","2060-2069","2070-2079","2080-2089","2090-2099"]
    
    # Création figure avec deux sous-graphes
    fig, axs = plt.subplots(
        1, 2, figsize=(16, 6),
        subplot_kw={'projection': ccrs.LambertConformal(central_longitude=3, central_latitude=48.6)}
    )

    # --- Température moyenne ---
    ax = axs[0]
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.coastlines('10m', color='black', linewidth=0.8)

    # Grille
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=False,
        linestyle='--',
        alpha=0.3
    )
    gl.top_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = mticker.FixedLocator(np.arange(lon_min, lon_max+0.01, 0.2))
    gl.ylocator = mticker.FixedLocator(np.arange(lat_min, lat_max+0.01, 0.2))


    #colormap
    couleurs = ['#ffffff',  '#ffffbb',  '#ffff99', '#ffff22','#fff000',  '#ff8000','#ff8800', '#ff2a00','#dd3300', '#990000','#770000', '#550000']
    cmap = colors.ListedColormap(couleurs)
    boundaries = [0,0.25,0.5,1, 1.25, 1.5, 1.75,2,2.5,3,4,5]
    norm = colors.BoundaryNorm(boundaries, cmap.N, clip=True)

    if i_param==0:
        vmin = 22
        vmax = 28
    if i_param==1:
        vmin = 28
        vmax = 38
    if i_param==2:
        vmin = 18
        vmax = 24

    mm0 = ax.pcolormesh(
        lons_data, lats_data, moy_T,
        vmin=vmin, vmax=vmax,
        cmap=mpl.cm.viridis, shading='auto',
        transform=ccrs.PlateCarree()
    )
    cbar0 = plt.colorbar(mm0, ax=ax, orientation='vertical', shrink=0.7)
    cbar0.set_label('Température moyenne (°C)', fontsize=12)
    ax.set_title(f"Température moyenne en periode de canicule {periode_bis[i_periode]}", fontsize=14)

    # --- Anomalie par rapport à Melun ---
    ax = axs[1]
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.coastlines('10m', color='black', linewidth=0.8)

    # Grille
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=False,
        linestyle='--',
        alpha=0.3
        )
    gl.xlabels_top = False
    gl.xlabels_bottom = True
    gl.ylabels_left = True
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = mticker.FixedLocator(np.arange(lon_min, lon_max+0.01, 0.2))
    gl.ylocator = mticker.FixedLocator(np.arange(lat_min, lat_max+0.01, 0.2))



    mm1 = ax.pcolormesh(
        lons_data, lats_data, anomalie_par_melun,
        norm=norm,
        cmap=cmap, shading='auto',
        transform=ccrs.PlateCarree()
    )
    cbar1 = plt.colorbar(mm1, ax=ax, orientation='vertical', shrink=0.7)
    cbar1.set_label('Anomalie de température (°C)', fontsize=12)
    ax.set_title(f"Anomalie de température en canicule par rapport à Melun {periode_bis[i_periode]}", fontsize=14)
    


    # Sauvegarde
    chemin_fig = "Cartes/"
    os.makedirs(chemin_fig, exist_ok=True)
    plt.savefig(chemin_fig + f"carte_{parametre[i_param]}_IDF_{periode_bis[i_periode]}.png", dpi=200)
    plt.close()

################################################################################################################################################################
################################################################################################################################################################
################################################################################################################################################################

###########################################
#   Chemins des données
###########################################
parametre = ["tasAdjust", "tasmaxAdjust", "tasminAdjust"]
periode = [ "20150101-20191231", #0
            "20200101-20291231", #1
            "20300101-20391231", #2
            "20400101-20491231", #3
            "20500101-20591231", #4
            "20600101-20691231", #5
            "20700101-20791231", #6
            "20800101-20891231", #7
            "20900101-20991231"] #8

###########################################
#   Zone géographique
###########################################
lat_min, lat_max = 48.3, 49.5  
lon_min, lon_max = 1.5, 3.3


for i_periode in range(0,9):
    i_param = 0
    T_data = xr.open_dataset(El_Allocator(i_param,i_periode))

    i_param = 1
    Tx_data = xr.open_dataset(El_Allocator(i_param,i_periode))

    i_param = 2
    Tn_data = xr.open_dataset(El_Allocator(i_param,i_periode))


    ###########################################
    #   Restriction des données à l'IDF 
    ###########################################
    i_param = 0
    T_data_IDF = mask_rectangle(T_data[parametre[i_param]], lat_min, lat_max, lon_min, lon_max)
    T_data_Melun = get_melun_tempe(T_data[parametre[i_param]])

    i_param = 1
    Tx_data_IDF = mask_rectangle(Tx_data[parametre[i_param]], lat_min, lat_max, lon_min, lon_max)
    Tx_data_Melun = get_melun_tempe(Tx_data[parametre[i_param]])

    i_param = 2
    Tn_data_IDF = mask_rectangle(Tn_data[parametre[i_param]], lat_min, lat_max, lon_min, lon_max)
    Tn_data_Melun = get_melun_tempe(Tn_data[parametre[i_param]])


    ###########################################
    #   Recherche des périodes de canicule
    ###########################################
    seuilx_IDF = 31
    seuiln_IDF = 21
    occurrence_canicule_IDF = occurrence_canicule(Tx_data_IDF, Tn_data_IDF, seuilx_IDF, seuiln_IDF)
    jour_canicule_IDF = jour_canicule(occurrence_canicule_IDF)


    ###########################################
    #   Restriction des données aux canicules
    ###########################################
    T_IDF_canicule = T_data_IDF.sel(time=jour_canicule_IDF)#.sel(time='2059')
    T_Melun_canicule = T_data_Melun.sel(time=jour_canicule_IDF)#.sel(time='2059')

    Tx_IDF_canicule = Tx_data_IDF.sel(time=jour_canicule_IDF)#.sel(time='2059')
    Tx_Melun_canicule = Tx_data_Melun.sel(time=jour_canicule_IDF)#.sel(time='2059')

    Tn_IDF_canicule = Tn_data_IDF.sel(time=jour_canicule_IDF)#.sel(time='2059')
    Tn_Melun_canicule = Tn_data_Melun.sel(time=jour_canicule_IDF)#.sel(time='2059')


    ###########################################
    #   Moyennes temporelles
    ###########################################
    i_param = 2

    if i_param==0:
        moy_T_IDF_canicule = T_IDF_canicule.mean(dim="time", skipna=True) - 273.15
        moy_T_melun_canicule = T_Melun_canicule.mean(dim="time", skipna=True) - 273.15

    elif i_param==1:
        moy_T_IDF_canicule = Tx_IDF_canicule.mean(dim="time", skipna=True) - 273.15
        moy_T_melun_canicule = Tx_Melun_canicule.mean(dim="time", skipna=True) - 273.15

    elif i_param==2:
        moy_T_IDF_canicule = Tn_IDF_canicule.mean(dim="time", skipna=True) - 273.15
        moy_T_melun_canicule = Tn_Melun_canicule.mean(dim="time", skipna=True) - 273.15

    anomalie_par_melun = moy_T_IDF_canicule - moy_T_melun_canicule

    AFFICHAGE(moy_T_IDF_canicule, anomalie_par_melun,i_param, i_periode, lat_min, lat_max, lon_min, lon_max)
    print(periode[i_periode])