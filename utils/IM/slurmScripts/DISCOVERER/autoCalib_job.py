#!/usr/bin/python3
#from __future__ import 
'''
    File name: auto_sun_calib.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug

    A script to calibrate the Measurement Set
'''


import glob
import os
import time
import re
import sys

# the index of current job
idx_this = int(sys.argv[1])

# the directory and files
os.chdir('/discofs/pjer1316/E20220519/proc')
base_dir = './MS_aw/'
all_files = sorted(glob.glob(base_dir+'*.MS'))

# calibrator
sources  = 'CasA_4_patch'  # source type
sourcedb = './CasA.sourcedb' # path to the source

###########################################################

f_sun = []
f_calib = []
for item_f in all_files:
        if '_SAP000_' in item_f:
                f_sun.append(item_f)
        if '_SAP001_' in item_f:
                f_calib.append(item_f)

f_sun = [f_sun[idx_this]]
f_calib = [f_calib[idx_this]]


print(f_sun)


run_step = [0,1,2]; # 0 for predict; 1 for applycal;  2 for applybeam
# [0,1,2] for complete calibration


pred_dir  = '_par_pred_all_LBA/'
apcal_dir = '_par_apcal_all_LBA/'
apbm_dir  = '_par_apbm_all_LBA/'


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
    for f_item in f_calib:
        print('predict : '+f_item)

        # use the template and the file name to make a 'XXXX.parset' file
        parset_content = predict_parset_template.replace('{{{1}}}',
                             f_item).replace('{{{2}}}',
                             sources).replace('{{{3}}}',sourcedb)

        # print(parset_content)
        subbd= re.search('_SB[0-9]{3}_',f_item).group(0)[1:6]
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
    for f_item in f_sun:
        print('applycal : '+f_item)

        apcal_content = apply_cal_template.replace('{{{1}}}',
                                   f_sun[idx_cur]).replace('{{{2}}}',f_calib[idx_cur])
        tfile = open(apcal_dir+subbd+'_applycal.parset', "w")
        tfile.write(apcal_content)
        tfile.close()
        # print(apcal_content)
        # call the NDPPP from system
        os.system('NDPPP '+apcal_dir+subbd+'_applycal.parset')
        idx_cur = idx_cur+1


# applybeam the parset
if 2 in run_step:
    if not os.path.exists(apbm_dir):
            os.makedirs(apbm_dir)
    for f_item in f_sun:
            # use the template and the file name to make a 'XXXX.parset' file
            apbm_content = apply_beam_template.replace('{{{1}}}',f_item)
            tfile = open(apbm_dir+subbd+'_applybeam.parset', "w")
            tfile.write(apbm_content)
            tfile.close()
            #print(apbm_content)
            # call the NDPPP from system
            os.system('NDPPP '+apbm_dir+subbd+'_applybeam.parset')


# print out the time
end = time.time()
print('Elapsed time (s):')
print(end - start)
