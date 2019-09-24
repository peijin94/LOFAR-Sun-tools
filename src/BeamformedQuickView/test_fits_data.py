
# test the write fits module
from lofarSun.lofarData import LofarDataBF

lofar_bf = LofarDataBF()
lofar_bf.load_sav("E:\\nextcloud\\meeting\\nacad\\2019_aut\\Lofar_spike\\data\\L599747_20170712_084137_short_data.sav")
#[X,Y,data_bf] = lofar_bf.bf_image_by_idx(30,100)
#lofar_bf.plot_bf_image_by_idx(30,100)
#lofar_bf.write_fits_full('.','test.fits')
