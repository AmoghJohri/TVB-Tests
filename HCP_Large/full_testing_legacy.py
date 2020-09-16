# importing libraries
import os
import math
import scipy
import nitime 
import warnings
import subprocess
import numpy             as np 
import scipy.io          as sio
import scipy.stats       as stat
from   scipy             import stats, signal
import matplotlib.pyplot as plt 
from   scipy.sparse      import lil_matrix
from   nitime.utils      import percent_change
from   nitime.timeseries import TimeSeries
from   rsHRF             import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils
from   nitime.analysis   import CorrelationAnalyzer, CoherenceAnalyzer

warnings.filterwarnings("ignore")

path_ = "/home/redhood/Desktop/Work/GSoC/Post-GSoC/Dummy/HCP_Large/HCP_YA_BIDS/derivatives"
fmri = path_+"/fMRI_time_series/"
functional_connectivity = path_+"/functional_connectivity/"
structural_connectivity = path_+"/structural_connectivity/"

def executeC(): 
    # store the return code of the c program(return 0) 
    # and display the output 
    s = subprocess.check_call("gcc tvbii_multicore.c -lpthread -lm -lgsl -lgslcblas -o tvbii; ./tvbii param_set.txt sub 1", shell = True) 

def get_fMRI(run, encoding, sub):
    return np.loadtxt(fmri + sub + "/" + sub + "_task-rfMRI_REST" + str(run) + "_" + encoding + "_space-MMP1_desc-preproc_hcp_fMRI.tsv")

def get_FC(run, encoding, sub):
    return np.loadtxt(functional_connectivity + sub + "/" + sub + "_task-rfMRI_REST" + str(run) + "_" + encoding + "_space-MMP1_desc-preproc_hcp_FC.tsv")

def get_weights(sub):
    return np.loadtxt(structural_connectivity + sub + "/" + sub + "_space-MMP1_desc-preproc_hcp_tvb-sc_weights.tsv")

def get_distances(sub):
    return np.loadtxt(structural_connectivity + sub + "/" + sub + "_space-MMP1_desc-preproc_hcp_tvb-sc_distances.tsv")


def make_input(run, encoding, subject_id):
    # does all the book-keeping with respect to arranging and channeling the input files
    try : os.remove("./C_Input/sub_SC_weights.txt")
    except: pass
    try: os.remove("./C_Input/sub_SC_distances.txt")
    except: pass
    np.savetxt('./C_Input/sub_SC_weights.txt', (get_weights(subject_id))/np.max(get_weights(subject_id)), delimiter=' ')
    np.savetxt('./C_Input/sub_SC_distances.txt', (get_distances(subject_id))/np.max(get_distances(subject_id)), delimiter=' ')
    f = open("./C_Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()
    # making relavant changes to the parameters file used for simulation
    temp[6] = str(int(0.72 * 1000 * 400))
    temp[7] = str(int(0.72 * 1000))
    f = open("./C_Input/param_set.txt", "w") 
    for each in temp:
        f.write(each)
        f.write(" ") 
    f.close()

def getCorrelation(run, encoding, subject_id):
    # obtains the correlation between empirical functional connectivity and simulated functional connectivity
    input_path_sim = "fMRI.txt"
    em_fc_matrix = get_FC(run, encoding, subject_id)
    sampling_interval = 0.72
    uidx = np.triu_indices(379, 1)
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


def main(runs, encoding, l, r):
    # Driver function 
    runs = runs
    encoding = encoding
    subjects = os.listdir(functional_connectivity)
    subjects.remove(".DS_Store")
    subjects = sorted(subjects)
    subjects = subjects[l:r]
    try: os.mkdir("Final_Output")
    except: pass
    for each in subjects:
        for e in encoding:
            for r in runs:
                J_i = np.asarray([[0.0 for i in range(379)] for j in range(len(g))])
                PCorr = [0. for i in range(len(g))]
                make_input(r, e, each)
                for i in range(len(g)):
                    print("Analysis of Subject: ", each)
                    print("Encoding: ", e)
                    print("Run: ", r)
                    print("Global Coupling: ", g[i])
                    alterGlobalCoupling(g[i])
                    executeC()
                    PCorr[i] = getCorrelation(r, e, each)
                    print("Global Coupling: ", g[i], " and Correlation: ", PCorr[i])
                    (J_i)[i] = np.loadtxt("J_i.txt")
                if not os.path.isdir("./Final_Output/" + each):
                    os.mkdir("./Final_Output/" + each)
                if not os.path.isdir("./Final_Output/" + each + "/" + e + "_" + str(r)):
                    os.mkdir(("./Final_Output/" + each + "/" + e + "_" + str(r)))
                path = "./Final_Output/" + each + "/" + e + "_" + str(r)
                np.savetxt(path + "/J_i.txt", (J_i).T, delimiter = " ")
                np.savetxt(path + "/PCorr.txt", np.asarray(PCorr), delimiter = " ")
    os.remove("fMRI.txt")
    os.remove("J_i.txt")
    os.remove("tvbii")
