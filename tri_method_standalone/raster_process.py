import numpy as np
import pandas as pd
import rasterio
import os
import glob
import datetime as dt
import matplotlib.pyplot as plt
import raster_proc as rp
import pickle
import sys

#Landsat filename convention
#LC08_038031_YYYYMMDD.tif
root_dir = ''
filepaths = glob.glob(root_dir+'*.tif')
files = [os.path.basename(x) for x in filepaths]

#Create folder for affine pickles, single text file for projections

outpath = ''
raster_bands = {}
raster_info = {}

for fp, fi in zip(filepaths,files):
    fi_dt = dt.datetime.strptime(fi[-12:-4],'%Y%m%d')
    print(fi[-12:-4])
    #Read in raster file
    band_list = [8,11,13]
    ds, bands = rp.read_raster(fp,band_list)

    bands[8] = rp.mask_list(bands[8],bands[11],vals=[322])*.1
    bands[13] = rp.mask_list(bands[13],bands[11],vals=[322])
    
    raster_bands[fi_dt.isoformat()] = bands
    raster_bands[fi_dt.isoformat()]['ef'] = None
    raster_info[fi_dt.isoformat()] = {'affine':ds.affine,'width':ds.width,'height':ds.height,'proj':ds.crs['init'],
                                      #extra variables for triangles, comment out all raster info if not wanting to reset everything
                                      'ndvio':0,'ndvis':0,'tir_max':0,'tir_min':0,'we_points':np.array(([0,0],[0,0]))
                                      }
    #break

#sys.exit('bye')
#Dump it into some pickles, need to write README (maybe automated?)
pickle.dump(raster_bands,open(outpath+'raster_bands.p','wb'))    
pickle.dump(raster_info,open(outpath+'raster_info.p','wb'))
