import xarray as xr
import numpy as np
import matplotlib.pyplot as plt 

#ouverture
tx = xr.open_dataset("C:/Users/rober/Downloads/tasmaxAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
tn = xr.open_dataset("C:/Users/rober/Downloads/tasminAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc")
#Zonage
tn = tn.isel(x=slice(100, 200), y=slice(1,200))
tx = tx.isel(x=slice(100, 200), y=slice(1,200))



def occurrence_canicule(tx,tn,seuilx,seuiln):
    cond = (tx["tasmaxAdjust"] >= 36).astype(bool) & (tn["tasminAdjust"] >= 21).astype(bool)

    c0 = cond
    c1 = cond.shift(time=1).fillna(False).astype(bool)
    c2 = cond.shift(time=2).fillna(False).astype(bool)

    occ = (c0 & c1 & c2)

    return xr.Dataset({"occurrence": occ.astype(int)})


canicule = occurrence_canicule(tx,tn,36,21)
print(canicule["occurrence"])
canicule["occurrence"].mean(dim="time").plot()
plt.show()



       
