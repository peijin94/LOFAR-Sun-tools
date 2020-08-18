#!/usr/bin/python

# note that this file is deprecated use the py_37 one

'''
    File name: display_lofar_sun.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug
    Python Version: 3.4 3.5
    
    Attenuation : This module can be used under 
    old version of python, but no longer maintained,
    please use the display_lofar_sun_py37.py with
    Python 3.7

    To plot the fits file produced by wsclean
    The coordinate transform is included

    Output flux unit : Jy/Beam
'''



import numpy as np
import os,sys
import argparse
import scipy
import scipy.ndimage
import sunpy
import sunpy.sun
from sunpy.coordinates import get_sun_P
from astropy.io import fits as fits
from numpy import cos,sin
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Ellipse
plt.ioff()

def get_cur_solar_centroid(header):
    # use the observation time to get the solar center
    [RA,DEC] = sunpy.sun.position(t=sunpy.time.parse_time(header['DATE-OBS']))
    return [RA.degree%360,DEC.degree%360]

def get_obs_image_centroid(header):
    # get the RA DEC center of the image from the solar center
    RA_obs = header['CRVAL1']
    DEC_obs = header['CRVAL2']
    return [RA_obs%360,DEC_obs%360]

def get_axis_obs(header):
    # make the header with the image
    # refer to https://www.atnf.csiro.au/computing/software/miriad/progguide/node33.html
    [RA_c,DEC_c] = get_obs_image_centroid(header)
    RA_ax_obs   = RA_c + ((np.arange(header['NAXIS1'])+1) 
                          -header['CRPIX1'])*header['CDELT1']/np.cos(header['CRVAL2'])
    DEC_ax_obs  = DEC_c+ ((np.arange(header['NAXIS2'])+1) 
                          -header['CRPIX2'])*header['CDELT2']
    return [RA_ax_obs,DEC_ax_obs]
    
def RA_DEC_shift_xy0(RA,DEC,RA_cent,DEC_cent):
    # transformation between the observed coordinate and the solar x-y coordinate
    # including the x-y shift
    x_geo = -(RA  -  RA_cent)*cos(DEC_cent)*3600
    y_geo = -(DEC_cent - DEC)*3600
    # (in arcsec)
    # the rotation angle of the sun accoording to the date
    return [x_geo,y_geo]

def sun_coord_trasform(data,header,act_r=True,act_s=False):
    # act_r : rotation operation
    # act_s : shift operation
    [RA_sun,DEC_sun] = get_cur_solar_centroid(header);
    [RA_obs,DEC_obs] = get_obs_image_centroid(header);
    x_shift_pix = (RA_sun  - RA_obs) /header['CDELT1']
    y_shift_pix = (DEC_sun - DEC_obs)/header['CDELT2']
    if act_s==False:
        x_shift_pix = 0
        y_shift_pix = 0
    rotate_angel = get_sun_P(sunpy.time.parse_time(header['DATE-OBS'])).degree
    if act_r==False:
        rotate_angel = 0
    data_tmp = scipy.ndimage.shift(data,(x_shift_pix,y_shift_pix))
    data_new = scipy.ndimage.rotate(data_tmp,rotate_angel,reshape=False)
    return data_new
    


def reduct_fits_image(fname):
    hdulist = fits.open(fname)
    hdu = hdulist[0]
    header = hdu.header
    freq = hdu.header['CRVAL3']/1e6
    data=np.zeros((hdu.header[3],hdu.header[4]), dtype=int)
    data = hdu.data
    data=data[0,0,:,:]
    [RA_sun,DEC_sun] = get_cur_solar_centroid(header)
    [RA_obs,DEC_obs] = get_obs_image_centroid(header)
    [RA_ax ,DEC_ax ] = get_axis_obs(header)

    [xx,yy] = RA_DEC_shift_xy0(RA_ax,DEC_ax,RA_obs,DEC_obs)
    data_new = sun_coord_trasform(data,header)
    return [xx,yy,data_new]

#def make_lofar_sun_map(fname):
    # TODO : to make a map data structure which will be compatible with SUNPY
#     return 0
    

