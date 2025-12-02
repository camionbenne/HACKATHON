import xarray as xr
import numpy as np

#ouverture
tx = xr.open_dataset("C:/Users/rober/Downloads/tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
tn = xr.open_dataset("C:/Users/rober/Downloads/tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")

#Zonage sur Paris
tn = tn.isel(x=slice(47, 49), y=slice(1,3))
tx = tx.isel(x=slice(47, 49), y=slice(1,3))



canicule = xr.Dataset(
    {
        "occurrence": (("time", "y", "x"), np.zeros((len(tn.time),len(tn.x),len(tn.y))))
        
    },
    coords={
        "x": tn.x,
        "y": tn.y,
        "time": tn.time
    }
)


def occurrence_canicule(tx,tn,seuilx,seuiln):
    times = tx.time
    longueur = tx.x
    largeur = tx.y
    for t in range(2,len(times)):
        print(t)
        for x in range(len(longueur)):
            for y in range(len(largeur)):
                cond1 = tx["tasmaxAdjust"].isel(time = t, x = x, y = y) >= seuilx and tn["tasminAdjust"].isel(time = t, x = x, y = y) >= seuiln
                cond2 = tx["tasmaxAdjust"].isel(time = t-1,x = x, y = y ) >= seuilx and tn["tasminAdjust"].isel(time = t-1,x = x, y = y) >= seuiln
                cond3 = tx["tasmaxAdjust"].isel(time = t-2,x = x, y = y) >= seuilx and tn["tasminAdjust"].isel(time = t-2,x = x, y = y) >= seuiln
                if all([cond1, cond2, cond3]):
                    canicule["occurrence"].data[t,y,x] = 1
                else:
                    canicule["occurrence"].data[t,y,x] = 0


occurrence_canicule(tx,tn,36,21)
print(canicule["occurrence"])


       
