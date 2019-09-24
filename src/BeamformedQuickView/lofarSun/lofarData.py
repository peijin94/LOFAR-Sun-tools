
from scipy.io import readsav
import matplotlib.dates as mdates
from lofarSun.lofarJ2000xySun import j2000xy
import datetime
import sys
import glob
import os
from astropy.io import fits as fits
import numpy as np
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

    def write_fits(self,dir,file_prefix,t_idx,f_idx):
        """
            write the data into fits files
        """
        if self.havedata:
            cube_ds = self.data_cube[f_idx,t_idx,:]

