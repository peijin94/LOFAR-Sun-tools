import numpy as np
import os
import re
import datetime
from astropy.io import fits as fits
import matplotlib.dates as mdates
import h5py
import matplotlib.pyplot as plt
from scipy import interpolate
from tqdm import tqdm
import torch
from lofarSun.BF.RFIconvFlag import *

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def h5_fetch_meta(f, SAP="000"):
    """get info from the h5 file

    Args:
        f (h5 file): target h5 file
        SAP (str, optional): Sub-Array-Pointing. Defaults to "000".

    Returns:
        list: metadata of the h5 file
    """    

    root_group = f["/"]

    sap_key = 'SUB_ARRAY_POINTING_'+SAP
    beam_key, *_ = filter(lambda x: 'BEAM' in x,
                          f[sap_key].keys())
    stokes_key, *_ = filter(lambda x: 'STOKES' in x,
                            f[sap_key][beam_key].keys())

    project_id= root_group.attrs['PROJECT_ID'], 
    obs_id= root_group.attrs['OBSERVATION_ID'],

    dataset_uri = f'/{sap_key}/{beam_key}/{stokes_key}'
    coordinates_uri = f'/{sap_key}/{beam_key}/COORDINATES/COORDINATE_1'
    pointing_ra = f[f'/{sap_key}/{beam_key}'].attrs['POINT_RA']
    pointing_dec = f[f'/{sap_key}/{beam_key}'].attrs['POINT_DEC']
    tsamp = f[f'/{sap_key}/{beam_key}'].attrs["SAMPLING_TIME"]
    antenna_set_name = root_group.attrs['ANTENNA_SET']
    telescop_name = root_group.attrs['TELESCOPE']
    target_name = root_group.attrs['TARGETS'][0].strip().lower()

    # get shape of the BF raw
    t_idx_count, f_idx_count = f[dataset_uri].shape

    t_start_bf = datetime.datetime.strptime(root_group.attrs["OBSERVATION_START_UTC"][0:26] + ' +0000',
                                            '%Y-%m-%dT%H:%M:%S.%f %z')
    t_end_bf = datetime.datetime.strptime(root_group.attrs["OBSERVATION_END_UTC"][0:26] + ' +0000',
                                          '%Y-%m-%dT%H:%M:%S.%f %z')

    # get the frequency axies
    freq = f[coordinates_uri].attrs["AXIS_VALUES_WORLD"] / 1e6
    t_all = np.linspace(mdates.date2num(t_start_bf),
                        mdates.date2num(t_end_bf), t_idx_count)

    return (dataset_uri, coordinates_uri, beam_key, stokes_key, pointing_ra, pointing_dec, tsamp, 
            project_id, obs_id, antenna_set_name, telescop_name, target_name, t_idx_count, f_idx_count,
            t_start_bf, t_end_bf, freq, t_all)

