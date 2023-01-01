#!/usr/bin/python3

DESCRIPTION = '''
    File name: LOFAR_h5_to_fits.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug
    Python Version: 3.*

    Split and down sample the dynamic spectrum of LOFAR observation

    Input  :  Huge hdf5 file of LOFAR Tied array beam formed observation
    Output :  Small fits file with json and png quickview
    
    
    +++++++++++++
    update: 
        2022-04-10: [Peijin] add beam pointing information to fits header
        2022-06-21: [Matia, Peijin] add arg parse to make it work in command line
'''


import os
import json
import datetime
from argparse import ArgumentParser

import h5py

import numpy as np

from astropy.io import fits as fits
import matplotlib.dates as mdates

import matplotlib
from sympy import arg

matplotlib.use('agg')
import matplotlib.pyplot as plt
import gc
from sunpy.coordinates.sun import sky_position as sun_position
import sunpy.coordinates.sun as sun_coord


def j2000xy(RA, DEC, t_sun):
    [RA_sun, DEC_sun] = sun_position(t_sun, False)
    rotate_angel = sun_coord.P(t_sun)

    # shift the center and transfer into arcsec
    x_shift = -(RA - RA_sun.degree) * 3600
    y_shift = (DEC - DEC_sun.degree) * 3600

    # rotate xy according to the position angle
    xx = x_shift * np.cos(-rotate_angel.rad) - y_shift * np.sin(-rotate_angel.rad)
    yy = x_shift * np.sin(-rotate_angel.rad) + y_shift * np.cos(-rotate_angel.rad)
    return [xx, yy]


def parse_args():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('beamformed_dataset', help='Input BeamFormed dataproduct')
    parser.add_argument('output_directory', help='output directory')

    parser.add_argument('--time_samples', help='time sample points', type=int, default=1800)
    parser.add_argument('--frequency_samples', help='number of samples of the frequency', type=int, default=800)

    parser.add_argument('--time_chunks', help='time chunks in minutes', type=int, default=30)
    parser.add_argument('--chop_off', help='chop every **interger** 15 minutes [00:15,00:30,00:45....]',
                        action='store_false')
    parser.add_argument('--averaging', help='use averaging to downsize, otherwise use sampling',
                        action='store_true')

    return parser.parse_args()



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


