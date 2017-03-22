import random, os
import math

randomCount = 1000
output_dir = "output"
gaussianSumCount = 6

if not os.path.exists("./" + output_dir):
    os.makedirs(output_dir)

def Rnd_Gauss(vgaussianSumCount):
    gRnd = 0
    for i in range(vgaussianSumCount):
        gRnd += round(random.uniform(0, 1), vgaussianSumCount)*2.0 - 1.0
    return gRnd

def Gen_Random(out_path, num):
    f = open("./" + out_path + "/random.txt", "w")
    for i in range(num-1):
        f.write(str("%.6f"  % (round(random.uniform(0, 1), gaussianSumCount))) + "\n")
    f.write(str("%.6f"  % (round(random.uniform(0, 1), gaussianSumCount))))
    
def Gen_Random_Gaussian(out_path,vgaussianSumCount,num):
    f = open("./" + out_path + "/randomGaussian.txt", "w")
    for i in range(num-1):
         f.write(str("%.6f"  % (Rnd_Gauss(vgaussianSumCount))) + "\n")
    f.write(str("%.6f"  % (Rnd_Gauss(vgaussianSumCount))))
        
def Gen_Random_Gaussian_2D(out_path,vgaussianSumCount,num):
    dX_sum = 0.0
    dY_sum = 0.0
    dX2_sum = 0.0
    dY2_sum = 0.0
    
    f = open("./" + out_path + "/randomGaussian2d.txt", "w")

    for i in range(num-1):
        rrg = Rnd_Gauss(vgaussianSumCount)
        ang_rad = math.pi*round(random.uniform(0, 1), vgaussianSumCount)
        gaussX=rrg*math.cos(ang_rad)   
        gaussY=rrg*math.sin(ang_rad)
        f.write(str("%.6f"  % (gaussX)) + "," + str("%.6f"  % (gaussY)) + "\n")

    rrg = Rnd_Gauss(vgaussianSumCount)
    ang_rad = math.pi*round(random.uniform(0, 1), vgaussianSumCount)
    gaussX=rrg*math.cos(ang_rad)   
    gaussY=rrg*math.sin(ang_rad)
    f.write(str("%.6f"  % (gaussX)) + "," + str("%.6f"  % (gaussY)) + "\n")
    
    dX_sum = dX_sum + gaussX
    dY_sum = dY_sum + gaussY
    dX2_sum = dX2_sum + gaussX*gaussX
    dY2_sum = dY2_sum + gaussY*gaussY
    
    dX_stddev = math.sqrt( dX2_sum/num - (dX_sum/num)*(dX_sum/num) )
    dY_stddev = math.sqrt( dY2_sum/num - (dY_sum/num)*(dY_sum/num) )

    f.write("----------------------------------------------------------------------" )
    f.write("\n" + str("%.6f"  % (dX_stddev)) + "," + str("%.6f"  % (dY_stddev)))

Gen_Random_Gaussian_2D(output_dir, gaussianSumCount, randomCount)        
Gen_Random(output_dir, randomCount)
Gen_Random_Gaussian(output_dir, gaussianSumCount, randomCount)