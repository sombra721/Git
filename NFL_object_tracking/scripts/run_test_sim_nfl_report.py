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

parser = OptionParser("run_test_sim_nfl_report.py -t <testname>")
parser.add_option('-t', "--testname", help='Name of the test.')
(options, args) = parser.parse_args()

test_name    = options.testname


# -----------------------------------------
# checkouts
home = "/home/mwcentral"  
if homeThisUser != home:
    print "WARNING: you are not conected to the Test Controller via the user name: mwcentral."

oDir = Directory(homeThisUser, "sim_nfl_report", test_name, "zebra-boeing")

# -----------------------------------------
# Functions   


def getCommandValidate(report,schema):
 programPath = ""
 reportsPath = "nfl_reports"
 schemaPath = "nfl_schemas"

 bashCommand = "python "+programPath+"/"+"validate_json.py"+" -j "+reportsPath+"/"+report+" -s "+reportsPath"+"/"+schema+" -m 1"
 return bashCommand


def validate_json_all():

 programPath = ""
 reportsPath = "nfl_reports"
 schemaPath = "nfl_schemas"

 # 5. Report.pdf

 bashCommand = getCommandValidate("pp.json","pp_sch.json")
 os.system(bashCommand)
 
 python validate_json.py -j nfl_reports/pp.json -s    nfl_schemas/pp_sch.json    -m 1
 python validate_json.py -j nfl_reports/pp_pd.json -s nfl_schemas/pp_pd_sch.json -m 1
 python validate_json.py -j nfl_reports/pp_g.json -s  nfl_schemas/pp_g_sch.json  -m 1

 # 3.Tracking Data.pdf

 python validate_json.py -j nfl_reports/p_gid_th.json -s nfl_schemas/p_gid_th_sch.json   -m 1
 python validate_json.py -j nfl_reports/p_gid_ta.json -s nfl_schemas/p_gid_ta_sch.json   -m 1

 python validate_json.py -j nfl_reports/p_gid_mh.json -s nfl_schemas/p_gid_mh_sch.json  -m 1
 python validate_json.py -j nfl_reports/p_gid_ma.json -s nfl_schemas/p_gid_ma_sch.json  -m 1

 python validate_json.py -j nfl_reports/gid_toff.json -s nfl_schemas/gid_toff_sch.json -m 1

 python validate_json.py -j nfl_reports/gid_tobj.json -s nfl_schemas/gid_tobj_sch.json -m 1

 python validate_json.py -j nfl_reports/gid_tch.json -s nfl_schemas/gid_tch_sch.json -m 1
 python validate_json.py -j nfl_reports/gid_tca.json -s nfl_schemas/gid_tca_sch.json -m 1

 python validate_json.py -j nfl_reports/gid_mch.json -s nfl_schemas/gid_mch_sch.json -m 1
 python validate_json.py -j nfl_reports/gid_mca.json -s nfl_schemas/gid_mca_sch.json -m 1


 # 4. Non-Tracking Data.pdf

 python validate_json.py -j nfl_reports/gid_pid_gs.json         -s nfl_schemas/gid_pid_gs_sch.json -m 1
 python validate_json.py -j nfl_reports/gid_pid_ge.json         -s nfl_schemas/gid_pid_ge_sch.json -m 1


def display_result(exit_code):
    print "\n --\n -- Compare results:\n"
    fresults = open(oDir.result, "r")
    print fresults.read()
    if exit_code == 0:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " PASSED"
    else:
        print "\nExit code: " + str(exit_code) +  "\n-- " + test_name + " Failed"
    print "\n -- Test finished!\n\n\n"
       
# ------------------------------------------
if __name__ == "__main__":
    # print the header
    run_test_common.print_header(test_name)

    # prepare for the test
    run_test_common.test_prepareRunDirectory(test_name, oDir.test_src_dir, oDir.zebra_qa_archive_path, oDir.test_run_dir, oDir.archive_path, oDir.config)

    # load the config file  
    config = run_test_common.read_test_config(oDir.config)
    TIMEOUT = config['TIMEOUT']
    cmp_opt = config['COMPARE_OPT']

    # run the test
    
    # copy test logs and results from the sim target to the controller.
    #file_list = ["alarm.log", "p6relay.log"]
    #run_test_common.test_copyTargetData_toTestController(user, machine, oDir.target_app_path, file_list, oDir.output_dir, oDir.target_deployment_info_dir, oDir.test_output_dir)
    #instead copy reports file to run_test/results dir

    validate_json_all()


    #Archive Test and Results
    run_test_common.archieve_tests(oDir.scripts_lib_path, "archive_run.py", oDir.test_run_dir, oDir.archive_path, test_name)
    
    display_result(exit_code)
    sys.exit(exit_code)