def read_file(fname_DS, time_samples, frequency_samples, time_chunks, chop_off, out_dir,averaging=True):
    """
    fname_DS: relative (or absolute) directory+fname to the .h5
    out_dir: relative (or absolute) directory+fname to the .h5
    """
    time_chunks = datetime.timedelta(minutes=time_chunks)
    h5_dir = os.path.dirname(fname_DS)
    h5_fname =  os.path.basename(fname_DS)
    out_dir = os.path.abspath(out_dir)
    os.chdir(h5_dir)
    f = h5py.File(h5_fname, 'r')
    root_group = f["/"]

    beam_key, *_ = filter(lambda x: 'BEAM' in x, f['SUB_ARRAY_POINTING_000'].keys())
    print('Found beam', beam_key)
    stokes_key, *_ = filter(lambda x: 'STOKES' in x, f['SUB_ARRAY_POINTING_000'][beam_key].keys())
    print('Stokes key', stokes_key)

    dataset_uri = f'/SUB_ARRAY_POINTING_000/{beam_key}/{stokes_key}'
    coordinates_uri = f'/SUB_ARRAY_POINTING_000/{beam_key}/COORDINATES/COORDINATE_1'
    pointing_ra = f[f'/SUB_ARRAY_POINTING_000/{beam_key}'].attrs['POINT_RA']
    pointing_dec = f[f'/SUB_ARRAY_POINTING_000/{beam_key}'].attrs['POINT_DEC']
    # load the BF file
    data_shape = f[dataset_uri].shape

    # get shape of the BF raw
    t_lines = data_shape[0]
    f_lines = data_shape[1]

    t_start_bf = datetime.datetime.strptime(root_group.attrs["OBSERVATION_START_UTC"][0:26] + ' +0000',
                                            '%Y-%m-%dT%H:%M:%S.%f %z')
    t_end_bf = datetime.datetime.strptime(root_group.attrs["OBSERVATION_END_UTC"][0:26] + ' +0000',
                                          '%Y-%m-%dT%H:%M:%S.%f %z')

    # get the frequency axies
    freq = f[coordinates_uri].attrs["AXIS_VALUES_WORLD"] / 1e6

    if chop_off:
        t_start_chunk = t_start_bf.replace(minute=int(np.ceil(t_start_bf.minute / 15) * 15),
                                           second=0,
                                           microsecond=0)
    else:
        t_start_chunk = t_start_bf
    chunk_num = int(np.floor((t_end_bf - t_start_chunk) / time_chunks))

    freq_select_idx = np.int32(np.linspace(0, f_lines - 1, frequency_samples))
    f_fits = freq[freq_select_idx]
    os.makedirs(out_dir, exist_ok=True)

    for idx_cur in range(chunk_num):
        print('processing chunk', idx_cur + 1, 'of', chunk_num)
        # select the time
        t_start_fits = t_start_chunk + idx_cur * 1.0 * time_chunks
        t_end_fits = t_start_chunk + (idx_cur + 1) * 1.0 * time_chunks

        t_ratio_start = (mdates.date2num(t_start_fits)
                         - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                           - mdates.date2num(t_start_bf))
        idx_start = int(t_ratio_start * (t_lines - 1))

        t_ratio_end = (mdates.date2num(t_end_fits)
                       - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                         - mdates.date2num(t_start_bf))
        idx_end = int(t_ratio_end * (t_lines - 1))
        pointing_x, pointing_y = j2000xy(pointing_ra, pointing_dec, t_start_fits)

        if averaging:
            stokes = averaging_stride(f[dataset_uri],int((idx_end - idx_start) / time_samples + 1),axis=0,
                    n_start=idx_start,n_end=idx_end)
        else:
            stokes = f[dataset_uri][
                 idx_start:idx_end:int((idx_end - idx_start) / time_samples + 1),
                 :]
        data_fits = 10.0 * np.log10(stokes, where=stokes > 0)[:, freq_select_idx]
        t_fits = np.linspace(mdates.date2num(t_start_fits), mdates.date2num(t_end_fits), data_fits.shape[0])

        hdu_lofar = fits.PrimaryHDU()
        hdu_lofar.data = data_fits
        hdu_lofar.header['SIMPLE'] = True
        hdu_lofar.header['BITPIX'] = 8
        hdu_lofar.header['NAXIS '] = 2
        hdu_lofar.header['NAXIS1'] = time_samples
        hdu_lofar.header['NAXIS2'] = frequency_samples
        hdu_lofar.header['EXTEND'] = True
        hdu_lofar.header['DATE'] = t_start_fits.strftime("%Y-%m-%d")
        hdu_lofar.header['CONTENT'] = t_start_fits.strftime("%Y/%m/%d") + ' Radio Flux Intensity LOFAR ' + \
                                      root_group.attrs['ANTENNA_SET']
        hdu_lofar.header['ORIGIN'] = 'ASTRON Netherlands'
        hdu_lofar.header['TELESCOP'] = root_group.attrs['TELESCOPE']
        hdu_lofar.header['INSTRUME'] = root_group.attrs['ANTENNA_SET']
        hdu_lofar.header['OBJECT'] = root_group.attrs['TARGETS'][0]
        hdu_lofar.header['DATE-OBS'] = t_start_fits.strftime("%Y/%m/%d")
        hdu_lofar.header['TIME-OBS'] = t_start_fits.strftime("%H:%M:%S.%f")
        hdu_lofar.header['DATE-END'] = t_end_fits.strftime("%Y/%m/%d")
        hdu_lofar.header['TIME-END'] = t_end_fits.strftime("%H:%M:%S.%f")
        hdu_lofar.header['BZERO'] = 0.
        hdu_lofar.header['BSCALE'] = 1.
        hdu_lofar.header['BUNIT'] = 'digits  '
        hdu_lofar.header['DATAMIN'] = np.min(data_fits)
        hdu_lofar.header['DATAMAX'] = np.max(data_fits)
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

        col_freq = fits.Column(name='FREQ', format='PD',
                               array=[np.array(f_fits)])
        col_time = fits.Column(name='TIME', format='PD',
                               array=[np.array(t_fits)])
        hdu_lofar_axes = fits.BinTableHDU.from_columns([col_freq, col_time])

        fname = t_start_fits.strftime("LOFAR_%Y%m%d_%H%M%S_") + root_group.attrs['ANTENNA_SET']  # + '.fits'

        out_path_fits = os.path.join(out_dir, fname + '.fits')
        out_path_png = os.path.join(out_dir, fname + '.png')
        out_path_json = os.path.join(out_dir, fname + '.json')

        full_hdu = fits.HDUList([hdu_lofar, hdu_lofar_axes])

        full_hdu.writeto(out_path_fits, overwrite=True)
        fig = plt.figure(figsize=(6, 4), dpi=120)
        ax = plt.gca()

        data_fits_new = data_fits - np.mean(
            np.sort(data_fits,0)[
                int(data_fits.shape[0]*0.1):int(data_fits.shape[0]*0.3),:],0)
        
        #np.tile(np.mean(data_fits, 0), (data_fits.shape[0], 1))
        ax.imshow(data_fits_new.T, aspect='auto', origin='lower',
                  vmin=(np.mean(data_fits_new) - 2 * np.std(data_fits_new)),
                  vmax=(np.mean(data_fits_new) + 3 * np.std(data_fits_new)),
                  extent=[t_fits[0], t_fits[-1], f_fits[0], f_fits[-1]], cmap='inferno')

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.set_xlabel('Time (UT)')
        ax.set_ylabel('Frequency (MHz)')
        ax.set_title(hdu_lofar.header['CONTENT'])
        fig.savefig(out_path_png)
        plt.close('all')

        lofar_json_dict = {'telescope': "LOFAR", 'instrume': root_group.attrs['ANTENNA_SET'],
                           'projectID': root_group.attrs['PROJECT_ID'], 'obsID': root_group.attrs['OBSERVATION_ID'],
                           'source': fname_DS, 'date': t_start_fits.strftime("%Y-%m-%d"),
                           'ra': pointing_ra,
                           'dec': pointing_dec,
                           'x': pointing_x,
                           'y': pointing_y,
                           'time': t_start_fits.strftime("%H:%M:%S.%f"),
                           'event': {"no_detection": True, "type": "none", "level": "none"}, 'n_freq': len(f_fits),
                           'n_time': len(t_fits), 'freq_range': [np.min(f_fits), np.max(f_fits)],
                           'time_range': [t_start_fits.strftime("%Y-%m-%d %H:%M:%S.%f"),
                                          t_end_fits.strftime("%Y-%m-%d %H:%M:%S.%f")]}

        with open(out_path_json, 'w') as fp:
            json.dump(lofar_json_dict, fp)

        gc.collect()


def main():
    args = parse_args()
    read_file(args.beamformed_dataset,
              args.time_samples,
              args.frequency_samples,
              args.time_chunks,
              args.chop_off,
              args.output_directory,
              args.averaging)


if __name__ == '__main__':
    main()
