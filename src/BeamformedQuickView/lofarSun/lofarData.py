
from scipy.io import readsav
import matplotlib.dates as mdates
from lofarSun.lofarJ2000xySun import j2000xy
import datetime
import sys
import glob
import os
from astropy.io import fits as fits
import numpy as np
from skimage import measure
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

class LofarDataBF:
    def __init__(self):
        self.fname = ''
        self.havedata = False

        self.title = ''
        self.data_cube = 0
        self.freqs_ds = 0
        self.time_ds = 0
        self.xb = 0
        self.yb = 0

    def load_sav(self, fname):
        self.fname = fname
        self.havedata = True

        data = readsav(fname, python_dict=True)

        self.title = data['ds'][0]['TITLE']
        self.data_cube = data['ds'][0]['CUBE']
        self.freqs_ds = data['ds'][0]['FREQS']
        self.time_ds = (data['ds'][0]['TIME']) / 3600 / 24 + mdates.date2num(datetime.datetime(1979, 1, 1))
        self.xb = data['ds'][0]['XB']
        self.yb = data['ds'][0]['YB']

    def load_sav_cube(self, fname):
        self.fname = fname
        self.havedata = True

        data = readsav(fname, python_dict=True)
        header_name  = 'cube_ds'

        self.title = data[header_name][0]['TITLE']
        self.data_cube = data[header_name][0]['CUBE']
        self.freqs_ds = data[header_name][0]['FREQS']
        self.time_ds = (data[header_name][0]['TIME']) / 3600 / 24 + mdates.date2num(datetime.datetime(1979, 1, 1))
        ra_beam = data[header_name][0]['RA']
        dec_beam = data[header_name][0]['DEC']
        [self.xb, self.yb] = j2000xy(ra_beam, dec_beam, mdates.num2date(self.time_ds[0]))

    def bf_image_by_idx(self,f_idx,t_idx,fov=3000,asecpix=60,extrap=True,interpm='cubic'):
        data_beam=self.data_cube[f_idx,t_idx,:]
        x = np.arange(-fov, fov, asecpix)
        y = np.arange(-fov, fov, asecpix)
        X, Y = np.meshgrid(x, y)
        method = interpm
        if extrap:
            r = 1.5*np.max(np.sqrt(self.xb**2+self.yb**2))
            theta = np.linspace(0,2*np.pi,36)
            bf_xb = np.hstack((self.xb,r*np.cos(theta)))
            bf_yb = np.hstack((self.yb,r*np.sin(theta)))
            data_beam_bf = np.hstack((data_beam,np.ones(np.size(theta))*0))#np.min(data_beam)))
        else:
            bf_xb = self.xb
            bf_yb = self.yb
            data_beam_bf = data_beam
        data_bf = griddata((bf_xb, bf_yb), data_beam_bf,
                    (X, Y), method=method, fill_value=np.min(data_beam))
        return [X,Y,data_bf]

    def bf_image_by_freq_time(self,freq,time,fov=3000,asecpix=60,extrap=True,interpm='cubic'):
        t_idx_select = (np.abs(self.time_ds - time)).argmin()
        f_idx_select = (np.abs(self.freqs_ds - time)).argmin()
        [X,Y,data_bf] = self.bf_image_by_idx(self,f_idx_select,t_idx_select,fov=fov,asecpix=asecpix,extrap=extrap,interpm=interpm)
        return [X,Y,data_bf]

    def bf_peak_size(self,X,Y,data_bf,asecpix):
        FWHM_thresh = np.max(data_bf)/2.0 #np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0
        img_bi = data_bf > FWHM_thresh
        bw_lb = measure.label(img_bi)
        rg_lb = measure.regionprops(bw_lb)
        x_peak = X[np.where(data_bf == np.max(data_bf))]
        y_peak = Y[np.where(data_bf == np.max(data_bf))]
        rg_id = bw_lb[np.where(data_bf == np.max(data_bf))]
        area_peak = rg_lb[int(rg_id)-1].area

        return x_peak,y_peak,area_peak



    def plot_bf_image_by_idx(self,f_idx,t_idx):
        if True:
            [X,Y,data_bf] = self.bf_image_by_idx(f_idx,t_idx,fov=3000,asecpix=20)
            ax = plt.gca()
            im = ax.imshow(data_bf, cmap='gist_heat',
                      origin='lower',extent=[np.min(X),np.max(X),np.min(Y),np.max(Y)])
            ax.set_xlabel('X (Arcsec)')
            ax.set_ylabel('Y (Arcsec)')
            ax.set_aspect('equal', 'box')
            plt.colorbar(im)
            FWHM_thresh = np.max(data_bf)/2.0 #np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0
            img_bi = data_bf > FWHM_thresh
            ax.contour(X,Y,data_bf,levels=[FWHM_thresh,FWHM_thresh*2*0.9],colors=['deepskyblue','forestgreen'])
            x_peak = X[np.where(data_bf == np.max(data_bf))]
            y_peak = Y[np.where(data_bf == np.max(data_bf))]
            
            ax.plot(960*np.sin(np.arange(0,2*np.pi,0.001)),
                        960*np.cos(np.arange(0,2*np.pi,0.001)),'w')
            ax.plot(x_peak,y_peak,'k+')
            plt.show()

    def write_fits(self,fdir,fprefix,f_idx,t_idx):
        """
            write the data into fits files
        """
        if self.havedata:
            cube_ds = self.data_cube[f_idx,:,:][:,t_idx,:]
            hdu_lofar = fits.PrimaryHDU()
            hdu_lofar.data = cube_ds.astype('float32')
            print(self.data_cube.shape)
            print(cube_ds.shape)
            hdu_lofar.header['SIMPLE']    =                    True          
            hdu_lofar.header['BITPIX']    =                    8 
            hdu_lofar.header['NAXIS ']    =                    3          
            hdu_lofar.header['NAXIS1']    =                 cube_ds.shape[0]      
            hdu_lofar.header['NAXIS2']    =                 cube_ds.shape[1]      
            hdu_lofar.header['NAXIS3']    =                 cube_ds.shape[2]
            hdu_lofar.header['EXTEND']    =                    True               
            hdu_lofar.header['DATE']      =  mdates.num2date(self.time_ds[t_idx[0]]).strftime("%Y-%m-%d")         
            hdu_lofar.header['CONTENT']   =  mdates.num2date(self.time_ds[t_idx[0]]).strftime("%Y/%m/%d") + ' LOFAR Beamform observation '
            hdu_lofar.header['ORIGIN']    = 'ASTRON Netherlands'
            hdu_lofar.header['TELESCOP']  =  "LOFAR"
            hdu_lofar.header['INSTRUME']  =  "LBA"          
            hdu_lofar.header['OBJECT']    =  "Sun"         
            hdu_lofar.header['DATE-OBS']  =  mdates.num2date(self.time_ds[t_idx[0]]).strftime("%Y/%m/%d")         
            hdu_lofar.header['TIME-OBS']  =  mdates.num2date(self.time_ds[t_idx[0]]).strftime("%H:%M:%S.%f")       
            hdu_lofar.header['DATE-END']  =  mdates.num2date(self.time_ds[t_idx[-1]]).strftime("%Y/%m/%d")         
            hdu_lofar.header['TIME-END']  =  mdates.num2date(self.time_ds[t_idx[-1]]).strftime("%H:%M:%S.%f")          
            hdu_lofar.header['BZERO']     =                   0. 
            hdu_lofar.header['BSCALE']    =                   1. 
            hdu_lofar.header['BUNIT']     = 'digits  '           
            hdu_lofar.header['DATAMIN']   =                    np.min(cube_ds) 
            hdu_lofar.header['DATAMAX']   =                    np.max(cube_ds) 
            hdu_lofar.header['CRVAL1']    =                    self.freqs_ds[f_idx[0]]
            hdu_lofar.header['CRPIX1']    =                    0
            hdu_lofar.header['CTYPE1']    = 'FREQ'          
            hdu_lofar.header['CDELT1']    =                    self.freqs_ds[f_idx[1]]-self.freqs_ds[f_idx[0]]
            hdu_lofar.header['CRVAL2']    =                    self.time_ds[t_idx[0]]
            hdu_lofar.header['CRPIX2']    =                    0 
            hdu_lofar.header['CTYPE2']    = 'TIME'    
            hdu_lofar.header['CDELT2']    =                    self.time_ds[t_idx[1]]-self.time_ds[t_idx[0]]  
            hdu_lofar.header['CRVAL3']    =                    0 
            hdu_lofar.header['CRPIX3']    =                    0 
            hdu_lofar.header['CTYPE3']    = 'BEAM'    
            hdu_lofar.header['CDELT3']    =                    1  
            hdu_lofar.header['HISTORY']   = '        '    

            col_f = fits.Column(name='FREQ',array=self.freqs_ds[f_idx],format="E")
            col_t = fits.Column(name='TIME',array=self.time_ds[t_idx],format="E")
            col_x = fits.Column(name='X',array=self.xb,format="E")
            col_y = fits.Column(name='Y',array=self.yb,format="E")
            hdu_f = fits.BinTableHDU.from_columns([col_f],name="FREQ")
            hdu_t = fits.BinTableHDU.from_columns([col_t],name="TIME")
            hdu_xy = fits.BinTableHDU.from_columns([col_x,col_y],name="BeamXY")

            hdul = fits.HDUList([hdu_lofar,hdu_f,hdu_t,hdu_xy])
            hdul.writeto(fprefix,overwrite=True)
    
    def write_fits_full(self,fdir,fprefix):
        if self.havedata:
            self.write_fits(fdir,fprefix,np.arange(len(self.freqs_ds)),np.arange(len(self.time_ds)))
