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


def get_obs_info_from_ms(fname):
    """ get observation information from ms

    Args:
        fname (string): measurement set name

    Returns:
        list : list of antenna name
        int : number of baselines
        string : telescope name
    """
    ant = pt.taql('select NAME from '+fname+'/ANTENNA').getcol("NAME")
    nbaseline = int((len(ant)+1)*len(ant)/2)
    telescope_name = pt.taql('select TELESCOPE_NAME from '+fname+'/OBSERVATION').getcol('TELESCOPE_NAME')[0]
    return ant, nbaseline, telescope_name


def get_t_from_ms(fname):
    """ get time information from ms

    Args:
        fname (string): measurement set name

    Returns:
        int : total number of time index
        list : time range
    """
    ant, nbaseline, telescope_name = get_obs_info_from_ms(fname)
    t_all  = pt.taql('select TIME from '+fname+' LIMIT ::$nbaseline').getcol('TIME')
    N_idx_time =  len(t_all)
    obs_this_tmp = pt.taql('select * from '+fname+'/OBSERVATION')
    time_range = (Time(obs_this_tmp.getcol('TIME_RANGE').ravel()[0:2]/3600/24.,
                           format='mjd').to_datetime())
    return N_idx_time, time_range

def get_freq_from_ms(fname):
    spw = pt.taql('select REF_FREQUENCY from '+fname+'/SPECTRAL_WINDOW')
    return spw.getcol('REF_FREQUENCY')[0]

def ms_datetime_to_index(fname, t, t_format='%H:%M:%S.%f'):
    """ convert datetime to index

    Args:
        fname (string): measurement set name
        t (datetime): datetime

    Returns:
        int : index
    """
    N_idx_time, time_range = get_t_from_ms(fname)
    t_start = datetime.datetime.strftime(time_range[0],t_format) 
    t_end   = datetime.datetime.strftime(time_range[1],t_format)
        
    # find out the index of 't_now_MS'
    t_now   = datetime.datetime.strptime(t   , t_format)
    t_start   = datetime.datetime.strptime(t_start  , t_format)
    t_end   = datetime.datetime.strptime(t_end   , t_format)
    now_idx = round((t_now-t_start)/(t_end-t_start) * N_idx_time) 
    return now_idx

def ms_index_to_datetime(fname, idx):
    N_idx_time, time_range = get_t_from_ms(fname)
    t_start = time_range[0]
    t_end   = time_range[1]
    t_now = float(idx) / float(N_idx_time) * (t_end - t_start) + t_start
    return t_now
    
#==============================================================================
# the cli entry points:

def pyms_overview_main():
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
        
        N_idx_time, time_range = get_t_from_ms(fname)
        ant, nbaseline, telescope_name = get_obs_info_from_ms(fname)

        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Input MS : '+fname)
        print('==============================================')
        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Antenna ')
        info_print('N Stations : \t',len(ant))
        info_print('N Baselines : \t',nbaseline)
        print(' ')

        print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Time ')
        info_print('N time slot : \t',N_idx_time)
        info_print('Obs Start t : \t', str(time_range[0])+' (UTC)')
        info_print('Obs End t : \t', str(time_range[1])+' (UTC)')
        info_print('T_end-T_start: \t', str((time_range[1]-time_range[0]).total_seconds()))
        info_print('dT:\t', str(round((time_range[1]-time_range[0]).total_seconds()/N_idx_time, 5)))
        info_print('Total t(raw): \t',pt.taql('select INTERVAL from '+fname+'/FEED').getcol('INTERVAL')[0])
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
        #obs_this_tmp.colnames()

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
        #obs_this_tmp.colnames()

        for rowid in spw.rownumbers():
            pointing = spw[rowid]['PHASE_DIR'].ravel()
            print(str(round(pointing[0]*180/np.pi,2))+'\t'+str(round(pointing[1]*180/np.pi,2))+'\t'+str(spw[rowid]['CODE'])+'\t'+str(spw[rowid]['NAME']))
        print(' ')


        print('==============================================')
        
        if options.verbose ==True:
            
            print(bcolors.OKGREEN+'[INFO]'+bcolors.ENDC+' Antenna set: ')
            ant_all = pt.taql('select * from '+fname+'/ANTENNA')
            show_col = ['NAME','MOUNT', 'DISH_DIAMETER', 'POSITION']
            print('AntName \t#Mount \tDiameter(m) \tPosXYZ(m)')
            #obs_this_tmp.colnames()

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

def pyms_datetime_to_index_main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default=None,
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-t", "--time", dest="time", default='12:00:00.000',
                      help="default time format is %H:%M:%S.%f, can be changed by -fmt")
    parser.add_option("--fmt", "--format", dest="format", default='%H:%M:%S.%f',
                      help="default is %H:%M:%S.%f")

    (options, args) = parser.parse_args()

    if options.filename==None:
        print(bcolors.FAIL+'Empty input.'+bcolors.ENDC)
    else:
        fname = options.filename
        
        t_format = options.format
        now_idx = ms_datetime_to_index(fname, options.time, t_format)
        print(now_idx)
    return 0


def pyms_index_to_datetime_main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", default=None,
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-i", "--idx", dest="idx", default='0',
                      help="index of the slot")
    parser.add_option("--fmt", "--format", dest="format", default='%H:%M:%S.%f',
                      help="default is %H:%M:%S.%f")

    (options, args) = parser.parse_args()

    if options.filename==None:
        print(bcolors.FAIL+'Empty input.'+bcolors.ENDC)
    else:
        fname = options.filename
        t_format = options.format
        t_now = ms_index_to_datetime(fname, options.idx)
        print(t_now.strftime(options.format))
    return 0