# Data Science and Advanced Python Project: Reproduce Published Results
# Don Enrico Esteve (P9550217B) and Elizabeth Vaisman (318775277)
# 01/29/2025

# Code for plotting the replicated results from van Vliet et al. (2018)

# ==================== #
#  Part 1: Initialize
# ==================== #

# Import necessary modules
try:
    import mne
    import conpy
    import matplotlib.pyplot as plt
    from mne.time_frequency import read_csd, pick_channels_csd 
    from mne.bem import _fit_sphere

    # Dedicated python scripts
    from replication_config import *

    # Set the logging level to show only error logs
    mne.set_log_level('ERROR')

except ImportError as e:
    print(f"There is an error importing a module. {e}. Please install it first.")


# ========================================================== #
#  Part 2: Estimating cross-spectral density (CSD) matrices
# ========================================================== #

def plot_csd_matrices(cond, sub_idx=0, mode_val='csd', meg_val="grad"):
    """
    Function that plots the cross-spectral density (CSD) matrices. 

    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively. 
    Default is the first subject (0), as it is the only file uploaded in GitHub.

    cond (str): The condition to be analyzed. Must be either "face", "scrambled", or "baseline".
    mode_val (str): Whether to plot the cross-spectral density (csd, the default), or the coherence (coh) between the channels.
    meg_val (str): Optional argument. The type of sensors to be used. Default is "grad".

    Returns: A 2x3 plot containing CSD plots for each frequency band. 
    CSDs are measured in femtoTesla squared over centimeter squared.
    """
    
    # Check if the condition is valid
    valid_conditions = ["face", "scrambled", "baseline"]
    if cond not in valid_conditions:
        raise ValueError(f"Invalid condition: {cond}. Valid conditions are {valid_conditions}.")

    # Ensure the subject index is valid
    if sub_idx < 0 or sub_idx >= len(subjects):
        raise IndexError(f"Subject index {sub_idx} is out of range. Valid indices are from 0 to {len(subjects)-1}.")

    try:
        # Read an mne.Info object from an epoched .fif file. Contains information about the sensors and methods of measurement
        info = mne.io.read_info(epo_path.format(subject=subjects[sub_idx]))
    except (AttributeError, IndexError) as e:
        raise RuntimeError(f"Error in reading .fif file: {e}")

    # Check if mode_val is valid
    if mode_val not in ['csd', 'coh']:
        raise ValueError(f"Invalid mode_val: {mode_val}. It must be either 'csd' or 'coh'.")
    
    # Check if meg_val is valid
    if meg_val not in ['grad', 'mag']:
        raise ValueError(f"Invalid meg_val: {meg_val}. It must be either 'grad' or 'mag'.")

    try:
        # Create a list called 'grads' that contain the channel names of type 'meg_val'.
        grads = [info['ch_names'][ch] for ch in mne.pick_types(info, meg=meg_val)]
    except ValueError as e:
        raise ValueError(f"Error in picking channels: {e}")

    try:
        # Read a CrossSpectralDensity object from an HDF5 file
        csd = read_csd(csd_path.format(subject=subjects[sub_idx], condition=cond))
    except AttributeError as e:
        raise RuntimeError(f"Error reading CSD: {e}")
    except OSError as e:
        raise FileNotFoundError(f"File not found: {e}")

    try:
        # Pick channels from the CSD matrix
        csd = pick_channels_csd(csd, grads)
    except UnboundLocalError:
        raise RuntimeError("The variable 'grads' was not defined properly.")

    # Plot matrices
    try:
        if mode_val == 'coh':
            # Plot the COH for all 6 frequency bands
            csd_all = csd.mean([f[0] for f in freq_bands], [f[1] for f in freq_bands])
            csd_all.plot(info, mode=mode_val)

        else:
            # Plot the CSD for the first 3 frequency bands 
            csd_top = csd.mean([f[0] for f in freq_bands[:3]], [f[1] for f in freq_bands[:3]])
            csd_top.plot(info, mode=mode_val, n_cols=3, show=False)

            # Plot the CSD for the last 3 frequency bands (separated from first 3 bands to see difference in scale)
            csd_bot = csd.mean([f[0] for f in freq_bands[3:]], [f[1] for f in freq_bands[3:]])
            csd_bot.plot(info, mode=mode_val, n_cols=3, show=False)
    except UnboundLocalError as e:
        raise RuntimeError(f"Error while plotting: {e}")

# ============================================ #
#  Part 3: Plot source estimation ingredients
# ============================================ #

