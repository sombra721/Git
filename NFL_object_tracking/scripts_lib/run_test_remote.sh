#! bin/bash

# ------------
# Description:
# ------------
# This script copies other scripts to "test_run" directory, then executes other
# script to run the test, copy test logs, compare logs against references, then
# archive the results.
#
# ~/checkouts/zebra-qa/tests/paint_hangar/01_alarm_status

# -------
# Syntax:
# -------
#  bash run_test.sh -d target_script_dir -t <TIMEOUT> -m [username@]target_machine 
#
# Example:
#  $ bash run_test_remote.sh -t 20 -s /opt/zebra/zebra -m 192.168.5.119 
#

USAGE="Usage: bash run_test_alarm.sh -t TIMEOUT -s /opt/zebra/zebra-boeing -m machine [-h help]"$'\n'

# -----------------------------------------------------------------------------------------
#create a run_test_alarm_new.sh
#that does only this funciton with thise argumants.

# run the test.

#test_run_remote $host_script_dir $target_machine $TIMEOUT,
test_run_remote()
{
   target_machine=$1 
   target_script_dir=$2
   TIMEOUT=$3
   
   echo "Start Boeing simulator on " $target_machine
   echo "-- The simulator is running for " $TIMEOUT "seconds..."
   ssh -Y -t -t $target_machine <<EOF
   cd $target_script_dir

   bash start.sh &
   sleep $TIMEOUT
   bash stop_test.sh &
   sleep 5

   exit
EOF
}

# -----------------------------------------------------------------------------------------
# -- main --

while getopts hs:t:m: OPT; do
	case "$OPT"	 in
		h)
			echo 
			echo $USAGE
        	echo 
			exit 0
			;;
		s)
			target_script_dir=$OPTARG
			;;	
		t)
			TIMEOUT=$OPTARG
			;;	
		m)
			target_machine=$OPTARG
			;;				
		\?)
			echo 
			echo $USAGE
 			echo
			exit 1
			;;
	esac
done


test_run_remote $target_machine $target_script_dir $TIMEOUT



