#!/usr/bin/python

# version 1.0
# date: 2014-08-27
#
# synopsys: 
#   get_tag_info.py -t <taglocfile> -i <info_output>
#
# Input formats:
#   Tag Locate file (-t <taglocfile>): 
#      Code,    id,     x,    y,   z, bat,   unix_time, unit, *, *  
#      T, 0020051C, 13.88,-4.89,2.74, 12,1356204375.758,1,*,S03-S06-S21
#

import json
import sys, getopt
import math
from optparse import OptionParser

#----------------------------
#Arguments

taglocfile = ""
infofile = ""

parser = OptionParser('get_tag_info.py -t <taglocfile> -i <info_file>')
parser.add_option('-t', "--taglocfile", help='Name of the Dart data file.', default = "tag_locate.csv")
parser.add_option('-i', "--taginfofile", help='Name of the tag info file.', default = "taginfo.json")
(options, args) = parser.parse_args()

taglocfile = options.taglocfile
taginfofile = options.taginfofile
#----------------------------
#Print arguments

print 'Tag locate file: ', taglocfile
print 'Tag info file: ', taginfofile

#----------------------------
#Configuration

#----------------------------
#Globals
tagLocCount = 0
Xmin = 1000.0
Xmax = -1000.0
Ymin = 1000.0
Ymax = -1000.0
Tmin = 9999999999.0
Tmax = -1000.0

#----------------------------
#line separator
line_sep_win = "\r\n" 
line_sep_linux = "\n" 

#----------------------------
#Process data files

def getIXYT_tag(locline):
    #T,0020051C,13.88,-4.89,2.74,12,1356204375.758,1,*,S03-S06-S21
    arrLocLine = locline.split(",")
    type = arrLocLine[0]
    id = arrLocLine[1]
    x_ft = float(arrLocLine[2])
    y_ft = float(arrLocLine[3])
    t = float( arrLocLine[6] )	
    return type,id,x_ft,y_ft,t
	
#-----------------------------------------------
# id dictionary
#  Used to store the previous location per tagId to be able to raw lines between consecutive blinks.

id_dict = {}
id_key = 0

#last locations for up to 256 tag_ids
maxTags = 256
arrTmin = [0.0] * maxTags
arrTmax = [0.0] * maxTags
arrXmin = [0.0] * maxTags
arrXmax = [0.0] * maxTags
arrYmin = [0.0] * maxTags
arrYmax = [0.0] * maxTags

def clearIdDictionary():
    global id_key
    global id_dict

    id_key = 0	
    id_dict.clear()	

def processMessageForStats(id, newX, newY, newT):
    global id_key
    global id_dict

    global arrTmin
    global arrTmax
    global arrXmin
    global arrXmax
    global arrYmin
    global arrYmax
    global Xmin
    global Xmax
    global Ymin
    global Ymax
    global Tmin
    global Tmax

    if newX < Xmin:        
        Xmin = newX     
    if newX > Xmax:        
        Xmax = newX 

    if newY < Ymin:        
        Ymin = newY     
    if newY > Ymax:        
        Ymax = newY    

    if newT < Tmin:        
        Tmin = newT     
    if newT > Tmax:        
        Tmax = newT 
	
    key = id_dict.get(id, 0)
    if key != 0:
        if key < maxTags:		
            if newX < arrXmin[key]:        
                arrXmin[key] = newX     
            if newX > arrXmax[key]:        
                arrXmax[key] = newX 

            if newY < arrYmin[key]:        
                arrYmin[key] = newY     
            if newY > arrYmax[key]:        
                arrYmax[key] = newY    

            if newT < arrTmin[key]:        
                arrTmin[key] = newT     
            if newT > arrTmax[key]:        
                arrTmax[key] = newT  
        else:
            print "Warning. More than " + str(maxTags) + " tags."                  
    else:
        id_key = id_key + 1
        id_dict[id] = id_key

        arrXmin[id_key] = newX     
        arrXmax[id_key] = newX 

        arrYmin[id_key] = newY     
        arrYmax[id_key] = newY    

        arrTmin[id_key] = newT     
        arrTmax[id_key] = newT 	 

    return 

# ------------------------------------------------
def genReport(fileTagInfo):
    
    fileTagInfo.write(" " + line_sep_win) 
    fileTagInfo.write('tagLocCount: ' + str(tagLocCount) + line_sep_win) 
    fileTagInfo.write(" " + line_sep_win) 
    fileTagInfo.write('Tmin: ' + str(Tmin) + line_sep_win)
    fileTagInfo.write('Tmax: ' + str(Tmax) + line_sep_win)
    fileTagInfo.write(" " + line_sep_win) 
    fileTagInfo.write('Xmin: ' + str(Xmin) + line_sep_win)
    fileTagInfo.write('Xmax: ' + str(Xmax) + line_sep_win)
    fileTagInfo.write(" " + line_sep_win) 
    fileTagInfo.write('Ymin: ' + str(Ymin) + line_sep_win)
    fileTagInfo.write('Ymax: ' + str(Ymax) + line_sep_win)
    fileTagInfo.write(" " + line_sep_win) 

    fileTagInfo.write("Statistics per tag_id:" + line_sep_win)

    for i in range(len(id_dict.keys())):  #figure this out
       tag_id = id_dict.keys()[i]  #figure this out
       k=i+1
       fileTagInfo.write('tag_id: ' + str(tag_id) + line_sep_win)  #tag_id is a string
       fileTagInfo.write('  ' + 'T  min: ' + str(arrTmin[k]) + '  max: ' + str(arrTmax[k])+ line_sep_win)
       fileTagInfo.write('  ' + 'X  min: ' + str(arrXmin[k]) + '  max: ' + str(arrXmax[k])+ line_sep_win)
       fileTagInfo.write('  ' + 'Y  min: ' + str(arrYmin[k]) + '  max: ' + str(arrYmax[k])+ line_sep_win)

# ------------------------------------------------
def main():

    #Globals
    global tagLocCount
    global line_sep_win

    fileTagInfo = open( taginfofile ,"w")

    clearIdDictionary()	
    strTagLocFile=open(taglocfile).read()
    arrTagLocFile = strTagLocFile.split( line_sep_linux )
       
    tagLocCount = len(arrTagLocFile)  

    for locline in arrTagLocFile:
        if locline[:1] != "!" and locline != "":          
            type, id, x, y, t = getIXYT_tag( locline )
            if type == 'T':
                processMessageForStats(id,x,y,t)

    genReport(fileTagInfo)				
					
    fileTagInfo.close()

# ------------------------------------------------
if __name__ == "__main__":
    main()
