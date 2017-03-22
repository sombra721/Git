#!/usr/bin/python

# version 1.1
#
# synopsys: 
#   compare_ent_locates -e <entitylocfile> -b <entitylocfile_baseline> 
#
# description: 
#   The files are compared line by line, looking if the x,y and t are the same, 
#   within an accepted minimal error.
#
# Input formats:
#   Entity Locate file line format: 
#      entity_id,     x,    y,   z, unix_time  
#      2100,      13.88,-4.89,2.74, 1356204375.758
#
#   Baseline Entity Locate file line format: 
#      entity_id,     x,    y,   z, unix_time  
#      2100,      13.88,-4.89,2.74, 1356204375.758   (same as above) 
#
# Log / Standard output
#   The result file contains a summary of the comprare results.
#

import math, os
from optparse import OptionParser

parser = OptionParser('compare_ent_locates -e <entitylocfile> -b <entitylocfile_baseline.')
parser.add_option('-e', "--entitylocfile", help='Name of the entity log file.')
parser.add_option('-b', "--entitylocfile_baseline", help='Name of the reference of the entity log file.')
(options, args) = parser.parse_args()

entitylocfile = options.entitylocfile
entitylocfile_baseline = options.entitylocfile_baseline

output_dir = "test_output"
gaussianSumCount = 6

if not os.path.exists("./" + output_dir):
    os.makedirs(output_dir)
  
def main():
  result_path = str(os.curdir) + "/" + output_dir + "/entity_compare_result.txt"
  fileResult = open( result_path ,"w")

  fileResult.write( "Entity location file: " + str(entitylocfile) + "\n")
  fileResult.write( "Entity location file - baseline: " + str(entitylocfile_baseline) + "\n")

  #line separator
  line_sep_linux = "\n"

  strEntityLocFile = open(entitylocfile).read()
  arrEntityLocFile = strEntityLocFile.split( line_sep_linux )

  strEntityLocFile_baseline = open(entitylocfile_baseline).read()
  arrEntityLocFile_baseline = strEntityLocFile_baseline.split( line_sep_linux )

  #Log: number of lines info (helps to know that all is working fine)
  fileResult.write("\nNumber of lines" + "\n")

  entityLocCount = len(arrEntityLocFile)
  fileResult.write("entityLocCount: "+ str(entityLocCount) + "\n")

  entityLocCount_baseline = len(arrEntityLocFile_baseline)
  fileResult.write("entityLocCount_baseline: " + str(entityLocCount_baseline) + "\n")

  #Allowed Errors
  e_dist_ft = 0.1
  e_time_sec = 0.01

  fileResult.write("\nAllowed errors")
  fileResult.write("\ne_dist_ft: " + str(e_dist_ft))
  fileResult.write("\ne_time_sec: " + str(e_time_sec) + "\n\n")

  #Compare Entity Locations to baseline
  iLn = 1
  errorCount = 0
  
  count = 0

  for loc_ln,loc_base_ln in map(None,arrEntityLocFile,arrEntityLocFile_baseline):
    if count < min(len(arrEntityLocFile)-1, len(arrEntityLocFile_baseline)-1):
      arrLocLn = loc_ln.split(',')

      #print "arrLocLn: ", arrLocLn
      x_ft = float(arrLocLn[1])
      y_ft = float(arrLocLn[2])
      t_s = float(arrLocLn[3])
      #print "loc_ln :", loc_ln, "type: ", type(loc_ln)
      arrLocBaseLn = str(loc_base_ln).split(",")
      #print "arrLocBaseLn", arrLocBaseLn, "     len:", len(arrLocBaseLn), "\n"
      #print "loc_base_ln type: ", type(loc_base_ln)
      xb_ft = float(arrLocBaseLn[1])
      yb_ft = float(arrLocBaseLn[2])
      tb_s = float(arrLocBaseLn[3])

      dx_ft = float(x_ft) - float(xb_ft)
      dy_ft = float(y_ft) - float(yb_ft)
      dt_s = float(t_s) - float(tb_s)

      dist_ft = math.sqrt( dx_ft*dx_ft + dy_ft*dy_ft )
      time_sec = abs( dt_s )

      error = 0
      # Check for differences in location and time
      if( float(dist_ft) > float(e_dist_ft) ):
        fileResult.write("Error. line= " + str(iLn) + " dist_ft= " + str(dist_ft) + "\n")
        error = error + 1
      if( float(time_sec) > float(e_time_sec) ):
        fileResult.write("Error. line= " + str(iLn) + "time_sec= " + str(time_sec) + "\n")
        error = error + 1
      if( error > 0 ):
        errorCount = errorCount + 1

      iLn = iLn + 1
      count+=1

    else:
      break

  print ' '
  fileResult.write("\nerrorCount: " + str(errorCount))


if __name__ == "__main__":
  main()
