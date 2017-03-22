#!/usr/bin/python

# version 1.0
#
# synopsys: 
#   svg_to_png.py -i <input_folder> -o <output_folder>
#
# description: 
#   The use of this program is to convert the .html in the input directory into formatted SVG files, then convert them into PNG files and store in the 
#   output directory.
#   Two python programs are used in this program
#      1: svg_format.py
#         Convert the input SVG files into formatted SVG form to make them acceptable by cairosvg.py. 
#      2: cairosvg.py
#         Convert the format files into PNG files.
#
# Input SVG formats (html):
#   SVG format such as:
#   <!DOCTYPE html>
#   <html>
#   <body>
#   <svg xmlns='http://www.w3.org/2000/svg' version='1.1' width="20480" height="11520" > 
#   ...
#
#   </svg>
#   </body>
#   </html>
#
# Output SVG formats (.svg):
#   SVG format such as:
#   <?xml version="1.0" standalone="no"?>
#   <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
#   <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="20480" height="11520" >
#   ...
#
#   </svg>
#   </body>
#   </html>
#

import os

scripts_lib = "~/checkouts/zebra-qa/scripts_lib"
input_dir = "test_output"
output_dir = "svg"
png_dir = "png"
crop_dir = "crop"
paste_dir = "out"

folder_list = [input_dir, output_dir, png_dir, crop_dir, paste_dir]

for i in folder_list:    
    for f in os.listdir(i):
        print i
        os.remove(i + "/" + f)

svg_generate_command = "python " + scripts_lib + "/svg_graph_for_tag_ent_locates.py -t input/tag_location_tail_off.csv -e input/ent_location_tail_off.csv -c input/standalone_entity.json --rs 64"

os.system(svg_generate_command)

current_dir = os.getcwd()
line_sep_win = "\r\n" 

os.chdir("./" + input_dir)
for file in os.listdir("./"):
    if file.endswith(".html"): 
        formatted_SVG_file = current_dir + "/" + output_dir + "/"+ file[:-4] + "svg"    
	with open(file, 'r') as fin:
	    ori_data = fin.read().splitlines(True)
	with open(formatted_SVG_file, 'w') as fout:
	    fout.writelines(ori_data)

	for i in range(3):
	    with open(formatted_SVG_file, 'r') as fin:
		data = fin.read().splitlines(True)
	    with open(formatted_SVG_file, 'w') as fout:
		fout.writelines(data[1:])

	# read the current contents of the file 
	f = open(formatted_SVG_file, "r") 
	text = f.read() 
	f.close() 

	# open the file again for writing 
	f = open(formatted_SVG_file, 'w') 
	f.write('<?xml version=\"1.0\" standalone=\"no\"?>' + line_sep_win) 
	f.write('<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"' + ' \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">' + line_sep_win)  
	f.write(text) 
	f.close() 

	with open(formatted_SVG_file, 'r') as fin:
	    lines = fin.readlines()
	with open(formatted_SVG_file, 'w') as fout:
	    fout.writelines(lines[:-2])
print "html files are convertted into SVG files."

os.chdir(current_dir + "/" + output_dir)
for file in os.listdir("./"):
    if file.endswith(".svg"): 
        png_file = current_dir + "/" + png_dir + "/" + file[:-3] + "png"      
        PNG_command = "python " + current_dir + "/" + "cairosvg.py " + file + " -f png -o " + png_file
        print "Converting " + file[:-3] + "svg to PNG form"
        os.system(PNG_command)

