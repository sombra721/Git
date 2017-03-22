# version 1.2
#
# synopsys: 
#   fix_file_dos_unix_format -i <input_text_dart_file> -o <output_csv_dart_file> 
#
# description: 
#   The program convert the EOL (end of line) characters from Windows format to Unix format.
#
# Input formats:
#   Entity Locate file line format: 
#      <Dart data>[\r\n]<Dart data>[\r\n] ... 
#   OR
#      <Dart data>[\r]<Dart data>[\n] ...  // messed up file

import os
from optparse import OptionParser

parser = OptionParser('python convert_to_dart_format.py -i <input_Dart_file> -o <output_Dart_file>.')
parser.add_option('-i', "--input", default="input.txt", help='Name of the text Dart data file.')
parser.add_option('-o', "--output", default="output.txt", help='Name of the csv Dart file.')
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output

def convert_to_Unix_form(in_file_name, out_file_name):
    infile = open(in_file_name)
    outfile = open(out_file_name, 'w')
    for line in infile:
        line = line.replace("\r\n", "\n")
        line = line.replace("\r", "\n")
        outfile.write(line)
    infile.close()
    outfile.close()

if __name__ == "__main__":   
    convert_to_Unix_form(input_file, output_file)

