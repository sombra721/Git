#!/usr/bin/python

# version 1.2
#
# synopsys: 
#   validate_tag_entity_locates.py -t <taglocfile> -e <entitylocfile> 
#
# description: 
#   The use case is one or more 'entities' (like football players) with two tags attached. 
#   This program takes as input the 'tag locate' file (.csv) 
#   and the 'entity location' from the tracker output
#   and validates the data for time sequence and other consistency checks.
#   The standard output is use 'print' indicate any validation issues.
#
# Input formats:
#   Locate file line format: 
#      Code,    id,     x,    y,   z, bat,   unix_time, unit, *, *  
#      T, 0020051C, 13.88,-4.89,2.74, 12,1356204375.758,1,*,S03-S06-S21
#
#   Entity Locate file (from Tracker) line format: 
#      entity_id,   x,    y,   z,  unix_time  
#      400,12.000000,9.600000,0.400000,1.700000
#
# Log / Standard output
#  The program prints the names of input files and number of lines.
#  The program keeps track of time order and log an error is time order is violated.
#
#  Note: when runing a test, the Log/Standard-output should be directed (>) to a file to be preserved in the test results archive.
#

import json
import sys, getopt
import math
from optparse import OptionParser

taglocfile = ""
entitylocfile = ""

parser = OptionParser('validate_tag_ent_locates.py -t <taglocfile> -e <entitylocfile>')
parser.add_option('-t', "--taglocfile", help='Name of the Dart data file.', default =False)
parser.add_option('-e', "--entitylocfile", help='Name of the output file.', default =False)
(options, args) = parser.parse_args()

taglocfile = options.taglocfile
entitylocfile = options.entitylocfile
svgfile = options.svgfile

if(taglocfile == "" and entitylocfile == ""): 
    print "============================================================="
    print "Error. No input files. At least one file is required."
    print "============================================================="
    sys.exit()

def main():
    print 'Tag locate file: ', taglocfile
    print 'Entity location file: ', entitylocfile
   
    #line separator
    line_sep_win = "\r\n" 
    line_sep_linux = "\n" 

    #Dimensions
    field_dx_ft = 300  
    field_dy_ft = 160  

    #-----------------
    tBeginAbsolute_s = 0.0
    tBegin_s = 1000.0
    tMin_s = 0.0    
    t_s = 0.0
    tPrev_s = 0.0 
    

    if(taglocfile != ""):
        strTagLocFile=open(taglocfile).read()
        arrTagLocFile = strTagLocFile.split( line_sep_linux )
        
        tagLocCount = len(arrTagLocFile)  
        print 'tagLocCount: ',tagLocCount   
        
        for locline in arrTagLocFile:
            if locline[:1] != "!" and locline != "":          
                arrLocLine = locline.split(",")
    
                #T,0020051C,13.88,-4.89,2.74,12,1356204375.758,1,*,S03-S06-S21
                arrLocLine = locline.split(",")
                x_ft = float(arrLocLine[2])
                y_ft = float(arrLocLine[3])
    
                if tBeginAbsolute_s <= 0:
                    t = float( arrLocLine[6] )
                    tBeginAbsolute_s = t - tBegin_s
                    print 'tBeginAbsolute_s: ',tBeginAbsolute_s   
                    print 'tBegin_s: ',tBegin_s
                    tMin_s = tBegin_s    
                t_s = t - tBeginAbsolute_s
                if t_s < tPrev_s:
                    dt_s = abs(t_s - tPrev_s)
                    print 'Error. Time order violation. dt = ', dt_s, "    In taglocfile at t = ", t
                if t_s < tMin_s:
                    tMin_s = t_s
                    print 'Error. Time order violation.  New tMin_s = ', tMin_s, "    In taglocfile at t = ", t
                tPrev_s = t_s 
    
        
        tPrev_s = 0.0 
    
    if(entitylocfile != ""):
        strEntityLocFile=open(entitylocfile).read()
        arrEntityLocFile = strEntityLocFile.split( line_sep_linux )

        entityLocCount = len(arrEntityLocFile)  
        print 'entityLocCount: ',entityLocCount   #Log: number of lines info (helps to know that all is working fine)   
        for locline in arrEntityLocFile:
            if locline[:1] != "!" and locline != "":  
                #400,12.000000,9.600000,0.400000,1.700000
                arrLocLine = locline.split(",")
                x_ft = float(arrLocLine[1])
                y_ft = float(arrLocLine[2])
    
                t = float(arrLocLine[4])  
    
                t_s = t - tBeginAbsolute_s
                if t_s < tPrev_s:
                    dt_s = t_s - tPrev_s
                    print 'Error. Time order violation. dt = ', dt_s, "    In entitylocfile at t = ", t
                if t_s < tMin_s:
                    tMin_s = t_s
                    print 'Error. Time order violation.  New tMin_s = ', tMin_s, "    In entitylocfile at t = ", t
                tPrev_s = t_s 


if __name__ == "__main__":
    main()
  

