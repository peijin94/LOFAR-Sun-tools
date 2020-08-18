
# test the write fits module
from lofarSun.lofarData import LofarDataBF
from astropy.io import fits as fits


lofar_bf = LofarDataBF()
#lofar_bf.load_sav("E:\\nextcloud\\meeting\\nacad\\2019_aut\\Lofar_spike\\data\\L599747_20170712_084137_short_data.sav")
#lofar_bf.bf_image_by_idx(30,100)
#bf_res,bf_err = lofar_bf.bf_fit_gauss_source_by_idx(30,100)
#lofar_bf.write_fits_full('.','demo.fits')
#print(bf_res)
#print(bf_err)

#lofar_bf.load_fits('test2.fits')
#lofar_bf.bf_image_by_idx(30,100)


bf_res,bf_err = lofar_bf.bf_fit_gauss_source_by_idx(30,100)
#lofar_bf.write_fits_full('.','test2.fits')
print(bf_res)
print(bf_err)

hdu = fits.open('demo.fits')

hdu.info()
data_cube = hdu[3].data['X']
print(hdu[2].data['TIME'])
print(hdu[0].data.shape)

hdu.close()
