#!/usr/bin/pyhton2

'''
    File name: auto_sun_calib.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug

    A script to calibrate the Measurement Set
    !loads file list from ms.json
'''

import glob
import os
import subprocess
import time
import numpy as np
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('std.log', 'a'))
print = logger.info
print('Logging_start')

###############  the configurations
base_dir = './'

sources  = 'TauAGG' #'CasA_4_patch'  # source type
sourcedb = base_dir+'taurus_1.sourcedb' # path to the source

sun_MS_dir   = base_dir+'MS_aw/' 
cal_MS_dir = base_dir+'MS_aw/' 

msfiles = 'ms.json'
# load file list
f = open (msfiles, "r")
meta = json.loads(f.read())


run_step = [0,1,2]; # 0 for predict; 1 for applycal;  2 for applybeam
# [0,1,2] for complete calibration
################


pred_dir  = '_par1_pred_all_LBA/'
apcal_dir = '_par1_apcal_all_LBA/'
apbm_dir  = '_par1_apbm_all_LBA/'


# generate subband list
fill3zero = lambda x: 'SB'+str(x).zfill(3)

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
    for idx,MS_cal in enumerate(meta['cal']):
        print('predict : '+MS_cal)
        # use the dir and the id to construct the file name
        
        parset_content = predict_parset_template.replace('{{{1}}}',
                             cal_MS_dir+MS_cal).replace('{{{2}}}',
                             sources).replace('{{{3}}}',sourcedb)
        tfile = open(pred_dir+MS_cal+'_predict.parset', "w")
        tfile.write(parset_content)
        tfile.close()
        # call the NDPPP from system
        os.system('NDPPP '+pred_dir+MS_cal+'_predict.parset')

# applycal the parset
if 1 in run_step:
    if not os.path.exists(apcal_dir):
            os.makedirs(apcal_dir)
    idx_cur = 0
    for idx,MS_sun in enumerate(meta['sun']):
        print('applycal : '+MS_sun)
        # use the dir and the id to construct the file name
        
        apcal_content = apply_cal_template.replace('{{{1}}}',
                                   sun_MS_dir+MS_sun).replace('{{{2}}}',cal_MS_dir+meta['cal'][idx])                                          
        tfile = open(apcal_dir+MS_sun+'_applycal.parset', "w")
        tfile.write(apcal_content)
        tfile.close()
                                                   
        # call the NDPPP from system
        os.system('NDPPP '+apcal_dir+MS_sun+'_applycal.parset')
        idx_cur = idx_cur+1


# applybeam the parset
if 2 in run_step:
    if not os.path.exists(apbm_dir):
            os.makedirs(apbm_dir)
    for idx,MS_sun in enumerate(meta['sun']):
            print('applybeam : '+MS_sun)
            # use the dir and the id to construct the file name
            
            apbm_content = apply_beam_template.replace('{{{1}}}',sun_MS_dir+MS_sun)
            tfile = open(apbm_dir+MS_sun+'_applybeam.parset', "w")
            tfile.write(apbm_content)
            tfile.close()
            # call the NDPPP from system
            os.system('NDPPP '+apbm_dir+MS_sun+'_applybeam.parset')


# print out the time
end = time.time()
print('Elapsed time (s):')
print(end - start)
