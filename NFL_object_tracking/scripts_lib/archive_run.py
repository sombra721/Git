#-------------------------------------------------------------------------------
# Name:       archive_run
# Author:      MT
# Created:     06/19/2014
# -----------------------------------------------------------------------------
# Description:
# ------------
# This script is used after the test is run to archive the test run.
# The script copies all files in the "test_run" directory to
# a newly created archive folder.

# Parameters:
#   $test_run_dir
#   $archive_dir
#   $test_name
#   
# Example of a test_name:
#
#    The Test name: "01_alarm_status"
#    Located at:  ~/checkouts/zebra-qa/tests/paint_hangar/01_alarm_status
#    Run at:      ~/checkouts/zebra-qa-archive/test_run       
#    Archived at: ~/checkouts/zebra-qa-archive/archive/<date>_01_alarm_status 
# -----------------------------------------------------------------------------
#!/usr/bin/python
import os, sys
import archive

def archive_test_run(test_run_dir, archive_dir, test_name):
    print " "
    print "==================================================================="
    print "Archiving Test Run ..."
    print " "

    home=os.getenv("HOME")
    print "=========", home

    test_run_dir = test_run_dir
    archive_dir  = archive_dir

    # if location of archive_dir does not exists, make it.
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # create a new folder of archive with timestamp included
    f=archive.Archive(sys.argv[3], sys.argv[1], sys.argv[2])
    date_string=f.date_string()
    test_archive_dir = archive_dir + "/" + date_string + "-" + test_name
    print "Archive folder: ", test_archive_dir
    
    if not os.path.exists(test_archive_dir):
        os.makedirs(test_archive_dir)

    # NOTE: later to consider this in Python.
    # copy all files from test to archive folder
    f.cp_all()
    print "Archive completed"
 	   
# -------------------------------------------------------------------------------------------------------
def main():

    # print usage to help users to use
    if len(sys.argv) < 4:
        print "Usage: params should be test_run_dir, archive_dir, test_name"
        print "E.g: checkouts/zebra-qa-archive/test_run checkouts/zebra-qa-archive/archive 01_alarm_status "
        exit(1)

    # archive
    test_run_dir = sys.argv[1]
    archive_dir  = sys.argv[2]
    test_name    = sys.argv[3]
    archive_test_run (test_run_dir, archive_dir, test_name )

    print "End archive_test.py main()"

if __name__ == '__main__':
    main()
