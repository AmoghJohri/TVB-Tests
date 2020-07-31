# importing libraries
import os
import scipy
import nitime 
import warnings
import subprocess
import numpy as np 
import scipy.io as sio
import scipy.stats as stat
from scipy import stats, signal
import matplotlib.pyplot as plt 
from scipy.sparse import lil_matrix
from nitime.utils import percent_change
from nitime.timeseries import TimeSeries
from nitime.analysis import CorrelationAnalyzer, CoherenceAnalyzer

warnings.filterwarnings("ignore")

def executeC(): 
    # store the return code of the c program(return 0) 
    # and display the output 
    s = subprocess.check_call("gcc tvbii_multicore.c -lpthread -lm -lgsl -lgslcblas -o tvbii; ./tvbii param_set.txt sub 1", shell = True) 

def get_path(group_name, subject_num, test_num):
    # gets the path for the directory corresponding to each combination of group, subject and test
    if subject_num < 10: return "./Data/" + group_name + "0" + str(subject_num) + "/"
    else: return "./Data/" + group_name + str(subject_num) + "/"

def make_input(group_id, subject_id):
    # does all the book-keeping with respect to arranging and channeling the input files
    try : os.remove("./C_Input/sub_SC_weights.txt")
    except : pass
    try: os.remove("./C_Input/sub_SC_distances.txt")
    except: pass
    path = get_path(group_id, subject_id, "T1")
    np.savetxt('./C_Input/sub_SC_weights.txt', np.loadtxt(path + "weights.txt"), delimiter=' ')
    np.savetxt('./C_Input/sub_SC_distances.txt', np.loadtxt(path + "tract_lengths.txt"), delimiter=' ')
    f = open("./C_Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()
    # making relavant changes to the parameters file used for simulation
    if (group_id == "CON" and int(subject_id) <= 4) or (group_id == "PAT" and int(subject_id) <= 8):
        TR = 2.1 
    else:
        TR = 2.4
    temp[6] = str(int(TR * 1000 * 200))
    temp[7] = str(int(TR * 1000))
    f = open("./C_Input/param_set.txt", "w") 
    for each in temp:
        f.write(each)
        f.write(" ") 
    f.close()

def getCorrelation(group_id, subject_id):
    # obtains the correlation between empirical functional connectivity and simulated functional connectivity
    input_path_sim = "fMRI.txt"
    input_path_em = get_path(group_id, subject_id, "T1") + "FC.mat"
    em_mat = scipy.io.loadmat(input_path_em)
    em_fc_matrix = em_mat["FC_cc_DK68"]
    sampling_interval = em_mat["TR"][0][0]
    uidx = np.triu_indices(68, 1)
    em_fc_z = np.arctanh(em_fc_matrix)
    em_fc = em_fc_z[uidx]
    tsr = np.loadtxt(input_path_sim)
    T = TimeSeries(tsr, sampling_interval=sampling_interval)
    C = CorrelationAnalyzer(T)
    sim_fc = np.arctanh(C.corrcoef)[uidx]
    sim_fc = np.nan_to_num(sim_fc)
    pearson_corr, _ = stat.pearsonr(sim_fc, em_fc)
    return pearson_corr

def alterGlobalCoupling(G):
    # alters the global coupling value for each iteration of parameter space exploration
    f = open("./C_Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()
    temp[1] = str(G) 
    f = open("./C_Input/param_set.txt", "w") 
    for each in temp:
        f.write(each)
        f.write(" ") 
    f.close()

if __name__== "__main__":
    # Driver function 
    Subjects = {}
    Subjects["CON"] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    Subjects["PAT"] = [1, 2, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25]
    tests = ["T1", "T2"]
    g = [(i/10)+0.01 for i in range(0,31,2)]
    g = sorted(g, reverse=True)
    for group_id in Subjects.keys():
        for subject_id in Subjects[group_id]:
            PCorr = [0.0 for i in range(len(g))]
            make_input(group_id, subject_id)
            for i in range(len(g)):
                print("Analysis of Subject: ", group_id + " " + str(subject_id))
                alterGlobalCoupling(g[i])
                executeC()
                PCorr[i] = getCorrelation(group_id, subject_id)
                print("Global Coupling: ", g[i], " and Correlation: ", PCorr[i])
            try : os.remove(get_path(group_id, subject_id, tests[0]) + "/Output/PCorr.txt")
            except : pass
            if not os.path.isdir(get_path(group_id, subject_id, tests[0]) + "/Output"):
                os.mkdir(get_path(group_id, subject_id, tests[0]) + "/Output")
            np.savetxt(get_path(group_id, subject_id, tests[0]) + "/Output/PCorr.txt", np.asarray(PCorr), delimiter = " ")
    os.remove("fMRI.txt")
    os.remove("tvbii")

