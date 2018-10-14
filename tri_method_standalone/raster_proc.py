import numpy as np
import rasterio

#Reads in a list of 
def read_raster(fp,band_list):
    ds = rasterio.open(fp)
    band_dict = dict.fromkeys(band_list,0)
    for x in band_list:
        band_dict[x] = ds.read(int(x))
    return ds, band_dict

def mask_list(orig,qa,vals=[2720.,2724.,2728.,2732.]): 
    masked = np.ma.MaskedArray(orig,~np.in1d(qa,vals))
    return masked

