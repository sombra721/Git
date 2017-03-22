#! bin/bash

# ------------
# Description:
# ------------
# 
# This scipt has two functions:
#   1.  The function crop_png crops a part of the PNG file.
#   2.  The function past_png pasts the PNG file (layer) into another PNG file (base).
# -------
# Syntax:
# -------
#   bash sample_script.sh
#

test_init()
{
   # png output
   png_dir=png

   # cropped output
   crop_dir=crop

   # base picture
   base_dir=base

   # pasted picture
   out_dir=out
   
   # size to be cropped
   width=2000
   length=500
   
   # size of the blank area
   blank_size=200

   # arrays for input file names, output file names, coordinates and offsets
   input_png=("svg_01_line.png" "svg_08_lineRnd05.png" "svg_02_lineMP.png" "svg_09_lineMPlarge.png" "svg_02_lineMP.png" "svg_03_diagonal.png" "svg_04_acceleration.png" "svg_05_circle.png" "svg_06_polynomial.png" "svg_07_actual.png" "svg_07_actual.png" "svg_10_lineMPoffset.png" "svg_10_lineMPoffset.png")
   output_png=("01_line.png" "08_lineRnd05.png" "02_lineMP_pop.png" "09_lineMPlarge.png" "02_lineMP_miss.png" "03_diagonal.png" "04_acceleration.png" "05_circle.png" "06_polynomial.png" "07_actual_st.png" "07_actual_pop.png" "10_lineMPoffset_jump.png" "10_lineMPoffset_tight.png")
   x_coor=(1350 1300 2000 2300 750 1275 1375 1875 1500 2150 1475 1925 800)
   y_coor=(175 325 825 1000 200 800 950 600 1000 1400 2700 1525 775)
   x_offset=(1900 1925 12700 12700 10450 1900 1800 3225 12000 3075 2600 8600 19200)
   y_offset=(1825 1725 2125 2225 2450 8800 10050 2500 10000 3925 0 2400 3725)
   len=${#input_png[*]} 
   base_file=base02_3500x16000.png
   y_past_off=0
}



crop_png1()
{
    for (( i=0; i<len; i++ ))    # For Sorting array elements using Bubble sort
    do
        convert $png_dir/${input_png[$i]} -crop ${x_coor[$i]}"x"${y_coor[$i]}+${x_offset[$i]}+${y_offset[$i]} +repage $crop_dir/${output_png[$i]}
    done
}


crop_png()
{  
    convert $png_dir/svg_01_line.png          -crop 1350"x"175+1900+1825 +repage $crop_dir/01_line.png
    convert $png_dir/svg_08_lineRnd05.png     -crop 1300"x"325+1925+1725 +repage $crop_dir/08_lineRnd05.png
    convert $png_dir/svg_02_lineMP.png        -crop 2000"x"825+12700+2125 +repage $crop_dir/02_lineMP_pop.png
    convert $png_dir/svg_09_lineMPlarge.png   -crop 2300"x"1000+12700+2225 +repage $crop_dir/09_lineMPlarge.png
    convert $png_dir/svg_02_lineMP.png        -crop 750"x"200+10450+2450 +repage $crop_dir/02_lineMP_miss.png
    convert $png_dir/svg_03_diagonal.png      -crop 1275"x"800+1900+8800 +repage $crop_dir/03_diagonal.png
    convert $png_dir/svg_04_acceleration.png  -crop 1375"x"950+1800+10050 +repage $crop_dir/04_acceleration.png
    convert $png_dir/svg_05_circle.png        -crop 1875"x"600+3225+2500 +repage $crop_dir/05_circle.png
    convert $png_dir/svg_06_polynomial.png    -crop 1500"x"1000+12000+10000 +repage $crop_dir/06_polynomial.png
    convert $png_dir/svg_07_actual.png        -crop 2150"x"1400+3075+3925 +repage $crop_dir/07_actual_st.png
    convert $png_dir/svg_07_actual.png        -crop 1475"x"2700+2600+0 +repage $crop_dir/07_actual_pop.png
    convert $png_dir/svg_10_lineMPoffset.png  -crop 1925"x"1525+8600+2400 +repage $crop_dir/10_lineMPoffset_jump.png
    convert $png_dir/svg_10_lineMPoffset.png  -crop 800"x"775+19200+3725 +repage $crop_dir/10_lineMPoffset_tight.png
}

paste_png1()
{
    python paste.py -b $base_dir/$base_file -l $crop_dir/${output_png[0]} -o $out_dir/tmp.png -x 50 -y 0
    for (( i=1; i<len; i++ ))   
    do  
        y_past_off=$(($((${y_coor[$i-1]}+200))+$y_past_off))
        python paste.py -b $out_dir/tmp.png -l $crop_dir/${output_png[i]} -o $out_dir/tmp.png -x 50 -y $y_past_off
    done
}

paste_png()
{
   python paste.py -b $base_dir/base02_3500x14000.png -l $crop_dir/01_line.png     -o $out_dir/tmp.png    -x 50 -y 0
   python paste.py -b $out_dir/tmp.png               -l $crop_dir/02_lineRnd.png  -o $out_dir/tmp.png    -x 50 -y 250
}

test_init
crop_png1
paste_png1
