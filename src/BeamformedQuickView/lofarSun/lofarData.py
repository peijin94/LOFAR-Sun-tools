from scipy.io import readsav
import matplotlib.dates as mdates
from lofarSun.lofarJ2000xySun import j2000xy
import datetime
import glob
import os
from astropy.io import fits as fits
import numpy as np
from skimage import measure
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from scipy.interpolate import interp2d
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import cv2
import sunpy
import sunpy.sun
from sunpy.coordinates.sun import sky_position as sun_position
import sunpy.coordinates.sun as sun_coord
import scipy
import scipy.ndimage
from matplotlib.patches import Ellipse

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

        self.title = str(data['ds'][0]['TITLE'],'utf-8')
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

        self.title = str(data[header_name][0]['TITLE'],'utf-8')
        self.data_cube = data[header_name][0]['CUBE']
        self.freqs_ds = data[header_name][0]['FREQS']
        self.time_ds = (data[header_name][0]['TIME']) / 3600 / 24 + mdates.date2num(datetime.datetime(1979, 1, 1))
        ra_beam = data[header_name][0]['RA']
        dec_beam = data[header_name][0]['DEC']
        [self.xb, self.yb] = j2000xy(ra_beam, dec_beam, mdates.num2date(self.time_ds[0]))


    def load_fits(self, fname):
        self.fname = fname
        self.havedata = True

        hdu = fits.open(fname)
        self.title = 'LOFAR BFcube'
        self.data_cube = hdu[0].data
        self.freqs_ds = hdu[1].data['FREQ'][:]
        self.time_ds = hdu[2].data['TIME'][:]
        self.xb = hdu[3].data['X']
        self.yb = hdu[3].data['Y']

    def bf_image_by_idx(self,f_idx,t_idx,fov=3000,asecpix=20,extrap=True,interpm='cubic'):
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
        Ibeam = data_beam
        return X,Y,data_bf,x,y,Ibeam

    def bf_image_by_freq_time(self,freq,time,fov=3000,asecpix=20,extrap=True,interpm='cubic'):
        t_idx_select = (np.abs(self.time_ds - time)).argmin()
        f_idx_select = (np.abs(self.freqs_ds - freq)).argmin()
        X,Y,data_bf = self.bf_image_by_idx(self,f_idx_select,t_idx_select,fov=fov,asecpix=asecpix,extrap=extrap,interpm=interpm)
        return [X,Y,data_bf]

    def bf_time_to_idx(self,time):
        return (np.abs(self.time_ds - time)).argmin()

    def bf_freq_to_idx(self,freq):
        return (np.abs(self.freqs_ds - freq)).argmin()

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

    def bf_fit_gauss_source_by_idx(self,f_idx,t_idx):
        X,Y,data_bf,x,y,Ibeam = self.bf_image_by_idx(f_idx,t_idx)
        FWHM_thresh = np.max(data_bf)*0.7 #np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0
        img_bi = data_bf > FWHM_thresh
        bw_lb = measure.label(img_bi)
        rg_lb = measure.regionprops(bw_lb)
        x_peak = X[np.where(data_bf == np.max(data_bf))]
        y_peak = Y[np.where(data_bf == np.max(data_bf))]
        rg_id = bw_lb[np.where(data_bf == np.max(data_bf))]
        area_peak = rg_lb[int(rg_id)-1].area
        bw_peak_area = (np.array(abs(bw_lb-rg_id)<0.1)*255).astype(np.uint8)

        dilate_size = int(x.size/30)

        kernel = np.ones((dilate_size,dilate_size),np.uint8)
        imdilate = cv2.dilate(bw_peak_area,kernel,iterations = 1)

        fbeams = interp2d(x,y,imdilate,kind='linear')
        peaks_in = np.array([fbeams(self.xb[tmp_id],self.yb[tmp_id]) for tmp_id in range(len(self.xb))]).reshape(-1)
        
        fit_xb = self.xb[peaks_in>0.5]
        fit_yb = self.yb[peaks_in>0.5]
        fit_Ib = Ibeam[peaks_in>0.5]

        #print(fit_Ib)

        def func_gaussian(xdata,s0,x_cent,y_cent,tile,x_sig,y_sig):
            x,y=xdata  
            xp = (x-x_cent) * np.cos(tile) - (y-y_cent) * np.sin(tile)
            yp = (x-x_cent) * np.sin(tile) + (y-y_cent) * np.cos(tile)
    
            flux  = s0 * ( np.exp( -(xp**2)/(2*x_sig**2) - (yp**2)/(2*y_sig**2) ) )
            return flux
        p0  = [np.max(fit_Ib), np.mean(fit_xb), np.mean(fit_yb),np.pi, np.std(fit_xb), np.std(fit_yb)]
        popt, pcov = curve_fit(func_gaussian, (fit_xb,fit_yb) , fit_Ib,p0=p0)
        bf_res={}
        bf_res["s0"]=popt[0]
        bf_res["x_cent"]=popt[1]
        bf_res["y_cent"]=popt[2]
        bf_res["tile"]=popt[3]
        bf_res["x_sig"]=popt[4]
        bf_res["y_sig"]=popt[5]

        bf_err={}
        bf_err["s0"]=pcov[0][0]
        bf_err["x_cent"]=pcov[1][1]
        bf_err["y_cent"]=pcov[2][2]
        bf_err["tile"]=pcov[3][3]
        bf_err["x_sig"]=pcov[4][4]
        bf_err["y_sig"]=pcov[5][5]
        
        tmp_theta = np.linspace(0,np.pi*2,100)
        tmp_xp = bf_res["x_sig"]*np.cos(tmp_theta)
        tmp_yp = bf_res["y_sig"]*np.sin(tmp_theta)
        tmp_x = bf_res["x_cent"]+tmp_xp*np.cos(-bf_res['tile']) - tmp_yp*np.sin(-bf_res['tile'])
        tmp_y = bf_res["y_cent"]+tmp_xp*np.sin(-bf_res['tile']) + tmp_yp*np.cos(-bf_res['tile'])


        ax = plt.gca()
        im = ax.imshow(data_bf, cmap='gist_heat',
                 origin='lower',extent=[np.min(X),np.max(X),np.min(Y),np.max(Y)])
        ax.plot(self.xb,self.yb,'k.')
        ax.plot(tmp_x,tmp_y,'k-')
        ax.plot(bf_res["x_cent"],bf_res["y_cent"],"k+")
        plt.savefig('test.pdf')

        return bf_res,bf_err

    def plot_bf_image_by_idx(self,f_idx,t_idx):
        if True:
            X,Y,data_bf = self.bf_image_by_idx(f_idx,t_idx,fov=3000,asecpix=20)
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
            print("Data shape:")
            print(self.data_cube.shape)

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
            hdu_lofar.header['TITLE']     =  self.title
            hdu_lofar.header['HISTORY']   = '        '    

            col_f = fits.Column(name='FREQ',array=self.freqs_ds[f_idx],format="D")
            col_t = fits.Column(name='TIME',array=self.time_ds[t_idx],format="D")
            col_x = fits.Column(name='X',array=self.xb,format="D")
            col_y = fits.Column(name='Y',array=self.yb,format="D")
            hdu_f = fits.BinTableHDU.from_columns([col_f],name="FREQ")
            hdu_t = fits.BinTableHDU.from_columns([col_t],name="TIME")
            hdu_xy = fits.BinTableHDU.from_columns([col_x,col_y],name="BeamXY")

            hdul = fits.HDUList([hdu_lofar,hdu_f,hdu_t,hdu_xy])
            hdul.writeto(fprefix,overwrite=True)
    
    def write_fits_full(self,fdir,fprefix):
        if self.havedata:
            self.write_fits(fdir,fprefix,np.arange(len(self.freqs_ds)),np.arange(len(self.time_ds)))

