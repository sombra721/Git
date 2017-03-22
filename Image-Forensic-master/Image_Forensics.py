#!/usr/bin/python 
# -*- coding: utf-8 -*-
__author__ = "Michael Tsai"
'''
The program first loads the image and converts it into grayscale, and obtain an array composed by numbers, which are pixel values for
each pixel. Basically, the values of the pixels which were duplicated will remain the same as the original parts in the image.
The program will automatically detect if there are two or more areas has the same pixel values, and then the result illustration where are the
duplication parts and their locations in a new image. 
'''
import matplotlib.image as picarray
from skimage import color 
import numpy as np
import scipy
import matplotlib.pyplot as plt

im1 = picarray.imread ('test.png')
im2 = color.rgb2gray(im1) 

H = im2.shape[0]
W = im2.shape[1]

print(H,W)

temp = np.zeros (im2.shape, 'int16')
result = np.zeros (im2.shape, 'int16')
result = 255-result

gap1, gap2, gap3, gap4 = 0,0,0,0 #0~63, 64~127, 128~ 191, 192~255
count1, count2, count3, count4 = 0,0,0,0
target_stack = np.zeros((2000, 5), 'int16')

print(im1[1][1][1])
for i in range(0, 2000, 1):
    target_stack[i][0] = -1

for i in range(0, H, 1):
    for j in range(0, W, 1):
        temp[i][j] = int(255*(0.299 * im1[i][j][0] + 0.587 * im1[i][j][1] + 0.114 * im1[i][j][2]))

for i in range(0, H, 1):
    for j in range(0, W,1):
        if (temp[i][j] < 64):
            gap1 = gap1 + 1
        elif (temp[i][j] < 128):
            gap2 = gap2 + 1
        elif (temp[i][j] < 192):
            gap3 = gap3 + 1
        elif (temp[i][j] < 256):
            gap4 = gap4 + 1

region1 = np.arange(gap1 * 3).reshape(gap1, 3) 
region2 = np.arange(gap2 * 3).reshape(gap2, 3) 
region3 = np.arange(gap3 * 3).reshape(gap3, 3) 
region4 = np.arange(gap4 * 3).reshape(gap4, 3) 

for i in range(0, H, 1):
    for j in range(0, W,1):
        if (temp[i][j] < 64):
            region1[count1][0] = temp[i][j]
            region1[count1][1] = i
            region1[count1][2] = j
            count1 = count1 + 1         
        elif (temp[i][j] < 128):
            region2[count2][0] = temp[i][j]
            region2[count2][1] = i
            region2[count2][2] = j
            count2 = count2 + 1
        elif (temp[i][j] < 192):
            region3[count3][0] = temp[i][j]
            region3[count3][1] = i
            region3[count3][2] = j
            count3 = count3 + 1
        elif (temp[i][j] < 256):
            region4[count4][0] = temp[i][j]
            region4[count4][1] = i
            region4[count4][2] = j
            count4 = count4 + 1

region1 = region1[region1[:,0].argsort()]
region2 = region2[region2[:,0].argsort()]
region3 = region3[region3[:,0].argsort()]
region4 = region4[region4[:,0].argsort()]

D_count = 0
find = 0

