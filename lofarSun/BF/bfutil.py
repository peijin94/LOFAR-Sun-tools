
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
from scipy import interpolate
from tqdm import tqdm

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

    source https://arxiv.org/pdf/1609.05940.pdf
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

def partition_avg(arr, ratio_range):
    #  average in a given ratio range to exclude extreme value
    arr_sort = np.sort(arr.ravel())
    nums = arr_sort[int(ratio_range[0]*arr_sort.shape[0]):int(ratio_range[1]*arr_sort.shape[0])]
    return np.mean(nums)


def get_cal_bandpass(freq_idx, h5dir, h5name,ratio_range=[0.2,0.8]):
    fname_DS=h5name
    this_dir = os.getcwd()
    os.chdir(h5dir)
    m = re.search('B[0-9]{3}', fname_DS)
    beam_this = m.group(0)[1:4]
    m = re.search('SAP[0-9]{3}', fname_DS)
    SAP = m.group(0)[3:6]

    f = h5py.File( fname_DS, 'r' )
    data_shape = f['SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/STOKES_0'].shape
    
    if data_shape[0]>1e3:
        sampling=int(data_shape[0]/1e3)
    else:
        sampling=1
    
    bandpass_cal=[]
    for this_freq_idx in tqdm(freq_idx,ascii=True,desc='Bulding Cal-bandpass'):
        data_lightcurve_cal=f['SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/STOKES_0'][::sampling,this_freq_idx]
        bandpass_cal.append(partition_avg(data_lightcurve_cal,ratio_range))
    
    os.chdir(this_dir)
    return bandpass_cal


def avg_with_lightening_flag(array_dirty,idx_start,idx_end,f_avg_range =[1600,3500] ,
                    peak_ratio=1.08,stride=96,rm_bandpass=True):
    """
    It's an averaging process but it can flag-out the time points with local discharges, 
    (the very bright and vertical lines)
    """

    collect_arr = []
    collect_start = idx_start+int(stride/2)
    for idx in tqdm(np.arange(int((idx_end-idx_start)/stride)-1)):
        data_segm = array_dirty[
            (idx_start+idx*stride):(idx_start+(idx+1)*stride),:]
        data_tmp = np.nanmean((data_segm[:,f_avg_range[0]:f_avg_range[1]]),axis=1)

        dummy_true = np.ones(stride)>0
        dummy_true[1:-1] = (~((data_tmp[0:-2]*peak_ratio<data_tmp[1:-1]) | (data_tmp[1:-1]>data_tmp[2:]*peak_ratio)))
        r0 = dummy_true

        dummy_true = np.ones(stride)>0
        dummy_true[0:-2] = (~((data_tmp[0:-2]*peak_ratio<data_tmp[1:-1]) | (data_tmp[1:-1]>data_tmp[2:]*peak_ratio)))
        r1 = dummy_true

        dummy_true = np.ones(stride)>0
        dummy_true[2:] = (~((data_tmp[0:-2]*peak_ratio<data_tmp[1:-1]) | (data_tmp[1:-1]>data_tmp[2:]*peak_ratio)))
        r2 = dummy_true

        select_non_thunder = np.where(
            (data_tmp<(2*np.std(data_tmp)+np.mean(data_tmp))) 
            & (data_tmp<0.5e13)
            & r0 &r1 &r2)
        collect_arr.append(np.mean(data_segm[select_non_thunder[0],:],axis=0))
        collect_end = idx_start+int(idx*stride/2)

    ds = (np.array(collect_arr))[:,:]

    if rm_bandpass:
        mean_substract = np.mean(
            np.sort(ds,0)[
                int(ds.shape[0]*0.1):int(ds.shape[0]*0.3),:],0)

        ds = ds/ np.tile(mean_substract,(ds.shape[0],1))
        
    return ds,collect_start,collect_end



def calibration_with_1bandpass_interp(
    dyspec_target, freq_target, bandpass_calibrator, freq_cal, calibrator,
    plot_things=False):
    '''
    Calibrates the target data using a calibrator with interpolation

    Input: target dynamic spectrum the **RAW** intensity read from H5, 
        the calibrator file, the calibrator name.
    Output: the calibrated dynamic spectrum of the target source
    '''
    # read the data
    dyspec_target, freq_target
    # plot the calibrator bandpass not interpolated

    
    bandpass_interpolated = np.ones((len(freq_target)))
    # extract the frequency where the calibrator observed
    indices_in_calibrator = np.where((freq_target>np.min(freq_cal)) & (freq_target<np.max(freq_cal)))[0]
    
    # make bandpass for all the frequencies
    funct = interpolate.interp1d(freq_cal, bandpass_calibrator)
    bandpass_interpolated[indices_in_calibrator] = funct(freq_target[indices_in_calibrator])
    bandpass_interpolated[:indices_in_calibrator[0]] = bandpass_interpolated[indices_in_calibrator[0]]
    bandpass_interpolated[indices_in_calibrator[-1]:] = bandpass_interpolated[indices_in_calibrator[-1]]



    if plot_things:
        fig = plt.figure(figsize=(6, 4), dpi=120)
        ax = plt.gca()
        ax.plot(freq_cal, np.log10(bandpass_calibrator),'+')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (dB)')
        fig.savefig('bandpass_calibrator_initial.png')

        # plot the interpolated bandpass
        
        fig = plt.figure(figsize=(6, 4), dpi=120)
        ax = plt.gca()
        ax.plot(freq_target, np.log10(bandpass_interpolated),'+')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (dB)')
        fig.savefig('bandpass_calibrator_interpolated.png')

    # convert from dB to raw flux
    # dyspec_target = 10**(dyspec_target/10)
    for i in range(len(freq_target)):
        dyspec_target[:,i] = dyspec_target[:,i]/bandpass_interpolated[i]*model_flux(calibrator, freq_target[i])

    return dyspec_target