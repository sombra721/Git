import os, sys

#PROP_SIZE=6
#properties=["" for i in range(PROP_SIZE)]

# controller directories.
checkouts_dir = os.path.join( os.path.expanduser("~"), "checkouts" )
zebra_qa_dir = os.path.join(checkouts_dir, "zebra-qa")
zebra_qa_deployments_dir = os.path.join( zebra_qa_dir, "deployments" )
zebra_qa_temp_dir = os.path.join(zebra_qa_dir, "temp")
zebra_deployment_info_dir = os.path.join(zebra_qa_temp_dir, "zebra_deployment_info")
zebra_deployment_info_history_dir = os.path.join(zebra_deployment_info_dir, "history")

# target directories.
config_dir = ""
remote_user_home_dir = "/home/zadmin"
remote_zebra_support_dir = os.path.join(remote_user_home_dir, "zebra_support")
remote_zebra_dir = "/opt/zebra"
remote_zebra_history_dir = os.path.join(remote_zebra_dir, "zebra_deployment_info/history")
 
# -----------------------------------------------------------------
def parse_properties_from_config_file(full_deploy_config_file):
    
    # file not found.
    if not os.path.exists(full_deploy_config_file):
        print "\nFile not found: ", full_deploy_config_file, "\n"
        sys.exit(1)
   
    # uses dictionary to hold the key/value pairs
    dict_deploy = dict()

    # parses config file onto "deploy" dictionary above.
    file = open(full_deploy_config_file, 'r')    
    while True:
        string = file.readline()
        # removes leading and trailling he whitespaces.
        line = string.strip()
        # skips blank lines.
        if not line: 
            break
        # skips comment lines.
        pos = line.find("!")
        #not comment line and not blanks line
        if (pos != 0) and line != "":     
            if pos > -1:  #-1 or 0
                command = line[0:pos+1]
            else:
                command = line

            # adds name/value pairs to the dictionary.
            item = command.split("=")
            dict_deploy[ item[0].strip() ] = item[1].strip()

    # assigns the deploy properties.
    file.close()
    return dict_deploy

# -----------------------------------------------------------------
def print_properties(properties):
    print '   release_directory =', properties[ 'release_directory' ] 
    print 'deploy_playbook_file =', properties[ 'deploy_playbook_file' ] 
    print '     inventory_dir   =', properties[ 'inventory_dir' ] 
    print '     inventory_file  =', properties[ 'inventory_file' ] 
    print '          hostnames  =', properties[ 'hostnames' ] 
    print '        deploy_tags  =', properties[ 'deploy_tags' ] 
    print '   deploy_skip_tags  =', properties[ 'deploy_skip_tags' ], '\n'

# -----------------------------------------------------------------
def print_line(line):
    print '------------------------------------------------------------------'
    print line, '\n'


