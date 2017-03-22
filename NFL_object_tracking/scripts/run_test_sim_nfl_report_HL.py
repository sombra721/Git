#-------------------------------------------------------------------------------
# Name:       run_test_sim_nfl_report
# Author:      
# Created:     
# -----------------------------------------------------------------------------
# Description:
# ------------
# 	Python program to run the sim_nfl_report test.
#
# Parameters:
#   test_name: a test folder name
#   
# Syntax:
#   python run_test_sim_nfl_report.py -t <test_name>     
#
# Example:
#   $ python run_test_sim_nfl_report.py -t 01_basic_json_validation   
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

parser = OptionParser("python run_test_sim_nfl_report.py -t <testname>")
parser.add_option('-t', "--testname", default="01_basic_json_validation", help='Name of the test.')
(options, args) = parser.parse_args()

test_name    = options.testname

# -----------------------------------------
# checkouts
home = "/home/mwcentral"  
if homeThisUser != home:
    print "WARNING: you are not conected to the Test Controller via the user name: mwcentral."

oDir = Directory(homeThisUser, "sim_nfl_reports", test_name, "zebra-boeing")

# -----------------------------------------
# Functions   
programPath = oDir.nfl_reports_path
reportsPath = oDir.test_run_dir + "/output"
schemasPath = programPath       + "/nfl_schemas"  

def getCommandValidate(report,schema):        
    bashCommand = "python " + programPath + "/validate_json.py " + \
                     " -j " + reportsPath + "/" + report + \
                     " -s " + schemasPath + "/" + schema + \
                     " -m 1" + " >> " + oDir.test_output_dir + "/" + "out_" + report + ".log"
    return bashCommand
          
def validate_json_all(report_test_json):
    report_data = json.load(open(report_test_json))
    for i in report_data["test"]:
        bashCommand = getCommandValidate( i["report"], i["schema"] )
        os.system(bashCommand)


def display_result(exit_code):
    print "\n --\n -- Compare results:\n"
    fresults = open(oDir.result, "r")
    print fresults.read()
    if exit_code == 0:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " PASSED"
    else:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " Failed"
    print "\n -- Test finished!\n\n\n"
      
 
# ---------------------------------------------------------------------------"
if __name__ == "__main__":
    # print the header
    run_test_common.print_header(test_name)

    # prepare for the test
    run_test_common.test_prepareRunDirectory(test_name, oDir.test_src_dir, oDir.zebra_qa_archive_path, oDir.test_run_dir, oDir.archive_path, oDir.config)

    # run the test
    validate_json_all(oDir.qa_tests_dir + "/" + "sim_nfl_reports" + "/" + test_name + "/" + "report_tests.json")
    
    # archive test and results
    run_test_common.archieve_tests(oDir.scripts_lib_path, "archive_run.py", oDir.test_run_dir, oDir.archive_path, test_name)
    
    #display_result(exit_code)
    #sys.exit(exit_code)
