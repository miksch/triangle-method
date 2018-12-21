import xarray as xr
import pandas as pd
import numpy as np
import re
import datetime as dt

#manipulating files to interface with xarray, rasterio, etc.


def all_files(fpath):
    return [os.path.join(fpath,f) for f in os.listdir(fpath) if not f.startswith('.')]

def fname_to_dt(fname,dt_str):
    '''
    This function assumes that the date string is between the last underscore and the file extension
    e.g. 
    '''
    fname_date = re.search('_(\d+).tif',fname).group(1)
    return dt.datetime.strptime(fname_date,dt_str)

def band_to_var(da,band_lookup,band_name='band'):
    '''
    Switches xarray.open_rasterio
    
    Args:
        da (xarray.DataArray):
        band_lookup (dict or pd.DataFrame with band int as index):
    '''
    band_list = []
    
    for b in da[band_name].values:
        try:
            temp_da = da.sel(band=b,drop=True)
            temp_da.name = band_lookup[b]
            band_list.append(temp_da.copy())           
        except Exception as e:
            print(e)
            continue
    out_dataset = xr.merge(band_list)
    out_dataset.attrs = temp_da.attrs
    return out_dataset
    
def append_rasterio(files,rewrite_bands=True,band_lookup=None,dt_str='%Y%m%d',**kwargs):
    
    '''
    Read multiple raster files with same size, projection, and bands and concatenate into one
    xarray DataArray. Appends along 'time' coordinate.
    
    Args:
        files (list): list of file paths for images to concatenate
        dt_str (str): datetime strptime representation in filename
        **kwargs (dict): xarray.open_rasterio() arguments
    
    Returns:
        xarray.DataArray object of images with coordinates (bands,y,x,time)
    
    Dependencies:
        fname_to_dt(fname,dt_str)
    
    TO-DO:
        -Re-write band coordinate to data variables based on band_retr class
    
    '''
    
    xr_list = []
    
    for f in files:
        try:
            temp_xr = xr.open_rasterio(f,**kwargs)
            file_date = fname_to_dt(f,dt_str)# + dt.timedelta(hours=18,minutes=7)
            temp_xr = temp_xr.assign_coords(**{'time':file_date})
            if rewrite_bands:
                temp_xr = band_to_var(temp_xr,band_lookup)
            else:
                temp_xr.name = 'band_values'
            xr_list.append(temp_xr.copy())           
        except Exception as e:
            print(e)
            continue
    try:
        return xr.concat(xr_list,dim='time')
    except Exception as e:
        print(e)
        return None
    
class band_retr(object):
    
    '''
    Convenience lass used to get around using band as a coordinate in xarray
    
    Args:
        file (str): file path to .csv file that contains
        param band_col (str): name of column for band number (default 'Band')
        param name_col (str): name of columns for band string representation (default 'Name')
        param file_kwargs (dict): dictionary of kwargs used in pd.read_csv()
    
    
    '''
    
    def __init__(self,file,band_col='Band',name_col='Name',**file_kwargs):
        self.file = file
        self.band_col = band_col
        self.name_col = name_col
        self.band_df = self._read_file(**file_kwargs)
        self.band_dict = dict(zip(self.band_df[band_col],self.band_df[name_col]))
        
    def __repr__(self):
        return str(self.band_dict)
        
    def _read_file(self,**file_kwargs):
        try:
            df = pd.read_csv(self.file,**file_kwargs)
            return df                           
        except Exception as e:
            print(e)
            return None 
        
    def band_str(self,band_str):
        '''
        
        '''
        try:
            return self.band_dict[band_str]
        except Exception as e:
            print(e)
            return None
        
class categorical_df(object):
    
    '''
    Convenience class for categorical plotting in seaborn
    '''
    
    def __init__(self,file,val_col='Value',type_col='Type',color_col='Color',**file_kwargs):
        self.file = file
        self.val_col = val_col
        self.type_col = type_col
        self.color_col = color_col
        self.categorical_df = self._read_file(**file_kwargs)
        
    def _read_file(self,**file_kwargs):
        try:
            df = pd.read_csv(self.file,**file_kwargs)
            return df                           
        except Exception as e:
            print(e)
            return None
    
    def val_type(self):
        return dict(zip(self.categorical_df[self.val_col],self.categorical_df[self.type_col]))
    
    def val_color(self):
        return dict(zip(self.categorical_df[self.val_col],self.categorical_df[self.color_col]))