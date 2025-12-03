from matplotlib import pyplot as plt
import pandas as pd
import xarray
import time
import matplotlib.colors as colors
import matplotlib.cm as cm

t0 = time.time()

FICHIER = 'tasAdjust_FR-Metro_CNRM-ESM2-1_ssp370_r1i1p1f2_CNRM-MF_CNRM-AROME46t1_v1-r1_MF-CDFt-ANASTASIA-SAFRAN-1991-2020_day_20150101-21001231.nc'

nc = xarray.open_dataset(FICHIER)

print(time.time()-t0)
mean_time = nc["tasAdjust"].mean(dim="time").where(nc["lon"] > 1, drop=True).where(nc["lon"] < 3, drop=True).where(nc["lat"] > 47, drop=True).where(nc["lat"] < 49, drop=True) - 273.15 - 10

# x_lims = (nc[x] # lat, lon vers x ou y ??



print(time.time()-t0)

#mean_time.plot(cmap="YlOrRd")
#plt.show()#cmap="Reds")


print(time.time()-t0)


def echelonnage(valeur, seuil):
	"""
	Pour une valeur x, renvoie la valeur la plus proche appartenant à IR*seuil = tous les multiples de seuils.
	e.g, x=12.3, d = .25, renvoie 12.25.
	"""
	q = valeur - valeur%seuil
	if q > seuil/2:
		return q+seuil
	return q


cmap = colors.ListedColormap(['#ffffbb', '#ffff99', '#ff8000', '#ff2a00', '#990000', '#660000'])
boundaries = [float('-Inf'), 1, 2, 3, 4, 5, float('Inf')]
norm = colors.BoundaryNorm(boundaries, cmap.N, clip=True)





plt.pcolormesh(mean_time, cmap=cmap, norm=norm)
plt.colorbar()
#cbar = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), orientation='vertical')

plt.show()




fig_width_cm = 20
fig_height_cm = 20
inches_per_cm = 1 / 2.54
fig_width = fig_width_cm * inches_per_cm # width in inches
fig_height = fig_height_cm * inches_per_cm       # height in inches
fig_size = [fig_width, fig_height]
fig, ax = plt.subplots(1,1,figsize=fig_size)#,constrained_layout=True)
fig.set_size_inches(fig_size)






mm=ax.contourf(lons_data, lats_data, moy_data,cmap=colormap)
cbar=plt.colorbar(mm,orientation='vertical',shrink=0.7,drawedges='True')
#A COMPLETER :
cbar.set_label('',fontsize=17)


def affichage(mask_x_periodes_canicules, temp_campagne):
	mask_x_periodes_canicules["temperature"] -= temp_campagne
	mask_x_periodes_canicules["temperature"]

