#!/usr/bin/python3


'''
    File name: LOFAR_H5_calibrate_fits.py
    Author: Cristina Cordun, Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug
    Python Version: 3.*

    Split and down sample the dynamic spectrum of LOFAR observation
    After that, calibrate the data with the help of a calibrator with a known model. The code works for the following calibrators:
    J0133-3629, 3C48, Fornax A, 3C 123, J0444+2809, 3C138, Pictor A, Taurus A, 3C147, 3C196, Hydra A, Virgo A, 
    3C286, 3C295, Hercules A, 3C353, 3C380, Cygnus A, 3C444, Cassiopeia A

    Input  :  Huge hdf5 file of LOFAR Tied array beam formed observation of the target source and its calibrator
    Output :  Small fits file with json and png quickview of the calibrated source
    
    
    +++++++++++++
    update: 
        2022-04-10: [Peijin] add beam pointing information to fits header
        2022-06-10: [Cristina] add feature cross calibration
        2022-06-10: [Peijin] Read calibrator name from H5 header
'''


from __future__ import absolute_import, division
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
matplotlib.use('agg')
import matplotlib.pyplot as plt

from lofarSun.BF.bfutil import model_flux

this_dir = os.getcwd()

import matplotlib as mpl
# try to use the precise epoch
mpl.rcParams['date.epoch']='1970-01-01T00:00:00'
try:
    mdates.set_epoch('1970-01-01T00:00:00')
except:
    pass



x_points = 900 # time sample points
y_points = -1 # f samples  (-1 for not down sampling, keep origional) 
chunk_t = datetime.timedelta(minutes=10)
chop_off = False # chop every **interger** 15 minutes [00:15,00:30,00:45....]

# IMORTANT!! give absolute (or relative) paths to the next array: first of the calibrator, and then of the target source
h5dirs = ['../h5testdata/cal/','../h5testdata/sun/']
out_dir_base = '../h5testdata/out/' # should be absolute dir starting from '/'
#calibrator_name = 'Cassiopeia A'
SAP_calibrator = '001'
SAP_target = '000'
work_dir = os.getcwd()

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '#'):
    '''
    The process bar function.
    To see the process while processing
    '''
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end ='\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
        
        
def print_name(name):
    print(name)
#f.visit(print_name)


def read_file(fname):
    '''
    This function reads a typical LOFAR LBA fits file

    Input: the path+name of the file
    Output: the dynamic spectrum, frequencies vector and time vector
    '''
    hdu = fits.open(fname)
    dyspec = hdu[0].data
    f_fits = hdu[1].data['FREQ'][:]
    t_fits = hdu[2].data['TIME'][:]
    return dyspec,f_fits,t_fits
 
def calibration(target_file, calibrator_file, calibrator):
    '''
    Calibrates the target data using a calibrator

    Input: the target file, the calibrator file, the calibrator name.
    Output: the calibrated dynamic spectrum of the target source
    '''
    # read the data
    dyspec_c, f_fits_c, t_fits_c  = read_file(calibrator_file)
    dyspec_target, f_fits_target, t_fits_target = read_file(target_file)
    
    # convert from dB to raw flux
    dyspec_c = 10**(dyspec_c/10)
    dyspec_target = 10**(dyspec_target/10)
    
    # code for averaging every 1 second: it does not solve the fluctuations
    # convert the data from raw units to sfu
    # duration = 0.0006991 # average every half a minute
    # for i in range(f_fits_target.shape[0]):
    #     time_start = t_fits_target[0]
    #     t_start = 0
    #     for t_end,t in enumerate(t_fits_c):
    #         if t-time_start > duration:
    #             dyspec_c[t_start:t_end,i] = np.mean(dyspec_c[t_start:t_end,i])
    #             time_start = t_fits_c[t_end+1]
    #             t_start = t_end+1
    #     dyspec_target[:,i] = dyspec_target[:,i]/dyspec_c[:,i]*model_flux(calibrator, f_fits_c[i])
    # return dyspec_target, f_fits_target, t_fits_target # the calibrated image in sfu, its frequency and time range

    for i in range(f_fits_target.shape[0]):
        dyspec_target[:,i] = dyspec_target[:,i]/dyspec_c[:,i]*model_flux(calibrator, f_fits_c[i])
    return dyspec_target, f_fits_target, t_fits_target # the calibrated image in sfu, its frequency and time range


