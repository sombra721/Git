#!/usr/bin/python

# version 1.8
# date: 2014-08-11
#
# synopsys: 
#   svg_graph_for_tag_ent_locates.py -t <taglocfile> -e <entitylocfile> -s <svgfile>
#
# Arguments options:
#   svg_graph_for_tag_ent_locates.py -t <taglocfile> -m <tagmodel_locfile> -e <entitylocfile> -r <entityreffile> -s <svgfile> -c <entityjsonfile> -L <tagL_id> -R <tagR_id> -E <ent_id>
#
# Note: most input argument are optional.
#
# Options to process selected tag ids
#   <tagL_id> <tagR_id> is used to process only these tags, and distiguish left and right with different colors.
#   <ent_id> is used to process only this entity id.  
#   OR 
#   <entityjsonfile> is used to provide many <tagL_id> <tagR_id> <ent_id> in sequence to generate many svg files.
#
# Example - test result visualization post-processing:
#   svg_graph_for_tag_ent_locates.py -t test_output/tag_location_tail_off.csv -e test_output/ent_location_tail_off.csv -c config/standalone_entity.json 
#
# Description: 
#   The use case is one or more 'entities' (like a football players) with two tags attached. 
#   This program takes as input the 'tag locate' file (.csv) -
#   and the 'entity location' from the tracker output
#   and generates an SVG (vector graphics) file.
#   This SVG file can be viewed in a browser, like IE10 (has good zoom) or Google Chrome.
#
# Input formats:
#   Tag Locate file (-t <taglocfile>): 
#      Code,    id,     x,    y,   z, bat,   unix_time, unit, *, *  
#      T, 0020051C, 13.88,-4.89,2.74, 12,1356204375.758,1,*,S03-S06-S21
#
#   Tag Model Locate file (-t <tagmodel_locfile>): 
#      id,     x,    y,   z, unix_time  
#      0020051C, 13.88,-4.89,2.74, 1356204375.758
#
#   Entity Locate file (-e <entitylocfile> from Tracker): 
#      entity_id,   x,    y,   z,  unix_time  
#      400,12.000000,9.600000,0.400000,1.700000
#
# Output formats:
#   SVG format such as:
#   <!DOCTYPE html>
#   <html>
#   <body>
#   <svg xmlns='http://www.w3.org/2000/svg' version='1.1'> 
#
#   This below is the football field, as a green rectangle and lines, in feet units. 
#   <rect x='0' y='0' width='1200' height='640' style='fill:rgb(255,255,255);stroke-width:2;stroke:rgb(0,255,0)' />
#   <line x1='120' y1='0' x2='120' y2='640' style='stroke:#00FF00;'/>
#   ...
#   <line x1='1080' y1='0' x2='1080' y2='640' style='stroke:#00FF00;'/>
#
#   These below are small rectangles representing tags and entity locations, 
#   where tag are black rgb(0,0,0) and the entity is dark red rgb(0,180,0) 
#   <rect x='-0.4' y='639.6' width='0.8' height='0.8' style='fill:rgb(180,0,0);' />
#   ...
#
#   </svg>
#   </body>
#   </html>
#
# Log / Standard output
#  The program prints tne names of input files and number of lines.
#  Log info is usefull to confirm that the program is processing the intended inputs and working fine. 
#
#  The program keeps track of time order and log an error is time order is violated.
#
#  Note: when runing a test, the Log/Standard-output should be directed (>) to a file to be preserved in the test results archive.
#

import json
import sys, getopt
import math
from optparse import OptionParser

#----------------------------
#Arguments

taglocfile = ""
entitylocfile = ""
entityreffile = ""
svgfile = "svg.html"
svgfilePlt = "plt.html"
entityjsonfile = ""
tagL_id = ""
tagR_id = ""
ent_id = ""

parser = OptionParser('svg_graph_for_tag_ent_locates.py -t <taglocfile> -m <tagmodel_locfile> -e <entitylocfile> -r <entityreffile> -s <svgfile> -c <entityjsonfile> -L <tagL_id> -R <tagR_id> -E <ent_id>')
parser.add_option('-t', "--taglocfile", help='Name of the Dart data file.', default = "")
parser.add_option('-m', "--tagmodellocfile", help='Name of the tag model data file.', default = "")
parser.add_option('-e', "--entitylocfile", help='Name of the Entity file.', default = "")
parser.add_option('-r', "--entityreffile", help='Name of the Reference Entity file.', default = "")
parser.add_option('--rs', help='Resolustion value', type="int", default = 5)
parser.add_option('-s', "--svgfile", help='Name of the svg graph file.', default = "svg.html")
parser.add_option('-c', "--entityjsonfile", help='Name of the entity configuration json file.', default = "")
parser.add_option('-L', "--tagL_id", help='Left tag id.  This is used to select a tag_id to graph.', default = "")
parser.add_option('-R', "--tagR_id", help='Right tag id.  This is used to select a tag_id to graph.', default = "")
parser.add_option('-E', "--ent_id", help='Entity id.  This is used to select an entity_id to graph.', default = "")
(options, args) = parser.parse_args()

taglocfile = options.taglocfile
tagmodellocfile = options.tagmodellocfile
entitylocfile = options.entitylocfile
entityreffile = options.entityreffile
svgfile = options.svgfile
entityjsonfile = options.entityjsonfile
tagL_id = options.tagL_id
tagR_id = options.tagR_id
ent_id = options.ent_id
resolution = options.rs

svgfilePlt = svgfile + "_plt.html" 

