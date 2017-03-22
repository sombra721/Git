# version 1.2
#
# synopsys: 
#   python dart_message_add_xy.py -i <input_Dart_file> -e <error_input_file> -o <output_Dart_file> -f <multiplier value>
#
# example: 
#   python dart_message_add_xy.py -i input.txt -e add_xy.txt -o output.txt -f 1.0
#
# description: 
#   This program add deviation values on x, y coordinates in the Dart input data. 
#   Two input files are needed for this program, one is the Dart data, the other one is the deviation values.
#   
#
# Input formats:
#   Input Dart file lin format: 
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2100, 13.88, -4.89,  2.74,        0,          0,                 0
#
#   Error input file line format: 
#                 x,         y
#         -0.454884,  1.711674
#
# Log / Standard output
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2100, 16.58, -4.89,  2.74,        0,          0,                 0

import csv
from optparse import OptionParser

parser = OptionParser('python dart_message_add_xy.py -i <input_Dart_file> -e <error_input_file> -o <output_Dart_file> -f <multiplier value>.')
parser.add_option('-i', "--input", default="input.txt", help='Name of the Dart data file.')
parser.add_option('-o', "--output", default="output.txt", help='Name of the output file.')
parser.add_option('-e', "--error", default="add_xy.txt", help='Name of the error data file.')
parser.add_option("-f", "--times", type=float, default=1.0, help='Error Multiplier.')
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output
error_file = options.error
error_times = options.times

input_table = []
error_table = []

def csv_to_table(csv_list, csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(row)
    return csv_list

def csv_writer(data, path):
    with open(path, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:           
            writer.writerow(line)
			
def add_error(vinput_list, verror_list):
    xi = 2
    yi = 3	
    for i in range(len(vinput_list)):
        temp_count = i % len(verror_list)
        x_inp = float(vinput_list[i][xi])   # X input
        y_inp = float(vinput_list[i][yi])   # Y input
        x_err = float(verror_list[temp_count][0])  # X error
        y_err = float(verror_list[temp_count][1])  # Y error
        temp_x = x_inp + float(error_times)*x_err
        temp_y = y_inp + float(error_times)*y_err
        vinput_list[i][xi] =temp_x
        vinput_list[i][yi] =temp_y
    return vinput_list
    
if __name__ == "__main__":
    csv_to_table(input_table, input_file)
    csv_to_table(error_table, error_file)    
    csv_writer(add_error(input_table, error_table), output_file)
