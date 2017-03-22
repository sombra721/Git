# version 1.1
#    Michael Tsai    
#
# synopsys: 
#    python compose.py -j <input_json_file>
#
# description: 
#    This program crops images listed in the json file, the size to be cropped is base on the arrays in the json file.
#    After cropping the images, it pastes the cropped images into another image.
#    The configurations and default values are stored in the json file.  
#   
#

import json, os, shutil 
from optparse import OptionParser
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

parser = OptionParser("compose.py -j <jsonfile>")
parser.add_option('-j', "--jasonfile", help='Name of the input json file.')
(options, args) = parser.parse_args()

jason_file = options.jasonfile
jason_data = json.load(open(jason_file))
png_dir = "png/"
crop_dir = "crop/"
base_dir = "base/"
out_dir = "out/"
num_image = len(jason_data["crop"])
base_file = jason_data["paste_base"]
output_file = jason_data["paste_output"]
font = ImageFont.truetype(jason_data["font"],40)

# margin on the top
head_margin = jason_data["paste_top_margin"]

# blank size between the line and the text
bet_line_text = jason_data["paste_margin_line_text"]

# blank size between the text and the image
bet_text_image = jason_data["paste_margin_text_image"]

# blank size between the image and the line of the next part
bet_image_line = jason_data["paste_y"]


def crop_image():
    for i in range (0, num_image):
        crop_command = "convert " + png_dir + jason_data["crop"][i]["src"] + " -crop " + jason_data["crop"][i]["dx"] + "x" + jason_data["crop"][i]["dy"] + "+" +jason_data["crop"][i]["x"] + "+" + jason_data["crop"][i]["y"] + " +repage " + crop_dir + jason_data["crop"][i]["out"]
        print crop_command
        os.system(crop_command)


def draw_line_text(input_image, output_image, x_off, y_off, i):
    im = Image.open(input_image) 
    
    x_length = im.size[0]

    draw = ImageDraw.Draw(im)    
    draw.line((0, y_off, x_length, y_off), fill=0, width=3)
    y_off+=bet_line_text

    draw.text((int(x_off), int(y_off)), jason_data["paste"][i]["text"],(0,0,0),font=font)
    im.save(output_image)
    y_off+=bet_text_image

    return y_off
    
def paste_figure():
    x_paste_offset = int(jason_data["paste_x"])
    y_paste_offset = head_margin

    shutil.copy(base_dir + base_file, out_dir + output_file)

    for i in range (0, num_image):
        y_paste_offset = draw_line_text(out_dir + output_file, out_dir + output_file, x_paste_offset, y_paste_offset, i)
	paste_command = "python paste.py -b " + out_dir + output_file + " -l " + crop_dir + jason_data["crop"][i]["out"] + " -o " + out_dir + output_file + " -x " + str(x_paste_offset) + " -y " + str(y_paste_offset)
        os.system(paste_command)
        y_paste_offset+=int(jason_data["crop"][i]["dy"])+bet_image_line 

if __name__ == "__main__":
#    crop_image()
    paste_figure()

