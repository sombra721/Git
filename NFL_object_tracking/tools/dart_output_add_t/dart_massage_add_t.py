# version 1.1
#
# synopsys: 
#   python dart_message_add_t.py -i <input_Dart_file> -t <time_input_file> -o <output_Dart_file> -f <multiplier_value>
#
# description: 
#   This program add deviation values on x, y coordinates in the Dart input data. 
#   Two input files are needed for this program, one is the Dart data, the other one is the deviation values.
#   
#
# Input formats:
#   Input Dart file lin format: 
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2100, 13.88, -4.89,  2.74,        0,     1000.0,                 0
#
#   Time offset input file line format: 
#                 t
#               0.05
#
# Log / Standard output
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2100, 16.58, -4.89,  2.74,        0,    1000.05,                 0

import csv
from optparse import OptionParser

parser = OptionParser('python dart_message_add_t.py -i <input_Dart_file> -t <time_input_file> -o <output_Dart_file> -f <multiplier_value>.')
parser.add_option('-i', "--input", help='Name of the Dart data file.')
parser.add_option('-o', "--output", help='Name of the output file.')
parser.add_option('-t', "--time_offset", help='Name of the time offset file.')
parser.add_option("-f", "--times", type=float, default=1.0, help='Multiplier.')
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output
time_file = options.time_offset
multiplier = options.times

input_table = []
time_table = []

ti=5
toi=0

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

def add_error(vinput_table, vtime_table):
    for i in range(len(vinput_table)):
        temp_count = i % len(vtime_table)
        t_inp = float(vinput_table[i][ti])
        t_offset = float(vtime_table[temp_count][toi])
        temp_t = t_inp + float(multiplier)*t_offset
        vinput_table[i][ti] =temp_t
    return vinput_list
    
if __name__ == "__main__":
    csv_to_table(input_table, input_file)
    csv_to_table(time_table, time_file)    
    csv_writer(add_error(input_table, time_table), output_file)