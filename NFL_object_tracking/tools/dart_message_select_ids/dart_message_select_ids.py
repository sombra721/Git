# version 2.0
#
# synopsys: 
#   python dart_message_select_ids.py -i <input_Dart_file> -d <tag_id/s> -o <output_Dart_file>
#
# description: 
#   This program extracts the messages with a given tag id/s into the output file.
#   The rest of the tags id are extracted into the skipoutput file.
#
# examples: 
#   python dart_message_select_ids.py -i input.txt -t 2011 -o output.txt
#   OR
#   python dart_message_select_ids.py -i input.txt -t 2011,2012 -o output.txt -s skipoutput.txt
#
# Input formats:
#   Input Dart file lin format: 
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2011, 13.88, -4.89,  2.74,        0,          0,                 0
#                 T,   2012, 13.88, -4.89,  2.74,        0,          0,                 0
#

import csv
from optparse import OptionParser
import fileinput   #file file read, without memory load

parser = OptionParser('python dart_message_select_ids.py -i <input_Dart_file> -t <tag_id> -o <output_Dart_file> -b <beginning_time> -e <end_time>')
parser.add_option('-i', "--input", default="input.txt", help='Name of the Dart data file.')
parser.add_option('-b', "--beginning", default="", help='The beginning of the timestamp to be extracted.')
parser.add_option('-e', "--end", default="", help='The beginning of the timestamp to be extracted.')
parser.add_option('-o', "--output", default="output.txt", help='Name of the output file.')
parser.add_option('-s', "--skipoutput", default="skipoutput.txt", help='Name of the skipoutput file.')
parser.add_option("-t", "--tag_id", default="", help='Tag Id')
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output
skipoutput_file = options.skipoutput
tag_id = options.tag_id
beginning_time = options.beginning
end_time = options.end

input_table = []
skip_table = []

if tag_id:
    arrTagId = tag_id.split(',')	
else:
    arrTagId = ""

def csv_to_table(inputFile, outList,skipOutList):

    print("Opening file..." + '\n')
    #f = open(inputFile)     # RAM intensive

    print("Reading Lines..." + '\n')
    #lines = f.readlines()   # RAM intensive

    print("Processing Lines..." + '\n')

    ii = 0
    count100K = 0
    #for row in lines:       # RAM intensive
    for row in fileinput.input([inputFile]):  # fileinput avoids memory load
        ii = ii + 1
        arrRow = row.split(',')
        if len(arrRow) < 6:
            print("Warning. Field Count < 6: " + row + '\n')
        else:
            messType = arrRow[0]

            bInclude = True
            if beginning_time:  
                if float(arrRow[6]) < float(beginning_time):  # time
                    bInclude = False

            if end_time:  
                if float(arrRow[6]) > float(end_time):
                    bInclude = False

            if arrTagId != "":
                if not arrRow[1] in arrTagId:   # tag_id 
                    bInclude = False

            if bInclude == True:
                outList.append(row)          # RAM intensive before write
            else:
                skipOutList.append(row)      # RAM intensive before write
        if ii > 100000:
            ii = 0
            count100K = count100K + 1
            print(str(count100K) + " x 100K")  	           
    #f.close()    # RAM intensive
    return 

def csv_writer(data, path):
    f = open(path,'w')
    for row in data:  
        f.write(row)
    f.close()

if __name__ == "__main__":
    csv_to_table(input_file, input_table,skip_table) 

    print("Saving Results..." + '\n')
    csv_writer(input_table, output_file)
    csv_writer(skip_table, skipoutput_file)
