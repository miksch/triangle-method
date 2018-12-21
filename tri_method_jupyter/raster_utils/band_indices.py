#functions for calculating band indicies and values

import numpy as np
import pandas as pd
import datetime as dt


#General band indicies

def NDVI(nir,red):
    return (nir-red)/(nir+red)

def NDBI(swir,nir):
    return (swir-nir)/(swir+nir)

#BCI

def tc_coeffs(platform='ls8'):
    '''
    Return
    
    possible platforms
    
    Inputs 
    
    Output
    
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
        param image : np.ndarray of image bands with shape (6,m,n) 
        param tc_coeffs : Array of tasseled cap coefficients with shape (6,6,1,1)
        param moments (int) : number of moments to calculate for the tasseled cap (default 3)
        
    Outputs
    ---
    np.ndarray of tc coefficients with shape
    '''
    
    image = np.repeat(image[np.newaxis,...],num_moments,axis=0)
    
    tc_coeffs = tc_coeffs[:num_moments,:,np.newaxis,np.newaxis]
    
    
    tci = image * tc_coeffs
    
    return np.sum(tci,axis=1)

def BCI(image,tc_coeffs=tc_coeffs('ls8')):
    '''
    
    '''
    
    tcap = tasseled_cap(image,tc_coeffs,num_moments=3)
    
    HVL_maxes = np.nanmax(tcap,axis=(1,2))[:,np.newaxis,np.newaxis]
    HVL_mins = np.nanmin(tcap,axis=(1,2))[:,np.newaxis,np.newaxis]
    
    HVL = (tcap - HVL_mins)/(HVL_maxes - HVL_mins)
    
    return ((HVL[0,...] + HVL[2,...])/2. - HVL[1,...])/ \
           ((HVL[0,...] + HVL[2,...])/2. + HVL[1,...])   

# Band normalization for triangle method 
