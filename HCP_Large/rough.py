import os 
import numpy as np

runs = [1, 2]
encoding = ["LR", "RL"]

path = "/home/redhood/Desktop/Work/GSoC/Post-GSoC/HCP_Large/HCP_YA_BIDS/derivatives"
fmri = path+"/fMRI_time_series/"
functional_connectivity = path+"/functional_connectivity/"
structural_connectivity = path+"/structural_connectivity/"

def get_fMRI(run, encoding, sub):
    return np.loadtxt(fmri + sub + "/" + sub + "_task-rfMRI_REST" + str(run) + "_" + encoding + "_space-MMP1_desc-preproc_hcp_fMRI.tsv")

def get_FC(run, encoding, sub):
    return np.loadtxt(functional_connectivity + sub + "/" + sub + "_task-rfMRI_REST" + str(run) + "_" + encoding + "_space-MMP1_desc-preproc_hcp_FC.tsv")

def get_weights(sub):
    return np.loadtxt(structural_connectivity + sub + "/" + sub + "_space-MMP1_desc-preproc_hcp_tvb-sc_weights.tsv")

def get_distances(sub):
    return np.loadtxt(structural_connectivity + sub + "/" + sub + "_space-MMP1_desc-preproc_hcp_tvb-sc_distances.tsv")
    
