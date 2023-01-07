# -*- coding: utf-8 -*-
"""
python version msoverview

Usage:

python -m pymsoverview -f xxxxx.MS [-v]

Written by Peijin Zhang
version 0.1 2022-5-23 00:24:52: Initial version
"""

import casacore
import casacore.tables as pt
import datetime

import astropy
from astropy.time import Time

import numpy as np
import sys

from optparse import OptionParser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def info_print(header, content):   
    print(bcolors.HEADER+str(header)+bcolors.ENDC+str(content)+'\t')

def human_format(number):
    units = ['', 'k', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(np.floor(np.log(number[0])/np.log(k)))
    return (number / k**magnitude, units[magnitude])
    
def main():

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default=None,
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="detailed info")

    (options, args) = parser.parse_args()

    if options.filename==None:
        print(bcolors.FAIL+'Empty input.'+bcolors.ENDC)
    else:
        fname = options.filename
        ant = pt.taql('select NAME from '+fname+'/ANTENNA').getcol("NAME")
        nbaseline = int((len(ant)+1)*len(ant)/2)

        t_all  = pt.taql('select TIME from '+fname+' LIMIT ::$nbaseline').getcol('TIME')
        N_idx_time =  len(t_all)
        obs_this_tmp = pt.taql('select * from '+fname+'/OBSERVATION')
        time_range = (Time(obs_this_tmp.getcol('TIME_RANGE').ravel()[0:2]/3600/24.,
                           format='mjd').to_datetime())
        telescope_name = pt.taql('select TELESCOPE_NAME from '+fname+'/OBSERVATION').getcol('TELESCOPE_NAME')[0]


        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Input MS : '+fname)
        print('==============================================')
        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Antenna ')
        info_print('N Stations : \t',len(ant))
        info_print('N Baselines : \t',nbaseline)
        print(' ')

        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Time ')
        info_print('N time slot : \t',N_idx_time)
        info_print('Obs Start t :\t', str(time_range[0])+' (UTC)')
        info_print('Obs End t :\t', str(time_range[1])+' (UTC)')
        info_print('Total time :\t',pt.taql('select INTERVAL from '+fname+'/FEED').getcol('INTERVAL')[0])
        print(' ')


        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Observation ')
        info_print('Telescope : \t',telescope_name)
        info_print('Observer : \t',pt.taql('select OBSERVER from '+fname+'/OBSERVATION').getcol('OBSERVER')[0])
        info_print('Project : \t',pt.taql('select PROJECT from '+fname+'/OBSERVATION').getcol('PROJECT')[0])
        if telescope_name=="LOFAR":
            info_print('Project PI: \t',
                       pt.taql('select LOFAR_PROJECT_PI from '+fname+'/OBSERVATION').getcol('LOFAR_PROJECT_PI')[0])
            info_print('LOFAR SASID: \t',
                       pt.taql('select LOFAR_OBSERVATION_ID from '+fname+'/OBSERVATION').getcol('LOFAR_OBSERVATION_ID')[0])
            info_print('LOFAR Target: \t',
                       pt.taql('select LOFAR_TARGET from '+fname+'/OBSERVATION').getcol('LOFAR_TARGET')['array'][0])
        print(' ')




        #info_print('Project PI: \t',pt.taql('select PROJECT from '+fname+'/OBSERVATION').getcol('PROJECT')[0])
        print('==============================================')

        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Spectral Windows: ')
        spw = pt.taql('select * from '+fname+'/SPECTRAL_WINDOW')
        show_col = ['NAME','NUM_CHAN', 'REF_FREQUENCY', 'TOTAL_BANDWIDTH', 'CHAN_FREQ', 'CHAN_WIDTH', 'EFFECTIVE_BW']
        print('Name \t#Chan \tCh0(Hz) \tTotBW(Hz) \tChFreq(Hz) \tChW(Hz) \tEffBW(Hz)')
        obs_this_tmp.colnames()

        for rowid in spw.rownumbers():
            line_print=''
            for idx,entry in enumerate(show_col):
                if idx<=1:
                    line_print += (str(spw[rowid][entry])+'\t')
                else:
                    num,mag = human_format(np.array([spw[rowid][entry]]).ravel())
                    line_print += (str(np.round(num,3))+mag+'\t')

            print(line_print)
        print(' ')



        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Fields: ')
        spw = pt.taql('select * from '+fname+'/FIELD')
        show_col = ['PHASE_DIR','CODE','NAME']
        print('RA(d) \tDEC(d) \tCode \tName')
        obs_this_tmp.colnames()

        for rowid in spw.rownumbers():
            pointing = spw[rowid]['PHASE_DIR'].ravel()
            print(str(round(pointing[0]*180/np.pi,3))+'\t'+str(round(pointing[1]*180/np.pi,3))+'\t'+str(spw[rowid]['CODE'])+'\t'+str(spw[rowid]['NAME']))
        print(' ')


        print('==============================================')
        
        if options.verbose ==True:
            
            print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Antenna set: ')
            ant_all = pt.taql('select * from '+fname+'/ANTENNA')
            show_col = ['NAME','MOUNT', 'DISH_DIAMETER', 'POSITION']
            print('AntName \t#Mount \tDiameter(m) \tPosXYZ(m)')
            obs_this_tmp.colnames()

            for rowid in ant_all.rownumbers():
                line_print=''
                for idx,entry in enumerate(show_col):
                    if idx<=1:
                        line_print += (str(ant_all[rowid][entry])+'\t')
                    else:
                        line_print += (str(np.round(ant_all[rowid][entry],3))+'\t')

                print(line_print)
            print(' ')

        #print(ant)
        return 0


if __name__ == "__main__":
    sys.exit(main())