if(taglocfile == "" and tagmodellocfile == "" and entitylocfile == "" and entityreffile == ""): 
    print "============================================================="
    print "Error. No input files. At least one file is required."
    print "============================================================="
    sys.exit()

#----------------------------
#Print arguments

print 'Tag locate file: ', taglocfile
print 'Tag model locate file: ', tagmodellocfile
print 'Entity location file: ', entitylocfile
print 'Entity Reference location file: ', entityreffile
print 'SVG graph file: ', svgfile, '  Plot SVG file: ',  svgfilePlt   
print 'Entity configuration json file: ', entityjsonfile
print 'tag Id - Left: ', tagL_id
print 'tag Id - Right: ', tagR_id
print 'entity Id: ', ent_id

#----------------------------
#Dimensions

x0_ft = 20
y00_ft = 20 #top border
field_dx_ft = 300  
field_dy_ft = 160  
y0_ft = y00_ft + field_dy_ft 

yard_lines_dx_ft = 30
marker_size_ft = 0.15
field_line_width_ft = 0.15
text_dy_ft = -0.125
text_size_ft = 0.25
marker_line_width_ft = 0.05
marker_model_line_width_ft = 0.03
angle_line_size_ft = 0.5
angle_line_width_ft = 0.03

x_max_ft = x0_ft + field_dx_ft
y_max_ft = y00_ft + field_dy_ft

#Coordinates 
pix_per_ft = resolution  
	
#Screen dimensions
x0 = x0_ft * pix_per_ft
y0 = y0_ft * pix_per_ft
field_dx = field_dx_ft * pix_per_ft 
field_dy = field_dy_ft * pix_per_ft
yard_lines_dx = yard_lines_dx_ft * pix_per_ft
marker_size = marker_size_ft * pix_per_ft
field_line_width = field_line_width_ft * pix_per_ft    
text_dy = text_dy_ft * pix_per_ft
text_size = text_size_ft * pix_per_ft
marker_line_width = marker_line_width_ft * pix_per_ft
marker_model_line_width = marker_model_line_width_ft * pix_per_ft
angle_line_size = angle_line_size_ft * pix_per_ft
angle_line_width = marker_line_width_ft * pix_per_ft

x_max = x_max_ft * pix_per_ft
y_max = y_max_ft * pix_per_ft

marker_size_hf = marker_size / 2.0

#----------------------------
#Configuration
text_out_t = 1
text_out_data = 1

#----------------------------
#Plots

angInvalid = -1000.0
distInvalid = -1000.0
velInvalid = -1000.0	
accInvalid = -1000.0	

xplt0_ft = 20
plotAxis_lineWidth_ft = 0.15
pltTextSize_ft = 3.0
pltXgap_ft = 5.0
pltYgap_ft = 5.0

plotData_lineWidth_ft = 0.1

time_ft_per_sec = 10  
ang_ft_per_deg = 0.15
dist_ft_per_ft = 0.2
vel_ft_per_ftps = 2	
acc_ft_per_fpss = 1	

xplt0 = xplt0_ft * pix_per_ft
plotAxis_lineWidth = plotAxis_lineWidth_ft * pix_per_ft
pltTextSize = pltTextSize_ft * pix_per_ft
pltXgap = pltXgap_ft * pix_per_ft
pltYgap = pltYgap_ft * pix_per_ft

plotData_lineWidth = plotData_lineWidth_ft * pix_per_ft

tMin_s =  1000.0 #sec
tMax_s =  1020.0 #sec
t0_s =    999.5 #sec
tTicGapCount =  10 

angMin_deg = -180.0 #deg
angMax_deg =  180.0 #deg
ang0_deg =      0.0 #deg
angTicGapCount =  9

distMin_ft =   0.0 #ft
distMax_ft = 300.0 #ft
dist0_ft =     0.0 #ft
distTicGapCount =  10

velMin_ftps =  0.0 #ft/sec
velMax_ftps = 32.0 #ft/sec
vel0_ftps =    0.0 #ft/sec
velTicGapCount =  8

accMin_ftpss = -20.0 #ft/sec^2
accMax_ftpss = 20.0 #ft/sec^2
acc0_ftpss =    0.0 #ft/sec^2
accTicGapCount =  10

time_pix_per_sec = time_ft_per_sec * pix_per_ft
ang_pix_per_deg = ang_ft_per_deg * pix_per_ft
dist_pix_per_ft = dist_ft_per_ft * pix_per_ft
vel_pix_per_ftps = vel_ft_per_ftps * pix_per_ft
acc_pix_per_fpss = acc_ft_per_fpss * pix_per_ft


# In pixels
angDy1  = (ang0_deg - angMin_deg)     * ang_pix_per_deg 
angDy0  = (angMax_deg - ang0_deg)     * ang_pix_per_deg 
distDy1 = (dist0_ft - distMin_ft)     * dist_pix_per_ft
distDy0 = (distMax_ft - dist0_ft)     * dist_pix_per_ft
velDy1  = (vel0_ftps - velMin_ftps)   * vel_pix_per_ftps
velDy0  = (velMax_ftps - vel0_ftps)   * vel_pix_per_ftps
accDy1  = (acc0_ftpss - accMin_ftpss) * acc_pix_per_fpss
accDy0  = (accMax_ftpss - acc0_ftpss) * acc_pix_per_fpss

yplt0_ft = 60
yplt0 = yplt0_ft * pix_per_ft

