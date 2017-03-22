# version 1.0
#
# synopsys: 
#   python random_meter_xy.py -i <input_rnd_xy_file> -o <output_stats_file> -s <svg_visualization>
#
# description: 
#   This program measures statitistics of a random x,y input file.
#
# Input formats:
#    x,  y
#    13.88, -4.89
#
# Log / Standard output
#    sum x2, etc.

import csv
from optparse import OptionParser
import math

parser = OptionParser('python random_meter_xy.py -i <input_rnd_xy_file> -o <output_stats_file> -s <svg_visualization>.')
parser.add_option('-i', "--input", help='Name of the x,y data file.', default = "randomGaussian2d.txt")
parser.add_option('-o', "--output", help='Name of the output file.', default = "stats.txt")
parser.add_option('-s', "--svg", help='Name of the svg visualization file.', default = "svg.html")
(options, args) = parser.parse_args()

input_file = options.input
output_file = options.output
svg_file = options.svg

input_table = []

listR = []

#----------------------------
#Coordinates 
pix_per_ft = 120 

svgSize_ft = 8 
svgXMax_ft = svgSize_ft
svgYMax_ft = svgSize_ft

x0_ft = svgSize_ft/2.0
y0_ft = svgSize_ft/2.0
marker_size_ft = 0.04
axisLineWidth_ft = 0.06

xAxisMax_ft = 3.0
yAxisMax_ft = 3.0
	
#Screen dimensions
svgXMax = svgXMax_ft * pix_per_ft
svgYMax = svgYMax_ft * pix_per_ft

x0 = x0_ft * pix_per_ft
y0 = y0_ft * pix_per_ft
marker_size = marker_size_ft * pix_per_ft
axisLineWidth = axisLineWidth_ft * pix_per_ft

xAxisMax = xAxisMax_ft * pix_per_ft
yAxisMax = yAxisMax_ft * pix_per_ft

marker_size_hf = marker_size / 2.0

#----------------------------
markerColor = "255,0,0"  #red
axisColor = "100,100,255"    #blue
r90Color = "255,0,255"   #magenta
stddevColor = "0,255,0"  #green

#----------------------------
#line separator
line_sep_win = "\r\n" 
line_sep_linux = "\n" 

