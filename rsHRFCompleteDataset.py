import scipy
import numpy as np
from rsHRF import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils

def get_path(group_name, subject_num):
    # gets the path for the directory corresponding to each combination of group, subject and test
    if subject_num < 10: return "./Data/" + group_name + "0" + str(subject_num) + "/FC.mat"
    else: return "./Data/" + group_name + str(subject_num) + "/FC.mat"

def getHRF(group_id, subject_id):
    # retrieves the HRF from the empirical fMRI time-series
    path = get_path(group_id, subject_id)
    mat = scipy.io.loadmat(path)
    # parameters required for HRF retrieval
    para = {}
    para['estimation'] = 'gamma'
    para['passband'] = [0.01, 0.08]
    para['TR'] = mat["TR"][0][0]
    para['T'] = 3
    para['T0'] = 1
    para['order'] = 3
    para['AR_lag'] = 1
    para['thr'] = 1
    para['len'] = 24
    para['min_onset_search'] = 4
    para['max_onset_search'] = 8
    para['dt'] = para['TR'] / para['T']
    para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                np.fix(para['max_onset_search'] / para['dt']) + 1,
                                dtype='int')
    if subject_id < 10: bold_sig = mat[group_id + "0" + str(subject_id) + "T1_ROIts_DK68"]
    else: bold_sig = mat[group_id + str(subject_id) + "T1_ROIts_DK68"]
    bold_sig = scipy.stats.zscore(bold_sig, ddof=1)
    bold_sig = np.nan_to_num(bold_sig) # replace nan with 0 and inf with large finite numbers
    beta_hrf, event_bold, bf  = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1)
    if not (para['estimation'] == 'sFIR' or para['estimation'] == 'FIR'):
        hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
    else:
        hrfa = beta_hrf
    np.savetxt('./RetrievedHRF/' + str(group_id) + str(subject_id) + 'retrievedHRF.txt', hrfa.T, delimiter=', ')
    # returns the length of the retrieved HRF and the BOLD Repetition Time
    return hrfa

if __name__== "__main__":
    # Driver function 
    Subjects = {}
    Subjects["CON"] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    Subjects["PAT"] = [1, 2, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 31]
    for group_id in Subjects.keys():
        for subject_id in Subjects[group_id]:
            hrf = getHRF(group_id,subject_id)
    print("All Done! Goodbye!")