y0Ang    = angDy0  + 3.5 * pltYgap
y0Dist   = y0Ang   + angDy1  + distDy0 + 3.5 * pltYgap
y0Vel    = y0Dist  + distDy1 + velDy0  + 3.5 * pltYgap
y0AccL   = y0Vel   + velDy1  + accDy0  + 3.5 * pltYgap
y0AccTL  = y0AccL  + accDy1  + accDy0  + 3.5 * pltYgap

# In pixels
tStart = 1000.0 #sec

tMin = xplt0 + (tMin_s - tStart)  * time_pix_per_sec 
tMax = xplt0 + (tMax_s - tStart) * time_pix_per_sec 
t0   = xplt0 + (t0_s   - tStart) * time_pix_per_sec 

pltXgapFactor = 0.5 

ang_t0 = t0 - pltXgapFactor * pltXgap
angMin = y0Ang - angMin_deg * ang_pix_per_deg 
angMax = y0Ang - angMax_deg * ang_pix_per_deg 
ang0   = y0Ang - ang0_deg   * ang_pix_per_deg 

dist_t0 = t0 - pltXgapFactor * pltXgap
distMin = y0Dist - distMin_ft * dist_pix_per_ft
distMax = y0Dist - distMax_ft * dist_pix_per_ft
dist0   = y0Dist - dist0_ft   * dist_pix_per_ft

vel_t0 = t0 - pltXgapFactor * pltXgap
velMin = y0Vel - velMin_ftps * vel_pix_per_ftps
velMax = y0Vel - velMax_ftps * vel_pix_per_ftps
vel0   = y0Vel - vel0_ftps   * vel_pix_per_ftps

acc_t0 = t0 - pltXgapFactor * pltXgap
accLMin = y0AccL - accMin_ftpss * acc_pix_per_fpss
accLMax = y0AccL - accMax_ftpss * acc_pix_per_fpss
accL0   = y0AccL - acc0_ftpss   * acc_pix_per_fpss

accTLMin = y0AccTL - accMin_ftpss * acc_pix_per_fpss
accTLMax = y0AccTL - accMax_ftpss * acc_pix_per_fpss
accTL0   = y0AccTL - acc0_ftpss   * acc_pix_per_fpss

#----------------------------
#line separator
line_sep_win = "\r\n" 
line_sep_linux = "\n" 

#----------------------------
#Process data files

def loadEntitiesFromFile(entity_json_file):
    #load entity config to be able to process the entities prest in a tag_location file in DART hub format
    # expect: entity_name = ['1_line', '2_line_mp', ...],  entity_id = [2001, 2002, ...], tagL_id = [2101, 2201, ...], tagR_id = [2102, 2202, ...]

    json_data=open(entity_json_file)
    entityData = json.load(json_data)
    entityCount = len( entityData["entities"] )
    
    ent_name = []
    ent_id = []
    tagL_id = []
    tagR_id = []
    
    for i in range (0, entityCount):
        ent_name.append( entityData["entities"][i]["name"] )
        ent_id.append( str( entityData["entities"][i]["id"] ))
        tagL_id.append( str( entityData["entities"][i]["tags"][0]["id"] ))
        tagR_id.append( str( entityData["entities"][i]["tags"][1]["id"] ))
    
    json_data.close()
    
    return ent_name, ent_id, tagL_id, tagR_id	

def getIXYT_tag(locline):
    #T,0020051C,13.88,-4.89,2.74,12,1356204375.758,1,*,S03-S06-S21
    arrLocLine = locline.split(",")
    type = arrLocLine[0]
    id = arrLocLine[1]
    x_ft = float(arrLocLine[2])
    y_ft = float(arrLocLine[3])
    t = float( arrLocLine[6] )	
    return type,id,x_ft,y_ft,t
	
def getIXYT_tagModel(locline):
    #0020051C,13.88,-4.89,2.74,1356204375.758
    arrLocLine = locline.split(",")
    id = arrLocLine[0]
    x_ft = float(arrLocLine[1])
    y_ft = float(arrLocLine[2])
    t = float( arrLocLine[4] )	
    return id,x_ft,y_ft,t

def getIXYT_entity(locline):
    global angInvalid
    #400,12.000000,9.600000,0.400000,1.700000       ,0.0,  0.0,0.0,0.0  //optional: angle, vel, accel, distance
    arrLocLine = locline.split(",")
    id = arrLocLine[0]
    x_ft = float(arrLocLine[1])
    y_ft = float(arrLocLine[2])
    t = float( arrLocLine[4] )	
    ang = angInvalid	
    vel = velInvalid	
    accL = accInvalid	
    accTL = accInvalid	
    dist = distInvalid	
    parCount = len(arrLocLine)
    if	parCount > 5:
        ang = float( arrLocLine[5] )	#angle in deg.
    if	parCount > 6:
        dist = float( arrLocLine[6] )	#distance in ft.
    if	parCount > 7:
        vel = float( arrLocLine[7] )	#velocity in ft/sec.
    if	parCount > 8:
        accL = float( arrLocLine[8] )	#acceleration Longitudinal in ft/sec^2.
    if	parCount > 9:
        accTL = float( arrLocLine[9] )	#acceleration Transversal (Left turn is possitive) in ft/sec^2.
    return id,x_ft,y_ft,t,ang,dist,vel,accL,accTL

# ------------------------------------------------
#Colors

tagLR_color = "0,0,0"  #black
tagLR_text_color = "127,127,127"  #gray
tagL_color = "70,0,0"  #black red
tagL_text_color = "177,127,127"  #gray red
tagR_color = "0,70,0"  #black green
tagR_text_color = "127,177,127"  #gray green

