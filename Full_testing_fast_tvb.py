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
from rsHRF import processing, canon, sFIR
from nitime.analysis import CorrelationAnalyzer, CoherenceAnalyzer

warnings.filterwarnings("ignore")

def executeC(): 
    # executing the fast_tvb code ("main.c")
    s = subprocess.check_call("gcc main.c -lpthread -lm -lgsl -lgslcblas -o tvbii; ./tvbii param_set weights tract_lengths ROIts_retrievedHRF 1", shell = True) 

def get_path(group_name, subject_num, test_num):
    # gets the pathname for the group-name (CON or PAT), subject-num and test-num (T1 or T2) of the subject
    if subject_num < 9: return "./Subjects/" + group_name + "0" + str(subject_num) + test_num
    else: return "./Subjects/" + group_name + str(subject_num) + test_num

def getHRF(subject_id, TR):
    # retrieving the Resting-State Hemodynamic Response Function from the ROIts.txt file 

    # parameters required for the retrieving the HRF
    para = {}
    para['estimation'] = 'canon2dd'     # estimation rule: here, we have fixed it to canonical 2dd which uses canonical HRF with time and dispersion derivatives
    para['passband'] = [0.01, 0.08]     # range of the band-pass filter applied to the input BOLD response
    para['TR'] = TR                     # BOLD repetition time (in seconds)
    para['T'] = 3                       # magnification factor of temporal grid with respect to TR. i.e. para.T=1 for no upsampling, para.T=3 for 3x finer grid
    para['T0'] = 1                      # position of the reference slice in bins, on the grid defined by para.T. For example, if the reference slice is the middle one, then para.T0=fix(para.T/2)
    para['TD_DD'] = 2                   # denotes that we use both time and dispersion derivatives with the canon2dd rule
    para['AR_lag'] = 1                  # noise autocorrelation
    para['thr'] = 1                     # (mean+) para.thr*standard deviation threshold to detect event
    para['len'] = 24                    # length of the Hemodynamic Response Function (in seconds)
    para['min_onset_search'] = 4        # minimum delay allowed between event and HRF onset (in seconds)
    para['max_onset_search'] = 8        # maximum delay allowed between event and HRF onset (in seconds)
    para['dt'] = para['TR'] / para['T'] # fine scale time resolution
    para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                np.fix(para['max_onset_search'] / para['dt']) + 1,
                                dtype='int')
    bold_sig = np.loadtxt("./Subjects/" + str(subject_id) + "/ROIts.txt")
    bold_sig = stats.zscore(bold_sig, ddof=1) # normalizing the input BOLD time-series
    bold_sig = np.nan_to_num(bold_sig)  # replace nan with 0 and inf with large finite numbers
    bold_sig = processing. \
            rest_filter. \
            rest_IdealFilter(bold_sig, para['TR'], para['passband']) # applying the bandpass filter
    temporal_mask = [] # for masking time-slices (empty temporal mask corresponds to all time-slices being included)
    beta_hrf, bf, event_bold = \
                canon.canon_hrf2dd.wgr_rshrf_estimation_canonhrf2dd_par2(
                    bold_sig, para, temporal_mask, 1
                )
    hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :]) # retrieved HRF
    np.savetxt('./Input/ROIts_retrievedHRF.txt', hrfa.T, delimiter=' ')
    return hrfa.shape[0]