def plot_image(fname,vmax_set=np.nan,log_scale=False):
    [xx,yy,data_new] = reduct_fits_image(fname)
    t_cur_datetime = sunpy.time.parse_time(fits.open(fname)[0].header['DATE-OBS'])
    solar_PA = get_sun_P(sunpy.time.parse_time(fits.open(fname)[0].header['DATE-OBS'])).degree
    freq_cur = fits.open(fname)[0].header[34]/1000000.
    b_major = fits.open(fname)[0].header['BMAJ']*3600
    b_min   = fits.open(fname)[0].header['BMIN']*3600
    b_angel = fits.open(fname)[0].header['BPA']+solar_PA # should consider the beam for the data
    #print(b_major,b_min,b_angel+solar_PA)
    fig=plt.figure(num=None, figsize=(8, 6),dpi=80)
    fig.text(1400,1800, str(int(freq_cur)) + 'MHz')
    ax = plt.gca()
    cmap_now = 'CMRmap_r'
    cmap_now = 'gist_ncar_r'
    vmin_now = 0
    if log_scale:
        data_new = 10*np.log10(data_new)
    if vmax_set>0:
        vmax_now = vmax_set
    else:
        vmax_now = 1.2*np.nanmax(data_new)
    ax.text(1400,1800, str(int(freq_cur)) + 'MHz')
    circle1 = plt.Circle((0,0), 960, color='r',fill=False)
    beam0 = Ellipse((-500, -1800), b_major, b_min, -b_angel)
    ax.text(-550,-1800,'Beam shape:',horizontalalignment='right',verticalalignment='center')
    ax.add_artist(circle1)
    ax.add_artist(beam0)
    plt.xlabel('X (ArcSec)')
    plt.ylabel('Y (ArcSec)')
    
    plt.imshow(data_new,vmin=vmin_now, vmax=vmax_now , 
                       interpolation='nearest',cmap=cmap_now, origin='lower',
                       extent=(min(xx),max(xx),min(yy),max(yy)))
    plt.colorbar()
    plt.xlim([-2500,2500])
    plt.ylim([-2500,2500])
    plt.title(str(t_cur_datetime))

    return fig


def get_beam(fname):
    solar_PA = get_sun_P(sunpy.time.parse_time(fits.open(fname)[0].header['DATE-OBS'])).degree
    b_maj =  fits.open(fname)[0].header['BMAJ']
    b_min  = fits.open(fname)[0].header['BMIN']
    b_ang = fits.open(fname)[0].header['BPA']+solar_PA # should consider the beam for the data
    return [b_maj,b_min,b_ang]

class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
        
if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(description=bcolors.BOLD+bcolors.OKBLUE+ '''
    Plot the LOFAR interferometry image of the sun, with [RA,DEC] transfered to the Heliocentric coordinate.
    [by Peijin Zhang, Pietro Zucca 2019 July]
    '''+bcolors.ENDC,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i','--input',metavar='xxx.fits', nargs='+',help="file(s) of the input fits produced by wsclean")
    parser.add_argument('-o','--output',metavar='event/img', action=readable_dir, default='.',help="output directory for the images")
    parser.add_argument('-m','--max',metavar='40.0', type=float ,help="set the vmax for all the images, if not set, use automatic value : 1.2*np.max(data)")
    parser.add_argument('-s','--show', action='store_true',help='show the image use X-window, otherwise save the plot as a png file')
    parser.add_argument('-t','--text',   action='store_true',help='display the header of the first fits file')
    parser.add_argument('-l','--log',   action='store_true', help='use log10() scale for the flux intensity in the image')
    

    
    args = parser.parse_args()
    #print(args.input)

    if (args.input) is None :
        parser.print_help()
    else:
        if args.text:
            print(repr(fits.open(args.input[0])[0].header))
        num=0
        for fname in args.input:
            print(bcolors.BOLD+bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+ 'processing ' +fname)
            if args.max is not None:
                fig = plot_image(fname,vmax_set=args.max,log_scale=args.log)
            else:
                fig = plot_image(fname)
            if args.show is True:
                plt.show(block=True)
            else:
                fig.savefig(os.path.join(args.output,'fig'+str(num).rjust(4,'0')+'.png'))   # save the figure to file
            plt.close(fig) 
            num=num+1

                