def DetectFake (region, gap, Stack_count, temp, target, find):   
    for i in range(0, gap, 1):
        tag = 0
        D_count = Stack_count
        if(i < gap -1 ) and (find == 0):
            if(region[i][0] == region[i + 1][0]):
                target[D_count][0] = region[i][0]
                target[D_count][1] = region[i][1]
                target[D_count][2] = region[i][2]
                target[D_count][3] = region[i + 1][1]
                target[D_count][4] = region[i + 1][2]
                D_count = D_count+1
                
            while(target[tag][0] != -1) and find==0:
                #print(i, tag, D_count, target[tag][0], target[tag][1], target[tag][2], target[tag][3], target[tag][4])
                
                if(target[tag][1] > 0 and target[tag][3] > 0 ): #up
                    flag = 0
                    for k in range(0, D_count, 1):
                        if(target[k][1] == target[tag][1] - 1) and (target[k][2] == target[tag][2]):
                            flag = 1
                    if(flag == 0):            
                        if(temp[target[tag][1] - 1][target[tag][2]] == temp[target[tag][3] - 1][target[tag][4]]):                         
                            target[D_count][0] = temp[target[tag][1] - 1][target[tag][2]]
                            target[D_count][1] = target[tag][1] - 1
                            target[D_count][2] = target[tag][2]
                            target[D_count][3] = target[tag][3] - 1
                            target[D_count][4] = target[tag][4]
                            D_count = D_count+1
                           
                            
                if(target[tag][2] > 0 and target[tag][4] > 0 ): #left
                    flag = 0
                    for k in range(0, D_count, 1):
                        if(target[k][1] == target[tag][1]) and (target[k][2] == target[tag][2] - 1):
                            flag = 1
                    if(flag == 0):                  
                        if(temp[target[tag][1]][target[tag][2]- 1] == temp[target[tag][3]][target[tag][4] - 1]):                            
                            target[D_count][0] = temp[target[tag][1]][target[tag][2]- 1]
                            target[D_count][1] = target[tag][1]
                            target[D_count][2] = target[tag][2] - 1
                            target[D_count][3] = target[tag][3]
                            target[D_count][4] = target[tag][4] - 1
                            D_count = D_count+1

                            
                if(target[tag][1] < H-1 and target[tag][3] < H-1 ): #down                
                    flag = 0
                    for k in range(0, D_count, 1):
                        if(target[k][1] == target[tag][1] + 1) and (target[k][2] == target[tag][2]):
                            flag = 1
                    if(flag == 0):                  
                        if(temp[target[tag][1] + 1][target[tag][2]] == temp[target[tag][3] + 1][target[tag][4]]):                           
                            target[D_count][0] = temp[target[tag][1] + 1][target[tag][2]]
                            target[D_count][1] = target[tag][1] + 1
                            target[D_count][2] = target[tag][2]
                            target[D_count][3] = target[tag][3] + 1
                            target[D_count][4] = target[tag][4]
                            D_count = D_count+1
                
                if(target[tag][2] < W-1 and target[tag][4] < W-1 ): #right               
                    flag = 0
                    for k in range(0, D_count, 1):
                        if(target[k][1] == target[tag][1]) and (target[k][2] == target[tag][2] + 1) or (target[k][3] == target[tag][1]) and (target[k][4] == target[tag][2] + 1):
                            flag = 1
                    if(flag == 0):                  
                        if(temp[target[tag][1]][target[tag][2] + 1] == temp[target[tag][3]][target[tag][4] + 1]):                           
                            target[D_count][0] = temp[target[tag][1]][target[tag][2] + 1]
                            target[D_count][1] = target[tag][1] 
                            target[D_count][2] = target[tag][2] + 1
                            target[D_count][3] = target[tag][3] 
                            target[D_count][4] = target[tag][4] + 1
                            D_count = D_count+1
                            
                tag = tag + 1
        
                if (D_count > 5) and tag == D_count:
                    print(D_count)
                    for z in range(1, D_count, 1):
                        result[target[z][1]][target[z][2]] = target[z][0]
                        result[target[z][3]][target[z][4]] = target[z][0]
                    
                    scipy.misc.imsave('result.png', result)
                    
                    find = 1

            for i in range(0, D_count, 1):
                target_stack[i][0] = -1
            D_count = 0
            tag = 0
 
    return find


DetectFake(region1, gap1, 0, temp, target_stack, find)            

DetectFake(region2, gap2, 0, temp, target_stack, find)

DetectFake (region3, gap3, 0, temp, target_stack, find)

DetectFake(region4, gap4, 0, temp, target_stack, find)

plt.figure
fig = plt.figure()

plt.subplot(121)
plt.imshow (im1, interpolation='nearest')
plt.set_cmap ('gray')
plt.title('Original Image')

frame1 = plt.gca()
frame1.axes.get_xaxis().set_visible(False)
frame1.axes.get_yaxis().set_visible(False)

plt.subplot(122)
plt.imshow (result, interpolation='nearest')
plt.set_cmap ('gray')
plt.title('Result')

frame1 = plt.gca()
frame1.axes.get_xaxis().set_visible(False)
frame1.axes.get_yaxis().set_visible(False)
plt.show() 