# data_array_uri=f[dataset_uri]
def downsample_h5_seg_by_time_ratio(data_array_uri, t_all, t_ratio_start, t_ratio_end, t_idx_count,  
                    t_c_ratio, f_c_ratio, averaging=True, flagging=False, t_idx_cut=256,
                    agg_factor=[1.66, 1.66, 0.45, 0.45], subband_edge=False, subband_ch=16, device=device):
    """ Downsample the h5 file by time ratio

    Args:
        data_array_uri (array): dynamic spectrum
        t_all (1d array): all time stamps
        t_ratio_start (float): start time ratio (0-1)
        t_ratio_end (float): end time ratio (0-1)
        t_idx_count (int): number of total time stamps
        t_c_ratio (int): time compression ratio
        f_c_ratio (int): frequency compression ratio
        averaging (bool, optional): averaging or direct sample. Defaults to True.
        flagging (bool, optional): flagging or not. Defaults to False.
        t_idx_cut (int, optional): factor to contour segment length for processing, to make use of the memory. Defaults to 256.
        agg_factor (list, optional): factor for flagging. Defaults to [1.66, 1.66, 0.45, 0.45].
        subband_edge (bool, optional): remove one channel every [subband num] channels. Defaults to False.
        subband_ch (int, optional): number of subbands per channel. Defaults to 16.
        device (device, optional): GPU or CPU, should be something like torch.device("cuda:0") . Defaults to device.

    Returns:
        list: [averaged dynamic spectrum, time stamps]
    """    

    idx_start = int(t_ratio_start * (t_idx_count - 1))
    idx_end = int(t_ratio_end * (t_idx_count - 1))
    time_window = t_c_ratio
    freq_window = f_c_ratio

    if averaging:
        segment_len = t_idx_cut * t_c_ratio
        num_segments = int((idx_end - idx_start) * (1.0 / segment_len))+1
        stokes_list = []
        t_list = []
        for idx_segment in np.arange(num_segments):
            stokes_tmp = data_array_uri[(idx_start + idx_segment * segment_len):np.min([
                idx_start + (idx_segment + 1) * segment_len, idx_end]), :]
            t_tmp = t_all[(idx_start + idx_segment * segment_len):np.min([
                idx_start + (idx_segment + 1) * segment_len, idx_end])]
            
            if subband_edge:
                # copy the n*16-1 channel to n*16 channel
                stokes_tmp[:, 0::subband_ch] = stokes_tmp[:, 1::subband_ch]

            if t_tmp.shape[0] >= t_c_ratio - 1:
                if flagging:
                    net = RFIconv(device=device)
                    net = init_RFIconv(
                        net, aggressive_factor=agg_factor, device=device).to(device)
                    with torch.no_grad():
                        output = net(
                            torch.tensor(stokes_tmp.squeeze()[None, None, :, :]).to(device)).squeeze().cpu().numpy()

                    conv_down_after_flag = F.conv2d(
                        torch.tensor(
                            stokes_tmp[None, None, :, :] * (~output[None, None, :, :])),
                        torch.ones([1, 1, time_window, freq_window]
                                   ) / freq_window / time_window,
                        stride=(time_window, freq_window), padding=(0, 0)).squeeze().numpy()
                    conv_down_weight_after_flag = F.conv2d(torch.tensor(1 - output[None, None, :, :]) * 1.0,
                                                           torch.ones([1, 1, time_window,
                                                                       freq_window]) / freq_window / time_window,
                                                           stride=(
                                                               time_window, freq_window),
                                                           padding=(0, 0)).squeeze().numpy()
                    small_arr = conv_down_after_flag / conv_down_weight_after_flag

                else:
                    small_arr = F.conv2d(torch.tensor(stokes_tmp[None, None, :, :]),
                                         torch.ones(
                                             [1, 1, time_window, freq_window]) / freq_window / time_window,
                                         stride=(time_window, freq_window), padding=(0, 0)).squeeze().numpy()

                stokes_list.append(small_arr)
                t_list.append(avg_1d(t_tmp, t_c_ratio).ravel())
        stokes = np.concatenate(stokes_list, axis=0)
        t_fits = np.concatenate(t_list, axis=0)

    else:
        stokes = data_array_uri[
            idx_start:idx_end:t_c_ratio, ::f_c_ratio]  # sampling the data
        t_fits = t_all[idx_start:idx_end:t_c_ratio]

    data_fits = stokes

    return data_fits, t_fits


