#!/usr/bin/python2

'''
    File name: auto_sun_calib.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug

    A script to calibrate the Measurement Set
'''



from __future__ import print_function
import glob
import os
import subprocess
import time
import numpy as np
import logging


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('std.log', 'a'))
print = logger.info
print('Logging_start')

###############  the configurations
base_dir = '/data/scratch/zhang/'

sources  = 'TauAGG'  # source type
sourcedb = base_dir+'taurus_1.sourcedb' # path to the source

sun_MS_dir   = base_dir+'MS/' # path to the dir contain sun's MS
calib_MS_dir = base_dir+'MS/' # path to the dir contain calibrator's MS
# better use the full directory

obs_sun_sap = '_SAP000'     # set to '' if none
obs_calib_sap = '_SAP001'     # set to '' if none

#obs_id_sun   = 'L722384' # obsid of the sun
obs_id_sun   = 'L701913' # obsid of the sun
#obs_id_calib = 'L701915' # obsid of the calibrator
obs_id_calib = 'L701913' # obsid of the calibrator

obs_sun_prefix   = '_autow' # prefix of the sun
obs_calib_prefix = '_autow' # prefix of the calibrator

idx_range_sun  = [23,43,10] # index range of the subband of the Sun
idx_range_cali = [83,103,10] # index range of the subband of the Sun
# start,end,stride

run_step = [0,1,2]; # 0 for predict; 1 for applycal;  2 for applybeam
# [0,1,2] for complete calibration
################


pred_dir  = '_par_pred_all_LBA/'
apcal_dir = '_par_apcal_all_LBA/'
apbm_dir  = '_par_apbm_all_LBA/'

sun_sb_arr   = np.arange(idx_range_sun[0],   idx_range_sun[1] +1 , idx_range_sun[2])
calib_sb_arr = np.arange(idx_range_cali[0] , idx_range_cali[1]+1 , idx_range_cali[2])

# to overwrite the subband index when the subband is not linearly distributed
sun_sb_arr   = [21 ]
calib_sb_arr = [x+60 for x in sub_sb_arr ]

# generate subband list
fill3zero = lambda x: 'SB'+str(x).zfill(3)
subband_sun    = list(map(fill3zero,sun_sb_arr))
subband_calibs = list(map(fill3zero,calib_sb_arr))


print(subband_sun)
print(subband_calibs)

# output ['SB092',......'SB099']

# template of the predict files
# msin.autoweight=true

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

start = time.time()


# predict the parset
if 0 in run_step:
    if not os.path.exists(pred_dir):
            os.makedirs(pred_dir)
    for subbd in subband_calibs:
        print('predict : '+subbd)
        # use the dir and the id to construct the file name
        MS_name = calib_MS_dir + obs_id_calib + obs_calib_sap + '_' +subbd+obs_calib_prefix+'_uv.MS'

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
    if not os.path.exists(apcal_dir):
            os.makedirs(apcal_dir)
    idx_cur = 0
    for subbd in subband_sun:
        print('applycal : '+subbd)
        # use the dir and the id to construct the file name
        MS_sun  = sun_MS_dir   + obs_id_sun   + obs_sun_sap   + '_'+subbd+obs_sun_prefix+'_uv.MS'
        MS_cali = calib_MS_dir + obs_id_calib + obs_calib_sap + '_'+subband_calibs[idx_cur]+obs_calib_prefix+'_uv.MS'
        # use the template and the file name to make a 'XXXX.parset' file

        apcal_content = apply_cal_template.replace('{{{1}}}',
                                   MS_sun).replace('{{{2}}}',MS_cali)
        tfile = open(apcal_dir+subbd+'_applycal.parset', "w")
        tfile.write(apcal_content)
        tfile.close()

        # call the NDPPP from system
        os.system('NDPPP '+apcal_dir+subbd+'_applycal.parset')
        idx_cur = idx_cur+1


# applybeam the parset
if 2 in run_step:
    if not os.path.exists(apbm_dir):
            os.makedirs(apbm_dir)
    for subbd in subband_sun:
            print('applybeam : '+subbd)
            # use the dir and the id to construct the file name
            MS_sun  = sun_MS_dir   + obs_id_sun   + obs_sun_sap   + '_'+subbd+obs_sun_prefix+'_uv.MS'
            # use the template and the file name to make a 'XXXX.parset' file
            apbm_content = apply_beam_template.replace('{{{1}}}',MS_sun)
            tfile = open(apbm_dir+subbd+'_applybeam.parset', "w")
            tfile.write(apbm_content)
            tfile.close()
            # call the NDPPP from system
            os.system('NDPPP '+apbm_dir+subbd+'_applybeam.parset')


# print out the time
end = time.time()
print('Elapsed time (s):')
print(end - start)
