# TVB-Tests

 This work is a part of [Google Summer of Code 2020](https://www.incf.org/activities/gsoc) (INCF - Project 8: Improvoing Personalized Models of fMRI Recordings Including Individual Region-Specific HRF in The Virtual Brain, under the mentorship of [Prof. Daniele Marinazzo](https://users.ugent.be/~dmarinaz/))

Here, we demonstrate various tests/tutorials for the tasks tasks that have been accomplished. To understand the following familiarity with The Virtual Brain(TVB) is necessary. For more information on TVB, visit: [https://www.thevirtualbrain.org/tvb/zwei](https://www.thevirtualbrain.org/tvb/zwei).

When using The Virtual Brain for scientific publications, please cite it as follows:  
<pre><code>Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
    The Virtual Brain: a simulator of primate brain network dynamics.
Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)</code></pre>

## Region-Specific Hemodynamic Response Function Mediated TVB BOLD Simulations

![Resting-State HRF Retrieval](https://raw.githubusercontent.com/compneuro-da/rsHRF/master/docs/BOLD_HRF.png)

### Introduction
fMRI is an indirect measure of neural activity. The resulting BOLD signal attributes to the underlying neural activity as well as the Hemodynamic Response Function (HRF). Hence, variability in the HRF can be confused with variability in the neural activity. Several studies have established that HRF varies across subjects as well as across brain regions for a particular subject. This makes it necessary to individually estimate the resting state HRF (rsHRF) across different regions of a brain. An effective methodology for the same has been suggested by [Wu et.al](10.1016/j.media.2013.01.003 "Link To Paper"). <br>
TVB makes use of a constant HRF (across subjects, and across brain-regions within a subject) which is convolved with the neural response to obtain BOLD simulation. Here, we have integrated the [rsHRF-toolbox](https://www.nitrc.org/projects/rshrf) with TVB to account for region-specific HRF for BOLD simulations.

### File Structure
```
exploring_the_rsHRF_BOLD_Monitor.ipynb
rsHRF_Mediated_Brain_Dynamics.ipynb
parameter_space_exploration.py

Input
|   FC.txt
|   ROIts.txt
|   areas.txt
|   average_orientations.txt
|   centres.txt
|   connectivity.h5
|   cortical.txt
|   dummy_rsHRF.txt
|   hemisphere.txt
|   region_labels.txt
|   tract_lengths.txt
└─> weights.txt

Subjects
│   CONXXTX (Control/Patients + number + T1/T2)
|   |   FC.txt
|   |   ROIts.txt
│   │   areas.txt
│   │   average_orientations.txt
│   │   centres.txt
|   |   connectivity.h5
│   │   cortical.txt
│   │   hemisphere.txt
|   |   region_labels.txt
│   │   tract_lengths.txt
│   │   weights.txt
|   |   Output
|   |   |   J_i.txt
|   └─> └─> PCorr.txt
│   
└───CONXXTX
    │   ...
```

### Tutorials
* **exploring_the_rsHRF_BOLD_Monitor.ipynb** is a tutorial for using the RestingStateHRF kernel which has been proposed as an addition to the existing TVB BOLD monitor.
* **rsHRF_Mediated_Brain_Dynamics.ipynb** is a tutorial for the complete workflow as described below:
    1. Using TVB to build a subject's virtual brain model.
    2. Obtaining the BOLD simulations from the model
        * Using the default TVB approach
        * Using the region-wise resting-state HRF approach.
    3. Parameter space exploration based on the obtained simulations.
<br> This is carried out along similar lines to the study at [https://github.com/the-virtual-brain/tvb-educase-braintumor](https://github.com/the-virtual-brain/tvb-educase-braintumor).

### Tests
> WIP
* **parameter_space_exploration.py** uses the **main.c**, which is theoretically similar, but computationally efficient implementation of the TVB simulations (for more information, visit: [https://github.com/BrainModes/fast_tvb](https://github.com/BrainModes/fast_tvb)). To perform the similar experimation as the second-point in *Tutorial*, over a number of subjects (in the directory *Subjects*). It performs a parameter space exploration over the *global coupling parameter* and the *feedback inhibhition parameter*. The results are stored in the *Output* directory for each subject.

### Data
The dataset has been obtained from [https://openneuro.org/datasets/ds001226/versions/00001](https://openneuro.org/datasets/ds001226/versions/00001), and preprocessed according to TVB requirements.