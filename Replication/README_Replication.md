In place of

Perform for each subject (subXXX) = "{subject}"
Setup "study_path/MEG/{subject}" as "{subject_dir}" and "study_path/subjects" as "{subjects_dir}""

# 00_fetch_data.py
# - Creates an "archive" directory that contains "ds117_R0.1.1_subXXX_raw.tgz"
# - Creates a "ds117" directory that contains the extracted files
# - Each extracted subject file contains the following directories: "anatomy", "behav", "BOLD", "diffusion", "MEG"

# 01_anatomy.py
# - Performs FreeSurfer -recon-all method on "ds117/{subject}/anatomy/highres001.nii.gz"
# - Convert multiecho flash (MEF) MRI data to FLASH 5 MRI "flash5.mgz"
# - Create 3-layer BEM from FLASH 5 MRI, "{subjects_dir}/{subject}/bem/inner_skull.surf, "outer_skin.surf", "outer_skull.surf"

# 02_filter.py
# - Drop EEG channels from and apply band-pass filtering (1-40 Hz) to "ds117/{subject}/MEG/run_XX_sss.fif" (6 runs)
# - High pass the EOG filters (>1 Hz) and save as "{subject_dir}/{subject}/run_XX-filt-1-40-raw_sss.fif" (6 runs)

# 03_ica.py
# - Define parameters for ICA to remove heart beats and eye blinks, and save as "{subject_dir}/{subject}-ica.fif"

# 04_epo.py
# - Make epochs (-0.2 to 2.9 s, baseline of -0.2 to 0 s) from band-pass filtered data
# - Load ICA object and apply to epoched data, and save as "{subject_dir}/{subject}-epo.fif"

# 05_csd.py
# - Load epoched data and compute wavelet-based CSD from 0 to 0.4 s, for each frequency band and {condition} = [face, scrambled]
# - Save CSD objects as "{subject_dir}/{subject}-{condition}-csd.h5" [PLOT 1]

# 06_fsaverage_src.py
# - Copy "FreeSurfer/subjects/fsaverage" to "{subjects_dir}"
# - Create source space on fsaverage brain and save as "{subjects_dir}/fsaverage/fsaverage-ico4-src.fif"

# 07_forward.py
# - Morph the fsaverage source space to each subject, and save as "{subject_dir}/{subject}/fsaverage_to_{subject}-ico4-src.fif" [PLOT 2]
# - Create forward models from single-layer BEM, and save as "{subject_dir}/fsaverage_to_{subject}-meg-ico4-fwd.fif" [PLOT 3]

# 08_select_vertices.py
# - Retain vertices of the forward models ≤7 cm from the sensors, and save as "{subject_dir}/{subject}-restricted-meg-ico4-fwd.fif" [PLOT 3]
# - Compute vertex pairs for which to compute connectivity, and save as "study_path/MEG/pairs.npy"

# 09_power.py
# - Compute DICS beamformers from the CSD and forward model for each condition, subject, and frequency band
# - Save output as "{subject_dir}/{subject}-{condition}-dics-power"

# 10_connectivity.py
# - Compute coherence-based all-to-all connectivity from restricted forward solution and vertex pairs for each condition and frequency band
# - Save output as "{subject_dir}/{subject}-{condition}-connectivity.h5"

# 11_grand_average_power.py
# - Average the power (source) estimates across subjects for each condition, and save as "study_path/MEG/{condition}-average-dics"
# - Compute contrast between face and scrambled relative to baseline, and save as "study_path/MEG/contrast-average-dics" [PLOT 4]

# 12_connectivity_stats.py
# - Average the connectivity across subjects for each condition, and save as "study_path/MEG/{condition}-average-connectivity.h5"
# - Compute contrast between face and scrambled, and save as "study_path/MEG/contrast-average-connectivity.h5"
# - Perform permutation test to guide pruning [PLOT 5] and parcellation [PLOT 6] of the contrast connectivity
# - Save pruned as "study_path/MEG/pruned-average-connectivity.h5"; parcellated as "study_path/MEG/parcellated-average-connectivity.h5"
