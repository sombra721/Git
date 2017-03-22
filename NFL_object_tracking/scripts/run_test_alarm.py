#-------------------------------------------------------------------------------
# Name:       run_test_alarm
# Author:      
# Created:     
# -----------------------------------------------------------------------------
# Description:
# ------------
# 	Python program to run the alarm test.
#
# Parameters:
#   test_name: a test folder name
#   host_name: IP address of a target machine 
#   
# Syntax:
#   run_test_alarm.py test_name host_name
#
# Example:
#  $ python run_test_alarm.py -t 01_alarm_status -m 192.168.30.207
#
# -----------------------------------------------------------------------------
#!/usr/bin/python
import time, os, sys
import json
import getopt
import math
from optparse import OptionParser
from os.path import expanduser
homeThisUser = expanduser("~")
lib_path = os.path.abspath(homeThisUser+ "/checkouts/zebra-qa/scripts_lib")
sys.path.append(lib_path)
import archive
import shutil
import distutils.core
from directory import Directory
import run_test_common


# -----------------------------------------
# Argument Parsing

parser = OptionParser("run_test_alarm.py -t <testname> -m <machine>")
parser.add_option('-t', "--testname", help='Name of the test.')
parser.add_option('-m', "--usermachine", help='username@address of the machine.')
(options, args) = parser.parse_args()

test_name = options.testname
user_machine = options.usermachine

if user_machine.find('@') < 0:
    user = "zadmin" 
    machine = user_machine
else:
    user = user_machine[:user_machine.index("@")]
    machine = user_machine[user_machine.index("@")+1:]

# -----------------------------------------
# checkouts
home = "/home/mwcentral"  
if homeThisUser != home:
    print "WARNING: you are not conected to the Test Controller via the user name: mwcentral."

oDir = Directory(homeThisUser, "paint_hangar", test_name, "zebra-boeing")

# -----------------------------------------
# Functions   
def test_compare():
    # Remove the last incomplete line, without a line feed.
    bashCommand = "bash " + oDir.scripts_lib_path + "/tail_off.sh " + oDir.alarm_log + " " + oDir.tmp_log
    os.system(bashCommand) 

    print " -- comparing logs ... \n"

    # exit code from the above python script:
    #    0   success
    #    1   failure
    bashCommand = "python " + oDir.compare + " " + oDir.tmp_log + " " + oDir.base_log + " " + cmp_opt + " > " + oDir.result
    err_code = os.system(bashCommand) 
    if not err_code == 0:
        err_code = 1
    return err_code

def display_result(exit_code):
    print "\n --\n -- Compare results:\n"
    fresults = open(oDir.result, "r")
    print fresults.read()
    if exit_code == 0:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " PASSED"
    else:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " Failed"
    print "\n -- Test finished!\n\n\n"
       
if __name__ == "__main__":
    # print the header
    run_test_common.print_header(test_name)

    # prepare for the test
    run_test_common.test_prepareRunDirectory(test_name, oDir.test_src_dir, oDir.zebra_qa_archive_path, oDir.test_run_dir, oDir.archive_path, oDir.config)

    # load the config file  
    config = run_test_common.read_test_config(oDir.config)
    TIMEOUT = config['TIMEOUT']
    cmp_opt = config['COMPARE_OPT']

    # copy test source files from the controller to the target for running test on the target.
    run_test_common.test_copyTestData_toTarget(user, machine, oDir.target_common_path, oDir.test_src_dir, oDir.target_script_path, "a")

    # run the test.
    run_test_common.run_the_test(user, machine, oDir.scripts_lib_path, "run_test_remote.sh", TIMEOUT, oDir.target_script_path)

    
    # copy test logs and results from the target to the controller.
    file_list = ["alarm.log", "p6relay.log"]
    run_test_common.test_copyTargetData_toTestController(user, machine, oDir.target_app_path, file_list, oDir.output_dir, oDir.target_deployment_info_dir, oDir.test_output_dir)

    exit_code = test_compare()

    #Archive Test and Results
    run_test_common.archieve_tests(oDir.scripts_lib_path, "archive_run.py", oDir.test_run_dir, oDir.archive_path, test_name)
    
    display_result(exit_code)
    sys.exit(exit_code)
