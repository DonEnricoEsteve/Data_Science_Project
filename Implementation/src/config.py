
freq_bands = [
        (3, 7),     # theta
        (7, 13),    # alpha
        (13, 17),   # low beta
        (17, 25),   # high beta 1
        (25, 31),   # high beta 2
    ]

# time ranges for topo-plot plotting purposes only
time_frames = [
    (0.0, 0.15),
    (0.15, 0.3),
    (0.3, 0.5),
    (0.5, 0.8),
]

# Define event_ids mapping with the name of condition and the integer id of the condition as defined in the.mat file
event_ids = {
    "food/short/rep1": 10, "food/medium/rep1": 12, "food/long/rep1": 14, 
    "food/short/rep2": 20, "food/medium/rep2": 22, "food/long/rep2": 24,
    "positive/short/rep1": 110, "positive/medium/rep1": 112, "positive/long/rep1": 114,
    "positive/short/rep2": 120, "positive/medium/rep2": 122, "positive/long/rep2": 124,
    "neutral/short/rep1": 210, "neutral/medium/rep1": 212, "neutral/long/rep1": 214,
    "neutral/short/rep2": 220, "neutral/medium/rep2": 222, "neutral/long/rep2": 224
}

# event_ids for combining epochs under those conditions (disregarding the lag), defined with new integer ids
new_event_ids = {"food_1": 1 , "food_2": 2, "positive_1": 3, "positive_2": 4, "neutral_1": 5, "neutral_2": 6}

# Define combination of conditions for contrating TFRs
pres_1 = ['food_1', 'positive_1', 'neutral_1']
pres_2 = ['food_2', 'positive_2', 'neutral_2']
food = ['food_1', 'food_2']
positive = ['positive_1', 'positive_2']
neutral = ['neutral_1', 'neutral_2']
nonfood = ['positive_1', 'positive_2', 'neutral_1', 'neutral_2']
nonfood_1 = ['positive_1', 'neutral_1']
nonfood_2 = ['positive_2', 'neutral_2']

#bad + reference channel names
bad_ch_names = ['A17','A203','TRIGGER','RESPONSE','MLzA','MLyA','MLzaA','MLyaA','MLxA','MLxaA','MRzA','MRxA','MRzaA','MRxaA','MRyA',
                'MCzA','MRyaA','MCzaA','MCyA','GzxA','MCyaA','MCxA','MCxaA','GyyA','GzyA','GxxA','GyxA','UACurrent','X1','X3','X5','X2','X4','X6']

# Data specific parameters:

channels_number = 246 #number of good data sensors

time_points = 1119 # number of time points in each event

oddball_id = 8 # the id of the oddball stimulus condition

baseline_time = (-0.3, 0.0)

post_stim_time = (0.0, 0.8)

# Paths for file accessing and results saving:

project_directory = "C:/Projects/Data_Science_Project/Implementation" 

subs_directory = f"{project_directory}/SUBS_DIR"

subject_directory_pattern = f"{subs_directory}/sub*"

mat_file_path_pattern = f"*.mat"

html_report_path = f"report.html"

h5_report_path = f"report.h5"

epochs_path = "orig_epo.fif"

epochs_combined_path = "combined_epo.fif"

evoked_path = "evo.fif"

psd_path = "psd.h5"

def get_tfr_contrast_path(con1, con2):
    evoked_tfr_contrast_path = f"evoked_tfr_{con1[0]}-{con2[0]}.h5"
    return evoked_tfr_contrast_path

def get_csd_path(condition):
    csd_path = f"csd_{condition}.h5"
    return csd_path

def get_csd_mean_path(condition):
    csd_mean_path = f"csd_mean_{condition}.h5"
    return csd_mean_path 

# Titles and sections for reporting purposes of results:

def get_report_titles(condition=None, contrast=None, fmin=None, fmax=None, tmin=None, tmax=None):
    report_titles = {'csd': f"CSD matrices for {condition}", 'csd_mean': f"CSD mean matrices for {condition}", 'coherence': f"Coherence mean matrices for {condition}", 
                    'tfr_contrast': f'Time-frequency representation for{contrast}', 'general_topoplots':f"across time topo-plots averaged for all conditions", 'gfp': f"Global Field Power",
                    'psd': 'Power Spectral Density for Evoked', 'tfr_contrast_topoplots':f"TFR Contrast Topoplot({contrast}, {fmin}-{fmax}Hz, {tmin}-{tmax}s)"}
    return report_titles

def get_report_sections(subject_num):
    report_sections = {'csd': f"{subject_num}/CSD", 'coherence': f"{subject_num}/Coherence", 'tfr_contrast':f"{subject_num}/TFR contrast", 
                    'tfr_contrast_topoplots':f"{subject_num}/TFR Contrast Topoplots", 'gfp': f"{subject_num}/GFP", 'psd': f"{subject_num}/PSD"}
    return report_sections