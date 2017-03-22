
import math, os, sys
from optparse import OptionParser
from os.path import expanduser

# uses library.
sys.path.append('../scripts_lib/')
from utils import *
from deployment_definitions import *

USAGE = 'Usage: \n' + \
        '  deploy_info.py -c deploy_config_file\n'

# -c option: uses deploy properties from predefined deployment file.
def get_properties_from_config_file(deploy_config_file):
    global deploy_playbook_file, inventory_dir, inventory_file, hostnames, release_directory, \
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

# ------------------------------------------------------------------
def ping_hosts(inv_file, h_name):
    # ansible ping
    params = " -m ping -u zadmin -i " + inv_file
    if not is_empty_string(h_name):
        params += " -l " + h_name
    params += " all"
    os.system("ansible " + params)    

# ------------------------------------------------------------------
def main(argv):
    global options, args
    parser = OptionParser(USAGE)
    parser.add_option('-c', "--config", default = "", help='to parse the variable in the file')
    (options, args) = parser.parse_args()

    # -c option.
    if not is_empty_string(options.config):
        get_properties_from_config_file(options.config)
        #
        full_release_directory = os.path.join( checkouts_dir, release_directory )
        full_release_file = os.path.join( full_release_directory, "zebra_release_info/" + release_directory + ".txt")
        if os.path.exists(full_release_file):
            print_line ("Release file:" + full_release_file )
            with open(full_release_file, 'r') as f:
                print f.read()
                f.close()
         
        # prints contents parsed from deployment file.
        print_line ("Deployment file:" + full_deploy_config_file) 
        print_properties(deploy_dict)  
    
        # prints inventory file.
        if is_empty_string(inventory_dir):            
            full_inventory_dir = os.path.join( full_release_directory, "zebra-config-management/inventories/")
        else:
            full_inventory_dir = os.path.join( checkouts_dir, inventory_dir.strip('"') )
        # 
        full_inventory_file = os.path.join( full_inventory_dir, inventory_file)
        if not os.path.exists(full_inventory_file):
            print "\nFile not found: ", full_inventory_file, "\n"
            sys.exit(1)

        print_line ("Inventory file: " + full_inventory_file)
        with open(full_inventory_file, 'r') as f:
            print f.read()
            f.close()

        # ansible ping
        print_line ("Pinging targets. Please wait ...")
        ping_hosts(full_inventory_file, hostnames)

        # display ansible deploy command:
        print_line ("Deployment ansible command line:")
        os.system("python deploy.py -p -c " + options.config)
        print_line (" ")
        

# ------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1:])

