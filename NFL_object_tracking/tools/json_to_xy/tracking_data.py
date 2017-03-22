#-------------------------------------------------------------------------------
# Name:       tracking_data.sh
# Author:      
# Created:    Michael Tsai
# -----------------------------------------------------------------------------
# Description:
# ------------
# 	This program produce the tracking data from the excel, it also generates the SVG file with only entity location data.
#
# -----------------------------------------------------------------------------
#
import json
from optparse import OptionParser
import os

parser = OptionParser("tracking_data.py -i <inputfile> -o <outputfile -m <mapfile>  -s <svgfile>")
parser.add_option('-i', "--inputfile", help='Name of the input file.')
parser.add_option('-m', "--mapfile", help='Name of the map file.')
parser.add_option('-o', "--outputfile", help='Name of the output file.')
parser.add_option('-s', "--svgfile", help='Name of the SVG file.')
(options, args) = parser.parse_args()

input_file = options.inputfile
map_file = options.mapfile
output_file = options.outputfile
svg_file = options.svgfile
svg_graph_file = "~/checkouts/zebra-qa/scripts_lib/svg_graph_for_tag_ent_locates.py"

f_in = open(input_file, "r")
num_lines = sum(1 for line in open(input_file))
f_o =open(output_file,"w")
map_data = json.load(open(map_file))

for line in f_in:
    data1 = json.loads(line)
    for i in range(len(map_data["map"])):
        k = int(map_data["map"][i]["os"])
        f_o.write(str(map_data["map"][i]["plid"]) + "," + str(data1["data"][k]) + "," + str(data1["data"][k+1]) + "," + str(data1["data"][k+2]) + "," + str(data1["t"]) + "\n") 

f_o.close()
os.system("python " + svg_graph_file + " -e " + output_file + " -s " + svg_file)