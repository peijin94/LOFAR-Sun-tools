from scipy.io import readsav
import matplotlib.dates as mdates
from matplotlib import rcParams

#import datetime,glob, os

from astropy import units as u
from astropy.coordinates import EarthLocation, SkyCoord
from astropy.io import fits
from astropy.time import Time

import numpy as np
import matplotlib.pyplot as plt

import sunpy
import sunpy.map
from sunpy.coordinates.sun import sky_position, P, earth_distance
from sunpy.coordinates import frames
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
import scipy.ndimage
from matplotlib.patches import Ellipse

from lofarSun.cli import pyms_utils

# try to use the precise epoch
rcParams['date.epoch'] = '1970-01-01T00:00:00'
try:
    mdates.set_epoch('1970-01-01T00:00:00')
except:
    pass


class IMdata:
    def __init__(self):
        self.havedata = False
        self.data = np.zeros(1)
        self.t_obs = np.zeros(1)
        self.freq = np.zeros(1)
        self.xx = np.zeros(1)
        self.yy = np.zeros(1)
        self.data_xy_calib = np.zeros(1)
        self.beamArea = np.zeros(1)
        self.fname = ''

    def load_fits(self, fname):
        if len(fname) > 0:
            self.havedata = True
            self.fname = fname
            hdulist = fits.open(fname)
            hdu = hdulist[0]
            self.header = hdu.header
            self.t_obs = sunpy.time.parse_time(
                self.header['DATE-OBS']).datetime
            self.freq = hdu.header['CRVAL3']/1e6
            data = np.zeros((hdu.header[3], hdu.header[4]), dtype=int)
            data = hdu.data
            self.data = data[0, 0, :, :]
            [RA_sun, DEC_sun] = self.get_cur_solar_centroid(t_obs=self.t_obs)
            [RA_obs, DEC_obs] = self.get_obs_image_centroid(self.header)
            [RA_ax, DEC_ax] = self.get_axis_obs(self.header)

            [self.xx, self.yy] = self.RA_DEC_shift_xy0(
                RA_ax, DEC_ax, RA_obs, DEC_obs)
            self.data_xy = self.sun_coord_trasform(
                self.data, self.header, True, True)
            [b_maj, b_min, b_ang] = self.get_beam()
            self.beamArea = (b_maj/180*np.pi) * \
                (b_min/180*np.pi)*np.pi / (4*np.log(2))
            self.data_xy_calib = self.data_xy * \
                (300/self.freq)**2/2/(1.38e-23)/1e26/self.beamArea

    def get_cur_solar_centroid(self, t_obs):
        # use the observation time to get the solar center
        [RA, DEC] = sky_position(t=t_obs, equinox_of_date=False)
        return [RA.degree % 360, DEC.degree % 360]

    def get_obs_image_centroid(self, header):
        # get the RA DEC center of the image from the solar center
        RA_obs = header['CRVAL1']
        DEC_obs = header['CRVAL2']
        return [RA_obs % 360, DEC_obs % 360]

    def get_axis_obs(self, header):
        # make the header with the image
        # refer to https://www.atnf.csiro.au/computing/software/miriad/progguide/node33.html
        if self.havedata:
            [RA_c, DEC_c] = self.get_obs_image_centroid(self.header)
            RA_ax_obs = RA_c + ((np.arange(header['NAXIS1'])+1)
                                - header['CRPIX1'])*header['CDELT1']/np.cos((header['CRVAL2'])/180.*np.pi)
            DEC_ax_obs = DEC_c + ((np.arange(header['NAXIS2'])+1)
                                  - header['CRPIX2'])*header['CDELT2']
            return [RA_ax_obs, DEC_ax_obs]
        else:
            print("No data loaded")

    def RA_DEC_shift_xy0(self, RA, DEC, RA_cent, DEC_cent):
        # transformation between the observed coordinate and the solar x-y coordinate
        # including the x-y shift
        x_geo = -(RA - RA_cent)*np.cos(DEC_cent/180.*np.pi)*3600
        y_geo = -(DEC_cent - DEC)*3600
        # (in arcsec)
        # the rotation angle of the sun accoording to the date
        return [x_geo, y_geo]

    def sun_coord_trasform(self, data, header, act_r=True, act_s=True):
        # act_r : rotation operation
        # act_s : shift operation
        if self.havedata:
            [RA_sun, DEC_sun] = self.get_cur_solar_centroid(self.t_obs)
            [RA_obs, DEC_obs] = self.get_obs_image_centroid(header)
            x_shift_pix = (RA_sun - RA_obs) / header['CDELT1']
            y_shift_pix = (DEC_sun - DEC_obs)/header['CDELT2']
            if act_s == False:
                x_shift_pix = 0
                y_shift_pix = 0
            rotate_angel = P(self.t_obs).degree
            if act_r == False:
                rotate_angel = 0
            data_tmp = scipy.ndimage.shift(data, (x_shift_pix, y_shift_pix))
            data_new = scipy.ndimage.rotate(
                data_tmp, rotate_angel, reshape=False)
            return data_new
        else:
            print("No data loaded")

    def get_beam(self):
        if self.havedata:
            solar_PA = P(self.t_obs).degree
            b_maj = self.header['BMAJ']
            b_min = self.header['BMIN']
            # should consider the beam for the data
            b_ang = self.header['BPA']+solar_PA
            return [b_maj, b_min, b_ang]
        else:
            print("No data loaded")

    def make_map(self, fov=2500):
        # still in beta version, use with caution
        # ref : https://gist.github.com/hayesla/42596c72ab686171fe516f9ab43300e2
        hdu = fits.open(self.fname)
        header = hdu[0].header
        data_jybeam = np.squeeze(hdu[0].data)

        data = data_jybeam*(300/self.freq)**2/2/(1.38e-23)/1e26/self.beamArea
        # speed of light 3e8, MHz 1e6

        obstime = Time(header['date-obs'])
        frequency = header['crval3']*u.Hz
        reference_coord = SkyCoord(header['crval1']*u.deg, header['crval2']*u.deg,
                                   frame='gcrs',
                                   obstime=obstime,
                                   distance=earth_distance(obstime),
                                   equinox='J2000')
        # location of the center of LOFAR
        lofar_loc = EarthLocation(
            lat=52.905329712*u.deg, lon=6.867996528*u.deg)
        lofar_coord = SkyCoord(lofar_loc.get_itrs(Time(obstime)))
        reference_coord_arcsec = reference_coord.transform_to(
            frames.Helioprojective(observer=lofar_coord))
        cdelt1 = (np.abs(header['cdelt1'])*u.deg).to(u.arcsec)
        cdelt2 = (np.abs(header['cdelt2'])*u.deg).to(u.arcsec)
        P1 = P(obstime)
        new_header = sunpy.map.make_fitswcs_header(data, reference_coord_arcsec,
                                                   reference_pixel=u.Quantity(
                                                       [header['crpix1']-1, header['crpix2']-1]*u.pixel),
                                                   scale=u.Quantity(
                                                       [cdelt1, cdelt2]*u.arcsec/u.pix),
                                                   rotation_angle=-P1,
                                                   wavelength=frequency.to(
                                                       u.MHz),
                                                   observatory='LOFAR')
        lofar_map = sunpy.map.Map(data, new_header)
        lofar_map_rotate = lofar_map.rotate()
        bl = SkyCoord(-fov*u.arcsec, -fov*u.arcsec,
                      frame=lofar_map_rotate.coordinate_frame)
        tr = SkyCoord(fov*u.arcsec, fov*u.arcsec,
                      frame=lofar_map_rotate.coordinate_frame)
        lofar_submap = lofar_map_rotate.submap(bottom_left=bl, top_right=tr)
        return lofar_submap

    def plot_image(self, log_scale=False, fov=2500, FWHM=False, gaussian_sigma=0,
                   ax_plt=None, **kwargs):
        if self.havedata:
            t_cur_datetime = self.t_obs
            solar_PA = P(self.t_obs).degree
            freq_cur = self.freq
            [b_maj, b_min, b_angel] = self.get_beam()
            b_maj = b_maj*3600
            b_min = b_min*3600
            data_new = gaussian_filter(
                self.data_xy_calib, sigma=gaussian_sigma)
            xx = self.xx
            yy = self.yy

            if ax_plt is None:
                fig = plt.figure()  # num=None, figsize=(8, 6),dpi=120)
                ax = plt.gca()
            else:
                fig = plt.gcf()  # num=None, figsize=(8, 6),dpi=120)
                ax = ax_plt

            # cmap_now = 'CMRmap_r'#,'gist_ncar_r','gist_heat'

            # set some default values
            if 'cmap' not in kwargs:
                kwargs['cmap'] = 'gist_heat'
            if 'vmin' not in kwargs:
                kwargs['vmin'] = 0
            if log_scale:
                data_new = 10*np.log10(data_new)
                kwargs['vmin'] = np.mean(data_new)-2*np.std(data_new)
            if 'vmax' not in kwargs:
                kwargs['vmax'] = 0.8*np.nanmax(data_new)
            ax.text(fov*0.55, fov*0.87, str(round(freq_cur, 2)
                                            ).ljust(5, '0') + 'MHz', color='w')
            circle1 = plt.Circle((0, 0), 960, color='C0', fill=False)
            beam0 = Ellipse((-fov*0.3, -fov*0.9), b_maj,
                            b_min, -(b_angel-solar_PA), color='w')

            # print(b_maj,b_min,b_angel,solar_PA)
            ax.text(-fov*0.35, -fov*0.9, 'Beam shape:',
                    horizontalalignment='right', verticalalignment='center', color='w')
            ax.add_artist(circle1)
            ax.add_artist(beam0)

            im = ax.imshow(data_new, interpolation='nearest', origin='lower',
                           extent=(min(xx), max(xx), min(yy), max(yy)), **kwargs)

            if FWHM:
                FWHM_thresh = 0.5*(np.max(data_new))
                ax.contour(xx, yy, data_new, levels=[
                           FWHM_thresh], colors=['deepskyblue'])

            plt.colorbar(im)
            plt.setp(ax, xlabel='X (ArcSec)', ylabel='Y (ArcSec)',
                     xlim=[-fov, fov], ylim=[-fov, fov],
                     title=str(t_cur_datetime))
            # plt.show()
            return [fig, ax, im]

        else:
            print("No data loaded")

    # find the pixel position of the maximum value in the array
    def peak_xy_coord_pix(self):
        if self.havedata:
            peak_xy_coord_pix = np.argwhere(
                self.data_xy_calib.T == np.nanmax(self.data_xy_calib.T))[0]
            return peak_xy_coord_pix
        else:
            print("No data loaded")

    def peak_xy_coord_arcsec(self):
        if self.havedata:
            peak_xy = self.peak_xy_coord_pix()
            peak_xy_arcsec = [self.xx[peak_xy[0]], self.yy[peak_xy[1]]]
            return peak_xy_arcsec
        else:
            print("No data loaded")

    # fit the image source to a 2-d gaussian funtion with sciPy's curve_fit
    def fit_gaussian2d(self, thresh=0.5, **kwargs):

        if self.havedata:
            idx_wanted = np.where(self.data_xy_calib.T >
                                  thresh*self.data_xy_calib.max())
            yv, xv = np.meshgrid(self.yy, self.xx)

            boundthis = [
                [0, np.min(xv[idx_wanted]), np.min(
                    yv[idx_wanted]), -1.1*np.pi, 0, 0],
                [3*np.max(self.data_xy_calib.T), np.max(xv[idx_wanted]), np.max(yv[idx_wanted]), 1.1*np.pi,
                 np.max(np.abs(xv))/2, np.max(np.abs(yv))/2]
            ]
            coord_x, coord_y = self.peak_xy_coord_arcsec()
            [b_maj, b_min, b_ang] = self.get_beam()
            print(b_maj)
            popt, pcov = curve_fit(func_gaussian, (xv[idx_wanted], yv[idx_wanted]),
                                   self.data_xy_calib.T[idx_wanted],
                                   p0=[np.max(self.data_xy_calib.T), coord_x,
                                       coord_y, 0, b_maj*3600, b_maj*3600],
                                   bounds=boundthis)

        return popt, pcov


