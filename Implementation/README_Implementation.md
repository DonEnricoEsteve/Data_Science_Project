## Pipeline Implementation

### Project Description and Goals:
In this part of the project we tried to implement the pipeline of Vliet et al. (2018) and use it to perform source localization and connectivity analyses on data obtained from the MEG-BIU lab. Due to lacking MRI data of the participants the full implementation of the pipeline was difficult and currently unaccomplished. The pipeline was implemented up until cross spectral density matrices computation (including), different additional analyses were included as: time-frequency representation, TFR topo-plots, global field power and power spectral density.

### Data Description:
Each participant from the 42 participants in the study was shown image repetitions. 
There were 18 conditions in the experiment, the images were categorized to 3 main semantic categories (food, positive and neutral), each image was shown twice (1st and 2nd presentation) and in varying lags between the repetitions (short, medium and long).
The participants' brain activity was recorded using a MEG 4D-Neuroimaging system. 
The raw data was preprocessed using Matlab, a low band pass filter of 30 Hz and a high band pass filter of 1Hz were used, artifacts of blinks and heart beats were excluded using ICA. The data was epoched in the time range of -0.3-0.8 s relative to event/stimuli onset. 

The data used in the implementation is:
* Epoched data in a mat file named “datafinalLow”.
* A raw MEG 4D recording for obtaining sensor locations.
* config and hsfile (head shape) accompanying the raw MEG recording.
For two participants from the 42 in the study (could be implemented for more  participants due to a presence of a loop).

The data plus html reports with results for the two participants can be found in the link: https://drive.google.com/drive/folders/1tZth2oi_OlHLtsFPGPjzpmj2g7FsJbw_?usp=sharing

### Repository Structure:
<pre>
Implementation
│   pyproject.toml
│   README_implementation.md
│   test_csd_report.html
│   __init__.py
│
├───src
│   │   add_to_report.py
│   │   config.py
│   │   __init__.py
│   │   __main__.py
│   │
│   ├───analyses
│   │       compute_csd.py
│   │       tfr_psd_analyses.py
│   │       __init__.py
│   │
│   └───mat_to_epochs_conversion
│           combine_epochs.py
│           convert_main_funcs.py
│           create_events_for_epochs.py
│           create_info.py
│           extract_from_dict.py
│           remove_oddball_trials.py
│           __init__.py
│
├───tests
│       input_validation_tests.py
│       output_tests.py
│       test_csd.py
│       __init__.py
│
└───SUBS_DIR
       ├───sample_subject
       │        sub001-baseline-csd.h5
       │        sub001-epo.fif
       │        sub001-face-csd.h5
       │        sub001-scrabled-csd.h5
       ├───subject_003
       │        config
       │        datafinalLow.mat
       │        hs_file
       │        fix_xc,lf_c,rfhp0.1Hz
       └───subject_004
                config
                datafinalLow.mat
                hs_file
                xc,hb,lf_c,rfhp0.1Hz
</pre>

### Implementation Steps:
1. Data conversion from epoched data saved in mat files to mne.EpochsArray using the modules in “mat_to_epochs_conversion” package.
2. Analysing data using the modules in “analyses” package. 
3. Plots were added to a report per subject using “add_to_report.py”.
4. Testing: 
   * specific input and output validation testing was incorporated in the code using the modules in the “tests” package, runtime typechecking is performed using @beartype.
   * Additional testing of the compute_csd function was added as a script under "tests" -> test_csd.py, and was run separately.
     Report for csd computation testing can be found under "Implementation".
        

__Note__: During run, close all figures that are not being automatically closed for run contnuation.

## Project usage

### Installation:
1. Clone the github repository: to your local machine.
2. Install the package dependencies into the virtual environment using: pip install . (optional: pip install .[dev] for further project development).
3. The data being used should be downloaded and located in the project’s directory  in a folder “SUBS_DIR”. Each subject’s data should be stored in a folder inside “SUBS_DIR” starting with “sub” due to pattern searching.
4. The 4 files for each subject (epoched .mat, raw 4D recording, hsfile and config) must exist in every subject's folder with a unique file of each type (due to pattern searching).
5. Run main.py using the following command after installation: python -m src

### Changes for usage on different data:
* config.py variables (inside src package) might need to be changed when using different data and project directory: 
freq_bands, time_frames, event_ids, new_event_ids, contrast combinations, bad_ch_names, channels_number, time_points, oddball_id, baseline_time, post_stim_time, project_directory.

* If the structure of the mat file and the names of the fields are different, changes need to be made in the extract_from_dict function in the module by the same name (change of keys names and heirarchy).

__Note:__ in config.py len(event_ids) should be devisible by len(new_event_ids) with no remanant, being used in combine_epochs to combine every x conditions in event_ids under a single condition in new_event_ids.

__Additional Notes__: 
* The function create_mne_info in create_info module in “mat_to_epochs_conversion” package is a function for manual creation of mne.Info instance, it is not used in main.py. The function can be used in the lack of a raw 4D recording, but then the topo-plots created using “add_to_report.py” need to be omitted due to lacking sensor locations.
Those two functions should be deleted from main.py:

        raw_info = create_info.extract_raw_info(folder)
        output_tests.test_raw_info(raw_info)

And the following function in main should be changed to contain mne_info=None:

epochs, evoked = convert_main_funcs.convert_mat_to_epochs(glob.glob(config.mat_file_path_pattern)[0], mne_info=raw_info) 

* Optional: for testing the compute_csd function in "analyses" against a reliable csd matrix, a folder called "sample_subject" 
should be created in "SUBS_DIR" containing the epochs fif file of the subject and all the CSDs calculated using the replication script/other reliable method, including the baseline CSD. Files of a sample subject for compute_csd testing can be found here: https://drive.google.com/drive/folders/1QPr3ld6anO-PrIGwzGZPpOsHpKLHyaCW

The following in test_csd.py might need to be changed:

<pre>
        package_path = "C:/Projects/food_meg_analyses"
        condition = file.split(f"{config.subs_directory}\\sample_subject\\sub001-")[1].split("-csd")[0]
</pre>

Run test_csd.py as a separate script.
