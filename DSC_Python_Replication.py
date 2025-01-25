# Data Science and Advanced Python Project: Reproduce Published Results
# Don Enrico Esteve (P9550217B) and Elizabeth Vaisman (318775277)
# 01/29/2025

# Code for plotting the replicated results from van Vliet et al. (2018)

# ======================================= #
#  Part 0: File pre- and post-processing
# ======================================= #

# Perform for each subject (subXXX) = "{subject}"
# Setup "study_path/MEG/{subject}" as "{subject_dir}" and "study_path/subjects" as "{subjects_dir}""

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

# ==================== #
#  Part 1: Initialize
# ==================== #

# Import necessary modules
try:
    import mne
    import conpy
    import os
    import matplotlib.pyplot as plt
    from fnames import FileNames
    from mne.time_frequency import read_csd, pick_channels_csd 
    from mne.bem import _fit_sphere

    # Set the logging level to show only error logs
    mne.set_log_level('ERROR')

except ImportError as error_module:
    print(f"There is an error importing a module. {error_module}. Please install it first.")

# Define subject directory
os.environ['SUBJECTS_DIR'] = "/Volumes/Seagate/DSC_Project/DSC_Project/Don/Replicate_Data/subjects"

# Initialize an object 'fname' of class 'Filenames'
try:
    fname = FileNames()
except NameError as e:
     print(f"In fnames.py, class {e}. Hence, there is an error initializing FileNames object")

# Directories for computing CSD matrices
fname.add('epo', 'Replicate_Data/MEG/{subject}/{subject}-epo.fif')
fname.add('csd', 'Replicate_Data/MEG/{subject}/{subject}-{condition}-csd.h5')

# Directories for plotting the source space and forward models
fname.add('fwd', 'Replicate_Data/MEG/{subject}/fsaverage_to_{subject}-meg-ico4-fwd.fif') # recursively subdivided icosahedron 4
fname.add('fwd_r', 'Replicate_Data/MEG/{subject}/{subject}-restricted-meg-ico4-fwd.fif')
fname.add('trans', 'Replicate_Data/ds117/{subject}/MEG/{subject}-trans.fif')

# Directories for computing grand average of cortical power (source) maps 
fname.add('ga_power', 'Replicate_Data/MEG/{condition}-average-dics')

# Directories for computing source-level functional connectivity
fname.add('ga_con', 'Replicate_Data/MEG/{condition}-average-connectivity.h5')

# Map subject key to valid subject number 
map_subjects = {
    'sub001': 'subject_01', 'sub002': 'subject_02', 'sub003': 'subject_03',
    'sub004': 'subject_05', 'sub006': 'subject_08', 'sub007': 'subject_09', 
    'sub008': 'subject_10', 'sub009': 'subject_11', 'sub010': 'subject_12', 
    'sub011': 'subject_14', 'sub012': 'subject_15', 'sub013': 'subject_16', 
    'sub014': 'subject_17', 'sub015': 'subject_18', 'sub017': 'subject_23', 
    'sub018': 'subject_24', 'sub019': 'subject_25',
}

# Define subjects for analyses
subjects = [s for s in sorted(map_subjects.keys())]

# Define frequency bands of interest
freq_bands = [
    (3, 7),     # theta
    (7, 13),    # alpha
    (13, 17),   # low beta
    (17, 25),   # high beta 1
    (25, 31),   # high beta 2
    (31, 40),   # low gamma
]

# ========================================================== #
#  Part 2: Estimating cross-spectral density (CSD) matrices
# ========================================================== #