def cook_fits_spectr_hdu(data_fits, t_fits, f_fits, t_start_fits, t_end_fits, stokes_key,
                         antenna_set_name, telescop_name, target_name,
                         pointing_ra, pointing_dec, pointing_x, pointing_y):
    # create fits hdu
    hdu_lofar = fits.PrimaryHDU()
    hdu_lofar.data = data_fits
    hdu_lofar.header['SIMPLE'] = True
    hdu_lofar.header['BITPIX'] = 8
    hdu_lofar.header['NAXIS '] = 2
    hdu_lofar.header['NAXIS1'] = data_fits.shape[0]
    hdu_lofar.header['NAXIS2'] = data_fits.shape[1]
    hdu_lofar.header['EXTEND'] = True
    hdu_lofar.header['DATE'] = t_start_fits.strftime("%Y-%m-%d")
    hdu_lofar.header['CONTENT'] = t_start_fits.strftime("%Y/%m/%d") + ' LOFAR ' + \
        antenna_set_name + ' ' + stokes_key
    hdu_lofar.header['ORIGIN'] = 'ASTRON Netherlands'
    hdu_lofar.header['TELESCOP'] = telescop_name
    hdu_lofar.header['INSTRUME'] = antenna_set_name
    hdu_lofar.header['OBJECT'] = target_name
    hdu_lofar.header['DATE-OBS'] = t_start_fits.strftime("%Y/%m/%d")
    hdu_lofar.header['TIME-OBS'] = t_start_fits.strftime("%H:%M:%S.%f")
    hdu_lofar.header['DATE-END'] = t_end_fits.strftime("%Y/%m/%d")
    hdu_lofar.header['TIME-END'] = t_end_fits.strftime("%H:%M:%S.%f")
    hdu_lofar.header['BZERO'] = 0.
    hdu_lofar.header['BSCALE'] = 1.
    hdu_lofar.header['BUNIT'] = 'digits  '
    hdu_lofar.header['DATAMIN'] = max(np.nanmin(data_fits), 1.e-10)
    hdu_lofar.header['DATAMAX'] = min(np.nanmax(data_fits), 1.e20)
    hdu_lofar.header['CRVAL1'] = 74700.
    hdu_lofar.header['CRPIX1'] = 0
    hdu_lofar.header['CTYPE1'] = 'Time [UT]'
    hdu_lofar.header['CDELT1'] = 0.25
    hdu_lofar.header['CRVAL2'] = 200.
    hdu_lofar.header['CRPIX2'] = 0
    hdu_lofar.header['CTYPE2'] = 'Frequency [MHz]'
    hdu_lofar.header['CDELT2'] = -1.
    hdu_lofar.header['RA'] = pointing_ra
    hdu_lofar.header['DEC'] = pointing_dec
    hdu_lofar.header['X'] = pointing_x
    hdu_lofar.header['Y'] = pointing_y

    hdu_lofar.header['HISTORY'] = '        '
    hdu_lofar.header['STOKES'] = stokes_key

    col_freq = fits.Column(name='FREQ', format='PD',
                           array=[np.array(f_fits)])
    col_time = fits.Column(name='TIME', format='PD',
                           array=[np.array(t_fits)])
    hdu_lofar_axes = fits.BinTableHDU.from_columns([col_freq, col_time])
    full_hdu = fits.HDUList([hdu_lofar, hdu_lofar_axes])

    return full_hdu


####################
# for averaging


def avg_1d(x, N):
    """very simple averaging for 1D array

    Args:
        x (array): input 1D array
        N (int): down-sample ratio

    Returns:
        array: averaged array
    """
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N::N] - cumsum[:-N:N]) / float(N)


