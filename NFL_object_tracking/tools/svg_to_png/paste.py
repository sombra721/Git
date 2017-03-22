from PIL import Image
from optparse import OptionParser

parser = OptionParser('paste.py -b <Original_SVG_file>')
parser.add_option('-b', "--basefile", help='Name of the base PNG file.', default = "")
parser.add_option('-l', "--layerfile", help='Name of the layer PNG file.', default = "")
parser.add_option('-o', "--outputfile", help='Name of the output PNG file.', default = "")
parser.add_option('-x', "--xoffset", help='Deviation of x coordinate.', default = "")
parser.add_option('-y', "--yoffset", help='Deviation of y coordinate.', default = "")
(options, args) = parser.parse_args()

basefile = options.basefile
layerfile = options.layerfile 
outfile = options.outputfile 
x = options.xoffset
y = options.yoffset

img = Image.open(basefile)
layer = Image.open(layerfile) # this file is the transparent one
img.paste(layer, (int(x),int(y)), mask=layer)
img.save(outfile)
