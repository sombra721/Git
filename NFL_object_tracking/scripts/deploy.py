import math, os, sys, datetime, shutil
from optparse import OptionParser
from os.path import expanduser

# uses library.
sys.path.append('../scripts_lib/')
from utils import *
from deployment_definitions import *

# Usage:
USAGE = 'Usage: \n' + \
       '  deploy.py -d project_dir -y yml_name [-i inventory_hosts] [-l hostnames] [-a app] [-t deploy_tags][-h help]\n'  + \
       '  OR\n'  + \
       '  deploy.py -c deploy_config_file\n'

# time stamp
time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# ----------------------------------------------------------------------------------------------------------
# -c option: uses deploy properties from predefined deployment file.
def get_properties_from_config_file(deploy_config_file):
    global deploy_playbook_file, inventory_dir, inventory_file, hostnames, release_directory, config_dir, \
           deploy_tags, deploy_skip_tags, full_deploy_config_file, deploy_dict

    # creates a dictionary using config file.    
    full_deploy_config_file = os.path.join( zebra_qa_deployments_dir, deploy_config_file )
    deploy_dict = parse_properties_from_config_file( full_deploy_config_file )

    # assigns values.
    release_directory = deploy_dict[ 'release_directory' ].strip('"')
    deploy_playbook_file = deploy_dict[ 'deploy_playbook_file' ].strip('"')
    inventory_dir = deploy_dict[ 'inventory_dir' ].strip('"')
    inventory_file = deploy_dict[ 'inventory_file' ].strip('"')
    hostnames = deploy_dict[ 'hostnames' ].strip('"')
    # do not strip the quotation: we need them for "--tags" and "--skip-tags" to work.
    deploy_tags = deploy_dict[ 'deploy_tags' ]
    deploy_skip_tags = deploy_dict[ 'deploy_skip_tags' ]
    config_dir = deploy_dict[ 'config_dir' ]

# ----------------------------------------------------------------------------------------------------------
# uses command line parameters.
def get_properties_from_command_line():
    global deploy_playbook_file, inventory_file, hostnames, release_directory, deploy_tags, deploy_skip_tags, deploy_dict
    #
    release_directory = options.reldir
    deploy_playbook_file = options.yaml
    inventory_file = options.inventory_file
    hostnames = options.hostnames
    app = options.app
    if options.tags:
        deploy_tags = '"' + options.tags + '"'
    # -a 
    if app == True:
        deploy_skip_tags = '"common"'

# ----------------------------------------------------------------------------------------------------------
# make two copies of the given file into zebra_deployment_info zebra_deploy_info/history directories.
def save_file ( full_dir, info_file ):
    # 1. prefix the file name with current timestamp.
    datetime_file = time_stamp + "_" + info_file
    # 2. copy it to zebra_deploy_info directory, and 
    full_info_file = os.path.join(full_dir, info_file)
    shutil.copy2( full_info_file, zebra_deployment_info_dir )
    # 3. also copy it to zebra_deploy_info/history directory.
    shutil.copy2( full_info_file, os.path.join(zebra_deployment_info_history_dir, datetime_file) )
        
# ----------------------------------------------------------------------------------------------------------
# target:
#   /opt/zebra/zebra_deploy_info
#       yyyymmdd-hhss_deploy_summary.txt
#       history/
#          yyyy.mm.dd_hh.mm.ss_deploy_summary.txt
def scp_deploy_info( _full_inventory_file ):

    # removes "zebra_qa" directory if exists.
    if os.path.exists(zebra_deployment_info_dir):
        shutil.rmtree(zebra_deployment_info_dir, ignore_errors=True)

    # makes new directory. 
    os.makedirs(zebra_deployment_info_history_dir)

    # saves deploy summary file.
    save_file (zebra_qa_temp_dir, 'deploy_summary.txt')

    # saves deploy definition file.
    # save_file (os.path.dirname(full_deploy_config_file), os.path.basename(full_deploy_config_file))

    # save deploy_info file
    full_deploy_info_file = os.path.join(zebra_qa_temp_dir, "deploy_info.txt")
    os.system ("python deploy_info.py -c " + options.config + " > " + full_deploy_info_file )
    save_file (os.path.dirname(full_deploy_info_file), os.path.basename(full_deploy_info_file))

    # scp to targets.
    # ansible -i hosts_san_jose  boeing_p5_p6 
    #         -u zadmin 
    #         -m copy -a "src=~/checkouts/temp  dest=/opt/zebra"    
    cmd = " -i " + _full_inventory_file + " " + hostnames + \
          " -u zadmin --sudo " + \
          " -m copy -a \"src=" + zebra_deployment_info_dir + " dest=" + remote_zebra_dir + "\""
    os.system("ansible " + cmd)

