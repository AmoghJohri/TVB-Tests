import os 
import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

subjects = os.listdir("./Data/")
CON = []
PAT = []
for each in subjects:
    if each[0] == "C":
        CON.append(each)
    else:
        PAT.append(each)

def get_path(estimation, subject):
    if estimation == "canon2dd":
        return "./Data/" + subject + "/Output_canon2dd/"
    else:
        return "./Data/" + subject + "/Output_gamma/"

def get_average_correlation(estimation, group):
    arr = []
   
    if group == "CON":
        lookup = CON
    else:
        lookup = PAT
    for each in lookup:
        arr.append(max(np.loadtxt(get_path(estimation,each)+ "PCorr.txt", delimiter="\n")))
    return sum(arr)/len(arr) 