# Function for plotting CSD matrices
def plot_csd_matrices(sub_idx, cond, mode_val='csd', meg_val="grad"):
    """
    Function that plots the cross-spectral density (CSD) matrices. 

    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively.
    cond (str): The condition to be analyzed. Must be either "face" or "scrambled"
    mode_val (str): Whether to plot the cross-spectral density (csd, the default), or the coherence (coh) between the channels.
    meg_val (str): Optional argument. The type of sensors to be used. Default is "grad".

    Returns: A 2x3 plot containing CSD plots for each frequency band. 
    CSDs are measured in femtoTesla squared over centimeter squared.
    """

    # Read an mne.Info object from an epoched .fif file. Contains information about the sensors and methods of measurement
    try:
        info = mne.io.read_info(fname.epo(subject=subjects[sub_idx]))
    except AttributeError:
        print("Error running 'mne.io.read_info()' because the key or/and directory for fname.add('epo', 'directory') is/are wrong.")
    except IndexError:
        print("Error running 'mne.io.read_info()' because the subject index exceeds 16.")

    # Create a list called 'grads' that contain the channel names of type 'meg_val'.
    try:
        grads = [info['ch_names'][ch] for ch in mne.pick_types(info, meg=meg_val)]
    except ValueError as e:
        print(f"The variable named 'grads' was not defined properly. {e}")

    # Read a CrossSpectralDensity object from an HDF5 file
    try:
        csd = read_csd(fname.csd(subject=subjects[sub_idx], condition=cond))
    except AttributeError:
        print("Error running 'read_csd()' because the key or/and directory for fname.add('csd', 'directory') is/are wrong.")

    # Pick channels from the CSD matrix
    try:
        csd = pick_channels_csd(csd, grads)
    except UnboundLocalError:
        print("The variable 'grads' was not defined properly. Check your input for the 'meg_val' field.")
    
    # Plot matrices
    if mode_val=='coh':
        # Plot the COH for all 6 frequency bands
        csd_all = csd.mean([f[0] for f in freq_bands], [f[1] for f in freq_bands])
        csd_all.plot(info, mode=mode_val)

    else:
        # Plot the CSD for the first 3 frequency bands
        csd_top = csd.mean([f[0] for f in freq_bands[:3]], [f[1] for f in freq_bands[:3]])
        csd_top.plot(info, mode=mode_val, n_cols=3, show=False)

        # Plot the CSD for the last 3 frequency bands
        csd_bot = csd.mean([f[0] for f in freq_bands[3:]], [f[1] for f in freq_bands[3:]])
        csd_bot.plot(info, mode=mode_val, n_cols=3, show=False)

# Plot CSD matrices for each frequency band of each condition for a given subject
plot_csd_matrices(sub_idx=0, cond="face", mode_val='coh', meg_val="grad")
plot_csd_matrices(sub_idx=0, cond="scrambled", mode_val='coh', meg_val="grad")

# =========================== #
#  Part 3: Plot source space
# =========================== #

# Function for plotting the source space
def plot_source_space(sub_idx, meg_val='sensors', surface_val='white'):
    """
    Function that plots the source space of each subject.
    The blue squares around the gray brain (head) model represent the sensors (magnetometers and gradiometers).
    The yellow dots within the brain (head) model represent the dipoles (source of currents).

    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively.
    meg_val (str): Optional argument. The type of sensors to be used. Default is "grad".
    surface_val (str): Optional argument.

    Returns: A PyVistaFigure object showing the 3D source space of a subject.
    """
    
    # Read two forward solutions (or lead fields)
    # The variable fwd and fwd_r differs in that the latter is restricted to the same vertices of the first subject 
    try:
        fwd = mne.read_forward_solution(fname.fwd(subject=subjects[sub_idx]))       # Used for cortical power mapping
        fwd_r = mne.read_forward_solution(fname.fwd_r(subject=subjects[sub_idx]))   # Used for connectivity analyses
    except AttributeError: 
        print("Error running 'mne.io.read_forward_solution()' because the key or/and directory for fname.add('fwd', 'directory') and fname.add('fwd_r', 'directory') is/are wrong.")
    except IndexError:
        print("Error running 'mne.io.read_forward_solution()' because the subject index exceeds 16.")

    # Load subject-specific transformation file that was produced during coregistration (Head <-> MRI transform)
    try:
        trans = fname.trans(subject=subjects[sub_idx])
    except AttributeError:
        print("The variable 'trans' is not defined properly because the key or/and directory for fname.add('trans', 'directory') is/are wrong.")
    except IndexError:
        print("Error as the subject index exceeds 16.")
    
    # Plot head, sensor, and source space alignment in 3D
    try:
        sourcespace = mne.viz.plot_alignment(fwd['info'], trans=trans, src=fwd_r['src'], meg=meg_val, surfaces=surface_val)
        return sourcespace.plotter.set_background('white')
    except ValueError as e:
        print(f"The PyVistaFigure object named 'fig' was not defined properly due to: {e}")

# Plot source space of a given subject
plot_source_space(sub_idx=0, meg_val="sensors", surface_val="white")

