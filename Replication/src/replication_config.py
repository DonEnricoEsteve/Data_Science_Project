# Define necessary module(s)
import os

# Define as the root directory (Replication) which contains both data and src directories
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Set location of surf files for source visualization
os.environ["SUBJECTS_DIR"] = os.path.join(base_dir, 'data', 'templates')

# Directories for plotting CSD matrices
epo_path = os.path.join(base_dir, 'data', 'csd', '{subject}-epo.fif')
csd_path = os.path.join(base_dir, 'data', 'csd', '{subject}-{condition}-csd.h5')

# Directories for plotting the source space and forward models
fwd_path = os.path.join(base_dir, 'data', 'source_models', 'fsaverage_to_{subject}-meg-ico4-fwd.fif')
fwd_r_path = os.path.join(base_dir, 'data', 'source_models', '{subject}-restricted-meg-ico4-fwd.fif')
trans_path = os.path.join(base_dir, 'data', 'source_models', '{subject}-trans.fif')

# Directories for plotting grand average of cortical power (source) maps
ga_power_path = os.path.join(base_dir, 'data', 'power', '{condition}-average-dics')

# Directories for plotting source-level functional connectivity
ga_con_path = os.path.join(base_dir, 'data', 'connectivity', '{condition}-average-connectivity.h5')

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
