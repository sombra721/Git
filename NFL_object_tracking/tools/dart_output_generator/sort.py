import csv
from optparse import OptionParser

parser = OptionParser("tracking_data.py -i <inputfile> -o <outputfile -m <mapfile>  -s <svgfile>")
parser.add_option('-i', "--inputfile", help='Name of the input file.')
parser.add_option('-o', "--outputfile", help='Name of the output file.')
(options, args) = parser.parse_args()

input_file = options.inputfile
output_file = options.outputfile

# list to store the data converted from csv file
csv_list = []

# convert csv to list and store the data in the list
def csv_to_list(csv_list, csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(row)
    return csv_list

csv_list = csv_to_list(csv_list, input_file)

# transfer the data to float datatype 
for i in range (len(csv_list)):
    print "id: " + csv_list[i][1] + " x: " + csv_list[i][2] + " y: " + csv_list[i][3]  + "\n"
    csv_list[i][6] = float(csv_list[i][6])

def getKey(item):
    return float(item[6])

csv_list.sort(key = getKey)
    
result = open(output_file, "wb")
writer = csv.writer(result)
for row in csv_list:
    writer.writerow(row)
    
result.close()
