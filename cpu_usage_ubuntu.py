#!/usr/bin/python 
# -*- coding: utf-8 -*-

'''
Created on 06.22.2016

@author: Michael Tsai
'''
from time import sleep
import sys
import datetime 
import time
import csv
import collections
import time
import natsort 
import re

class GetCpuLoad(object):
    '''
    classdocs
    '''


    def __init__(self, percentage=True, sleeptime = 1):
        self.percentage = percentage
        self.cpustat = '/proc/stat'
        self.sep = ' ' 
        self.sleeptime = sleeptime

    def getcputime(self):
        '''
        http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux
        read in cpu information from file
        The meanings of the columns are as follows, from left to right:
            0cpuid: number of cpu
            1user: normal processes executing in user mode
            2nice: niced processes executing in user mode
            3system: processes executing in kernel mode
            4idle: twiddling thumbs
            5iowait: waiting for I/O to complete
            6irq: servicing interrupts
            7softirq: servicing softirqs

        #the formulas from htop 
             user    nice   system  idle      iowait irq   softirq  steal  guest  guest_nice
        cpu  74608   2520   24433   1117073   6176   4054  0        0      0      0


        Idle=idle+iowait
        NonIdle=user+nice+system+irq+softirq+steal
        Total=Idle+NonIdle # first line of file for all cpus

        CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)
        '''
        cpu_infos = {} #collect here the information
        with open(self.cpustat,'r') as f_stat:
            lines = [line.split(self.sep) for content in f_stat.readlines() for line in content.split('\n') if line.startswith('cpu')]

            #compute for every cpu
            for cpu_line in lines:
                if '' in cpu_line: cpu_line.remove('')#remove empty elements
                cpu_line = [cpu_line[0]]+[float(i) for i in cpu_line[1:]]#type casting
                cpu_id,user,nice,system,idle,iowait,irq,softrig,steal,guest,guest_nice = cpu_line

                Idle=idle+iowait
                NonIdle=user+nice+system+irq+softrig+steal

                Total=Idle+NonIdle
                #update dictionionary
                cpu_infos.update({cpu_id:{'total':Total,'idle':Idle}})
                ts = int(time.time())
                st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                cpu_infos.update({"timestamp":st})
            return cpu_infos

    def getcpuload(self):
        '''
        CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)
        '''
        start = self.getcputime()
        #wait a second
        sleep(self.sleeptime)
        stop = self.getcputime()

        cpu_load = {}

        for cpu in start: 
            if "cpu" in cpu:
                Total = stop[cpu]['total']
                PrevTotal = start[cpu]['total']

                Idle = stop[cpu]['idle']
                PrevIdle = start[cpu]['idle']
                CPU_Percentage=((Total-PrevTotal)-(Idle-PrevIdle))/(Total-PrevTotal)*100
                cpu_load.update({cpu: CPU_Percentage})
        cpu_load.update({"timestamp":start["timestamp"]})
        print "cpu_load:\n", cpu_load
        return cpu_load

def convert_dict_key(key):
    try:
        return int(key.split('_')[1])
    except:
        return key

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

if __name__=='__main__':
    cpu_max = {}
    x = GetCpuLoad()
    outputfile = "cpu_usage.csv"
    for i in x.getcpuload().keys():
        if "cpu" in i:
            cpu_max[i] = 0
    print "cpu_max: \n", cpu_max
    od = collections.OrderedDict(sorted(x.getcpuload().items()))
    sorted_keys = natural_sort(x.getcpuload())
    with open(outputfile, 'wb') as f:  # Just use 'w' mode in 3.x
        #w = csv.DictWriter(f, od.keys())
        w = csv.DictWriter(f, sorted_keys)
        w.writeheader()
    while True:
        try:
            data = x.getcpuload()
            od = collections.OrderedDict(sorted(data.items()))
            for i in data.keys():
                if "cpu" in i:
                    if float(cpu_max[i]) < float(data[i]):
                        cpu_max[i] = float(data[i])
            with open(outputfile, 'a') as f:  # Just use 'w' mode in 3.x
                w = csv.DictWriter(f, sorted_keys)
                w.writerow(od)
            print "cpu_max: \n", cpu_max
        except KeyboardInterrupt:
            #od = collections.OrderedDict(sorted(cpu_max.items()))
            od = collections.OrderedDict(sorted((key, value) for key, value in cpu_max.items()))
            
            with open(outputfile, 'a') as f:  # Just use 'w' mode in 3.x
                w = csv.DictWriter(f, sorted_keys)
                w.writerow(od)
            sys.exit("Finished") 
