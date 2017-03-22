# version 1.2
#
# synopsys: 
#   python dart_message_mixer.py -i <input_Dart_folder> -d <tag_id/s> -o <output_Dart_folder> -m <output_file>
#
# description: 
#   This program mixes DART message files so that they are sorted by time.
#
# examples: 
#   python dart_message_mixer.py 
#   OR
#   python dart_message_mixer.py -i input -o output -m output_filename 
#   OR
#   python dart_message_mixer.py -i input -m output_filename 
#
# Input formats:
#   Input Dart file lin format: 
#       Data Header, Tag ID,     x,     y,     z,  battery,  timestamp,  virtual group ID
#                 T,   2011, 13.88, -4.89,  2.74,        0,          0,                 0
#                 T,   2012, 13.88, -4.89,  2.74,        0,          0,                 0

import os, csv
from optparse import OptionParser

parser = OptionParser('python dart_message_mixer.py -i <input_dir> -o <output_dir>')
parser.add_option('-i', "--input", default="input", help='Name of the input directory.')
parser.add_option('-o', "--output", default="", help='Name of the output directory.')
parser.add_option('-m', "--outputfile", default="result.csv", help='Name of the output file.')
(options, args) = parser.parse_args()

input_dir = options.input 
output_dir = options.output
output_file = options.outputfile

current_dir = os.getcwd()

# list to store the data converted from csv file
csv_list = []

# convert csv to list and store the data in the list
def csv_to_list(csv_list, csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(row)
    return csv_list
	
def csv_to_list_NotUsed(outList, inputFile):
    f = open(inputFile)
    lines = f.readlines()
    for row in lines:  
        outList.append(row)
    f.close()
    return 	

# load csv file(s) from the input folder
os.chdir("./" + input_dir)
for file in os.listdir("./"):
    if file.endswith(".csv"):       
        csv_to_list(csv_list, file)
    if file.endswith(".txt"):       
        csv_to_list(csv_list, file)		

# transfer the data to float datatype 
for i in range (len(csv_list)):
    try:
        csv_list[i][6] = float(csv_list[i][6]) # time
    except:
        print "Except. Line = " + str(i) + " | " + csv_list[i][6] + " | " + csv_list[i]	
		
def getKey(item):
    return float(item[6])

csv_list.sort(key = getKey)

os.chdir(current_dir)

if not output_dir == "":
    #if not os.path.exists("/" + output_dir):  #rga-1. This may work only in Linux, but not sure in Cgiwin.
    if not output_dir in os.listdir(current_dir):
        os.makedirs(output_dir)
    f_output = open("./" + output_dir + "/" + output_file, "wb")
else:
    f_output = open(output_file, "wb")
   
writer = csv.writer(f_output)
for row in csv_list:
    writer.writerow(row)
    
f_output.close()