# Function for plotting the source space
def plot_source_space(sub_idx=0, meg_val='sensors', surface_val='white'):
    """
    Function that plots the source space of each subject.
    The blue squares around the gray brain (head) model represent the sensors (magnetometers and gradiometers).
    The yellow dots within the brain (head) model represent the dipoles (source of currents).

    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively. 
    Default is the first subject (0), as it is the only file uploaded in GitHub.

    meg_val (str): Optional argument. The type of sensors to be used. Default is "sensors".
    surface_val (str): Optional argument.

    Returns: A PyVistaFigure object showing the 3D source space of a subject.
    """
    
    # Read two forward solutions (or lead fields)
    # The variable fwd and fwd_r differs in that the latter is restricted to the same vertices of the first subject 
    try:
        fwd = mne.read_forward_solution(fwd_path.format(subject=subjects[sub_idx]))  # Used for cortical power mapping
        fwd_r = mne.read_forward_solution(fwd_r_path.format(subject=subjects[sub_idx]))  # Used for connectivity analyses
    except IndexError:
        raise IndexError(f"Subject index {sub_idx} is out of range. Valid indices are from 0 to {len(subjects) - 1}.")
    except (AttributeError, ValueError) as e:
        raise RuntimeError(f"Error reading forward solutions: {e}")

    # Load subject-specific transformation file that was produced during coregistration (Head <-> MRI transform)
    try:
        trans = trans_path.format(subject=subjects[sub_idx])
    except (AttributeError, IndexError) as e:
        raise RuntimeError(f"Error loading transformation file: {e}")
    
    # Plot head, sensor, and source space alignment in 3D
    try:
        sourcespace = mne.viz.plot_alignment(fwd['info'], trans=trans, src=fwd_r['src'], meg=meg_val, surfaces=surface_val)
        return sourcespace.plotter.set_background('white')
    except ValueError as e:
        raise RuntimeError(f"Error plotting source space: {e}")

# Function to plot the forward model for a given subject
def plot_forward_model(sub_idx=0):
    """
    Plots the 3D forward model for the given subject index.
    
    Parameters:
    sub_idx (int): The index of the subject to be analyzed. Ranges from 0 to 16 for subjects 1 to 17, respectively.
    Default is the first subject (0), as it is the only file uploaded in GitHub.
    
    Returns: A Matplotlib object showing the 3D forward model of a subject.
    """
    
    # Read the forward solution for the subject using MNE
    try:
        fwd_r = mne.read_forward_solution(fwd_r_path.format(subject=subjects[sub_idx])) 
    except AttributeError:
        raise RuntimeError("Error running 'mne.read_forward_solution()' because the key or/and directory for fname.add('fwd_r', 'directory') is/are wrong.")
    except IndexError:
        raise IndexError("Error running 'mne.read_forward_solution()' because the subject index exceeds 16.")
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
        ax.quiver(source_rr[:, 0], source_rr[:, 1], source_rr[:, 2],
                tan1[:, 0], tan1[:, 1], tan1[:, 2], color='k', length=0.003, linewidth=0.5, label="Tangential direction 1")

        # Plot the second tangential direction (blue arrows)
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

    # Check if the condition is valid
    valid_conditions = ["face", "scrambled", "contrast"]
    if cond not in valid_conditions:
        raise ValueError(f"Invalid condition: {cond}. Valid conditions are {valid_conditions}.")

    # Load the grand average power maps
    try:
        stc_cond = mne.read_source_estimate(ga_power_path.format(condition=cond))
    except (FileNotFoundError, OSError) as e:
        raise OSError(f"Error loading power map: {e}")

    # Show absolute power for the given condition
    try:
        # Subject input only for anatomy (surf_inflated_lh)
        stc_cond.plot(subject='sub001', views=views_val, hemi=hemi_val, background='white', 
                      foreground='black', time_label='', initial_time=1)
    except Exception as e:
        raise RuntimeError(f"Error while plotting {stc_cond} power map: {e}")

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
        con = conpy.read_connectivity(ga_con_path.format(condition='pruned'))
        con_parc = conpy.read_connectivity(ga_con_path.format(condition='parcelled'))
    except AttributeError:
        raise FileNotFoundError("Error running conpy.read_connectivity() because the key or/and directory for 'ga_con' is/are wrong.")
    
    # Obtain a summary of the connectivity as a SourceEstimate object
    try:
        stc = con.make_stc(summary=summary_val, weight_by_degree=False)
    except ValueError as e:
        raise ValueError(f"Error generating SourceEstimate for summary value '{summary_val}': {e}")
    
    # Plot degree map
    try:
        brain = stc.plot(subject='fsaverage', hemi=hemi_val, background='white', foreground='black', 
                         time_label='', initial_time=1)
        brain.add_annotation('aparc', borders=2)
    except ValueError as e:
        raise ValueError(f"Error plotting degree map: {e}")
    except UnboundLocalError:
        raise RuntimeError("The variable 'stc' was not defined properly. Check your input for the 'summary' field.")
    
    # Plot circular connectogram
    try:
        con_parc.plot(title='Parcel-wise Connectivity (Circular Connectogram)', facecolor='white', textcolor='black', node_edgecolor='white', colormap='plasma_r', vmin=0, show=False)
    except UnboundLocalError:
        raise RuntimeError("The variable 'con_parc' was not defined properly.")