# Function to plot the forward model for a given subject
def plot_forward_model(sub_idx):
    """
    Plots the 3D forward model for the given subject index.

    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively.
    
    Returns: A Matplotlib object showing the 3D forward model of a subject.
    """
    
    # Read the forward solution for the subject using MNE
    try:
        fwd_r = mne.read_forward_solution(fname.fwd_r(subject=subjects[sub_idx])) 
    except AttributeError:
        print("Error running 'mne.read_forward_solution()' because the key or/and directory for fname.add('fwd_r', 'directory') is/are wrong.")
    except IndexError:
        print("Error running 'mne.read_forward_solution()' because the subject index exceeds 16.")
    else:
        # Fit a sphere to the source points and get the center
        _, center = _fit_sphere(fwd_r['source_rr'])
        
        # Calculate the radial coordinate system components (tan1, tan2)
        _, tan1, tan2 = conpy.forward._make_radial_coord_system(fwd_r['source_rr'], center)

        # Extract the source points (locations of the sources in 3D)
        source_rr = fwd_r['source_rr']

        # Create a figure for 3D plotting
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot the first tangential direction (black arrows)
        # 'tan1' represents the first tangential direction
        ax.quiver(source_rr[:, 0], source_rr[:, 1], source_rr[:, 2],
                tan1[:, 0], tan1[:, 1], tan1[:, 2], color='k', length=0.003, linewidth=0.5, label="Tangential direction 1")

        # Plot the second tangential direction (blue arrows)
        # 'tan2' represents the second tangential direction
        ax.quiver(source_rr[:, 0], source_rr[:, 1], source_rr[:, 2],
                tan2[:, 0], tan2[:, 1], tan2[:, 2], color='b', length=0.003, linewidth=0.5, label="Tangential direction 2")

        # Set the labels for the axes
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        
        # Set the title for the plot
        ax.set_title('Forward Model (Leadfield)')
        
        # Display the legend in the plot
        ax.legend()

        # Remove the axes lines for a cleaner visualization
        ax.set_axis_off()

        # Show the 3D plot
        plt.show()

# Plot forward model of a given subject
plot_forward_model(sub_idx=0)

# ========================================================= #
#  Part 4: Plot grand average cortical power (source) maps
# ========================================================= #

def plot_grandavg_power(cond='contrast', views_val="med", hemi_val="split"):
    """
    Function that plots the grand averaged (across subjects) cortical power maps of each condition
     
    Parameters:
    cond (str): The condition to be analyzed. Must be either "face", "scrambled", or 'contrast'. Default is 'contrast'.
    views_val (str): Optional argument. The view to display the cortical power map. Default is "dorsal".
    hemi_val (str): Optional argument. The hemisphere to display. Default is "split".

    Returns: The average cortical power map (alpha band) for a given condition across subjects.
    """

    # Load the grand average power maps
    try:
        stc_cond = mne.read_source_estimate(fname.ga_power(condition=cond))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error loading power map: {e}")

    # Show absolute power for the given condition
    try:
        # Subject input only for anatomy (surf_inflated_lh)
        stc_cond.plot(subject='sub002', views=views_val, hemi=hemi_val, background='white', 
                      foreground='black', time_label='', initial_time=1)
    except Exception as e:
        print(f"Error while plotting {stc_cond} power map: {e}")

plot_grandavg_power(cond='contrast', views_val="lateral", hemi_val="split")

# ================================================= #
#  Part 5: Plot results from connectivity analysis
# ================================================= #

def plot_connectivity_contrast(summary_val='degree', hemi_val='both'):
    """
    Function that plots two images for functional connectivity of the contrast condition.
    The degree map shows, for each source point, the percentage of connections that survived the statistical threshold and clustering operations.
    The circular connectogram shows the number of connections between each parcel (defined from aparc atlas).

    Parameters:
    summary_val (str): Optional argument. Method of summarizing the adjacency data to instantiate the SourceEstimate object. Default is "degree".
    hemi_val (str): Optional argument. The hemisphere to display. Default is "split".

    Returns:
    1. A SourceEstimate object that is the degree map
    2. Circular connectogram
    """

    # Read the connectivity estimates
    try:
        con = conpy.read_connectivity(fname.ga_con(condition='pruned'))
        con_parc = conpy.read_connectivity(fname.ga_con(condition='parcelled'))
    except AttributeError:
        print("Error running conpy.read_connectivity() because the key or/and directory for fname.add('ga_con', 'directory') is/are wrong.")

    # Obtain a summary of the connectivity as a SourceEstimate object
    try:
        stc = con.make_stc(summary=summary_val, weight_by_degree=False)
    except ValueError as e:
        print(f"{e}")
    
    # Plot degree map
    try:
        brain = stc.plot(subject='fsaverage', hemi=hemi_val, background='white', foreground='black', 
                         time_label='', initial_time=1)
        brain.add_annotation('aparc', borders=2)
    except ValueError as e:
        print(f"{e}")
    except UnboundLocalError:
        print("The variable 'stc' was not defined properly. Check your input for the 'summary' field.")

    # Plot circular connectogram
    try:
        con_parc.plot(title='Parcel-wise Connectivity (Circular Connectogram)', facecolor='white', textcolor='black', node_edgecolor='white', colormap='plasma_r', vmin=0, show=False)
    except UnboundLocalError:
        print("The variable 'con_parc' was not defined properly.")

# Plot connectivity results
plot_connectivity_contrast(summary_val="absmax", hemi_val="split")