# convert h5 to fits for both the source and the calibrator
calibrator_read = True
calibrator_name = ''
for h5dir in h5dirs:
    os.chdir(work_dir) # go back home
    os.chdir(h5dir)  # the dir contains the h5
    if calibrator_read == True:
        calibrator_read = False
        out_dir_base_local = 'calibrator_fits' 
        SAP = SAP_calibrator
    else:
        out_dir_base_local = 'Sun_fits'
        SAP = SAP_target

    for fname_DS in glob.glob('./*.h5'):
        
        m = re.search('B[0-9]{3}', fname_DS)
        m.group(0)
        beam_this = m.group(0)[1:4]

        f = h5py.File( fname_DS, 'r' )
        group = f['/']
        #keys = sorted(['%s'%item for item in sorted(list(group.attrs))])
        
        # obtain name of calibrator
        target_obs = group.attrs['TARGETS']
        calibrator_name = [x for x in target_obs if x!='Sun'][0]
        
        data_shape = f['SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/STOKES_0'].shape

        # get shape of the BF raw
        t_lines = data_shape[0]
        f_lines = data_shape[1]

        # get the time parameters
        tsamp = f['/SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/COORDINATES/COORDINATE_0'].attrs['INCREMENT']
        tint = f['/'].attrs['TOTAL_INTEGRATION_TIME']


        t_start_bf = datetime.datetime.strptime(group.attrs['OBSERVATION_START_UTC'][0:26]+' +0000',
                                                '%Y-%m-%dT%H:%M:%S.%f %z')
        t_end_bf = datetime.datetime.strptime(group.attrs['OBSERVATION_END_UTC'][0:26]+' +0000',
                                                '%Y-%m-%dT%H:%M:%S.%f %z')
        
        out_dir = out_dir_base_local+fname_DS.split('/')[-1].split('.')[0]+'/'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)


        # get the frequency axies
        freq = f['/SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/COORDINATES/COORDINATE_1'].attrs['AXIS_VALUES_WORLD']/1e6
        this_ra = f['/SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this].attrs['POINT_RA']
        this_dec = f['/SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this].attrs['POINT_DEC']

        if chop_off :
            t_start_chunk = mdates.num2date((np.ceil(mdates.date2num(t_start_bf)*24*4.))/4/24)
        else:
            t_start_chunk = t_start_bf

        chunk_num = ((t_end_bf-t_start_chunk)/chunk_t)

        if y_points>0:
            freq_select_idx = np.int32(np.linspace(0,f_lines-1,y_points))
        else:
            freq_select_idx = np.arange(f_lines)
        
        f_fits = freq[freq_select_idx]


        for idx_cur in np.arange(int(chunk_num)):
            printProgressBar(idx_cur + 1, int(chunk_num), prefix = 'Progress:', suffix = 'Complete', length = 50)

            # select the time
            t_start_fits = t_start_chunk + idx_cur*1.0*chunk_t
            t_end_fits  = t_start_chunk + (idx_cur+1)*1.0*chunk_t

            t_ratio_start = (mdates.date2num(t_start_fits) 
                            - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                            - mdates.date2num(t_start_bf))
            idx_start = int(t_ratio_start*(t_lines-1))

            t_ratio_end  =   (mdates.date2num(t_end_fits) 
                            - mdates.date2num(t_start_bf)) / (mdates.date2num(t_end_bf)
                                                            - mdates.date2num(t_start_bf))
            idx_end = int(t_ratio_end*(t_lines-1))

            stokes = f['/SUB_ARRAY_POINTING_'+SAP+'/BEAM_'+beam_this+'/STOKES_0'][idx_start:idx_end:int((idx_end-idx_start)/x_points+1),:]
            stokes = np.abs(stokes) + 1e-7
            data_fits = 10.0*np.log10(stokes)[:,freq_select_idx]
            t_fits = np.linspace(mdates.date2num(t_start_fits),mdates.date2num(t_end_fits),data_fits.shape[0])

            hdu_lofar = fits.PrimaryHDU()
            hdu_lofar.data = data_fits
            hdu_lofar.header['SIMPLE']    =                    True          
            hdu_lofar.header['BITPIX']    =                    8 
            hdu_lofar.header['NAXIS ']    =                    2          
            hdu_lofar.header['NAXIS1']    =                 x_points          
            hdu_lofar.header['NAXIS2']    =                 y_points          
            hdu_lofar.header['EXTEND']    =                    True               
            hdu_lofar.header['DATE']      =  t_start_fits.strftime('%Y-%m-%d')         
            hdu_lofar.header['CONTENT']   =  t_start_fits.strftime('%Y/%m/%d') + ' Radio Flux Intensity LOFAR ' + group.attrs['ANTENNA_SET']
            hdu_lofar.header['ORIGIN']    = 'ASTRON Netherlands'
            hdu_lofar.header['TELESCOP']  =  group.attrs['TELESCOPE']
            hdu_lofar.header['INSTRUME']  =  group.attrs['ANTENNA_SET']          
            hdu_lofar.header['OBJECT']    =  group.attrs['TARGETS'][0]         
            hdu_lofar.header['DATE-OBS']  =  t_start_fits.strftime('%Y/%m/%d')         
            hdu_lofar.header['TIME-OBS']  =  t_start_fits.strftime('%H:%M:%S.%f')       
            hdu_lofar.header['DATE-END']  =  t_end_fits.strftime('%Y/%m/%d')         
            hdu_lofar.header['TIME-END']  =  t_end_fits.strftime('%H:%M:%S.%f')          
            hdu_lofar.header['BZERO']     =                   0. 
            hdu_lofar.header['BSCALE']    =                   1. 
            hdu_lofar.header['BUNIT']     = 'digits  '           
            hdu_lofar.header['DATAMIN']   =                  np.min(data_fits) 
            hdu_lofar.header['DATAMAX']   =                  np.max(data_fits) 
            hdu_lofar.header['CRVAL1']    =               74700. 
            hdu_lofar.header['CRPIX1']    =                    0 
            hdu_lofar.header['CTYPE1']    = 'Time [UT]'          
            hdu_lofar.header['CDELT1']    =                 0.25 
            hdu_lofar.header['CRVAL2']    =                 200. 
            hdu_lofar.header['CRPIX2']    =                    0 
            hdu_lofar.header['CTYPE2']    = 'Frequency [MHz]'    
            hdu_lofar.header['CDELT2']    =                  -1.  
            hdu_lofar.header['HISTORY']   = '        '      
            hdu_lofar.header['BEAM-RA']   = this_ra 
            hdu_lofar.header['BEAM-DEC']   = this_dec    


            col_freq = fits.Column(name='FREQ', format='D',array=f_fits)
            col_time = fits.Column(name='TIME', format='D',array=t_fits)
            
            hdu_f = fits.BinTableHDU.from_columns([col_freq],name="FREQ")
            hdu_t = fits.BinTableHDU.from_columns([col_time],name="TIME")

            fname = t_start_fits.strftime('LOFAR_%Y%m%d_%H%M%S_')+group.attrs['ANTENNA_SET']+'.fits'

            #full_hdu = fits.HDUList([hdu_lofar, hdu_lofar_axes])
            
            hdul = fits.HDUList([hdu_lofar,hdu_f,hdu_t])
            hdul.writeto(out_dir+fname,overwrite=True)
            fig = plt.figure(figsize=(6, 4), dpi=120)
            ax = plt.gca()

            
            bandpass_arr = [np.mean(tmp[np.where((tmp>np.sort(tmp)[int(0.03*tmp.shape[0])]) 
                        & (tmp<np.sort(tmp)[int(0.2*tmp.shape[0])]))])  for tmp in list(data_fits.T)]

            data_fits_new = data_fits-np.tile(np.mean(data_fits,0),(data_fits.shape[0],1))
            data_fits_new = data_fits-np.tile(bandpass_arr,(data_fits.shape[0],1))

            im = ax.imshow(data_fits_new.T,aspect='auto',  origin='lower', 
                    vmin=(np.mean(data_fits_new)-2*np.std(data_fits_new)),
                    vmax=(np.mean(data_fits_new)+3*np.std(data_fits_new)),
                    extent=[t_fits[0],t_fits[-1],f_fits[0],f_fits[-1]],cmap='inferno')

            ax.xaxis_date()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.set_xlabel('Time (UT)')
            ax.set_ylabel('Frequency (MHz)')
            ax.set_title(hdu_lofar.header['CONTENT'])
            cbar = plt.colorbar(im)
            cbar.set_label('Power [dB]', rotation = 270, verticalalignment='baseline')
            fig.savefig(out_dir+fname.split('.')[0]+'.png')

            lofar_json_dict = {}

            lofar_json_dict['telescope']= 'LOFAR'
            lofar_json_dict['instrume']  =  group.attrs['ANTENNA_SET']
            lofar_json_dict['projectID'] =  group.attrs['PROJECT_ID']
            lofar_json_dict['obsID'] =  group.attrs['OBSERVATION_ID']
            lofar_json_dict['source']=fname_DS
            lofar_json_dict['date']  = t_start_fits.strftime('%Y-%m-%d')
            lofar_json_dict['time']  =  t_start_fits.strftime('%H:%M:%S.%f')
            lofar_json_dict['event'] = {'detection': True ,'type':'III','level':'strong'}
            lofar_json_dict['n_freq']  = len(f_fits)
            lofar_json_dict['n_time']  = len(t_fits)
            lofar_json_dict['freq_range'] = [np.min(f_fits),np.max(f_fits)]
            lofar_json_dict['time_range'] = [t_start_fits.strftime('%Y-%m-%d %H:%M:%S.%f'),t_end_fits.strftime('%Y-%m-%d %H:%M:%S.%f')]


            #print(json.dumps(lofar_json_dict, indent=4, sort_keys=True))
            plt.close('all')
            with open(out_dir+fname.split('.')[0]+'.json', 'w') as fp:
                json.dump(lofar_json_dict, fp)

print('Calibrator:',calibrator_name)


# calibrate the target source with the help of the calibrator with fits files

# go back home
os.chdir(work_dir)
# save the name of the files
names_calibrator = []
names_sun = []
calibrator = True
for h5dir in h5dirs:
    if calibrator == True:
        for file in os.listdir(h5dir+'/calibrator_fits'):
            if file.endswith(".fits"):
                path_calibrator = h5dir+'/calibrator_fits/'
                names_calibrator.append(file)
        calibrator = False
    else: 
        for file in os.listdir(h5dir+'/Sun_fits'):
            if file.endswith(".fits"):
                path_sun = h5dir+'/Sun_fits/'
                names_sun.append(file)


# calibrate file by file
for i in range(len(names_calibrator)):
    data_calibrated, f_fits, t_fits = calibration(path_sun+names_sun[i],path_calibrator+names_calibrator[i],calibrator_name)
    hdu = fits.open(path_sun+names_sun[i])
    hdu[0].data = data_calibrated

    if not os.path.exists(out_dir_base):
        os.makedirs(out_dir_base)

    hdul.writeto(out_dir_base+names_sun[i],overwrite=True)

    fig = plt.figure(figsize=(6, 4), dpi=120)
    ax = plt.gca()
   
    data_fits_new = np.log10(data_calibrated)
    im = ax.imshow((data_fits_new.T),aspect='auto',  origin='lower', 
            extent=[t_fits[0],t_fits[-1],f_fits[0],f_fits[-1]],cmap='inferno')#, norm=matplotlib.colors.LogNorm())

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.setp(ax.get_xticklabels(), rotation=20, fontsize=10)
    ax.set_xlabel('Time (UT)')
    ax.set_ylabel('Frequency (MHz)')
    ax.set_title(hdu_lofar.header['CONTENT'])
    
    cbar = plt.colorbar(im, ax = ax)
    cbar.set_label(r'$\rm log_{10}(Flux [sfu])$', rotation = 270, verticalalignment='baseline')
    fig.savefig(out_dir_base+names_sun[i][:-5]+'.png')