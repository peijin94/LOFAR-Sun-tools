
from scipy.io import readsav
import matplotlib.dates as mdates
from lofarSun.lofarJ2000xySun import j2000xy
import datetime
import sys
import glob
import os
from astropy.io import fits as fits
import numpy as np
import matplotlib.pyplot as plt

class LofarData:
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

    def write_fits(self,dir,file_name,cutdata=1):
        """
            write the data into fits files
        """
        if self.havedata:
            pass