def func_gaussian(xdata, s0, x_cent, y_cent, tile, x_sig, y_sig):
    x, y = xdata
    xp = (x-x_cent) * np.cos(tile) - (y-y_cent) * np.sin(tile)
    yp = (x-x_cent) * np.sin(tile) + (y-y_cent) * np.cos(tile)

    flux = s0 * (np.exp(-(xp**2)/(2*x_sig**2) - (yp**2)/(2*y_sig**2)))
    return flux


def get_tile_ellipse_from_fit(popt):

    # FWHM ~= 2*sqrt(2*ln(2))*sigma

    t = np.linspace(0, 2*np.pi, 100)
    t_rot = -popt[3]
    Ell = np.array([popt[4]*np.cos(t)*np.sqrt(2*np.log(2)),
                    popt[5]*np.sin(t)*np.sqrt(2*np.log(2))])
    # u,v removed to keep the same center location
    R_rot = np.array([[np.cos(t_rot), -np.sin(t_rot)],
                     [np.sin(t_rot), np.cos(t_rot)]])
    # 2-D rotation matrix

    Ell_rot = np.zeros((2, Ell.shape[1]))
    for i in range(Ell.shape[1]):
        Ell_rot[:, i] = np.dot(R_rot, Ell[:, i])

    return Ell_rot