#                      0:red         1:green       2:blue        3:magenta     4:light_blue  5:dark_yellow  6:orange     7:violet     8:mid_blue  9:dark red 
arrEntityColor =     ["255,0,0",    "0,200,0",    "0,0,255",    "200,0,200",  "0,200,200",  "127,127,0",   "255,127,0", "100,0,200", "0,100,200","180,0,0"]
arrEntityTextColor = ["255,127,127","127,230,127","127,127,255","230,127,230","127,230,230","167,167,90",  "255,167,90","140,80,255","80,140,255","250,40,40"]

entity_ref_color = "255,100,100"  #clear red

angle_color = "255,0,0"  #red

plotAngColor = "255,0,0"  #red
plotVelColor = "0,255,0"  #red
plotAccColor = "0,0,255"  #red
plotDistColor = "0,0,0"  #black

plotTicColor = "200,200,200"  #light gray

def getColors_tag(id):
    global tagLR_color
    global tagLR_text_color
    global tagL_color
    global tagL_text_color
    global tagR_color
    global tagR_text_color

    global tagL_id
    global tagR_id

    markerColor = tagLR_color
    textColor = tagLR_text_color
    if( tagL_id == id ): 
        markerColor = tagL_color
        textColor = tagL_text_color
    if( tagR_id == id ): 
        markerColor = tagR_color
        textColor = tagR_text_color

    return markerColor,textColor

def getColors_entity(id):
    global arrEntityColor
    global arrEntityTextColor

    col_index = int(id) % 10
    markerColor = arrEntityColor[col_index]
    textColor = arrEntityTextColor[col_index]

    return markerColor,textColor

def getColors_entity_ref():
    global entity_ref_color
	
    markerColor = entity_ref_color
    textColor = entity_ref_color

    return markerColor,textColor

#-----------------------------------------------
# id dictionary
#  Used to store the previous location per tagId to be able to raw lines between consecutive blinks.

id_dict = {}
id_key = 0

#last locations for up to 32 tag_ids
maxTags = 32
arrXlast = [0.0] * maxTags
arrYlast = [0.0] * maxTags

arrTLast = [0.0] * maxTags
arrAngLast = [0.0] * maxTags
arrDistLast = [0.0] * maxTags
arrVelLast = [0.0] * maxTags
arrAccLLast = [0.0] * maxTags
arrAccTLLast = [0.0] * maxTags

def clearIdDictionary():
    global id_key
    global id_dict

    id_key = 0	
    id_dict.clear()	

def getLastXYandUpdate(id,newX,newY):
    global id_key
    global id_dict
    global arrXlast
    global arrYlast
	
    key = id_dict.get(id, 0)
    if key != 0:
        #print("key = " + str(key))
        if key < maxTags:		
            x = arrXlast[key]        
            y = arrYlast[key]       
            valid = True		
            arrXlast[key] = newX        
            arrYlast[key] = newY       
        else:
            x = 0.0        
            y = 0.0
            valid = False		
    else:
        id_key = id_key + 1
        id_dict[id] = id_key
        #print("tag added.  key = " + str(id_key)) 
        x = 0.0        
        y = 0.0
        valid = False		
        arrXlast[id_key] = newX        
        arrYlast[id_key] = newY       
    return x,y,valid  #x,y are previous x,y

def getLastDataAndUpdate(id,newT,newAng,newDist,newVel,newAccL,newAccTL):
    global id_key
    global id_dict
    global arrTLast
    global arrAngLast
    global arrDistLast
    global arrVelLast
    global arrAccLLast
    global arrAccTLLast
	
    key = id_dict.get(id, 0)
    if key != 0:
        #print("key = " + str(key))
        if key < maxTags:		
            tt =    arrTLast[key]        
            ang =   arrAngLast[key]        
            dist =  arrDistLast[key]       
            vel =   arrVelLast[key]       
            accL =  arrAccLLast[key]        
            accTL = arrAccTLLast[key]        
            valid = True		
            arrTLast[key] =     newT        
            arrAngLast[key] =   newAng        
            arrDistLast[key] =  newDist       
            arrVelLast[key] =   newVel       
            arrAccLLast[key] =  newAccL        
            arrAccTLLast[key] = newAccTL        
        else:
            tt =    0.0        
            ang =   0.0        
            dist =  0.0
            vel =   0.0
            accL =  0.0        
            accTL = 0.0
            valid = False		
    else:
        id_key = id_key + 1
        id_dict[id] = id_key
        #print("tag added.  key = " + str(id_key)) 
        tt =    0.0        
        ang =   0.0        
        dist =  0.0
        vel =   0.0
        accL =  0.0        
        accTL = 0.0
        valid = False		
        arrTLast[id_key] =     newT        
        arrAngLast[id_key] =   newAng        
        arrDistLast[id_key] =  newDist       
        arrVelLast[id_key] =   newVel       
        arrAccTLast[id_key] =  newAccL        
        arrAccTLLast[id_key] = newAccTL       
    return tt,ang,dist,vel,accL,accTL,valid  #tt,ang,dist,vel,accL,accTL are previous tt,ang,dist,vel,accL,accTL
	
# ------------------------------------------------
# svg plot

