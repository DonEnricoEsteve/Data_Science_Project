
freq_bands = [
        (3, 7),     # theta
        (7, 13),    # alpha
        (13, 17),   # low beta
        (17, 25),   # high beta 1
        (25, 31),   # high beta 2
    ]

time_frames = [
    (0, 0.15)
    (0.15, 0.3)
    (0.3, 0.5)
    (0.5, 0.8)

]
# Define event_ids mapping
event_ids = {
    "food/short/rep1": 10, "food/medium/rep1": 12, "food/long/rep1": 14, 
    "food/short/rep2": 20, "food/medium/rep2": 22, "food/long/rep2": 24,
    "positive/short/rep1": 110, "positive/medium/rep1": 112, "positive/long/rep1": 114,
    "positive/short/rep2": 120, "positive/medium/rep2": 122, "positive/long/rep2": 124,
    "neutral/short/rep1": 210, "neutral/medium/rep1": 212, "neutral/long/rep1": 214,
    "neutral/short/rep2": 220, "neutral/medium/rep2": 222, "neutral/long/rep2": 224
}

new_event_ids = {"food_1": 1 , "food_2": 2, "positive_1": 3, "positive_2": 4, "neutral_1": 5, "neutral_2": 6}

# Define combination of conditions
pres_1 = ['food_1', 'positive_1', 'neutral_1']
pres_2 = ['food_2', 'positive_2', 'neutral_2']
food = ['food_1', 'food_2']
positive = ['positive_1', 'positive_2']
neutral = ['neutral_1', 'neutral_2']
nonfood = ['positive_1', 'positive_2', 'neutral_1', 'neutral_2']
nonfood_1 = ['positive_1', 'neutral_1']
nonfood_2 = ['positive_2', 'neutral_2']

oddball_id = 8

baseline_time = (-0.3, 0)

post_stim_time = (0, 0.8)

project_directory = "C:/Users/eliza/Documents/DS_project"

subs_directory = f"{project_directory}/SUBS_DIR"

subject_directory_pattern = f"{subs_directory}/sub*"

mat_file_path_pattern = f"*.mat"

html_report_path = f"report.html"

h5_report_path = f"report.h5"