# ----------------------------------------------------------------------------------------------------------
# http://docs.ansible.com/intro_adhoc.html  "Introduction to Ad-Hoc Commands"
#   example: $ ansible raleigh -m shell -a 'echo $TERM'
#
# Steps:
# - make dir /home/zadmin/zebra_support
# - make dir /opt/zebra/zebra_deployment_info/history/yyyymmdd_hhmmss_mws_boeing
# - copy files
#        from: /home/zadmin/mws_boeing/*.config and *.json
#        to:   /opt/zebra/zebra_deployment_info/history/yyyymmdd_hhmmss_mws_boeing/
#
def backup_remote_config_files( _full_inventory_file, _config_dir ):
    if is_empty_string(_config_dir):
        return
    remote_src_dir = os.path.join(remote_user_home_dir, _config_dir)
    remote_dest_dir = os.path.join(remote_zebra_history_dir, time_stamp + "_" + _config_dir)
    cmd_shell = " -i " + _full_inventory_file + " " + hostnames + " -u zadmin --sudo -m shell -a " + \
                " \" if [ ! -d " + remote_zebra_support_dir + " ]; then mkdir " + remote_zebra_support_dir + " ; fi; " + \
                "    mkdir " + remote_dest_dir + " && " + \
                "    cp " + remote_src_dir + "/*.config " + remote_dest_dir + " ; " + \
                "    cp " + remote_src_dir + "/*.json " + remote_dest_dir + "\""
    os.system("ansible " + cmd_shell)

#
# ----------------------------------------------------------------------------------------------------------
def main(argv):
    global options, args, cmd_deploy_tags, cmd_skip_tags, full_release_directory, config_dir

    # ------------------------------------------------------------------------------------------------------
    # parses command line arguments.
    parser = OptionParser(USAGE)
    parser.add_option('-c', "--config", default = "", help='to parse the variable in the file')
    parser.add_option('-d', "--reldir", help='Name of the release directory')
    parser.add_option('-y', "--yaml", help='Name of the YAML play book file.')
    parser.add_option('-i', "--inventory_file",  default = "hosts_san_jose", help='Name of the inventory file.')
    parser.add_option('-l', "--hostnames", help='List of hostnames to deploy.')
    parser.add_option('-t', "--tags", help='to deploy with deploy tags')
    parser.add_option('-a', "--app", \
                            action="store_true", \
                            default=False, \
                            help='to deploy application only, like --skip-tags "common", (excluding OS parts)')
    parser.add_option('-p', "--display", \
                            action="store_true", \
                            default=False, \
                            help='to display the ansible deploy command.')
    (options, args) = parser.parse_args()

    # --------------------------------------------------------------------------------------------------------
    # assigns deployment parameters using input arguments.

    # $ deploy.py -c deploy_config_file
    if not is_empty_string(options.config):
        try:
            get_properties_from_config_file(options.config)
        except:
            pass
    # $ deploy.py -d project_dir -y yml_name [-i inventory_hosts] [-l hostnames] [-a app] [-t deploy_tags][-h help]
    else:
        get_properties_from_command_line()

    # --------------------------------------------------------------------------------------------------------
    # starts validating deployment parameters.
    #
    cmd_deploy_tags = ""
    cmd_skip_tags = ""

    # limit to subset of hosts
    if not is_empty_string(hostnames):
        cmd_deploy_tags += " -l " + hostnames

    # --tags
    if not is_empty_string(deploy_tags):
        cmd_deploy_tags += " --tags " + deploy_tags 

    # --skip-tags
    if not is_empty_string(deploy_skip_tags): 
        cmd_skip_tags =  " --skip-tags " + deploy_skip_tags

    # boeing.yml
    if not deploy_playbook_file:
        print "Error: Playbook file is not defined"
        print USAGE
        sys.exit(1)

    # inventory directory.  
    full_release_directory = os.path.join( checkouts_dir, release_directory)
    if is_empty_string(inventory_dir):    
        full_inventory_dir = os.path.join( full_release_directory, "zebra-config-management/inventories")
    else:
        full_inventory_dir = os.path.join( checkouts_dir, inventory_dir )

    # inventory file.
    full_inventory_file = os.path.join( full_inventory_dir, inventory_file)
    if not os.path.exists(full_inventory_file):
        print "\nFile not found: ", full_inventory_file, "\n"
        sys.exit(1)

    # command line. 
    deploy_cmd = "bash deploy-playbook.sh  -d " + release_directory + \
                 " -vvv " + deploy_playbook_file +  \
                 " -i " + full_inventory_file + \
                 " -u zadmin " + \
                 cmd_deploy_tags + \
                 cmd_skip_tags

    # display only.
    if options.display == True:
        print deploy_cmd

    # S T A R T S    D E P L O Y I N G  . . .
    else:
        scp_deploy_info( full_inventory_file )
        backup_remote_config_files( full_inventory_file, config_dir )
        os.system(deploy_cmd)
        
# ------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1:])