def plot_xy(id, x_ft, y_ft, t, ang, dist, vel, accL, accTL, markerColor,markerType, textColor, fileSvg):
    # Globals
    global x0
    global y0
    global pix_per_ft
    global marker_size
    global marker_size_hf
    global text_dy
    global text_size
    global marker_line_width
    global angle_line_size 
    global angle_line_width
    global angle_color

    global text_out_t
    global text_out_data
	
    global line_sep_win
	
    x = x0 + x_ft * pix_per_ft
    y = y0 - y_ft * pix_per_ft

	# top-left for a square marker
    x1 = x - marker_size_hf
    y1 = y - marker_size_hf

    if markerType=="r":
        #<rect x='54.64' y='439.36' width='0.8' height='0.8' style='fill:rgb(180,0,0);' />
        out = "<rect x=\"" + str(x1) + "\" y=\"" + str(y1) + "\" width=\""+str(marker_size)+"\" height=\""+str(marker_size)+"\" style=\"fill:rgb(" + markerColor + ");\" />"
    else: #markerType=="c"
        out = "<circle cx=\"" + str(x) + "\" cy=\"" + str(y) + "\" r=\""+str(marker_size)+"\" style=\"stroke:rgb(" + markerColor + "); stroke-width:" + str(marker_size/8.0) + "; fill:none;\" />"
    fileSvg.write(out + line_sep_win)   

    #<line x1="197.4" y1="120.0" x2="204.6" y2="120.0" style="stroke:rgb(0,66,0);stroke-width:0.4" />
    xp,yp,valid = getLastXYandUpdate(id,x,y)
    if valid == True:	
        out = "<line x1=\"" + str(xp) + "\" y1=\"" + str(yp) + "\" x2=\"" + str(x) + "\" y2=\"" + str(y) + "\" style=\" stroke:rgb(" + markerColor + "); stroke-width:" + str(marker_line_width) + "\" />"
        fileSvg.write(out + line_sep_win)   

    if ang > -360:
        aRad = math.radians(ang)
        xa = angle_line_size * math.cos(aRad) 
        ya = - angle_line_size * math.sin(aRad)  # '-' sign is due to y screen grows down, while real coords has y growing up.
        out = "<line x1=\"" + str(x) + "\" y1=\"" + str(y) + "\" x2=\"" + str(x+xa) + "\" y2=\"" + str(y+ya) + "\" style=\" stroke:rgb(" + angle_color + "); stroke-width:" + str(angle_line_width) + "\" />"
        fileSvg.write(out + line_sep_win)  

    if text_out_t == 1:          
        t_str = str(round(t, 2))[-5:]			
        #<text x="127.200000763" y="117.1" style="fill:rgb(0,0,0); stroke: none; font-size: 1.0px;">0.10</text>
        out = "<text x=\"" + str(x1) + "\" y=\"" + str(y1+text_dy) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + t_str + "</text>"
        fileSvg.write(out + line_sep_win) 

    if text_out_data == 1: #ang,vel,acc,dist	         
        text_data_y0 = y1 - 12*text_dy
        line_interY = 2 * text_dy	

        if ang > -360:
            ang_str = str(round(ang, 0))[-5:]			
            out = "<text x=\"" + str(x1) + "\" y=\"" + str(text_data_y0) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + ang_str + "</text>"
     	    fileSvg.write(out + line_sep_win) 

        if dist > -999:
            dist_str = str(round(dist, 1))[-5:]			
            out = "<text x=\"" + str(x1) + "\" y=\"" + str(text_data_y0-line_interY) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + dist_str + "</text>"
            fileSvg.write(out + line_sep_win) 

        if vel > -999:
            vel_str = str(round(vel, 1))[-5:]			
            out = "<text x=\"" + str(x1) + "\" y=\"" + str(text_data_y0-2*line_interY) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + vel_str + "</text>"
            fileSvg.write(out + line_sep_win) 

        if accL > -999:
            accL_str = str(round(accL, 1))[-5:]			
            out = "<text x=\"" + str(x1) + "\" y=\"" + str(text_data_y0-3*line_interY) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + accL_str + "</text>"
            fileSvg.write(out + line_sep_win) 

        if accTL > -999:
            accTL_str = str(round(accTL, 1))[-5:]			
            out = "<text x=\"" + str(x1) + "\" y=\"" + str(text_data_y0-4*line_interY) + "\" style=\" fill:rgb(" + textColor + "); stroke: none; font-size: " + str(text_size) + "px;\">" + accTL_str + "</text>"
            fileSvg.write(out + line_sep_win) 
			
    return valid  #prevous x,y is valid (i.e, this x,y is not the first x,y)

