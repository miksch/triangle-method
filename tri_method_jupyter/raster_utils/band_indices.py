#functions for calculating band indicies and values

import numpy as np
import pandas as pd
import datetime as dt
from scipy import stats

#General band indicies

def NDVI(nir,red):
    '''
    
    Args:
    
    Returns:
    '''
    
    NDVI = (nir - red) / (nir + red)
    
    return NDVI

def NDBI(swir,nir):
    '''
    
    Args:
    
    Returns:
    '''
    
    NDBI = (swir-nir)/(swir+nir)
    
    return NDBI

#BCI

def tc_coeffs(platform='ls8'):
    '''
    Return tasseled cap coefficients [citation needed] for ls8 and ls7 platforms
    
    Platforms:
    'ls8' : Landsat 8
    'ls7' : Landsat 7
    
    Args:
        platform (str) : String alias of satellite platform
    
    Returns:
        np.ndarray of tassled cap coefficients
    '''
    
    #Blue, Green, Red, NIR, SWIR1, SWIR2
    #Bands 2, 3, 4, 5, 6, and 7
    ls8_tc = np.array([[0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872],
                       [-0.2941, -0.243, -0.5242, 0.7276, 0.0713, -0.1608],
                       [0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559],
                       [-0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773],
                       [-0.3294, 0.0557, 0.1056, 0.1855, -0.4349, 0.8085],
                       [0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252]])
    
    #Bands 1, 2, 3, 4, 5, and 6
    ls7_tc = np.array([[0.3561, 0.3972, 0.3904, 0.6966, 0.2286, 0.1596],
                       [-0.3344, -0.3544, -0.4556, 0.6966, -0.0242, -0.2630],
                       [0.2626, 0.2141, 0.0926, 0.0656, -0.7629, -0.5388],
                       [0.0805, -0.0498, 0.1950, -0.1327, 0.5752, -0.7775],
                       [-0.7252, -0.0202, 0.6683, 0.0631, -0.1494, -0.0274],
                       [0.4000, -0.8172, 0.3832, 0.0602, -0.1095, 0.0985]])
    
    tc_dict = dict([('ls8',ls8_tc),
                    ('ls7',ls7_tc)])
    
    try:
        platform = platform.lower()
        return tc_dict[platform]
    except Exception as e:
        print(e)
        return None
    
def tasseled_cap(image,tc_coeffs,num_moments=3):
    '''
    
    Args:
        image (np.ndarray) : np.ndarray of image bands with shape (6,m,n) 
        tc_coeffs (np.ndarray) : Array of tasseled cap coefficients with shape (6,6,1,1)
        moments (int) : number of moments to calculate for the tasseled cap (default 3)
        
    Returns:
        np.ndarray of tc coefficients with shape
    '''
    
    #Stack images 
    image = np.repeat(image[np.newaxis,...],num_moments,axis=0)
    
    tc_coeffs = tc_coeffs[:num_moments,:,np.newaxis,np.newaxis]
    
    tci = image * tc_coeffs
    
    return np.sum(tci,axis=1)

def BCI(image,tc_coeffs=tc_coeffs('ls8')):
    '''
    
    '''
    
    #Calculate tassled caps for each band
    tcap = tasseled_cap(image,tc_coeffs,num_moments=3)
    
    #Find maxes in the first three (HVL) bands
    HVL_maxes = np.nanmax(tcap,axis=(1,2))[:,np.newaxis,np.newaxis]
    HVL_mins = np.nanmin(tcap,axis=(1,2))[:,np.newaxis,np.newaxis]
    
    #Normalize tassled cap values from HVL max and min
    HVL = (tcap - HVL_mins) / (HVL_maxes - HVL_mins)
    
    return ((HVL[0,...] + HVL[2,...])/2. - HVL[1,...])/ \
           ((HVL[0,...] + HVL[2,...])/2. + HVL[1,...])   


# Band normalization for triangle method 

#Get the temperatures, warm edge line, and slope/intercept values for the warm edge 
#Based on two points
def warm_edge(points, num_range=None):
    '''
    
    Args:
    
    Returns:
    
    ''' 
      
    m,b = stats.linregress(points)[0:2]    
    #ts = np.linspace(num_range[0],num_range[1],100)
    
    return m, b

#Calculate evaporative fraction for normalized triangle 
#Based on slope/intercept of warm edge
def evap_fraction(t_star, fr, m, b):
    '''
    
    Args:
    
    Returns:
    
    '''
    
    x_vals = (fr - b) / m
    ef_soil = 1 - t_star / x_vals
    
    return ef_soil * (1 - fr) + 1. * fr

def t_star(tir, tmax, tmin):
    '''
    
    Args:
    
    Returns:
    
    '''
    
    t_star = (tir - tmin) / (tmax - tmin)
    
    return t_star

def fr(ndvi, ndvi_s, ndvi_0):
    '''
    
    Args:
    
    Returns:
    
    '''
    
    Fr = ((ndvi - ndvi_0) / (ndvi_s - ndvi_0)) ** 2
    
    return Fr