def averaging_stride(arr_query, n_point, axis=0, start_idx=-1, end_idx=-1):
    """
    Perform downsampling of a 2D array by averaging over strided subarrays.
    
    This function is designed for scenarios where the 2D array is large but the
    number of points to average (n_point) is small. The resulting array is not
    significantly smaller than the original.

    Parameters
    ----------
    arr_query : numpy.ndarray
        The 2D array to be downsampled.
    n_point : int
        Number of points in each strided subarray over which the averaging is performed.
    axis : int, optional
        The axis along which to average, either 0 or 1. Default is 0.
    start_idx : int, optional
        The starting index for averaging. Default is the first index of the array.
    end_idx : int, optional
        The ending index for averaging. Default is the last index of the array.

    Returns
    -------
    numpy.ndarray
        The resulting downsampled array.

    Examples
    --------
    >>> arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
    >>> averaging_stride(arr, 2, axis=0)
    Output will be the downsampled array along axis 0.

    Notes
    -----
    This function is optimized for small downsampling ratios where n_point is small.
    """
    start_idx = 0 if start_idx < 0 else start_idx
    end_idx = arr_query.shape[axis] if end_idx < 0 else end_idx
    out_size = ((end_idx-start_idx) // n_point)

    res = 0
    if axis == 1:
        res = np.mean(np.array(([arr_query[:, (start_idx+idx):(start_idx+(out_size)*n_point+idx):n_point]
                                 for idx in range(n_point)])), axis=0)
    else:
        res = np.mean(np.array(([arr_query[(start_idx+idx):(start_idx+(out_size)*n_point+idx):n_point, :]
                                 for idx in range(n_point)])), axis=0)
    return res



def averaging_walk(arr_query, n_point, axis=0, start_idx=-1, end_idx=-1):
    """
    Perform downsampling of a 2D array by averaging over contiguous subarrays.

    This function is designed for scenarios where the 2D array is large and the
    number of points to average (n_point) is also large. The result is a much
    smaller array.

    Parameters
    ----------
    arr_query : numpy.ndarray
        The 2D array to be downsampled.
    n_point : int
        Number of points in each subarray over which the averaging is performed.
    axis : int, optional
        The axis along which to average, either 0 or 1. Default is 0.
    start_idx : int, optional
        The starting index for averaging. Default is the first index of the array.
    end_idx : int, optional
        The ending index for averaging. Default is the last index of the array.

    Returns
    -------
    numpy.ndarray
        The resulting downsampled array.

    Example
    -------
    >>> arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
    >>> averaging_walk(arr, 2, axis=0)
    Output will be the downsampled array along axis 0.

    Notes
    -----
    This function is optimized for large downsampling ratios where n_point is large.
    """
    
    start_idx = 0 if start_idx < 0 else start_idx
    end_idx = arr_query.shape[axis] if end_idx < 0 else end_idx
    out_size = ((end_idx-start_idx) // n_point)

    res = 0
    if axis == 1:
        res = np.mean(np.stack(
            ([(arr_query[:, (start_idx+idx*n_point):(start_idx+(idx+1)*n_point)]) for idx in range(out_size)]), axis=2), axis=axis)
    else:
        res = np.mean(np.stack(
            ([(arr_query[(start_idx+idx*n_point):(start_idx+(idx+1)*n_point), :]) for idx in range(out_size)]), axis=2).swapaxes(1, 2), axis=axis)
    return res


def model_flux(calibrator, frequency):
    '''
    Calculates the model flux for calibration using a known set of calibrators.
    
    Parameters:
    -----------
    calibrator : str
        Name of the calibrator source.
    frequency : float
        Frequency in MHz for which to calculate the flux.
        
    Returns:
    --------
    float
        Model flux in sfu (solar flux units).
        
    Notes:
    ------
    The parameters for each calibrator source are sourced from https://arxiv.org/pdf/1609.05940.pdf.
    '''
    
    cal_params = {
        'j0133-3629': [1.0440, -0.662, -0.225],
        '3c48': [1.3253, -0.7553, -0.1914, 0.0498],
        'fora': [2.218, -0.661],
        '3c123': [1.8017, -0.7884, -0.1035, -0.0248, 0.0090],
        'j0444-2809': [0.9710, -0.894, -0.118],
        '3c138': [1.0088, -0.4981, -0.155, -0.010, 0.022],
        'pica': [1.9380, -0.7470, -0.074],
        'taua': [2.9516, -0.217, -0.047, -0.067],
        '3c247': [1.4516, -0.6961, -0.201, 0.064, -0.046, 0.029],
        '3c196': [1.2872, -0.8530, -0.153, -0.0200, 0.0201],
        'hyda': [1.7795, -0.9176, -0.084, -0.0139, 0.030],
        'vira': [2.4466, -0.8116, -0.048],
        '3c286': [1.2481, -0.4507, -0.1798, 0.0357],
        '3c295': [1.4701, -0.7658, -0.2780, -0.0347, 0.0399],
        'hera': [1.8298, -1.0247, -0.0951],
        '3c353': [1.8627, -0.6938, -0.100, -0.032],
        '3c380': [1.2320, -0.791, 0.095, 0.098, -0.18, -0.16],
        '3c444': [3.3498, -1.0022, -0.22, 0.023, 0.043],
        'casa': [3.3584, -0.7518, -0.035, -0.071]
    }
    # Fetch the parameters
    params = cal_params.get(calibrator.lower())
    
    # Check if the calibrator exists
    if params is None:
        raise ValueError(f"Invalid calibrator: {calibrator}")
        
    # Calculate the flux model
    freq_GHz = frequency / 1e3
    flux_model = sum(p * np.log10(freq_GHz) ** j for j, p in enumerate(params))
    return 10 ** flux_model * 1e-4


def partition_avg(arr, ratio_range):
    #  average in a given ratio range to exclude extreme value
    arr_sort = np.sort(arr.ravel())
    nums = arr_sort[int(ratio_range[0]*arr_sort.shape[0]) 
                    :int(ratio_range[1]*arr_sort.shape[0])]
    return np.mean(nums)


def get_cal_bandpass(freq_idx, h5dir, h5name, ratio_range=[0.2, 0.8]):
    fname_DS = h5name
    this_dir = os.getcwd()
    os.chdir(h5dir)
    m = re.search('B[0-9]{3}', fname_DS)
    beam_this = m.group(0)[1:4]
    m = re.search('SAP[0-9]{3}', fname_DS)
    SAP = m.group(0)[3:6]

    f = h5py.File(fname_DS, 'r')
    data_shape = f['SUB_ARRAY_POINTING_'+SAP +
                   '/BEAM_'+beam_this+'/STOKES_0'].shape

    if data_shape[0] > 1e3:
        sampling = int(data_shape[0]/1e3)
    else:
        sampling = 1

    bandpass_cal = []
    for this_freq_idx in tqdm(freq_idx, ascii=True, desc='Bulding Cal-bandpass'):
        data_lightcurve_cal = f['SUB_ARRAY_POINTING_'+SAP +
                                '/BEAM_'+beam_this+'/STOKES_0'][::sampling, this_freq_idx]
        bandpass_cal.append(partition_avg(data_lightcurve_cal, ratio_range))

    os.chdir(this_dir)
    return bandpass_cal


def avg_with_lightening_flag(array_dirty, idx_start, idx_end, f_avg_range=[1600, 3500],
                             peak_ratio=1.08, stride=96, rm_bandpass=True):
    """
    It's an averaging process but it can flag-out the time points with local discharges, 
    (the very bright and vertical lines)
    """

    collect_arr = []
    collect_start = idx_start+int(stride/2)
    for idx in tqdm(np.arange(int((idx_end-idx_start)/stride)-1)):
        data_segm = array_dirty[
            (idx_start+idx*stride):(idx_start+(idx+1)*stride), :]
        data_tmp = np.nanmean(
            (data_segm[:, f_avg_range[0]:f_avg_range[1]]), axis=1)

        dummy_true = np.ones(stride) > 0
        dummy_true[1:-1] = (~((data_tmp[0:-2]*peak_ratio < data_tmp[1:-1])
                            | (data_tmp[1:-1] > data_tmp[2:]*peak_ratio)))
        r0 = dummy_true

        dummy_true = np.ones(stride) > 0
        dummy_true[0:-2] = (~((data_tmp[0:-2]*peak_ratio < data_tmp[1:-1])
                            | (data_tmp[1:-1] > data_tmp[2:]*peak_ratio)))
        r1 = dummy_true

        dummy_true = np.ones(stride) > 0
        dummy_true[2:] = (~((data_tmp[0:-2]*peak_ratio < data_tmp[1:-1])
                          | (data_tmp[1:-1] > data_tmp[2:]*peak_ratio)))
        r2 = dummy_true

        select_non_thunder = np.where(
            (data_tmp < (2*np.std(data_tmp)+np.mean(data_tmp)))
            & (data_tmp < 0.5e13)
            & r0 & r1 & r2)
        collect_arr.append(
            np.mean(data_segm[select_non_thunder[0], :], axis=0))
        collect_end = idx_start+int(idx*stride/2)

    ds = (np.array(collect_arr))[:, :]

    if rm_bandpass:
        mean_substract = np.mean(
            np.sort(ds, 0)[
                int(ds.shape[0]*0.1):int(ds.shape[0]*0.3), :], 0)

        ds = ds / np.tile(mean_substract, (ds.shape[0], 1))

    return ds, collect_start, collect_end


def lin_interp(x, y, i, half):
    return x[i] + (x[i+1] - x[i]) * ((half - y[i]) / (y[i+1] - y[i]))

def FWHM(x, y):
    """
    Determine the FWHM position [x] of a distribution [y]
    """
    half = max(y)/2.0
    signs = np.sign(np.add(y, -half))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    return [lin_interp(x, y, zero_crossings_i[0], half),
            lin_interp(x, y, zero_crossings_i[-1], half)]


def DecayExpTime(x,y):
    thresh = np.max(y)/np.exp(1)
    signs = np.sign(np.add(y, -thresh))
    zero_crossings = (signs[0:-2] != signs[1:-1])
    zero_crossings_i = np.where(zero_crossings)[0]
    return [x[np.argmax(y)], lin_interp(x, y, zero_crossings_i[-1], thresh) ]


def fit_biGaussian(x,y):
    """
    Derive the best fit curve for the flux-time distribution
    """
    from scipy.optimize import curve_fit
    popt, pcov = curve_fit(biGaussian,x,y,p0=(x[np.argmax(y)],np.std(x)/3,np.std(x),1),bounds=([-np.inf,-1e-5,-1e-5,0],[np.inf,np.inf,np.inf,np.inf]))
    return popt


def biGaussian(x,x0,sig1,sig2,A):
    # combine 2 gaussian:
    return A*np.exp(-0.5*((x-x0)/
        (sig1*(x<x0)+sig2*(x>=x0)))**2)
    

def mask_extend_xy_npix(mask, n_pix_x, n_pix_y):
    """
    Extend a 2D boolean mask along both x and y axes by a specified number of pixels.
    
    This function takes a 2D mask and extends the 'False' values in both x and y directions 
    based on the number of pixels specified. The purpose is to enlarge masked areas in a 2D array 
    by including adjacent pixels.

    Parameters:
    -------------
    mask : ndarray (2D)
        A 2D boolean mask where 'True' represents areas to keep and 'False' represents areas to mask.
    n_pix_x : int
        Number of pixels to extend the mask in the x-direction.
    n_pix_y : int
        Number of pixels to extend the mask in the y-direction.

    Returns:
    -------------
    mask_extend : ndarray (2D)
        The extended 2D mask.

    """
    
    # Initialize an output mask of the same shape as the input, filled with 'True'
    mask_extend = np.ones_like(mask)
    # Loop through each row in the mask
    for i in range(mask.shape[0]):        
        # Find indices in the row where the mask is 'False'
        idx = np.where(1 - mask[i, :])[0]
        # Extend the mask in both x and y directions for each found index
        for j in idx:
            mask_extend[max(i - n_pix_y + 1, 0):min(i + n_pix_y, mask.shape[0]),
                        max(j - n_pix_x + 1, 0):min(j + n_pix_x, mask.shape[1])] = 0            
    return mask_extend



def flag_frequency_slices(dynspec_cal, mask_cal, ratio_flag=1.5, lower_perc=15, upper_perc=40):
    """
    Flag individual pixels in each frequency slice of the calibration dynamic spectrum.

    This function flags pixels based on a condition that compares the pixel value to
    the mean of a specific range of values in the dynamic spectrum.

    Parameters:
    -------------
    dynspec_cal : ndarray
        The calibration dynamic spectrum.
    mask_cal : ndarray
        The existing mask for the calibration dynamic spectrum.
    
    Returns:
    -------------
    ndarray
        Updated mask for the calibration dynamic spectrum.
    """
    for freq_idx in np.arange(dynspec_cal.shape[1]):
        mask_freq = mask_cal[:, freq_idx]
        dyspec_freq = dynspec_cal[:, freq_idx]
        
        idx = np.where(dyspec_freq > ratio_flag * np.mean(dyspec_freq[np.where(
            (dyspec_freq > np.percentile(dyspec_freq, lower_perc)) & 
            (dyspec_freq < np.percentile(dyspec_freq, upper_perc)))[0]]))[0]
        
        mask_freq[idx] = 0
        mask_cal[:, freq_idx] = mask_freq
    
    return mask_cal


def perform_linear_interpolation(dynspec_cal_copy, mask_cal, t_cal):
    """
    Perform linear interpolation for flagged pixels in each frequency slice of the dynamic spectrum.

    Parameters:
    -------------
    dynspec_cal_copy : ndarray
        Copy of the calibration dynamic spectrum that will be modified.
    mask_cal : ndarray
        The existing mask for the calibration dynamic spectrum.
    t_cal : ndarray
        Time array corresponding to the calibration dynamic spectrum.

    Returns:
    -------------
    ndarray
        The modified calibration dynamic spectrum after performing interpolation.
    """
    
    robust_fill_value = 0
    for freq_idx in np.arange(dynspec_cal_copy.shape[1]):
        mask_freq = mask_cal[:, freq_idx]
        dyspec_freq = dynspec_cal_copy[:, freq_idx]
        try:
            res_interp = np.interp(t_cal[~mask_freq], t_cal[mask_freq], dyspec_freq[mask_freq])
            robust_fill_value = np.nanmean(res_interp)
        except:
            res_interp = np.full_like(t_cal[~mask_freq], robust_fill_value)
            # print error message if interpolation fails
            print("Warning: interpolation failed for frequency slice", freq_idx)
        dynspec_cal_copy[~mask_freq, freq_idx] = res_interp.ravel()
        
    
    return dynspec_cal_copy


def proc_calib_dynspec(dynspec_sun, dynspec_cal, time_sun, freq_sun, t_cal, f_cal, abs_thresh=1e14):
    """
    Calibrate and process a dynamic spectrum using a series of masking, flagging, and interpolation steps.
    
    Parameters:
    -----------
    dynspec_sun : ndarray
        The dynamic spectrum of the Sun.
    dynspec_cal : ndarray
        The dynamic spectrum that needs to be calibrated.
    time_sun : ndarray
        The time array corresponding to the dynamic spectrum of the Sun.
    freq_sun : ndarray
        The frequency array corresponding to the dynamic spectrum of the Sun.
    t_cal : ndarray
        The time array corresponding to the dynamic spectrum that needs to be calibrated.
    f_cal : ndarray
        The frequency array corresponding to the dynamic spectrum that needs to be calibrated.
    abs_thresh : float, optional
        The absolute threshold for initial masking. Defaults to 1e14.

    Returns:
    --------
    tuple
        - calibrated_dynspec : ndarray
            The calibrated dynamic spectrum.
        - dynspec_cal : ndarray
            Original dynamic spectrum for calibration.
        - dynspec_cal_copy : ndarray
            Processed dynamic spectrum after flagging and interpolation.
        - mask_cal : ndarray
            Mask after initial flagging.
        - mask_cal_2nd : ndarray
            Mask after second round of flagging.

    """

    # Step 1: Initial masking based on absolute threshold
    mask_cal = (dynspec_cal < abs_thresh)
    
    # Step 2: Flagging pixels in each frequency slice
    mask_cal = flag_frequency_slices(dynspec_cal, mask_cal)

    # Step 3: Extending the mask
    mask_cal = mask_extend_xy_npix(mask_cal, 2, 16)
    
    # Step 4: Linear interpolation for flagged pixels
    dynspec_cal_copy = dynspec_cal.copy()
    dynspec_cal_copy = perform_linear_interpolation(dynspec_cal_copy, mask_cal, t_cal)

    # Step 5: Second round of flagging based on snapshot median
    num_all_freq = dynspec_cal_copy.shape[1]
    freq_sub_ranges = np.array_split(np.arange(num_all_freq), num_all_freq // 15)
    mask_cal_2nd = np.ones_like(dynspec_cal_copy).astype(bool)
    for freq_range in freq_sub_ranges:
        midval = np.median(dynspec_cal_copy[:, freq_range], axis=1)
        flag_exceptional = dynspec_cal_copy[:, freq_range] < midval[:, None] * 2
        mask_cal_2nd[:, freq_range] *= flag_exceptional
    
    # Step 6: Interpolation after second-round flagging
    dynspec_cal_copy = perform_linear_interpolation(dynspec_cal_copy, mask_cal_2nd, t_cal)

    # Step 7: Averaging the dynamic spectrum
    dynspec_cal_copy_averaging = averaging_stride(dynspec_cal_copy, 16, 0)
    t_cal_averaging = averaging_stride(t_cal[:, None], 16, 0)

    # Step 8: Calibrating the dynamic spectrum
    calib_bandpass = np.zeros_like(dynspec_sun)
    tmp_calib_lst = []
    for time_idx, time in enumerate(t_cal_averaging):
        tmp_calib_lst.append(np.interp(freq_sun, f_cal, dynspec_cal_copy_averaging[time_idx, :]))
    tmp_calib_arr = np.array(tmp_calib_lst)
    for freq_idx, freq in enumerate(freq_sun):
        calib_bandpass[:, freq_idx] = np.interp(time_sun, t_cal_averaging[:, 0], tmp_calib_arr[:, freq_idx])
    model_arr = np.array([model_flux('CasA', freq) for freq in freq_sun])
    model_final = np.repeat(model_arr[:, None], calib_bandpass.shape[0], axis=1).T
    calibrated_dynspec = dynspec_sun / calib_bandpass * model_final

    return calibrated_dynspec, dynspec_cal, dynspec_cal_copy, mask_cal, mask_cal_2nd