def plot_graph_xy(valid, id, t, ang, dist, vel, accL, accTL, markerColor, textColor, fileSvg):
    # Globals
    global plotData_lineWidth
    global line_sep_win

    tp,angp,distp,velp,accLp,accTLp,data_valid = getLastDataAndUpdate(id,t,ang,dist,vel,accL,accTL)

    #ttp,valp,valid = getLastXYandUpdate(id,tt,val)
    tt  = xplt0 + (t - tStart) * time_pix_per_sec
    ttp = xplt0 + (tp - tStart) * time_pix_per_sec 

    if ang > -360:
        if valid == True:
            val  = y0Ang - ang * ang_pix_per_deg
            valp = y0Ang - angp * ang_pix_per_deg
            out = "<line x1=\"" + str(ttp) + "\" y1=\"" + str(valp) + "\" x2=\"" + str(tt) + "\" y2=\"" + str(val) + "\" style=\" stroke:rgb(" + plotAngColor + "); stroke-width:" + str(plotData_lineWidth) + "\" />"
            fileSvg.write(out + line_sep_win)   

    if dist > -999:
        if valid == True:	
            val  = y0Dist - dist * dist_pix_per_ft
            valp = y0Dist - distp * dist_pix_per_ft
            out = "<line x1=\"" + str(ttp) + "\" y1=\"" + str(valp) + "\" x2=\"" + str(tt) + "\" y2=\"" + str(val) + "\" style=\" stroke:rgb(" + plotDistColor + "); stroke-width:" + str(plotData_lineWidth) + "\" />"
            fileSvg.write(out + line_sep_win)   

    if vel > -999:
        if valid == True:	
            val  = y0Vel - vel * vel_pix_per_ftps
            valp = y0Vel - velp * vel_pix_per_ftps
            out = "<line x1=\"" + str(ttp) + "\" y1=\"" + str(valp) + "\" x2=\"" + str(tt) + "\" y2=\"" + str(val) + "\" style=\" stroke:rgb(" + plotVelColor + "); stroke-width:" + str(plotData_lineWidth) + "\" />"
            fileSvg.write(out + line_sep_win)   

    if accL > -999:
        if valid == True:	
            val  = y0AccL - accL * acc_pix_per_fpss
            valp = y0AccL - accLp * acc_pix_per_fpss
            out = "<line x1=\"" + str(ttp) + "\" y1=\"" + str(valp) + "\" x2=\"" + str(tt) + "\" y2=\"" + str(val) + "\" style=\" stroke:rgb(" + plotAccColor + "); stroke-width:" + str(plotData_lineWidth) + "\" />"
            fileSvg.write(out + line_sep_win)   
    if accTL > -999:
        if valid == True:	
            val  = y0AccTL - accTL * acc_pix_per_fpss
            valp = y0AccTL - accTLp * acc_pix_per_fpss
            out = "<line x1=\"" + str(ttp) + "\" y1=\"" + str(valp) + "\" x2=\"" + str(tt) + "\" y2=\"" + str(val) + "\" style=\" stroke:rgb(" + plotAccColor + "); stroke-width:" + str(plotData_lineWidth) + "\" />"
            fileSvg.write(out + line_sep_win)   

def plotDrawAxis(fileSvg, pltX0,pltXmin,pltXmax, pltY0,pltYmin,pltYmax, pltColor, pltYlabel_str, y0_u,yMin_u,yMax_u, xTicGapCount,yTicGapCount):
    #x Tics
    for ktx in range(1,xTicGapCount):
        pltXtic = pltXmin + ktx*(pltXmax - pltXmin)/xTicGapCount 	
        xTic_str = "<line x1=\"" + str(pltXtic) + "\" y1=\"" + str(pltYmin) + "\" x2=\"" + str(pltXtic) + "\" y2=\"" + str(pltYmax) + "\" style=\" stroke:rgb(" + plotTicColor + "); stroke-width:" + str(plotAxis_lineWidth/2.0) + "\" />"
        fileSvg.write(xTic_str + line_sep_win) 

    #y Tics
    yTextOffset = 0.2 * pltYgap	
    for kty in range(1,yTicGapCount):
        pltYtic = pltYmin + kty*(pltYmax - pltYmin)/yTicGapCount 	
        yTic_str = "<line x1=\"" + str(pltXmin) + "\" y1=\"" + str(pltYtic) + "\" x2=\"" + str(pltXmax) + "\" y2=\"" + str(pltYtic) + "\" style=\" stroke:rgb(" + plotTicColor + "); stroke-width:" + str(plotAxis_lineWidth/2.0) + "\" />"
        fileSvg.write(yTic_str + line_sep_win) 

        yTic_u = yMin_u + kty*(yMax_u - yMin_u)/yTicGapCount 	
        yTicLabel_str = "<text x=\"" + str(pltX0) + "\" y=\"" + str(pltYtic + yTextOffset) + "\" style=\" fill:rgb(" + pltColor + "); stroke: none; font-size: " + str(pltTextSize) + "px;\">" + str( '%.0f'%yTic_u ) + "</text>"
        fileSvg.write(yTicLabel_str + line_sep_win)   
		
    #x Axis	
    x0Axis_str = "<line x1=\"" + str(pltXmin) + "\" y1=\"" + str(pltY0) + "\" x2=\"" + str(pltXmax) + "\" y2=\"" + str(pltY0) + "\" style=\" stroke:rgb(" + pltColor + "); stroke-width:" + str(plotAxis_lineWidth) + "\" />"
    fileSvg.write(x0Axis_str + line_sep_win)   

    #y Axis	
    y0Axis_str = "<line x1=\"" + str(pltXmin) + "\" y1=\"" + str(pltYmin) + "\" x2=\"" + str(pltXmin) + "\" y2=\"" + str(pltYmax) + "\" style=\" stroke:rgb(" + pltColor + "); stroke-width:" + str(plotAxis_lineWidth) + "\" />"
    fileSvg.write(y0Axis_str + line_sep_win) 
	
    yMaxAxis_str = "<line x1=\"" + str(pltXmin) + "\" y1=\"" + str(pltYmax) + "\" x2=\"" + str(pltXmax) + "\" y2=\"" + str(pltYmax) + "\" style=\" stroke:rgb(" + pltColor + "); stroke-width:" + str(plotAxis_lineWidth) + "\" />"
    fileSvg.write(yMaxAxis_str + line_sep_win)   

    yMinAxis_str = "<line x1=\"" + str(pltXmin) + "\" y1=\"" + str(pltYmin) + "\" x2=\"" + str(pltXmax) + "\" y2=\"" + str(pltYmin) + "\" style=\" stroke:rgb(" + pltColor + "); stroke-width:" + str(plotAxis_lineWidth) + "\" />"
    fileSvg.write(yMinAxis_str + line_sep_win)   

    #x Labels	
    xLabel_str    = "<text x=\"" + str(pltXmax - 2.0 * pltXgap) + "\" y=\"" + str(pltYmin + pltYgap) + "\" style=\" fill:rgb(" + pltColor + "); stroke: none; font-size: " + str(pltTextSize) + "px;\">" + "time [sec]" + "</text>"
    fileSvg.write(xLabel_str + line_sep_win)   

    #y Labels	
    yLabel_str    = "<text x=\"" + str(pltX0) + "\" y=\"" + str(pltYmax - pltYgap) + "\" style=\" fill:rgb(" + pltColor + "); stroke: none; font-size: " + str(pltTextSize) + "px;\">" + pltYlabel_str + "</text>"
    fileSvg.write(yLabel_str + line_sep_win)   

    yMinLabel_str = "<text x=\"" + str(pltX0) + "\" y=\"" + str(pltYmin + yTextOffset) + "\" style=\" fill:rgb(" + pltColor + "); stroke: none; font-size: " + str(pltTextSize) + "px;\">" + str( '%.0f'%yMin_u ) + "</text>"
    fileSvg.write(yMinLabel_str + line_sep_win)   

    yMaxLabel_str = "<text x=\"" + str(pltX0) + "\" y=\"" + str(pltYmax + yTextOffset) + "\" style=\" fill:rgb(" + pltColor + "); stroke: none; font-size: " + str(pltTextSize) + "px;\">" + str( '%.0f'%yMax_u ) + "</text>"
    fileSvg.write(yMaxLabel_str + line_sep_win)   

				
