import pandas as pd
import xarray
import time

t0 = time.time()

FICHIER = 'tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-SAFRAN-1991-2020_day_20150101-21001231.nc'

print(time.time()-t0)

nc = xarray.open_dataset(FICHIER)


print(time.time()-t0)
mean_time = nc["tasAdjust"].mean(dim="time")

print(time.time()-t0)
mean_time.plot()

print(time.time()-t0)



