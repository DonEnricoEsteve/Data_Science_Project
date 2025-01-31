# Run the functions in plot_replicated_files.py

# Import necessary modules
try:
    from plot_replicated_files import *

except ImportError as e:
    print(f"There is an error importing a module. {e}. Please install it first.")

# Plot cross-spectral density matrices for each frequency band of each condition for a given subject
plot_csd_matrices(sub_idx=0, cond="face", mode_val='csd', meg_val="grad")

# Plot coherence matrices for each frequency band of each condition for a given subject
plot_csd_matrices(sub_idx=0, cond="scrambled", mode_val='coh', meg_val="grad")

# Plot source space of a given subject
plot_source_space(sub_idx=0, meg_val="sensors", surface_val="white")

# Plot forward model of a given subject
plot_forward_model(sub_idx=0)

# Plot grand average cortical power map of the contrast condition (face-scrambled) / baseline for the alpha band
plot_grandavg_power(cond='contrast', views_val="lateral", hemi_val="split")

# Plot connectivity results
plot_connectivity_contrast(summary_val="absmax", hemi_val="split")