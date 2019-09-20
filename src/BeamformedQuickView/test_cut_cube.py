
# cut and averaging the data into .fits file

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import readsav
from scipy.interpolate import griddata,interp2d
import datetime
import matplotlib.dates as mdates
from skimage import measure


class lofar_data:
    pass

if __name__ == "__main__":
    
    f_name = '../data/cube_ds_0012kHz_01dt20170712_0842_20170712_0843.sav'
    data = readsav(f_name, python_dict=True)

    header_name = 'cube_ds'

    title = data[header_name][0]['TITLE']
    data_cube = data[header_name][0]['CUBE']
    freqs_ds = data[header_name][0]['FREQS']
    time_ds = (data[header_name][0]['TIME'])/3600/24 + mdates.date2num(datetime.datetime(1979,1,1))
    xb = data[header_name][0]['XB']
    yb = data[header_name][0]['YB']

    data_beam = data_cube[20,130,:]
    x = np.linspace(-1,1,100)
    y =  np.linspace(-1,1,100)
    X, Y = np.meshgrid(x,y)
    method='nearest'#'cubic'
    data_bf = griddata((xb, yb), data_beam, (X, Y), method=method)

    data_ds = data_cube[:,:,0]

    ax = plt.gca()
    ax.imshow(data_ds,aspect='auto',  origin='lower',
                vmin=(np.mean(data_ds)-2*np.std(data_ds)),
                vmax=(np.mean(data_ds)+3*np.std(data_ds)),
                extent=[time_ds[0],time_ds[-1],freqs_ds[0],freqs_ds[-1]],cmap='inferno')
    ax.xaxis_date()
    ax.set_xlabel('Time (UT)')
    ax.set_ylabel('Frequency (MHz)')
    ax.set_title('LOFAR Beamform Observation '+ mdates.num2date(time_ds[0]).strftime('%Y/%m/%d'))
    plt.xticks(rotation=25)


    x = np.arange(-3000, 3000, 15)
    y = np.arange(-3000, 3000, 15)
    X, Y = np.meshgrid(x, y)
    method = "cubic"
    data_bf = griddata((xb, yb), data_beam,
                    (X, Y), method=method, fill_value=np.min(data_beam))

    FWHM_thresh = np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0
    img_bi = data_bf > FWHM_thresh
    bw_lb = measure.label(img_bi)
    rg_lb = measure.regionprops(bw_lb)
    x_peak = X[np.where(data_bf == np.max(data_bf))]
    y_peak = Y[np.where(data_bf == np.max(data_bf))]
    rg_id = bw_lb[np.where(data_bf == np.max(data_bf))]
    area_peak = rg_lb[int(rg_id)-1].area



    plt.figure(6)
    ax = plt.gca()
    ax.imshow(bw_lb, cmap='hot',
            origin='lower',extent=[np.min(X),np.max(X),np.min(Y),np.max(Y)])
    ax.set_xlabel('X (Arcsec)')
    ax.set_ylabel('Y (Arcsec)')
    ax.set_aspect('equal', 'box')
    print(np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0)
    ax.contour(X,Y,data_bf,levels=[np.min(data_bf)+(np.max(data_bf)-np.min(data_bf))/2.0],colors=['deepskyblue'])

    plt.show()
