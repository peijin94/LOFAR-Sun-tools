
# The UI interface and analysis of the lofar solar beam from

import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '..')

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import matplotlib
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from skimage import measure
import matplotlib.dates as mdates
import resource_rc
from lofarSun.BF import BFcube
from pandas.plotting import register_matplotlib_converters
import platform


import matplotlib as mpl
# try to use the precise epoch
mpl.rcParams['date.epoch']='1970-01-01T00:00:00'
try:
    mdates.set_epoch('1970-01-01T00:00:00')
except:
    pass
import os
here = os.path.dirname(os.path.realpath(__file__))

register_matplotlib_converters()

if platform.system() != "Darwin":
    matplotlib.use('TkAgg')
else:
    print("Detected MacOS, using the default matplotlib backend: " +
          matplotlib.get_backend())
matplotlib.use('Qt5Agg')

class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi(here+"/layout.ui", self)

        self.move(10,30)
        self.init_graph()
        self.setWindowIcon(QIcon(":/GUI/resource/lofar.png"))
        self.addToolBar(NavigationToolbar(self.mplw.canvas, self))
        self.dataset = BFcube()

        self.asecpix = 20

        self.x_select = 0
        self.y_select = 0
        self.selected = False
        self.interpset = 'cubic'
        self.keyaval = False
        self.extrapolate = True

        self.interp_nearest.setChecked(False)
        self.interp_linear.setChecked(False)
        self.interp_cubic.setChecked(True)

        self.show_disk.setChecked(True)
        self.show_FWHM.setChecked(True)
        self.show_peak.setChecked(True)

        self.action_prefix = '<span style=\" font-size:12pt; font-weight:600; color:#18B608;\" >[Action] </span>'
        self.info_prefix = '<span style=\" font-size:12pt; font-weight:600; color:#0424AE;\" >[Info] </span>'

        # define all the actions
        self.button_gen.clicked.connect(self.showBeamForm)
        self.pointing.clicked.connect(self.showPointing)
        self.loadsav.triggered.connect(self.update_lofarBF)
        self.loadcube.triggered.connect(self.update_lofar_cube)
        self.loadfits.triggered.connect(self.update_lofar_fits)
        self.spectroPlot.clicked.connect(self.spectroPlot_func)

        self.t_idx_select = 0
        self.f_idx_select = 0

        self.interp_nearest.toggled.connect(lambda:self.btnstate(self.interp_nearest))
        self.interp_linear.toggled.connect(lambda:self.btnstate(self.interp_linear))
        self.interp_cubic.toggled.connect(lambda:self.btnstate(self.interp_cubic))

        QShortcut(Qt.Key_Up, self, self.keyUp)
        QShortcut(Qt.Key_Down, self, self.keyDown)
        QShortcut(Qt.Key_Left, self, self.keyLeft)
        QShortcut(Qt.Key_Right, self, self.keyRight)

    def btnstate(self,b):
        self.interpset = (b.text().lower())

    @staticmethod
    def move_window(window, dx, dy):
        """Move a matplotlib window to a given x and y offset, independent of backend"""
        if matplotlib.get_backend() == "Qt5Agg":
            window.move(dx, dy)
        else:
            window.wm_geometry("+{dx}+{dy}".format(dx=dx, dy=dy))

    def init_graph(self):
        self.mplw.canvas.axes.clear()
        self.mplw.canvas.axes.imshow(plt.imread(here+'/resource/login.png'))
        self.mplw.canvas.axes.set_axis_off()
        self.mplw.canvas.draw()

    def update_lofarBF(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.dataset.fname, _ = QFileDialog.getOpenFileName(self,"Load idl SAVE cube",
                                                  "","IDL Files (*.sav);;All Files (*)",
                                                  options=options)
        if self.dataset.fname:
            print(self.dataset.fname)
            if len(self.dataset.fname):
                self.dataset.load_sav_xy(self.dataset.fname)
                self.mplw.canvas.axes.clear()
                self.draw_ds_after_load()
                self.beamSet.clear()
                self.beamSet.addItems([str(x).rjust(3,'0') for x in range(self.dataset.xb.shape[0])])
        
    def update_lofar_cube(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.dataset.fname, _ = QFileDialog.getOpenFileName(self,"Load idl SAVE cube",
                                                  "","IDL Files (*.sav);;All Files (*)",
                                                  options=options)
        if self.dataset.fname:
            print(self.dataset.fname)
            if len(self.dataset.fname):        
                self.dataset.load_sav_radec(self.dataset.fname)
                self.mplw.canvas.axes.clear()
                self.draw_ds_after_load()
                self.beamSet.clear()
                self.beamSet.addItems([str(x).rjust(3,'0') for x in range(self.dataset.xb.shape[0])])

    def update_lofar_fits(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.dataset.fname, _ = QFileDialog.getOpenFileName(self,"Load fits cube",
                                                  "","Fits Files (*.fits);;All Files (*)",
                                                  options=options)
        if self.dataset.fname:
            print(self.dataset.fname)
            if len(self.dataset.fname):        
                self.dataset.load_fits(self.dataset.fname)
                self.mplw.canvas.axes.clear()
                self.draw_ds_after_load()
                self.beamSet.clear()
                self.beamSet.addItems([str(x).rjust(3,'0') for x in range(self.dataset.xb.shape[0])])



    def draw_ds_after_load(self,idx_cur=0,conn_click=True):
        data_ds = np.array(self.dataset.data_cube[:, :, idx_cur])
        #print(self.dataset.time_ds)
        ax_cur = self.mplw.canvas.axes
        self.dataset.plot_bf_dyspec(idx_cur,ax_cur)
        self.mplw.canvas.draw()
        self.mplw.canvas.mpl_connect('button_release_event', self.onclick)
        self.log.append(self.action_prefix+'Load : '+self.dataset.fname+' Beam-'+str(idx_cur))

    def spectroPlot_func(self):
        self.mplw.canvas.axes.clear()
        this_idx = self.beamSet.currentIndex()
        print(this_idx)
        self.draw_ds_after_load(idx_cur=this_idx)

    def onclick(self,event):
        if ~event.dblclick and event.button==1:

            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))
            self.x_select = event.xdata
            self.y_select = event.ydata
            self.input_t.setText(mdates.num2date(self.x_select).strftime('%H:%M:%S.%f'))
            self.input_f.setText('{:06.3f}'.format(self.y_select))
            self.t_idx_select = (np.abs(self.dataset.time_ds - self.x_select)).argmin()
            self.f_idx_select = (np.abs(self.dataset.freqs_ds - self.y_select)).argmin()

            if self.selected:
                if len(self.mplw.canvas.axes.lines)>0:
                    self.mplw.canvas.axes.lines.remove(self.mplw.canvas.axes.lines[0])
            self.mplw.canvas.axes.plot(self.x_select, self.y_select, 'w+', markersize=25, linewidth=2)
            self.mplw.canvas.draw()
            self.selected = True
            self.keyaval = True
            print(plt.fignum_exists(4))
            if plt.fignum_exists(4):
                self.showBeamForm()

    def showPointing(self):
        if self.dataset.havedata:
            plt.figure(5)
            self.move_window(plt.get_current_fig_manager().window, 1150, 550)
            plt.plot(self.dataset.xb,self.dataset.yb,'b.')
            for idx in list(range(self.dataset.xb.shape[0])):
                plt.text(self.dataset.xb[idx],self.dataset.yb[idx],str(idx))
            ax = plt.gca()
            ax.set_xlabel('X (Arcsec)')
            ax.set_ylabel('Y (Arcsec)')
            ax.set_aspect('equal', 'box')

            plt.show()


    def keyUp(self):
        self.stepNear(1,0)

    def keyDown(self):
        self.stepNear(-1,0)


    def keyLeft(self):
        self.stepNear(0,-1)

    def keyRight(self):
        self.stepNear(0,1)

    def stepNear(self,f_move,t_move):
        if self.keyaval:
            self.t_idx_select = self.t_idx_select + t_move
            self.f_idx_select = self.f_idx_select + f_move
            self.x_select = self.dataset.time_ds[self.t_idx_select]
            self.y_select = self.dataset.freqs_ds[self.f_idx_select]
            self.input_t.setText(mdates.num2date(self.x_select).strftime('%H:%M:%S.%f'))
            self.input_f.setText('{:06.3f}'.format(self.y_select))

            if self.selected:
                self.mplw.canvas.axes.lines.remove(self.mplw.canvas.axes.lines[0])
            self.mplw.canvas.axes.plot(self.x_select, self.y_select, 'w+', markersize=25, linewidth=2)
            self.mplw.canvas.draw()
            self.selected = True
            self.keyaval = True
            if plt.fignum_exists(4):
                self.showBeamForm()


    def showBeamForm(self):
        if not self.selected:
            QMessageBox.about(self, "Attention", "Select a time-frequency point!")
        elif self.dataset.havedata:

            X,Y,data_bf,x,y,Ibeam = self.dataset.bf_image_by_idx(self.f_idx_select,\
                            self.t_idx_select,fov=3000,asecpix=self.asecpix,\
                            extrap=self.extrapolate,interpm=self.interpset)

            
            self.log.append(self.action_prefix+' Beam Form at'+
                            mdates.num2date(self.x_select).strftime('%H:%M:%S.%f') +' of '
                            '{:06.3f}'.format(self.y_select)+'MHz')

            fig = plt.figure(num=4)
            self.move_window(plt.get_current_fig_manager().window, 1150, 50)

            fig.clear()
            ax = fig.add_subplot(111)
            im = ax.imshow(data_bf, cmap='gist_heat',
                      origin='lower',extent=[np.min(X),np.max(X),np.min(Y),np.max(Y)])
            ax.set_xlabel('X (Arcsec)')
            ax.set_ylabel('Y (Arcsec)')
            ax.set_aspect('equal', 'box')
            plt.colorbar(im)
            print(np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0)
            
            FWHM_thresh = np.max(data_bf)/2.0 #np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0
            img_bi = data_bf > FWHM_thresh
            if self.show_FWHM.isChecked():
                ax.contour(X,Y,data_bf,levels=[FWHM_thresh,FWHM_thresh*2*0.9],colors=['deepskyblue','forestgreen'])
            bw_lb = measure.label(img_bi)
            rg_lb = measure.regionprops(bw_lb)
            x_peak = X[np.where(data_bf == np.max(data_bf))]
            y_peak = Y[np.where(data_bf == np.max(data_bf))]
            rg_id = bw_lb[np.where(data_bf == np.max(data_bf))]
            area_peak = rg_lb[int(rg_id)-1].area

            self.log.append(self.info_prefix+' [XY_peak:('+
                            '{:7.1f}'.format(x_peak[0])+','+
                            '{:7.1f}'.format(y_peak[0])+') asec] '+
                            '[Area:('+'{:7.1f}'.format(area_peak*(self.asecpix/60)**2)+
                            ') amin2]')

            if self.show_FWHM.isChecked():
                ax.contour(X,Y,np.abs(bw_lb-rg_id)<0.1,levels=[0.5],colors=['lime'])

            if self.show_disk.isChecked():
                ax.plot(960*np.sin(np.arange(0,2*np.pi,0.001)),
                        960*np.cos(np.arange(0,2*np.pi,0.001)),'w')

            if self.show_peak.isChecked():
                ax.plot(x_peak,y_peak,'k+')

            fig.canvas.draw()
            plt.show()


def main():

    app = QApplication([])
    window = MatplotlibWidget()
    window.show()
    app.exec_()


if __name__=='__main__':
    main()