class LofarDataCleaned:
    def __init__(self):
        self.havedata = False

    def load_fits(self,fname):
        if len(fname)>0:
            self.havedata = True
            self.fname = fname
            hdulist = fits.open(fname)
            hdu = hdulist[0]
            self.header = hdu.header
            self.t_obs = sunpy.time.parse_time(self.header['DATE-OBS']).datetime
            self.freq = hdu.header['CRVAL3']/1e6
            data=np.zeros((hdu.header[3],hdu.header[4]), dtype=int)
            data = hdu.data
            self.data=data[0,0,:,:]
            [RA_sun,DEC_sun] = self.get_cur_solar_centroid(t_obs=self.t_obs)
            [RA_obs,DEC_obs] = self.get_obs_image_centroid(self.header)
            [RA_ax ,DEC_ax ] = self.get_axis_obs(self.header)

            [self.xx,self.yy] = self.RA_DEC_shift_xy0(RA_ax,DEC_ax,RA_obs,DEC_obs)
            self.data_xy = self.sun_coord_trasform(self.data,self.header,True,True)
            [b_maj,b_min,b_ang] = self.get_beam()
            self.beamArea = (b_maj/180*np.pi)*(b_min/180*np.pi)*np.pi /(4*np.log(2))
            self.data_xy_calib = self.data_xy*(300/self.freq)**2/2/(1.38e-23)/1e26/self.beamArea
            
            
    

    
    def get_cur_solar_centroid(self,t_obs):
            # use the observation time to get the solar center
        [RA,DEC] = sun_position(t=t_obs, equinox_of_date=False)
        return [RA.degree%360,DEC.degree%360]

    def get_obs_image_centroid(self,header):
        # get the RA DEC center of the image from the solar center
        RA_obs = header['CRVAL1']
        DEC_obs = header['CRVAL2']
        return [RA_obs%360,DEC_obs%360]

    def get_axis_obs(self,header):
        # make the header with the image
        # refer to https://www.atnf.csiro.au/computing/software/miriad/progguide/node33.html
        if self.havedata:
            [RA_c,DEC_c] = self.get_obs_image_centroid(self.header)
            RA_ax_obs   = RA_c + ((np.arange(header['NAXIS1'])+1) 
                                -header['CRPIX1'])*header['CDELT1']/np.cos((header['CRVAL2'])/180.*np.pi)
            DEC_ax_obs  = DEC_c+ ((np.arange(header['NAXIS2'])+1) 
                                -header['CRPIX2'])*header['CDELT2']
            return [RA_ax_obs,DEC_ax_obs]
        else:
            print("No data loaded")
            
    def RA_DEC_shift_xy0(self,RA,DEC,RA_cent,DEC_cent):
        # transformation between the observed coordinate and the solar x-y coordinate
        # including the x-y shift
        x_geo = -(RA  -  RA_cent)*np.cos(DEC_cent/180.*np.pi)*3600
        y_geo = -(DEC_cent - DEC)*3600
        # (in arcsec)
        # the rotation angle of the sun accoording to the date
        return [x_geo,y_geo]

    def sun_coord_trasform(self,data,header,act_r=True,act_s=True):
        # act_r : rotation operation
        # act_s : shift operation
        if self.havedata:
            [RA_sun,DEC_sun] = self.get_cur_solar_centroid(self.t_obs);
            [RA_obs,DEC_obs] = self.get_obs_image_centroid(header);
            x_shift_pix = (RA_sun  - RA_obs) /header['CDELT1']
            y_shift_pix = (DEC_sun - DEC_obs)/header['CDELT2']
            if act_s==False:
                x_shift_pix = 0
                y_shift_pix = 0
            rotate_angel = sun_coord.P(self.t_obs).degree
            if act_r==False:
                rotate_angel = 0
            data_tmp = scipy.ndimage.shift(data,(x_shift_pix,y_shift_pix))
            data_new = scipy.ndimage.rotate(data_tmp,rotate_angel,reshape=False)
            return data_new
        else:
            print("No data loaded")
                        

    #def make_lofar_sun_map(fname):