def make_input(subject_id, TR):
    # book-keeping for file arrangement, parameter values, etc, for each subject

    try : os.remove("./Input/weights.txt")
    except : pass
    try: os.remove("./Input/tract_lengths.txt")
    except: pass
    try: os.remove("./Input/ROIts_retrievedHRF.txt")
    except: pass

    path = "./Subjects/" + str(subject_id) + "/"
    np.savetxt('./Input/weights.txt', np.loadtxt(path + "weights.txt"), delimiter=' ')
    np.savetxt('./Input/tract_lengths.txt', np.loadtxt(path + "tract_lengths.txt"), delimiter=' ')
    hrf_len = getHRF(subject_id, TR)
    f = open("Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()

    # setting the appropriate parameters for BOLD simulations
    temp[7] = str(int(TR * 1000 * 200)) 
    temp[8] = str(hrf_len)
    temp[9] = str(int(TR * 1000))
    f = open("Input/param_set.txt", "w") 
    for each in temp:
        f.write(each)
        f.write(" ") 
    f.close()

def getCorrelation(subject_id):
    # obtains the correlation between the simulated Functional Connectivity to the empirical Functional Connectivity

    input_path_sim = "fMRI.txt"
    input_path_em = "./Subjects/" + str(subject_id) + "/FC.txt"
    # getting the empirical functional connectivity
    em_fc_matrix = np.loadtxt(input_path_em)
    uidx = np.triu_indices(68, 1)
    em_fc_z = np.arctanh(em_fc_matrix)
    em_fc = em_fc_z[uidx]
    # getting the simulated functional connectivity
    tsr = np.loadtxt(input_path_sim)
    T = TimeSeries(tsr, sampling_interval=2.1)
    C = CorrelationAnalyzer(T)
    sim_fc = np.arctanh(C.corrcoef)[uidx]
    # getting the correlation value (Pearson's R)
    pearson_corr, _ = stat.pearsonr(sim_fc, em_fc)
    return pearson_corr

def alterGlobalCoupling(G):
    # alters the global coupling parameter for each iteration through parameter space exploration
    f = open("Input/param_set.txt", "r")
    for line in f:
        temp = line.split()
        break
    f.close()
    temp[1] = str(G) 
    f = open("Input/param_set.txt", "w") 
    for each in temp:
        f.write(each)
        f.write(" ") 
    f.close()

if __name__== "__main__": #
    # Driver function 

    # two groups of subjects: CON - Control Group and PAT - Patients
    groups = ["CON", "PAT"] 
    # test number: T1 - First Test and T2 - Second Test
    tests = ["T1", "T2"]
    # Subject IDs - as of now we have only dealt with the Control Group Subjects
    ID_list = {"CON":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}
    # BOLD Repetition Time corresponding to each subject
    TR_list = {"CON":[2.1, 2.1, 2.1, 2.1, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4]}
    # values over which the parameter space exploration is performed (parameter: Global Coupling)
    g = [0.01, 0.3, 0.59, 0.88, 1.17, 1.46, 1.75, 2.04, 2.33, 2.62, 2.91]
    # Main Loop
    for j in range(len(ID_list[groups[0]])):
        # to store the Feedback Inhibhition Parameter values for each subject (num-of-brain-regions x iterations-in-parameter-space-exploration)
        J_i = np.asarray([[0 for i in range(68)] for j in range(len(g))])
        # to store the Correlation value of the simulated functional connectivity and empirical functional connectivity (for each value of global coupling parameter)
        PCorr = [0 for i in range(len(g))]
        make_input(ID_list[groups[0]][j], TR_list[groups[0]][j])
        # Iterating over different values of global coupling parameter
        for i in range(len(g)):
            print("Analysis of Subject: ", ID_list[groups[0]][j])
            alterGlobalCoupling(g[i])
            executeC()
            PCorr[i] = getCorrelation(ID_list[groups[0]][j])
            (J_i).T[i] = np.loadtxt("J_i.txt")
            print("Global Coupling: ", g[i], " and Correlation: ", PCorr[i])
        np.savetxt(get_path(groups[0], ID_list[groups[0]][j], tests[0]) + "/Output/J_i.txt", (J_i).T, delimiter = " ")
        np.savetxt(get_path(groups[0], ID_list[groups[0]][j], tests[0]) + "/Output/PCorr.txt", np.asarray(PCorr), delimiter = " ")
    os.remove("fMRI.txt")
    os.remove("J_i.txt")
    os.remove("tvbii")
    print("Analysis for all the subjects has concluded! Goodbye!")
