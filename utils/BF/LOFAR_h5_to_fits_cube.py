"""
Split and down sample the dynamic spectrum of LOFAR observation

Input  :  Huge hdf5 files of LOFAR Tied array beam formed observation
Output :  Data cube for quickview

============
by Peijin.Zhang & Pietro Zucca 2019.10.27

Modified  [2021-02-18]
Recommend to run in docker:
https://hub.docker.com/repository/docker/peijin/lofarsun

"""


from __future__ import absolute_import, division
import glob
import os
import json
from astropy.io import fits as fits
import lofarSun
import matplotlib.dates as mdates
import h5py
import datetime
import numpy as np
import re
from lofarSun.BF.lofarJ2000xySun import j2000xy
import matplotlib.pyplot as plt

import matplotlib as mpl
# try to use the precise epoch
mpl.rcParams['date.epoch']='1970-01-01T00:00:00'
try:
    mdates.set_epoch('1970-01-01T00:00:00')
except:
    pass

datadir = '/data/scratch/zucca/EVENT_20220519/data/TAB/' # and dir contains only h5 target data
t_downsamp = datetime.timedelta(seconds=2) # time averaging length
f_downsamp_n = 2 # freq averaging index range
t_cut_start_ratio = 0.55
t_cut_end_ratio = 0.75

x_points = 2000 # maximum gap


os.chdir(datadir)  # the dir contains the h5
fnames_DS = sorted(glob.glob('*SAP000*.h5')) # find all the h5 file of this observation
out_fname = '/data001/scratch/zhang/EVENT_20220519/EVENT_20220519.fits'

print('Loading hdf and raw')


# gather everything from the h5 files
for this_f_index in np.arange(len(fnames_DS)):
    
    
    m = re.search('B[0-9]{3}', fnames_DS[this_f_index])
    m.group(0)
    beam_this = m.group(0)[1:4]
    
    f = h5py.File( fnames_DS[this_f_index], 'r' )
    print('B'+str(this_f_index)+' | ',end='')
    data_shape = f['SUB_ARRAY_POINTING_000/BEAM_'+beam_this+'/STOKES_0'].shape

    # get shape of the BF raw
    t_lines = data_shape[0]
    f_lines = data_shape[1]

    # get the time parameters
    tsamp = f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this+"/COORDINATES/COORDINATE_0"].attrs["INCREMENT"]
    f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this].attrs['POINT_RA']
    
    tint = f["/"].attrs["TOTAL_INTEGRATION_TIME"]
    group = f["/"]
    t_start_bf = datetime.datetime.strptime(group.attrs["OBSERVATION_START_UTC"][0:26]+' +0000',
                                               '%Y-%m-%dT%H:%M:%S.%f %z')
    t_end_bf = datetime.datetime.strptime(group.attrs["OBSERVATION_END_UTC"][0:26]+' +0000',
                                               '%Y-%m-%dT%H:%M:%S.%f %z')

    # get the frequency axies
    freq = f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this+"/COORDINATES/COORDINATE_1"].attrs["AXIS_VALUES_WORLD"]/1e6

    t_start_chunk = t_start_bf

    chunk_t  = t_downsamp
    chunk_num = ((t_end_bf-t_start_chunk)/chunk_t)




    idx_mark=0
    idx_for_t_averaging = np.arange(int(chunk_num*(t_cut_end_ratio-t_cut_start_ratio))) + \
                    int(chunk_num*t_cut_start_ratio)

    for idx_cur in idx_for_t_averaging:
    # select the time
        t_start_fits = t_start_chunk + idx_cur*1.0*chunk_t
        t_end_fits   = t_start_chunk + (idx_cur+1)*1.0*chunk_t

        t_ratio_start = (mdates.date2num(t_start_fits) 
                         - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                           - mdates.date2num(t_start_bf))
        idx_start = int(t_ratio_start*(t_lines-1))

        t_ratio_end  =   (mdates.date2num(t_end_fits) 
                        - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                          - mdates.date2num(t_start_bf))
        idx_end = int(t_ratio_end*(t_lines-1))
        stokes = f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this+"/STOKES_0"][idx_start:idx_end:int((idx_end-idx_start)/x_points+1),:]
        stokes = np.abs(stokes) + 1e-7
        array_this = np.mean(np.mean(stokes,0).reshape(-1,f_downsamp_n),1).T

        if idx_mark==0:
            array_all = array_this
            idx_mark=1
            t_fits  = mdates.date2num(t_start_fits)
        else:
            array_all  = np.vstack((array_all,array_this))
            t_fits  = np.append(t_fits,mdates.date2num(t_start_fits))

    array_all_t = array_all
        
    this_ra = f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this].attrs['POINT_RA']
    this_dec = f["/SUB_ARRAY_POINTING_000/BEAM_"+beam_this].attrs['POINT_DEC']
    
    
    if this_f_index==0:
        array_all_beam = [array_all_t]
        ra_all   = this_ra
        dec_all  = this_dec
    else:
        array_all_beam = np.append(array_all_beam,[array_all_t],axis=0)
        ra_all  = np.append(ra_all, this_ra)
        dec_all = np.append(dec_all, this_dec)
        
