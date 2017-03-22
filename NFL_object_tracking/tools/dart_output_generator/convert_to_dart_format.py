# version 1.1
#
# synopsys: 
#   convert_to_dart_format -i <input_text_dart_file> -o <output_csv_dart_file> 
#
# description: 
#   The program convert the EOL (end of line) characters from Windows format to Unix format.
#
# Input formats:
#   Entity Locate file line format: 
#      <Dart data>|<Dart data>|<Dart data>|<Dart data>|[\r\n]<Dart data>[\r\n] ... 
#
#   Baseline Entity Locate file line format: 
#      <Dart data>[\n]<Dart data>[\n] <Dart data>[\n] <Dart data>[\n] ...
#
# Log / Standard output
#   The result file contains a the Dart data file in with the EOL characters in Unix format.
#

import os
from optparse import OptionParser

parser = OptionParser('python convert_to_dart_format.py -i <input_Dart_file> -o <output_Dart_file>.')
parser.add_option('-i', "--input", help='Name of the text Dart data file.')
parser.add_option('-o', "--output", help='Name of the csv Dart file.')
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output
temp_file = "temp.csv"

def combine_all(vinput_file):
    infile = open(vinput_file)
    outfile = open(temp_file, 'w')
    for line in infile:
        line = line.strip()
        outfile.write(line)
    infile.close()
    outfile.close()

def convert_to_Unix_form(vtemp_file, voutput_file):
    infile = open(vtemp_file)
    outfile = open(voutput_file, 'w')
    for line in infile:
        line = line.replace("|", "\n")
        outfile.write(line)
    infile.close()
    outfile.close()
    os.remove(vtemp_file)
    
if __name__ == "__main__":   
    combine_all(input_file)
    convert_to_Unix_form(temp_file, output_file)

sort_command = "python sort.py -i " + output_file + " -o " + "sorted_" + output_file
os.system(sort_command)
