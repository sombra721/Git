# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 13:00:08 2014

@author: MTsai
"""

# Example use:
# test_proj = "nfl" OR "paint_hangar"
# target_app_dir = "zebra-boeing"
# oDir = Directory(homeThisUser, test_proj, test_name, target_app_dir)

# Notes
#self.TIMEOUT = "60" use from Config on tracker tests 

class Directory:
    def __init__(self, v_user_dir, v_test_proj, v_test_name, v_target_app_dir):
        self.user_dir = v_user_dir
        self.test_name = v_test_name        
        self.test_proj = v_test_proj
        self.target_app_dir = v_target_app_dir  #alarm log

        # zebra-qa
        self.checkouts_dir = self.user_dir + "/" + "checkouts"
        self.qa_dir = self.checkouts_dir + "/" + "zebra-qa"

        # tests -------------- 
        self.qa_tests_dir = self.qa_dir + "/" + "tests"
        self.qa_test_proj_path = self.qa_tests_dir + "/" + self.test_proj
        self.test_src_dir = self.qa_test_proj_path + "/" + self.test_name
               
        # scripts-lib -------------- 
        self.scripts_lib_dir = "scripts_lib"
        self.scripts_lib_path = self.qa_dir + "/" + self.scripts_lib_dir
        self.compare = self.scripts_lib_path + "/" + "Compare.py"

        # simulation -------------- 
        self.simulation_dir   = "simulation"
        self.simulation_path  = self.qa_dir + "/" + self.simulation_dir
        self.nfl_reports_path = self.simulation_path  + "/nfl_reports"


        # zebra-qa-archive ------------
        self.zebra_qa_archive_dir = "zebra-qa-archive"
        self.zebra_qa_archive_path = self.checkouts_dir + "/" + self.zebra_qa_archive_dir
        self.test_run_dir = self.zebra_qa_archive_path + "/test_run"
        self.archive_path = self.zebra_qa_archive_path + "/archive"

        # test run -----------------
        self.test_config_file = "run_test.conf"
        self.config = self.test_run_dir + "/" + self.test_config_file

        # test baseline 
        self.baseline_dir = "baseline"
        self.base_log = self.test_run_dir + "/" + self.baseline_dir + "/" + "boeing_standalone_alarm_baseline.log"

        # test run - output
	self.tag_location = "tag_location.csv"
	self.ent_location = "ent_location.csv"

        self.output_dir = self.test_run_dir + "/" + "output"

        self.alarm_log = self.output_dir + "/" + "alarm.log"
        self.tag_in_log = self.output_dir +"/" + self.tag_location
        self.ent_in_log = self.output_dir  +"/" + self.ent_location

        # test run - test output
	self.tag_location_tail_off = "tag_location_tail_off.csv"
	self.ent_location_tail_off = "ent_location_tail_off.csv"

        self.test_output_dir = self.test_run_dir + "/" + "test_output"

        self.result = self.test_output_dir + "/" + "result.txt"
        self.tmp_log = self.test_output_dir + "/" + "alarm_tmp.log"
        self.tag_result_log = self.test_output_dir  + "/" + self.tag_location_tail_off
        self.ent_result_log = self.test_output_dir  + "/" + self.ent_location_tail_off

        self.validation_log = self.test_output_dir + "/" + "validation.log"

        # target results directory ------------- 
        self.target_zebra = "/opt/zebra"
        self.deployment_info_dir = "zebra_deployment_info"

        self.target_common_dir = "common"
        self.target_datapump_dir = "zebra-datapump"  #tracker tag and entity csv
        self.target_scripts_dir = "scripts"

        self.target_deployment_info_dir = self.target_zebra + "/" + self.deployment_info_dir

        self.target_app_path = self.target_zebra + "/" + self.target_app_dir  #alarm log
        self.target_script_path = self.target_app_path + "/" + self.target_scripts_dir
        self.target_common_path = self.target_app_path + "/" + self.target_common_dir

        self.target_datapump_dir = self.target_zebra + "/" + self.target_datapump_dir  #tracker tag and entity csv




