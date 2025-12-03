import xarray as xr

# Chemin vers ton fichier .nc
file_path = "/home/imane/HACKATHON/tasmax/tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-ALPX-3-1991-2020_day_20150101-20191231.nc"

# Ouvrir le fichier
ds = xr.open_dataset(file_path)
print(ds.data_vars)

