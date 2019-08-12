#!/usr/bin/python

'''
    File name: get_datetime_index.py
    Author: Peijin Zhang, Pietro Zucca
    Acknowledge: Sarrvesh Seethapuram Sridhar
    Date created: 2019-Aug
    Python Version: 3

    Given the starting and ending time point and 
    total index, Find out the index of some time 
    points between the starting and ending
'''


import datetime

t_start_MS = '14:17:00.0'   # start time point
t_end_MS   = '16:16:59.4'   # end time point
MS_record_total = 42912     # record of the MS
# these can be find these from $>msoverview in=LXXXXX_XXXXX.MS 


t_now_MS = ['14:17:00.0','14:22:00.0']  # a few time points


# find out the index of 't_now_MS'
t_format = '%H:%M:%S.%f'
t_start = datetime.datetime.strptime(t_start_MS , t_format)
t_end   = datetime.datetime.strptime(t_end_MS   , t_format)
t_now   = [datetime.datetime.strptime(x   , t_format) for x in t_now_MS]
now_idx = [round((x-t_start)/(t_end-t_start) * MS_record_total) for x in t_now]
print(now_idx)