def plotDrawAllAxis(fileSvg):
    plotDrawAxis(fileSvg, ang_t0,tMin,tMax, ang0,angMin,angMax,     plotAngColor, "Angle [deg]",      ang0_deg,angMin_deg,angMax_deg,       tTicGapCount,angTicGapCount)
    plotDrawAxis(fileSvg, dist_t0,tMin,tMax, dist0,distMin,distMax, plotDistColor, "Distance [ft]",   dist0_ft,distMin_ft,distMax_ft,       tTicGapCount,distTicGapCount)
    plotDrawAxis(fileSvg, vel_t0,tMin,tMax, vel0,velMin,velMax,     plotVelColor, "Velocity [ft/sec]",     vel0_ftps,velMin_ftps,velMax_ftps,    tTicGapCount,velTicGapCount)
    plotDrawAxis(fileSvg, acc_t0,tMin,tMax, accL0,accLMin,accLMax,     plotAccColor, "Forward Acceleration [ft/sec^2]", acc0_ftpss,accMin_ftpss,accMax_ftpss, tTicGapCount,accTicGapCount)
    plotDrawAxis(fileSvg, acc_t0,tMin,tMax, accTL0,accTLMin,accTLMax,     plotAccColor, "Turning Acceleration [ft/sec^2]", acc0_ftpss,accMin_ftpss,accMax_ftpss, tTicGapCount,accTicGapCount)


def plot_field(fileSvg):
    #Globals
    global x0
    global y0
    global field_dx
    global field_dy
    global yard_lines_dx
    global field_line_width
    global line_sep_win

    #Colors
    field_color = "0,255,0"  #green
    field_colorN = "#00FF00"  #green

    #<rect x='0' y='0' width='1200' height='640' style='fill:rgb(255,255,255);stroke-width:2;stroke:rgb(0,255,0)' />
    fld_y1 = y0
    fld_y2 = y0 - field_dy
    fileSvg.write("<rect x=\""+str(x0)+"\" y=\""+str(fld_y2)+"\" width=\"" + str(field_dx) + "\" height=\"" + str(field_dy) + "\" style=\"fill:rgb(255,255,255);stroke-width:"+str(field_line_width)+";stroke:rgb(" + str(field_color) + ");\" />" + str(line_sep_win))   
    
    for k in range(1,10):
        x = x0 + k * yard_lines_dx
        #<line x1='120' y1='0' x2='120' y2='640' style='stroke:#00FF00;'/>
        out = "<line x1=\"" + str(x) + "\" y1=\""+str(fld_y1)+"\" x2=\"" + str(x) + "\" y2=\"" + str(fld_y2) + "\" style=\" stroke:" + str(field_colorN) + ";\"/>"
        #out = ...                                                          + "\" style=\" stroke-width:"+str(field_line_width)+";stroke:" + str(field_colorN) + 
        fileSvg.write(out + line_sep_win)   

def plot_svg_header(fileSvg,vxMax,vyMax):
    #Globals
    global line_sep_win

    #SVG header  (inside HTML page)
    fileSvg.write("<!DOCTYPE html>" + line_sep_win)   
    fileSvg.write("<html>" + line_sep_win)   
    fileSvg.write("<body>" + line_sep_win)   
    fileSvg.write("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" + str(vxMax) + "\"" + " height=\"" + str(vyMax) + "\" >" + line_sep_win)   

def plot_svg_footer(fileSvg):
    #Globals
    global line_sep_win

    #SVG footer  (inside HTML page)
    fileSvg.write("</svg>" + line_sep_win)   
    fileSvg.write("</body>" + line_sep_win)   
    fileSvg.write("</html>" + line_sep_win)   
		
