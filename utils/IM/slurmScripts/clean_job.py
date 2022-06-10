#!/usr/bin/python3
#from __future__ import 
'''
    File name: clean_job.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug

    A script to clean
'''


import glob
import os
import time
import re
import sys

# the index of current job
idx_this = int(sys.argv[1])

os.chdir('/discofs/pjer1316/E20220519/proc')
base_dir = './MS_aw/'
outdir = './fits/'

all_files = sorted(glob.glob(base_dir+'*.MS'))

f_sun = []
f_calib = []
for item_f in all_files:
        if '_SAP000_' in item_f:
                f_sun.append(item_f)
        if '_SAP001_' in item_f:
                f_calib.append(item_f)

f_sun = [f_sun[idx_this]]


print(f_sun)



clean_cmd = """
wsclean -mem 95  -no-reorder -no-update-model-required \
 -mgain 0.7 -weight briggs 0 -multiscale \
 -auto-mask 3 -auto-threshold 0.3   \
 -size 1024 1024 -scale 10asec  -pol I -data-column CORRECTED_DATA \
 -niter 2000 -intervals-out 1100 -interval  5600 7801 \
 -fit-beam -name {{{1}}} {{{2}}}

"""

start = time.time()


for f_item in f_sun:
        print('clean : '+f_item)

        # print(parset_content)
        subbd= re.search('_SB[0-9]{3}_',f_item).group(0)[1:6]
        # use the template and the file name to make a 'XXXX.parset' file
        this_clean = clean_cmd.replace('{{{1}}}',
                             outdir+subbd).replace('{{{2}}}',
                             f_item)
        
        #print(this_clean)
        os.system(this_clean)
        

end = time.time()
print('Elapsed time (s):')
print(end - start)