#----------------------------
def csv_to_table(csv_list, csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            csv_list.append(row)
    return csv_list

#----------------------------
def svgGenXY(input_table,svgfile):
    for i in range(len(input_table)):
        x = float(input_table[i][0])
        y = float(input_table[i][1])
        drawXY(x,y, svgfile)
    return

def drawStats(svgfile,r_ft,statsColor):
    lw = axisLineWidth/2.0
    r = r_ft * pix_per_ft
    outR = "<circle cx=\"" + str(x0) + "\" cy=\"" + str(y0) + "\" r=\"" + str(r) + "\" style=\" stroke:rgb(" + statsColor + "); stroke-width:" + str(lw) + "; fill:none;\"  />"
    svgfile.write(outR + line_sep_win)   
    return

def drawAxisLineX(svgfile,x_ft,lineWidth):
    x = x0 + x_ft * pix_per_ft
    yMin = y0 - (- yAxisMax)
    yMax = y0 + (- yAxisMax) 
    outX = "<line x1=\"" + str(x) + "\" y1=\"" + str(yMin) + "\" x2=\"" + str(x) + "\" y2=\"" + str(yMax) + "\" style=\" stroke:rgb(" + axisColor + "); stroke-width:" + str(lineWidth) + "\" />"
    svgfile.write(outX + line_sep_win)   
    return

def drawAxisLineY(svgfile,y_ft,lineWidth):
    y = y0 - y_ft * pix_per_ft
    xMin = x0 - (- xAxisMax)
    xMax = x0 + (- xAxisMax) 
    outY = "<line x1=\"" + str(xMin) + "\" y1=\"" + str(y) + "\" x2=\"" + str(xMax) + "\" y2=\"" + str(y) + "\" style=\" stroke:rgb(" + axisColor + "); stroke-width:" + str(lineWidth) + "\" />"
    svgfile.write(outY + line_sep_win)   
    return
	
def drawAxis(svgfile):
    lw = axisLineWidth/2.0
    drawAxisLineX(svgfile,0.0,axisLineWidth)
    drawAxisLineX(svgfile,-2.0,lw)
    drawAxisLineX(svgfile,-1.0,lw)
    drawAxisLineX(svgfile,1.0,lw)
    drawAxisLineX(svgfile,2.0,lw)

    drawAxisLineY(svgfile,0.0,axisLineWidth)
    drawAxisLineY(svgfile,-2.0,lw)
    drawAxisLineY(svgfile,-1.0,lw)
    drawAxisLineY(svgfile,1.0,lw)
    drawAxisLineY(svgfile,2.0,lw)
    return

def drawXY(x_ft,y_ft,svgfile):
    x = x0 + x_ft * pix_per_ft
    y = y0 - y_ft * pix_per_ft

	# top-left for a square marker
    x1 = x - marker_size_hf
    y1 = y - marker_size_hf
		
    #<rect x='54.64' y='439.36' width='0.8' height='0.8' style='fill:rgb(180,0,0);' />
    out = "<rect x=\"" + str(x1) + "\" y=\"" + str(y1) + "\" width=\""+str(marker_size)+"\" height=\""+str(marker_size)+"\" style=\" fill:rgb(" + markerColor + ");\" />"
    svgfile.write(out + line_sep_win)   
    return
	
def svgPlotHeader(fileSvg):
    #Globals
    global line_sep_win

    #SVG header  (inside HTML page)
    fileSvg.write("<!DOCTYPE html>" + line_sep_win)   
    fileSvg.write("<html>" + line_sep_win)   
    fileSvg.write("<body>" + line_sep_win)   
    fileSvg.write("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"" + str(svgXMax) + "\"" + " height=\"" + str(svgYMax) + "\" >" + line_sep_win)   

def svgPlotFooter(fileSvg):
    #Globals
    global line_sep_win

    #SVG footer  (inside HTML page)
    fileSvg.write("</svg>" + line_sep_win)   
    fileSvg.write("</body>" + line_sep_win)   
    fileSvg.write("</html>" + line_sep_win) 
	
#----------------------------
def calcStats(input_table, outputfile):
    dX_sum = 0.0
    dY_sum = 0.0
    dX2_sum = 0.0
    dY2_sum = 0.0

    dR_sum = 0.0
    dR2_sum = 0.0
	
    num = len(input_table)
    for i in range(num):
        x = float( input_table[i][0] )
        y = float( input_table[i][1] )
    
        r = math.sqrt( x*x + y*y )
        listR.append(r);
		
        dX_sum = dX_sum + x
        dY_sum = dY_sum + y
        dX2_sum = dX2_sum + x*x
        dY2_sum = dY2_sum + y*y
        dX_sum = dX_sum + x

        dR_sum = dR_sum + r
        dR2_sum = dR2_sum + r*r
 	
    xStdDev = math.sqrt( dX2_sum/num - (dX_sum/num)*(dX_sum/num) )
    yStdDev = math.sqrt( dY2_sum/num - (dY_sum/num)*(dY_sum/num) )
    rStdDev = math.sqrt( dR2_sum/num - (dR_sum/num)*(dR_sum/num) )
	
    listR.sort()
    rMin = listR[0]; 
    rMax = listR[num-1]; 

    percentile = 90.0/100.0	
    i90 = int( num*percentile )
    r90 = listR[i90]; 
	
    outputfile.write("Statistics:" + line_sep_win)
    line = "Count = " + str(num);
    outputfile.write(line + line_sep_win)

    line = "R min = " + str("%.3f" % rMin);
    outputfile.write(line + line_sep_win)
    line = "R max = " + str("%.3f" % rMax);
    outputfile.write(line + line_sep_win)

    line = "X Std Dev [ft] = " + str("%.3f" % xStdDev);
    outputfile.write(line + line_sep_win)
    line = "Y Std Dev [ft] = " + str("%.3f" % yStdDev);
    outputfile.write(line + line_sep_win)
    line = "R Std Dev [ft] = " + str("%.3f" % rStdDev);
    outputfile.write(line + line_sep_win)

    line = "r90 [ft] = " + str("%.3f" % r90);
    outputfile.write(line + line_sep_win)

    return r90, rStdDev
  
#----------------------------
if __name__ == "__main__":
    outfile = open(output_file, 'w')
    svgfile = open(svg_file, 'w')

    csv_to_table(input_table, input_file)
    r90_ft, rStdDev_ft = calcStats(input_table, outfile)

    svgPlotHeader(svgfile)
    drawAxis(svgfile)
    svgGenXY(input_table,svgfile)
    drawStats(svgfile,r90_ft,r90Color)
    drawStats(svgfile,rStdDev_ft,stddevColor)
    svgPlotFooter(svgfile)

    svgfile.close()
    outfile.close()

#----------------------------
