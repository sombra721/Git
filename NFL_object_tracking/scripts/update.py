# ------------------------------------------------------------------------------------------
# This script is used to update the local repos with tags define in a release control file,
# e.g. zebra-qa/sw_releases/boeing_1.0.0.1.txt
#
# If a local repos does not exist, then the script will clone it first then update it  
# using the specified release tag in the release control file.
#
# Usage:
#       update.py -d <working directory> -r <release control file name>
# Example:
# 	update.py -d boeing_release -r boeing_1.0.0.1.txt
# ------------------------------------------------------------------------------------------
import getopt
import os, sys, shutil
from os.path import expanduser

# uses library.
sys.path.append('../scripts_lib/')
from utils import *
from deployment_definitions import *


USAGE='Usage: update.py [-d <directory>] -r <release file>'

COMM_ANNOTATION='!'
ROOT_DIR = os.path.join( expanduser("~"), "checkouts")
RELEASE_INFO = "zebra_release_info"

qa_dir = os.path.join(ROOT_DIR, "zebra-qa")
sw_releases_dir = os.path.join(qa_dir, "sw_releases")
temp_dir = os.path.join(qa_dir, "temp")
cur_dir = os.getcwd()
project_dir = ""
link_prefix = "https://bitbucket.org/bobkuehne/"
clean = False

# ------------------------------------------------------------------
# Notes:
#   The "repos" variable here most likely contain the tag name at end, 
#   e.g "zebra-datapump#BOEING_RELEASE_1.0"
#
def clone(working_dir, repos):
    print "\n--Cloning " + repos + "..."
    # if not exists, make it.  
    if not os.path.exists(working_dir):
    	os.makedirs(working_dir)
    # go to the project directory, then clone the repos.
    os.chdir(working_dir)
    os.system("hg clone " + link_prefix + repos)

# ------------------------------------------------------------------
# hg pull and update
def update(repos_dir, tag):
    print "\n--Updating [" + tag + "] " + repos_dir + "..."
    # go to the repos directory, then update it using the give tag.
    os.chdir(repos_dir)
    os.system("hg pull")
    
    # -C:              update clean
    # -r <revision> :  update to the specific revision, either a tag 
    #      or the first 7-digit HEX num of a changeset, aka commit number
    # Ex: given  !BOEING_P1P2_RELEASE_20140806  changeset: 350:96d9a1c0505f
    #     run either:
    #      hg update -C -r BOEING_P1P2_RELEASE_20140806
    #      hg update -C -r 96d9a1c
    os.system("hg update -C -r " + tag)



# ------------------------------------------------------------------
def update_all(working_dir, repos_file):
    # use the release file to update all repositories
    inFile = open(repos_file, "r")
    seperator="#"
    for line in inFile:
        line = trim_comment(line)
        if line == "":
            continue
        if line.find(seperator) > -1 :
            # sample line: "zebra-config-management#RELEASE_1.0"
            info = line.split(seperator)
            repos = os.path.join(working_dir, info[0])

            # -- cloning...
            # if path not exists, then clone it.
            if not os.path.exists(repos):
                clone(working_dir, line.rstrip('\n'));

            # -- updating...
            # repos exists, so update it.
            else:
                update( repos, info[1].rstrip('\n'))
    inFile.close()
    os.chdir(cur_dir)

# ------------------------------------------------------------------
def trim_comment(line):
    # try to find "!" in the string
    try:
        # substring( 0, pos("!") )
        line=line[0:line.index(COMM_ANNOTATION)] 
    # "!" is not found.       
    except ValueError:
        pass
    # remove leading and trailling whitespaces.
    return line.strip()

# ------------------------------------------------------------------
def create_release_info(full_release_dir, full_release_file, version_string):
    
    full_release_info_dir = os.path.join(full_release_dir, RELEASE_INFO)

    # if not exists, make it.  
    if not os.path.exists(full_release_info_dir):
    	os.makedirs(full_release_info_dir)

    # version.txt
    file = open(os.path.join(full_release_info_dir, "version.txt"), "w")
    file.write(version_string)
    file.close()

    # boeing_1.0.0.8.txt
    shutil.copy2( full_release_file, full_release_info_dir )

    # deployment_info.txt
    os.system( "bash get_summary.sh -d " + os.path.basename(full_release_dir) )
    shutil.copy2( os.path.join(zebra_qa_temp_dir, 'deploy_summary.txt'), full_release_info_dir )
    
# ------------------------------------------------------------------
def main(argv):
    directory = ''
    release_file = ''
    release_base_name = ''
    project_dir = ''
    _release_file_name = ''

    try:
        opts, args = getopt.getopt(argv,"hcd:r:",["directory=","releaseFile="])
        if not opts:
            print 'No options supplied. ', USAGE
            sys.exit(0)
    except getopt.GetoptError:
        print USAGE
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print USAGE
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
            project_dir = os.path.join(ROOT_DIR, directory) 
        elif opt in ("-r", "--release"):
            _release_file_name = arg
            release_base_name = os.path.splitext(arg)[0]
            release_file = os.path.join(cur_dir, arg)
            if not os.path.exists(release_file):
                release_file = os.path.join(sw_releases_dir, arg)

    # default project_dir
    if project_dir == '':
        project_dir = os.path.join(ROOT_DIR, os.path.splitext(_release_file_name)[0])

    # release file does not exist.
    if not os.path.exists(release_file):
        print "Error: file does not exist!\n", release_file
        sys.exit()
    else:
        if not os.path.exists(project_dir):
            update_all(project_dir, release_file)   
            create_release_info(project_dir, release_file, release_base_name) 
        else:
            print "\nPlease remove the existing dir:", project_dir, "\n"
     
# ------------------------------------------------------------------
if __name__ == '__main__':
    main(sys.argv[1:])

