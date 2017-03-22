import os, sys, shutil
import distutils.core

def print_header(v_test_name):
    print "\n\n================================================================================================\n"
    print "prepare for " + v_test_name + " test...\n"

def test_prepareRunDirectory(test_name, v_test_src_dir, v_qa_archive_path, v_test_run_dir, v_archive_path, v_config):
    if not os.path.exists(v_test_src_dir):
        print "\nError: directory not found!"
        sys.exit()

    if not test_name:
        print " -- missing test name from the argument"
        sys.exit()

    if not os.path.exists(v_qa_archive_path):
        os.makedirs(v_qa_archive_path)
    
    shutil.rmtree(v_test_run_dir)

    if not os.path.exists(v_test_run_dir):
        os.makedirs(v_test_run_dir) 

    if not os.path.exists(v_archive_path):
        os.makedirs(v_archive_path) 

    print "-- copy test files to " + v_test_run_dir + "\n"

    distutils.dir_util.copy_tree(v_test_src_dir, v_test_run_dir)

    # temp system env variables $TIMEOUT, $COMPARE_OPT
    bashCommand = "source " + v_config
    os.system(bashCommand)    

def test_copyTargetData_toTestController(v_user, v_machine, v_target_source_path, v_file_list, v_destination_path, v_target_deployment_info_dir, v_test_output_path):
    print "-- copying logs and results from the target to the controller ...\n"
    for i in v_file_list:
        bashCommand = "rsync -vpc " + v_user + "@" + v_machine +":" +  v_target_source_path + "/" + i + " " + v_destination_path
        os.system(bashCommand) 

    bashCommand = "rsync -vpc " + v_user + "@" + v_machine +":" + v_target_deployment_info_dir +"/deploy_summary.txt " + v_test_output_path
    os.system(bashCommand)

    
def test_copyTestData_toTarget(v_user, v_machine, v_target_common_path, v_test_src_dir, v_target_script_path, v_stop_option):
    print "---\n"
    dst = v_user + "@" + v_machine  + ":" + v_target_common_path + "/" 
    print "-- copying files to " + dst + "..."

    bashCommand = "rsync -vpc " + v_test_src_dir + "/config" + "/" + "models.json " + dst 
    os.system(bashCommand) 

    file_list = ["standalone.config", "standalone_entity.json", "standalone_tag_positions.csv"]

    # -v: verbal,  -p: preserse file permission, -c: checksum
#    bashCommand = "rsync -vpc " + v_test_src_dir  + "/config" + "/" + "boeing_standalone.config " + dst 
#    os.system(bashCommand)     
   
#    bashCommand = "rsync -vpc " + v_test_src_dir + "/config" + "/" + "boeing_standalone_entity.json " + dst 
#    os.system(bashCommand) 
   

   
#    bashCommand = "rsync -vpc " + v_test_src_dir + "/data" + "/" + "boeing_standalone_tag_positions.csv " + dst 
#    os.system(bashCommand) 
   
    dst = v_user + "@" + v_machine  + ":" + v_target_script_path + "/"
    print "-- copying files to " + dst + "..."

    bashCommand = "rsync -vpc " + v_test_src_dir + "/" + "start.sh " + dst 
    os.system(bashCommand)     

    # a means Alarm
    if v_stop_option == "a":
        bashCommand = "rsync -vpc " + v_test_src_dir + "/" + "stop_test.sh " + dst 
        os.system(bashCommand)
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/config" + "/" + "boeing_" + file_list[0] + " " + dst 
        os.system(bashCommand)
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/config" + "/" + "boeing_" + file_list[1] + " " + dst 
        os.system(bashCommand)
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/data" + "/" + "boeing_" + file_list[2] + " " + dst 
        os.system(bashCommand)

    # n means NFL
    elif v_stop_option == "n":
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/config" + "/" + file_list[0] + " " + dst 
        os.system(bashCommand)
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/config" + "/" + file_list[1] + " " + dst 
        os.system(bashCommand)
        bashCommand = "rsync -vpc " + v_test_src_dir  + "/data" + "/" + file_list[2] + " " + dst 
        os.system(bashCommand)
          

def run_the_test(v_user, v_machine, v_scripts_lib_path, v_test_shell_file, v_timeout, v_target_script_path):
    bashCommand = "bash " + v_scripts_lib_path  + "/" + v_test_shell_file + " -t " + v_timeout + " -s " + v_target_script_path + " -m " + v_user + "@" + v_machine
    os.system(bashCommand)

def read_test_config(v_config_file):
    file1 = open(v_config_file, 'r')
    var = dict()
    while True:
        string = file1.readline()
        line = string.strip()
        if not line: 
            break
        pos = line.find("!")
        if (pos != 0) and line != "":     #not comment line and not blanks line
            if pos > -1:  #-1 or 0
                command = line[0:pos+1]
            else:
                command = line
            cname = command.split("=")
            var[ cname[0].strip() ] = cname[1].strip()
    return var

def archieve_tests(v_scripts_lib_path, v_archive_file, v_test_run_dir, v_archive_path, v_test_name):
    bashCommand = "python " + v_scripts_lib_path + "/" + v_archive_file + " " + v_test_run_dir + " " + v_archive_path + " " + v_test_name
    os.system(bashCommand)