# TODO : to make a map data structure which will be compatible with SUNPY
    #     return 0
        
    def get_beam(self):
        if self.havedata:
            solar_PA = sun_coord.P(self.t_obs).degree
            b_maj =  self.header['BMAJ']
            b_min  = self.header['BMIN']
            b_ang = self.header['BPA']+solar_PA # should consider the beam for the data
            return [b_maj,b_min,b_ang]
        else:
            print("No data loaded")
            

    def plot_image(self,vmax_set=np.nan,log_scale=False,FWHM=False):
        if self.havedata:
            t_cur_datetime = self.t_obs
            solar_PA = sun_coord.P(self.t_obs).degree
            freq_cur = self.freq
            [b_maj,b_min,b_angel] = self.get_beam()
            b_maj = b_maj*3600
            b_min = b_min*3600
            data_new = gaussian_filter(self.data_xy_calib,sigma=9)
            xx = self.xx
            yy = self.yy

           
            #print(b_major,b_min,b_angel+solar_PA)
            fig=plt.figure()#num=None, figsize=(8, 6),dpi=120)
            ax = plt.gca()
            cmap_now = 'CMRmap_r'
            cmap_now = 'gist_ncar_r'
            cmap_now = 'gist_heat'
            vmin_now = 0
            if log_scale:
                data_new = 10*np.log10(data_new)
            if vmax_set>0:
                vmax_now = vmax_set
            else:
                vmax_now = 1.2*np.nanmax(data_new)
            ax.text(1400,1800, str(int(freq_cur)) + 'MHz',color='w')
            circle1 = plt.Circle((0,0), 960, color='r',fill=False)
            beam0 = Ellipse((-500, -1800), b_maj, b_min, -b_angel ,color='w')
            print(b_angel)
            ax.text(-600,-1800,'Beam shape:',horizontalalignment='right',verticalalignment='center' ,color='w')
            ax.add_artist(circle1)
            ax.add_artist(beam0)
            plt.xlabel('X (ArcSec)')
            plt.ylabel('Y (ArcSec)')
            
            plt.imshow(data_new,vmin=vmin_now, vmax=vmax_now , 
                            interpolation='nearest',cmap=cmap_now, origin='lower',
                            extent=(min(xx),max(xx),min(yy),max(yy)))

            if FWHM:
                FWHM_thresh=0.5*(np.max(data_new))
                ax.contour(xx,yy,data_new,levels=[FWHM_thresh],colors=['deepskyblue'])
                
            plt.colorbar()
            plt.xlim([-2500,2500])
            plt.ylim([-2500,2500])
            plt.title(str(t_cur_datetime))

            plt.show()
            return [fig,ax]

        else:
            print("No data loaded")
            

