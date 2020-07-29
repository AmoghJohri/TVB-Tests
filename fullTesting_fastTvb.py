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
from rsHRF import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils
from nitime.analysis import CorrelationAnalyzer, CoherenceAnalyzer

warnings.filterwarnings("ignore")

def executeC(): 
    # store the return code of the c program(return 0) 
    # and display the output 
    s = subprocess.check_call("gcc main.c -lpthread -lm -lgsl -lgslcblas -o tvbii; ./tvbii param_set weights tract_lengths ROIts_retrievedHRF 1", shell = True) 

def get_path(group_name, subject_num, test_num):
    # gets the path for the directory corresponding to each combination of group, subject and test
    if subject_num < 10: return "./Data/" + group_name + "0" + str(subject_num) + "/"
    else: return "./Data/" + group_name + str(subject_num) + "/"

def getHRF(group_id, subject_id):
    # retrieves the HRF from the empirical fMRI time-series
    path = get_path(group_id, subject_id, "T1")
    mat = scipy.io.loadmat(path + "FC.mat")
    # parameters required for HRF retrieval
    para = {}
    para['estimation'] = 'canon2dd'
    para['passband'] = [0.01, 0.08]
    para['TR'] = mat["TR"][0][0]
    para['T'] = 3
    para['T0'] = 1
    para['AR_lag'] = 1
    para['TD_DD'] = 2
    para['localK'] = 2
    para['thr'] = 1
    para['len'] = 25
    para['min_onset_search'] = 4
    para['max_onset_search'] = 8
    para['dt'] = para['TR'] / para['T']
    para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                np.fix(para['max_onset_search'] / para['dt']) + 1,
                                dtype='int')
    if subject_id < 10: bold_sig = mat[group_id + "0" + str(subject_id) + "T1_ROIts_DK68"]
    else: bold_sig = mat[group_id + str(subject_id) + "T1_ROIts_DK68"]
    bold_sig = stats.zscore(bold_sig, ddof=1)
    bold_sig = np.nan_to_num(bold_sig) # replace nan with 0 and inf with large finite numbers
    bf = basis_functions.basis_functions.get_basis_function(bold_sig.shape, para)
    beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1, bf)
    hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])

    np.savetxt('./C_Input/ROIts_retrievedHRF.txt', hrfa.T, delimiter=' ')
    # returns the length of the retrieved HRF and the BOLD Repetition Time
    return hrfa.shape[0], para['TR']

def make_input(group_id, subject_id):
    # does all the book-keeping with respect to arranging and channeling the input files
    try : os.remove("./C_Input/weights.txt")
    except : pass
    try: os.remove("./C_Input/tract_lengths.txt")
    except: pass
    try: os.remove("./C_Input/ROIts_retrievedHRF.txt")
    except: pass
    path = get_path(group_id, subject_id, "T1")
    np.savetxt('./C_Input/weights.txt', np.loadtxt(path + "weights.txt"), delimiter=' ')
    np.savetxt('./C_Input/tract_lengths.txt', np.loadtxt(path + "tract_lengths.txt"), delimiter=' ')
    hrf_len, TR = getHRF(group_id, subject_id)
    f = open("./C_Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()
    # making relavant changes to the parameters file used for simulation
    temp[6] = str(int(TR * 1000 * 200))
    temp[7] = str(int(TR * 1000))
    temp[10] = str(hrf_len)
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
            J_i = np.asarray([[0.0 for i in range(68)] for j in range(len(g))])
            PCorr = [0.0 for i in range(len(g))]
            make_input(group_id, subject_id)
            for i in range(len(g)):
                print("Analysis of Subject: ", group_id + " " + str(subject_id))
                alterGlobalCoupling(g[i])
                executeC()
                PCorr[i] = getCorrelation(group_id, subject_id)
                print("Global Coupling: ", g[i], " and Correlation: ", PCorr[i])
                (J_i)[i] = np.loadtxt("J_i.txt")
                print(J_i[i])
            try : os.remove(get_path(group_id, subject_id, tests[0]) + "/Output/J_i.txt")
            except : pass
            try : os.remove(get_path(group_id, subject_id, tests[0]) + "/Output/PCorr.txt")
            except : pass
            if not os.path.isdir(get_path(group_id, subject_id, tests[0]) + "/Output"):
                os.mkdir(get_path(group_id, subject_id, tests[0]) + "/Output")
            np.savetxt(get_path(group_id, subject_id, tests[0]) + "/Output/J_i.txt", (J_i).T, delimiter = " ")
            np.savetxt(get_path(group_id, subject_id, tests[0]) + "/Output/PCorr.txt", np.asarray(PCorr), delimiter = " ")
    os.remove("fMRI.txt")
    os.remove("J_i.txt")
    os.remove("tvbii")
