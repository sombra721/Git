#-------------------------------------------------------------------------------
# Name:       run_test_tracker
# Author:      
# Created:     
# -----------------------------------------------------------------------------
# Description:
# ------------
# 	Python program to run the tracker test.
#
# Parameters:
#   test_name: a test folder name
#   host_name: IP address of a target machine 
#   
# Syntax:
#   run_test_tracker.sh test_name host_name
#
# Example:
#  $ python run_test_tracker.py -t 01_tracker_line -m 192.168.30.207
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
from Compare import simpleMatch, complexMatch
import archive
import shutil
import distutils.core
from directory import Directory
import run_test_common

# -----------------------------------------
# Argument Parsing

parser = OptionParser("run_test_tracker.py -t <testname> -m <machine>")
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

oDir = Directory(homeThisUser, "nfl", test_name, "zebra-boeing")

# -----------------------------------------
# Functions
def tailoff_csv():
   bashCommand = "bash " + oDir.scripts_lib_path  + "/tail_off.sh " + oDir.tag_in_log + " " + oDir.tag_result_log
   os.system(bashCommand) 

   bashCommand = "bash " + oDir.scripts_lib_path  + "/tail_off.sh " + oDir.ent_in_log + " " + oDir.ent_result_log
   os.system(bashCommand)         

   print "--- removing the last line of the new log ..." 

def test_generate_svg():
    print "Generate the SVG file(s) --  archive"
    os.chdir(oDir.test_run_dir)
    if svg_out == "S":
        print "Single"
        bashCommand = "python " + oDir.scripts_lib_path  + "/svg_graph_for_tag_ent_locates.py -t " + oDir.test_output_dir + "/" + oDir.tag_location_tail_off + " -e " + oDir.test_output_dir + "/" + oDir.ent_location_tail_off + " -s " + oDir.test_run_dir + "/test_output/svg.html"
        os.system(bashCommand) 
    elif svg_out == "M":
        print "Multiple"
        bashCommand = "python " + oDir.scripts_lib_path  + "/svg_graph_for_tag_ent_locates.py -t " + oDir.test_output_dir + "/" + oDir.tag_location_tail_off +" -e " +  oDir.test_output_dir + "/" + oDir.ent_location_tail_off + " -c " + oDir.test_run_dir + "/config/standalone_entity.json"
        os.system(bashCommand) 

def test_compare_ent():
    print "compare the ent_location and the ent_location then put the results in the -- archive"
    bashCommand = "python " + oDir.scripts_lib_path + "/compare_ent_locates.py -e " + oDir.test_output_dir + "/" + oDir.ent_location_tail_off + " -b " + oDir.test_run_dir + "/" + oDir.baseline_dir + "/" + "ent_location_baseline.csv"
    os.system(bashCommand) 

if __name__ == "__main__":
    # print the header
    run_test_common.print_header(test_name)
 
    # prepare for the test  
    run_test_common.test_prepareRunDirectory(test_name, oDir.test_src_dir, oDir.zebra_qa_archive_path, oDir.test_run_dir, oDir.archive_path, oDir.config)
  
    config = run_test_common.read_test_config(oDir.config)
    TIMEOUT = config['TIMEOUT']
    svg_out = config['SVG_OUT'] 
  
    # copy test source files from the controller to the target for running test on the target.
    run_test_common.test_copyTestData_toTarget(user, machine, oDir.target_common_path, oDir.test_src_dir, oDir.target_script_path, "n")

    # run the test.
    run_test_common.run_the_test(user, machine, oDir.scripts_lib_path, "run_test_remote.sh", TIMEOUT, oDir.target_script_path)

    # copy test logs and results from the target to the controller.
    file_list = [oDir.tag_location, oDir.ent_location]
    run_test_common.test_copyTargetData_toTestController(user, machine, oDir.target_datapump_dir, file_list, oDir.output_dir, oDir.target_deployment_info_dir, oDir.test_output_dir)
    
    tailoff_csv()
    
    test_generate_svg()

    test_compare_ent()

    #Archive Test and Results
    run_test_common.archieve_tests(oDir.scripts_lib_path, "archive_run.py", oDir.test_run_dir, oDir.archive_path, test_name)

    print "\n -- Test finished!\n\n\n"
