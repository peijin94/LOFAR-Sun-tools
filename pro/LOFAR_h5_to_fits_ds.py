#!/usr/bin/python3



'''
    File name: LOFAR_h5_to_fits.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug
    Python Version: 3.4

    Split and down sample the dynamic spectrum of LOFAR observation

    Input  :  Huge hdf5 file of LOFAR Tied array beam formed observation
    Output :  Small fits file with json and png quickview
'''



from __future__ import absolute_import, division
import glob
import os
import json
from astropy.io import fits as fits
import matplotlib.dates as mdates
import h5py
import datetime
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
this_dir = os.getcwd()


x_points = 900 # time sample points
y_points = 400 # f samples
chunk_t = datetime.timedelta(minutes=15)
chop_off = True # chop every **interger** 15 minutes [00:15,00:30,00:45....]

# note that all dirs should be absolute dir startting from '/'
os.chdir('/data/scratch/zhang/')  # the dir contains the h5
fname_DS = "L701913_SAP000_B000_S0_P000_bf.h5"
out_dir = '/data/scratch/zhang/h5_to_fits_json/output/'




def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '#'):
    """
    The process bar function.
    To see the process while processing
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end ='\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
        
        
f = h5py.File( fname_DS, 'r' )
def print_name(name):
    print(name)
#f.visit(print_name)


group = f["/"]
keys = sorted(["%s"%item for item in sorted(list(group.attrs))])
#for key in keys:
#    print(key + " = " + str(group.attrs[key]))


data_shape = f['SUB_ARRAY_POINTING_000/BEAM_000/STOKES_0'].shape


# load the BF file
f = h5py.File( fname_DS, 'r' )
data_shape = f['SUB_ARRAY_POINTING_000/BEAM_000/STOKES_0'].shape

# get shape of the BF raw
t_lines = data_shape[0]
f_lines = data_shape[1]

# get the time parameters
tsamp = f["/SUB_ARRAY_POINTING_000/BEAM_000/COORDINATES/COORDINATE_0"].attrs["INCREMENT"]
tint = f["/"].attrs["TOTAL_INTEGRATION_TIME"]

t_start_bf = datetime.datetime.strptime(group.attrs["OBSERVATION_START_UTC"].decode("utf-8")[0:26]+' +0000',
                                           '%Y-%m-%dT%H:%M:%S.%f %z')
t_end_bf = datetime.datetime.strptime(group.attrs["OBSERVATION_END_UTC"].decode("utf-8")[0:26]+' +0000',
                                           '%Y-%m-%dT%H:%M:%S.%f %z')

# get the frequency axies
freq = f["/SUB_ARRAY_POINTING_000/BEAM_000/COORDINATES/COORDINATE_1"].attrs["AXIS_VALUES_WORLD"]/1e6

if chop_off :
    t_start_chunk = mdates.num2date((np.ceil(mdates.date2num(t_start_bf)*24*4.))/4/24)
else:
    t_start_chunk = t_start_bf
    
chunk_num = ((t_end_bf-t_start_chunk)/chunk_t)

freq_select_idx = np.int32(np.linspace(0,f_lines-1,y_points))
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
    
    stokes = f["/SUB_ARRAY_POINTING_000/BEAM_000/STOKES_0"][idx_start:idx_end:int((idx_end-idx_start)/x_points+1),:]
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
    hdu_lofar.header['DATE']      =  t_start_fits.strftime("%Y-%m-%d")         
    hdu_lofar.header['CONTENT']   =  t_start_fits.strftime("%Y/%m/%d") + ' Radio Flux Intensity LOFAR ' + group.attrs['ANTENNA_SET'].decode("utf-8")
    hdu_lofar.header['ORIGIN']    = 'ASTRON Netherlands'
    hdu_lofar.header['TELESCOP']  =  group.attrs['TELESCOPE'].decode("utf-8")
    hdu_lofar.header['INSTRUME']  =  group.attrs['ANTENNA_SET'].decode("utf-8")          
    hdu_lofar.header['OBJECT']    =  group.attrs['TARGETS'][0].decode("utf-8")         
    hdu_lofar.header['DATE-OBS']  =  t_start_fits.strftime("%Y/%m/%d")         
    hdu_lofar.header['TIME-OBS']  =  t_start_fits.strftime("%H:%M:%S.%f")       
    hdu_lofar.header['DATE-END']  =  t_end_fits.strftime("%Y/%m/%d")         
    hdu_lofar.header['TIME-END']  =  t_end_fits.strftime("%H:%M:%S.%f")          
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
    
    
    col_freq = fits.Column(name='FREQUENCY', format='PD',
                     array=[np.array(f_fits)])
    col_time = fits.Column(name='TIME', format='PD',
                     array=[np.array(t_fits)])
    hdu_lofar_axes = fits.BinTableHDU.from_columns([col_freq, col_time])
    
    
    
    fname = t_start_fits.strftime("LOFAR_%Y%m%d_%H%M%S_")+group.attrs['ANTENNA_SET'].decode("utf-8")+'.fits'
    
    #full_hdu = fits.HDUList([hdu_lofar, hdu_lofar_axes])
    hdu_lofar.writeto(out_dir+fname,overwrite=True)
    fig = plt.figure(figsize=(6, 4), dpi=120)
    ax = plt.gca()
    
    data_fits_new = data_fits-np.tile(np.mean(data_fits,0),(data_fits.shape[0],1))
    ax.imshow(data_fits_new.T,aspect='auto',  origin='lower', 
               vmin=(np.mean(data_fits_new)-2*np.std(data_fits_new)),
               vmax=(np.mean(data_fits_new)+3*np.std(data_fits_new)),
               extent=[t_fits[0],t_fits[-1],f_fits[0],f_fits[-1]],cmap='inferno')
    
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (UT)')
    ax.set_ylabel('Frequency (MHz)')
    ax.set_title(hdu_lofar.header['CONTENT'])
    fig.savefig(out_dir+fname.split('.')[0]+'.png')
    
    lofar_json_dict = {}

    lofar_json_dict['telescope']= "LOFAR"
    lofar_json_dict['instrume']  =  group.attrs['ANTENNA_SET'].decode("utf-8")
    lofar_json_dict['projectID'] =  group.attrs['PROJECT_ID'].decode("utf-8")
    lofar_json_dict['obsID'] =  group.attrs['OBSERVATION_ID'].decode("utf-8")
    lofar_json_dict['source']=fname_DS
    lofar_json_dict['date']  = t_start_fits.strftime("%Y-%m-%d")
    lofar_json_dict['time']  =  t_start_fits.strftime("%H:%M:%S.%f")
    lofar_json_dict['event'] = {"detection": True ,"type":"III","level":"strong"}
    lofar_json_dict['n_freq']  = len(f_fits)
    lofar_json_dict['n_time']  = len(t_fits)
    lofar_json_dict['freq_range'] = [np.min(f_fits),np.max(f_fits)]
    lofar_json_dict['time_range'] = [t_start_fits.strftime("%Y-%m-%d %H:%M:%S.%f"),t_end_fits.strftime("%Y-%m-%d %H:%M:%S.%f")]


    #print(json.dumps(lofar_json_dict, indent=4, sort_keys=True))
    plt.close('all')
    with open(out_dir+fname.split('.')[0]+'.json', 'w') as fp:
        json.dump(lofar_json_dict, fp)