[xx,yy] = j2000xy(ra_all,dec_all,t_start_fits)    

y_points = array_all_beam.shape[2]
freq_select_idx = np.int32(np.linspace(0,f_lines-1,y_points))
f_fits = freq[freq_select_idx]


cube_ds = array_all_beam.swapaxes(0,2)
hdu_lofar = fits.PrimaryHDU()
hdu_lofar.data = cube_ds.astype('float32')
print("Data shape:")
print(cube_ds.shape)

hdu_lofar.header['SIMPLE']    =                    True          
hdu_lofar.header['BITPIX']    =                    8 
hdu_lofar.header['NAXIS ']    =                    3          
hdu_lofar.header['NAXIS1']    =                 cube_ds.shape[0]      
hdu_lofar.header['NAXIS2']    =                 cube_ds.shape[1]      
hdu_lofar.header['NAXIS3']    =                 cube_ds.shape[2]
hdu_lofar.header['EXTEND']    =                    True               
hdu_lofar.header['DATE']      =  t_start_bf.strftime("%Y-%m-%d")         
hdu_lofar.header['CONTENT']   =  t_start_bf.strftime("%Y/%m/%d") + ' LOFAR Beamform observation '
hdu_lofar.header['ORIGIN']    = 'ASTRON Netherlands'
hdu_lofar.header['TELESCOP']  =  "LOFAR"
hdu_lofar.header['INSTRUME']  =  "LBA"          
hdu_lofar.header['OBJECT']    =  "Sun"         
hdu_lofar.header['DATE-OBS']  =  t_start_bf.strftime("%Y/%m/%d")         
hdu_lofar.header['TIME-OBS']  =  t_start_bf.strftime("%H:%M:%S.%f")       
hdu_lofar.header['DATE-END']  =  t_end_bf.strftime("%Y/%m/%d")         
hdu_lofar.header['TIME-END']  =  t_end_bf.strftime("%H:%M:%S.%f")          
hdu_lofar.header['BZERO']     =                   0. 
hdu_lofar.header['BSCALE']    =                   1. 
hdu_lofar.header['BUNIT']     = 'digits  '           
hdu_lofar.header['DATAMIN']   =                    np.min(cube_ds) 
hdu_lofar.header['DATAMAX']   =                    np.max(cube_ds) 
hdu_lofar.header['CRVAL1']    =                    f_fits[0]
hdu_lofar.header['CRPIX1']    =                    0
hdu_lofar.header['CTYPE1']    = 'FREQ'          
hdu_lofar.header['CDELT1']    =                    np.mean(np.diff(f_fits))
hdu_lofar.header['CRVAL2']    =                    t_fits[0] 
hdu_lofar.header['CRPIX2']    =                    0
hdu_lofar.header['CTYPE2']    = 'TIME'    
hdu_lofar.header['CDELT2']    =                    np.mean(np.diff(t_fits))  
hdu_lofar.header['CRVAL3']    =                    0 
hdu_lofar.header['CRPIX3']    =                    0 
hdu_lofar.header['CTYPE3']    = 'BEAM'    
hdu_lofar.header['CDELT3']    =                    1  
hdu_lofar.header['TITLE']     =  "Lofar Solar beamformed"
hdu_lofar.header['HISTORY']   = '        '    

col_f = fits.Column(name='FREQ',array=f_fits,format="D")
col_t = fits.Column(name='TIME',array=t_fits,format="D")
col_x = fits.Column(name='X',array=xx,format="D")
col_y = fits.Column(name='Y',array=yy,format="D")
hdu_f = fits.BinTableHDU.from_columns([col_f],name="FREQ")
hdu_t = fits.BinTableHDU.from_columns([col_t],name="TIME")
hdu_xy = fits.BinTableHDU.from_columns([col_x,col_y],name="BeamXY")

hdul = fits.HDUList([hdu_lofar,hdu_f,hdu_t,hdu_xy])
hdul.writeto(out_fname,overwrite=True)
