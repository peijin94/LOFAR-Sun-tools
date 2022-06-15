
import numpy as np
import glob
import os
import re
import json
from astropy.io import fits as fits
import matplotlib.dates as mdates
import h5py
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def averaging_stride(arr_query, n_point, axis=0, n_start = -1, n_end=-1 ):
    """
    Averaging for big 2D-array but small down-sample ratio
    (n_point should be small, returns a not-very-small array)
    author: Peijin Zhang
    datetime: 2022-6-14 11:14:53
    """
    if n_start<0:
        n_start = 0
    if n_end<0:
        n_end = arr_query.shape[axis]-1
    out_size = int((n_end-n_start)/n_point)
    
    res=0
    if axis==1:
        res = np.mean(np.array(([arr_query[:,(n_start+idx):(n_start+(out_size)*n_point+idx):n_point]
                           for idx in range(n_point) ])),axis=0)
    else:    
        res = np.mean(np.array(([arr_query[(n_start+idx):(n_start+(out_size)*n_point+idx):n_point,:]
                           for idx in range(n_point) ])),axis=0)
    return res
        
    
    
def averaging_walk(arr_query, n_point, axis=0, n_start = -1, n_end=-1 ):
    """
    Averaging for big 2D-array but small big-sample ratio 
    (n_point should be large, returns a tiny array)
    author: Peijin Zhang
    datetime: 2022-6-14 11:41:57
    """
    if n_start<0:
        n_start = 0
    if n_end<0:
        n_end = arr_query.shape[axis]
    out_size = int((n_end-n_start)/n_point)
    
    res=0
    if axis==1:
        res = np.mean(np.stack(
    ([(arr_query[:,(n_start+idx*n_point):(n_start+(idx+1)*n_point)]) for idx in range(out_size) ]),axis=2),axis=axis)
    else:    
        res = np.mean(np.stack(
    ([(arr_query[(n_start+idx*n_point):(n_start+(idx+1)*n_point),:]) for idx in range(out_size) ]),axis=2).swapaxes(1,2),axis=axis)
    return res


   
def model_flux(calibrator, frequency):
    '''
    Calculates the model matrix for flux calibration for a range of known calibrators:
    J0133-3629, 3C48, Fornax A, 3C 123, J0444+2809, 3C138, Pictor A, Taurus A, 3C147, 3C196, Hydra A, Virgo A, 
    3C286, 3C295, Hercules A, 3C353, 3C380, Cygnus A, 3C444, Cassiopeia A

    Input: the calibrator name, frequency range, and time range
    Output: the calibration matrix (in sfu)
    '''
    parameters = []

    Cal_dict = {'J0133-3629':[1.0440,-0.662,-0.225],
                '3C48': [1.3253,-0.7553,-0.1914,0.0498],
                'ForA': [2.218,-0.661],
                '3C123':[1.8017,-0.7884,-0.1035,-0.0248,0.0090],
                'J0444-2809':[0.9710,-0.894,-0.118],
                '3C138':[1.0088,-0.4981,-0.155,-0.010,0.022,],
                'PicA':[1.9380,-0.7470,-0.074],
                'TauA':[2.9516,-0.217,-0.047,-0.067],
                '3C247':[1.4516,-0.6961,-0.201,0.064,-0.046,0.029],
                '3C196':[1.2872,-0.8530,-0.153,-0.0200,0.0201],
                'HydA':[1.7795,-0.9176,-0.084,-0.0139,0.030],
                'VirA':[2.4466,-0.8116,-0.048],
                '3C286':[1.2481 ,-0.4507 ,-0.1798 ,0.0357 ],
                '3C295':[1.4701,-0.7658,-0.2780,-0.0347,0.0399],
                'HerA':[1.8298,-1.0247,-0.0951],
                '3C353':[1.8627,-0.6938,-0.100,-0.032],
                '3C380':[1.2320,-0.791,0.095,0.098,-0.18,-0.16],
                '3C444':[3.3498,-1.0022,-0.22,0.023,0.043],
                'CasA':[3.3584,-0.7518,-0.035,-0.071]}
    if calibrator in Cal_dict.keys():
        parameters = Cal_dict[calibrator]
    else:  raise ValueError(calibrator, "is not in the calibrators list")
        
    flux_model = 0
    frequency /= 10**3 # convert from MHz to GHz
    for j,p in enumerate(parameters):
        flux_model += p*np.log10(frequency)**j
    flux_model = 10**flux_model # because at first the flux is in log10
    return flux_model*10**(-4) #convert form Jy to sfu
