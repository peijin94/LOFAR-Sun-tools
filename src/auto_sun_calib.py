import glob
import os
import subprocess

###############  the configurations
sources  = 'TauAGG'  # source type
sourcedb = 'taurus_1.sourcedb' # path to the source

sun_MS_dir   = 'MS/' # path to the dir contain sun's MS 
calib_MS_dir = 'MS/' # path to the dir contain calibrator's MS

obs_id_sun   = 'L722384' # obsid of the sun
obs_id_calib = 'L701915' # obsid of the calibrator

idx_range_sun  = [32,39] # index range of the subband of the Sun
idx_range_cali = [92,99] # index range of the subband of the Sun

run_step = [0]; # 0 for predict; 1 for applycal;  2 for applybeam
		# [0,1,2] for complete calibration
################





# generate subband list
fill3zero = lambda x: 'SB'+str(x).zfill(3)
subband_sun    = map(fill3zero,range(idx_range_sun[0],idx_range_sun[1]))
subband_calibs = map(fill3zero,range(idx_range_cali[0],idx_range_cali[1]))
# output ['SB092',......'SB099']

# template of the predict files
predict_parset_template = """
msin={{{1}}}
msout=.

steps=[gaincal]

gaincal.usebeammodel=True
gaincal.solint=4 
gaincal.sources={{{2}}}
gaincal.sourcedb={{{3}}}
gaincal.onebeamperpatch=True
gaincal.caltype=diagonal

"""

apply_cal_template = """
msin={{{1}}}
msout=.
msin.datacolumn=DATA
msout.datacolumn=CORR_NO_BEAM

steps=[applycal]

applycal.parmdb={{{2}}}/instrument
applycal.updateweights=True
"""

apply_beam_template = """
msin={{{1}}}
msout=.
msin.datacolumn=CORR_NO_BEAM 
msout.datacolumn=CORRECTED_DATA 
steps =[applybeam] 
applybeam.updateweights=True
"""

# predict the parset
if 0 in run_step:
	pred_dir = 'pred/'
	if not os.path.exists(pred_dir):
    		os.makedirs(pred_dir)
	for subbd in subband_calibs:
		# use the dir and the id to construct the file name
		MS_name = calib_MS_dir+obs_id_calib+'_'+subbd+'_uv.MS'
	
		# use the template and the file name to make a 'XXXX.parset' file 
		parset_content = predict_parset_template.replace('{{{1}}}',
                             MS_name).replace('{{{2}}}',
                             sources).replace('{{{3}}}',sourcedb)
		tfile = open(pred_dir+subbd+'_predict.parset', "w")
		tfile.write(parset_content)
		tfile.close()

		# call the NDPPP from system
		os.system('NDPPP '+pred_dir+subbd+'_predict.parset')

# applycal the parset
if 1 in run_step:
        apcal_dir = 'apcal/'
        if not os.path.exists(apcal_dir):
                os.makedirs(apcal_dir)
        idx_cur = 0
        for subbd in subband_sun:
                # use the dir and the id to construct the file name
                MS_sun  = sun_MS_dir+obs_id_sun+'_'+subbd+'_uv.MS'
                MS_cali = calib_MS_dir+obs_id_calib+'_'+subband_calibs[idx_cur]+'_uv.MS'

                # use the template and the file name to make a 'XXXX.parset' file 
                apcal_content = apply_cal_template.replace('{{{1}}}',
                                         MS_sun).replace('{{{2}}}',MS_cali)
                tfile = open(apcal_dir+subbd+'_predict.parset', "w")
                tfile.write(apcal_content)
                tfile.close()

                # call the NDPPP from system
                os.system('NDPPP '+apcal_dir+subbd+'_predict.parset')
                idx_cur = idx+1

                os.makedirs(apcal_dir)



# applybeam the parset
if 2 in run_step:
        apbm_dir = 'apbm/'
        if not os.path.exists(apbm_dir):
                os.makedirs(apbm_dir)
        for subbd in subband_sun:
                # use the dir and the id to construct the file name
                MS_sun  = sun_MS_dir+obs_id_sun+'_'+subbd+'_uv.MS'

                # use the template and the file name to make a 'XXXX.parset' file 
                apbm_content = apply_beam_template.replace('{{{1}}}',MS_sun)
                tfile = open(apbm_dir+subbd+'_predict.parset', "w")
                tfile.write(apbm_content)
                tfile.close()

                # call the NDPPP from system
                os.system('NDPPP '+apbm_dir+subbd+'_predict.parset')


