<h1> Important details about the Replication </h1>

This markdown file is presented in place of all files and scripts for replication. Unlike in the repository of van Vliet et al. (2018), some files for plotting purposes are made available. These files are outputs from running certain parts of the pipeline.

This file also describes the purpose of each numbered (00-12) Python script of van Vliet et al. (2018) and outlines how each script was used during the replication. The steps that yield the plots in the "DSC_Python_Plot_Replication.py" script are identified with **[PLOT]**.

<h3> General instructions for using the scripts </h3>

* Define your study_path. 
* Download the "data" folder from this link: https://drive.google.com/drive/folders/12HLqUYrPtiYSf5Ni7tTC4XWkFPLKYR55?usp=sharing
* After cloning the repo, put the "data" folder inside "study_path/Replication"
* Run the functions defined in "plot_replicated_files.py" using "main.py".

<h3> Notes about the full replication process in our local machine </h3>

* Each subject (subXXX) = "{subject}"
* Setup "study_path/MEG/{subject}" as "{subject_dir}" and "study_path/subjects" as "{subjects_dir}"

<h3> 00_fetch_data.py </h3>

* Creates an "archive" directory that contains "ds117_R0.1.1_subXXX_raw.tgz"
* Creates a "ds117" directory that contains the extracted files
* Each extracted subject file contains the following directories: "anatomy", "behav", "BOLD", "diffusion", "MEG"

<h3> 01_anatomy.py </h3>

* Performs FreeSurfer -recon-all method on "ds117/{subject}/anatomy/highres001.nii.gz"
* Convert multiecho flash (MEF) MRI data to FLASH 5 MRI "flash5.mgz"
* Create 3-layer BEM from FLASH 5 MRI, "{subjects_dir}/{subject}/bem/inner_skull.surf, "outer_skin.surf", "outer_skull.surf"

<h3> 02_filter.py </h3>

* Drop EEG channels from and apply band-pass filtering (1-40 Hz) to "ds117/{subject}/MEG/run_XX_sss.fif" (6 runs)
* High pass the EOG filters (>1 Hz) and save as "{subject_dir}/{subject}/run_XX-filt-1-40-raw_sss.fif" (6 runs)

<h3> 03_ica.py </h3>

* Define parameters for ICA to remove heart beats and eye blinks, and save as "{subject_dir}/{subject}-ica.fif"

<h3> 04_epo.py </h3>

* Make epochs (-0.2 to 2.9 s, baseline of -0.2 to 0 s) from band-pass filtered data
* Load ICA object and apply to epoched data, and save as "{subject_dir}/{subject}-epo.fif"

<h3> 05_csd.py </h3>

* Load epoched data and compute wavelet-based CSD from 0 to 0.4 s, for each frequency band and {condition} = [face, scrambled]
* Save CSD objects as "{subject_dir}/{subject}-{condition}-csd.h5" **[PLOT 1]**

<h3> 06_fsaverage_src.py </h3>

* Copy "FreeSurfer/subjects/fsaverage" to "{subjects_dir}"
* Create source space on fsaverage brain and save as "{subjects_dir}/fsaverage/fsaverage-ico4-src.fif"

<h3> 07_forward.py </h3>

* Morph the fsaverage source space to each subject, and save as "{subject_dir}/{subject}/fsaverage_to_{subject}-ico4-src.fif" **[PLOT 2]**
* Create forward models from single-layer BEM, and save as "{subject_dir}/fsaverage_to_{subject}-meg-ico4-fwd.fif" **[PLOT 3]**

<h3> 08_select_vertices.py </h3>

* Retain vertices of the forward models ≤7 cm from the sensors, and save as "{subject_dir}/{subject}-restricted-meg-ico4-fwd.fif" **[PLOT 3]**
* Compute vertex pairs for which to compute connectivity, and save as "study_path/MEG/pairs.npy"

<h3> 09_power.py </h3>

* Compute DICS beamformers from the CSD and forward model for each condition, subject, and frequency band
* Save output as "{subject_dir}/{subject}-{condition}-dics-power"

<h3> 10_connectivity.py </h3>

* Compute coherence-based all-to-all connectivity from restricted forward solution and vertex pairs for each condition and frequency band
* Save output as "{subject_dir}/{subject}-{condition}-connectivity.h5"

<h3> 11_grand_average_power.py </h3>

* Average the power (source) estimates across subjects for each condition, and save as "study_path/MEG/{condition}-average-dics"
* Compute contrast between face and scrambled relative to baseline, and save as "study_path/MEG/contrast-average-dics" **[PLOT 4]**

<h3> 12_connectivity_stats.py </h3>

* Average the connectivity across subjects for each condition, and save as "study_path/MEG/{condition}-average-connectivity.h5"
* Compute contrast between face and scrambled, and save as "study_path/MEG/contrast-average-connectivity.h5"
* Perform permutation test to guide pruning **[PLOT 5]** and parcellation **[PLOT 6]** of the contrast connectivity
* Save pruned as "study_path/MEG/pruned-average-connectivity.h5"; parcellated as "study_path/MEG/parcellated-average-connectivity.h5"
