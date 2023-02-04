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
    """ get metadata from h5 file

    Args:
        f (_type_): _description_
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
                    agg_factor=[1.66, 1.66, 0.45, 0.45], device=device):

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

            if t_tmp.shape[0] >= t_c_ratio - 1:
                if flagging:
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


def averaging_stride(arr_query, n_point, axis=0, n_start=-1, n_end=-1):
    """
    Averaging for big 2D-array but small down-sample ratio
    (n_point should be small, returns a not-very-small array)
    author: Peijin Zhang
    datetime: 2022-6-14 11:14:53
    """
    if n_start < 0:
        n_start = 0
    if n_end < 0:
        n_end = arr_query.shape[axis]-1
    out_size = int((n_end-n_start)/n_point)

    res = 0
    if axis == 1:
        res = np.mean(np.array(([arr_query[:, (n_start+idx):(n_start+(out_size)*n_point+idx):n_point]
                                 for idx in range(n_point)])), axis=0)
    else:
        res = np.mean(np.array(([arr_query[(n_start+idx):(n_start+(out_size)*n_point+idx):n_point, :]
                                 for idx in range(n_point)])), axis=0)
    return res


def averaging_walk(arr_query, n_point, axis=0, n_start=-1, n_end=-1):
    """
    Averaging for big 2D-array but small big-sample ratio 
    (n_point should be large, returns a tiny array)
    author: Peijin Zhang
    datetime: 2022-6-14 11:41:57
    """
    if n_start < 0:
        n_start = 0
    if n_end < 0:
        n_end = arr_query.shape[axis]
    out_size = int((n_end-n_start)/n_point)

    res = 0
    if axis == 1:
        res = np.mean(np.stack(
            ([(arr_query[:, (n_start+idx*n_point):(n_start+(idx+1)*n_point)]) for idx in range(out_size)]), axis=2), axis=axis)
    else:
        res = np.mean(np.stack(
            ([(arr_query[(n_start+idx*n_point):(n_start+(idx+1)*n_point), :]) for idx in range(out_size)]), axis=2).swapaxes(1, 2), axis=axis)
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

    Cal_dict = {'J0133-3629': [1.0440, -0.662, -0.225],
                '3C48': [1.3253, -0.7553, -0.1914, 0.0498],
                'ForA': [2.218, -0.661],
                '3C123': [1.8017, -0.7884, -0.1035, -0.0248, 0.0090],
                'J0444-2809': [0.9710, -0.894, -0.118],
                '3C138': [1.0088, -0.4981, -0.155, -0.010, 0.022,],
                'PicA': [1.9380, -0.7470, -0.074],
                'TauA': [2.9516, -0.217, -0.047, -0.067],
                '3C247': [1.4516, -0.6961, -0.201, 0.064, -0.046, 0.029],
                '3C196': [1.2872, -0.8530, -0.153, -0.0200, 0.0201],
                'HydA': [1.7795, -0.9176, -0.084, -0.0139, 0.030],
                'VirA': [2.4466, -0.8116, -0.048],
                '3C286': [1.2481, -0.4507, -0.1798, 0.0357],
                '3C295': [1.4701, -0.7658, -0.2780, -0.0347, 0.0399],
                'HerA': [1.8298, -1.0247, -0.0951],
                '3C353': [1.8627, -0.6938, -0.100, -0.032],
                '3C380': [1.2320, -0.791, 0.095, 0.098, -0.18, -0.16],
                '3C444': [3.3498, -1.0022, -0.22, 0.023, 0.043],
                'CasA': [3.3584, -0.7518, -0.035, -0.071]}
    if calibrator in Cal_dict.keys():
        parameters = Cal_dict[calibrator]
    else:
        raise ValueError(calibrator, "is not in the calibrators list")

    flux_model = 0
    frequency /= 10**3  # convert from MHz to GHz
    for j, p in enumerate(parameters):
        flux_model += p*np.log10(frequency)**j
    flux_model = 10**flux_model  # because at first the flux is in log10
    return flux_model*10**(-4)  # convert form Jy to sfu


def partition_avg(arr, ratio_range):
    #  average in a given ratio range to exclude extreme value
    arr_sort = np.sort(arr.ravel())
    nums = arr_sort[int(ratio_range[0]*arr_sort.shape[0])                    :int(ratio_range[1]*arr_sort.shape[0])]
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
    indices_in_calibrator = np.where(
        (freq_target > np.min(freq_cal)) & (freq_target < np.max(freq_cal)))[0]

    # make bandpass for all the frequencies
    funct = interpolate.interp1d(freq_cal, bandpass_calibrator)
    bandpass_interpolated[indices_in_calibrator] = funct(
        freq_target[indices_in_calibrator])
    bandpass_interpolated[:indices_in_calibrator[0]
                          ] = bandpass_interpolated[indices_in_calibrator[0]]
    bandpass_interpolated[indices_in_calibrator[-1]                          :] = bandpass_interpolated[indices_in_calibrator[-1]]

    if plot_things:
        fig = plt.figure(figsize=(6, 4), dpi=120)
        ax = plt.gca()
        ax.plot(freq_cal, np.log10(bandpass_calibrator), '+')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (dB)')
        fig.savefig('bandpass_calibrator_initial.png')

        # plot the interpolated bandpass

        fig = plt.figure(figsize=(6, 4), dpi=120)
        ax = plt.gca()
        ax.plot(freq_target, np.log10(bandpass_interpolated), '+')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (dB)')
        fig.savefig('bandpass_calibrator_interpolated.png')

    # convert from dB to raw flux
    # dyspec_target = 10**(dyspec_target/10)
    for i in range(len(freq_target)):
        dyspec_target[:, i] = dyspec_target[:, i] / \
            bandpass_interpolated[i]*model_flux(calibrator, freq_target[i])

    return dyspec_target
