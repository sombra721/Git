#-------------------------------------------------------------------------------
# Name:       run_test_alarm
# Author:      
# Created:     
# -----------------------------------------------------------------------------
# Description:
# ------------
# 	Python program to call a bash script run_test_alarm.sh
#
# Parameters:
#   test_name: a test folder name
#   host_name: IP address of a target machine 
#   
# Syntax:
#   run_test_alarm.sh test_name host_name
#
# Example:
#  $ python run_test_alarm.py -t 01_alarm_status -m mwcentral@192.168.5.119
#
# -----------------------------------------------------------------------------
#!/usr/bin/python
import time, os, sys
import json
import getopt
import math

def main(argv):
    testname = ''
    machine = ''
    projectdir = ''
    exit_code = 0
    try:
        opts, args = getopt.getopt(argv,"ht:m:d:",["testname=","machine=", "projectdir"])
    except getopt.GetoptError:
        print 'run_test_alarm.py -t <testname> -m <machine> -d <projectdir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'run_test_alarm.py -t <testname> -m <machine> -d <projectdir>'
            sys.exit()
        elif opt in ("-t", "--testname"):
            testname = arg
        elif opt in ("-m", "--machine"):
            machine = arg
        elif opt in ("-d", "--projectdir"):
            projectdir = arg
    print 'Test Name: ', testname
    print 'Machine: ', machine
    print 'Project Dir: ', projectdir

    bashCommand = "bash run_test_alarm.sh " + " -d " + projectdir + " -t " + testname + " -m " + machine 
    print bashCommand

    exit_code = os.system(bashCommand)
    sys.exit (exit_code)

if __name__ == '__main__':
    main(sys.argv[1:])