# ------------------------------------------------
def genSvg(vSvgFile,vSvgFilePlt,tagL_id,tagR_id,ent_id):
    #Globals
    global angInvalid
    global velInvalid
    global accInvalid
    global distInvalid

    global line_sep_win

    fileSvgPlt = open( vSvgFilePlt ,"w")
    plot_svg_header(fileSvgPlt,x_max,y_max)

    fileSvg = open( vSvgFile ,"w")
    plot_svg_header(fileSvg,x_max,y_max)
    plot_field(fileSvg)
    if text_out_data == 1:
        plotDrawAllAxis(fileSvgPlt)

    if(taglocfile != ""):
        fileSvg.write(" " + line_sep_win) 
	
        clearIdDictionary()	
        strTagLocFile=open(taglocfile).read()
        arrTagLocFile = strTagLocFile.split( line_sep_linux )
        
        tagLocCount = len(arrTagLocFile)  
        print 'tagLocCount: ',tagLocCount   

        bSelectedTag = True;
        if(tagL_id == "" and tagR_id == "" ): 
            bSelectedTag = False;

        #Draw Tag Locations in taglocfile
        markerType = "r"
        for locline in arrTagLocFile:
            if locline[:1] != "!" and locline != "":          
                type, id, x_ft, y_ft, t = getIXYT_tag( locline )
                if type == 'T':				
                    if( (bSelectedTag == False) or (tagL_id == id) or (tagR_id == id) ):  
                        markerColor, textColor = getColors_tag(id)
                        plot_xy(id,x_ft,y_ft,t, angInvalid,distInvalid,velInvalid,accInvalid,accInvalid, markerColor,markerType,textColor,fileSvg)

    if(tagmodellocfile != ""):
        fileSvg.write(" " + line_sep_win) 
	
        clearIdDictionary()	
        strTagModelLocFile=open(tagmodellocfile).read()
        arrTagModelLocFile = strTagModelLocFile.split( line_sep_linux )
        
        tagModelLocCount = len(arrTagModelLocFile)  
        print 'tagModelLocCount: ',tagModelLocCount   

        bSelectedTag = True;
        if(tagL_id == "" and tagR_id == "" ): 
            bSelectedTag = False;

        #Draw Tag Locations in taglocfile
        markerType = "c"
        for locline in arrTagModelLocFile:
            if locline[:1] != "!" and locline != "":          
                id, x_ft, y_ft, t = getIXYT_tagModel( locline )
                if( (bSelectedTag == False) or (tagL_id == id) or (tagR_id == id) ):  
                    markerColor, textColor = getColors_tag(id)
                    plot_xy(id,x_ft,y_ft,t, angInvalid,distInvalid,velInvalid,accInvalid,accInvalid, markerColor,markerType,textColor,fileSvg)
						
    if(entitylocfile != ""):
        fileSvg.write(" " + line_sep_win) 
	
        clearIdDictionary()	
        strEntityLocFile=open(entitylocfile).read()
        arrEntityLocFile = strEntityLocFile.split( line_sep_linux )

        entityLocCount = len(arrEntityLocFile)  
        print 'entityLocCount: ',entityLocCount   #Log: number of lines info (helps to know that all is working fine)

        bSelectedEnt = True;
        if(ent_id == ""): 
            bSelectedEnt = False;

        #Draw Entity Locations in entitylocfile
        markerType = "r"
        for locline in arrEntityLocFile:
            if locline[:1] != "!" and locline != "":  
                id, x_ft, y_ft, t, ang, dist, vel, accL, accTL = getIXYT_entity( locline )
                if( (bSelectedEnt == False) or (ent_id == id) ):  
                    markerColor, textColor = getColors_entity(id)
                    prev_valid = plot_xy(id,x_ft,y_ft,t, ang,dist,vel,accL,accTL, markerColor,markerType,textColor,fileSvg)
                    if text_out_data == 1:
                        plot_graph_xy(prev_valid, id, t, ang,dist,vel,accL,accTL, markerColor, textColor, fileSvgPlt)
					
    if(entityreffile != ""):
        fileSvg.write(" " + line_sep_win) 
	
        clearIdDictionary()	
        strEntityRefFile=open(entityreffile).read()
        arrEntityRefFile = strEntityRefFile.split( line_sep_linux )

        entityRefCount = len(arrEntityRefFile)  
        print 'entityRefCount: ',entityRefCount 

        #Draw Entity Reference Locations in entityreffile
        markerType = "r"
        for locline in arrEntityRefFile:
            if locline[:1] != "!" and locline != "":  
                id, x_ft, y_ft, t, ang, dist, vel, accL, accTL = getIXYT_entity( locline )
                markerColor, textColor = getColors_entity_ref()
                plot_xy(id,x_ft,y_ft,t, ang,dist,vel,accL,accTL ,markerColor,markerType,textColor,fileSvg)
					
    plot_svg_footer(fileSvg)
    fileSvg.close()
    plot_svg_footer(fileSvgPlt)
    fileSvgPlt.close()

# ------------------------------------------------
def main():

    if (entityjsonfile != ""):
        arrEntName, arrEntId, arrTagIdL, arrTagIdR = loadEntitiesFromFile(entityjsonfile)
        entCount = len( arrEntName )
        for i in range (0, entCount):
            vSvgFile = "test_output/" + "svg_" + arrEntName[i] + ".html"		
            vSvgFilePlt = "test_output/" + "plt_" + arrEntName[i] + ".html"		
            vTagL_id = arrTagIdL[i]
            vTagR_id = arrTagIdR[i]
            vEnt_id = arrEntId[i]	
            genSvg(vSvgFile,vSvgFilePlt,vTagL_id,vTagR_id,vEnt_id)
        
    else: 
        genSvg(svgfile,svgfilePlt,tagL_id,tagR_id,ent_id)


if __name__ == "__main__":
    main()
