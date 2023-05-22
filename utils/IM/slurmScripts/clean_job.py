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

# the directory and files

sun_dir='/wrk/group/corona/peijin/LC4/MStgt/t1245_1305/'
work_dir='/proj/group/corona/radio/data/LC4_ciara/preproc/'
sasid_sun   = 'L401013' # obsid of the sun
outdir = work_dir+'fits/'

os.chdir(work_dir)

f_sun_set=sorted(glob.glob(sun_dir+sasid_sun+'*.MS'))
f_sun = [f_sun_set[idx_this]]


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
