"""

Itterate over all subjects folders, convert mat files of epoched data to EpochsArray instances, combine epochs
to the desired conditions and save the two epochs arrays to fif files.
Analyse epochs_combined data using CSD, TFR, GFP, PSD and topo plots. 

Subjects foldes must contain only one mat file that contains the epoched data and one raw MEG bti recording.

"""
"""importations of libraries"""

if __name__ == "__main__":

    try:
        import sys
        import os 
        import numpy as np
        import mne, glob, warnings, traceback
        from mne.time_frequency import csd_morlet, read_spectrum, read_csd, read_tfrs
        from pymatreader import read_mat
        from src import config
        from mat_to_epochs_conversion import convert_main_funcs, combine_epochs, create_info # using * didn't work for some reason
        from analyses import compute_csd, tfr_psd_analyses
        import add_to_report
        from tests import output_tests, input_validation_tests
    
    except Exception as e:
        print("problem with modules importation in __main__.py")

    try:
        print("Start of script run")
        package_path = config.project_directory
        if os.path.exists(package_path):
            if package_path not in sys.path:
                sys.path.insert(0, package_path)
        else:
            raise FileNotFoundError(f"The path {package_path} doesn't exist")

        if not os.path.exists(config.subs_directory):
            raise FileNotFoundError(f"The path {config.subs_directory} doesn't exist")

        directory_pattern = config.subject_directory_pattern # directory pattern for itterating over subject folders


        
        # itterate over all subjects folders
        for folder in glob.iglob(directory_pattern): 


            if os.path.exists(folder): # the subject folder that contains the mat file with epoched data and the raw MEG recordings per subject

                try:  
                    
                    # extract subject number from the name of the folder:
                    subject_num = folder.split("SUBS_DIR\\", 1)[1]


                    os.chdir(folder)

                    raw_info = create_info.extract_raw_info(folder)
                    output_tests.test_raw_info(raw_info)

                    
                    # recieves a file path to the mat file, glob.glob returns a list of all paths found with the pattern.
                    # [0] for returning the first and only element in the list.
                    epochs, evoked = convert_main_funcs.convert_mat_to_epochs(glob.glob(config.mat_file_path_pattern)[0], mne_info=raw_info) 
                    
                    # combine epochs by new conditions (new_event_ids):
                    epochs_combined = combine_epochs(epochs, config.event_ids, config.new_event_ids)
                    output_tests.test_epochs_combined(epochs_combined)

                    # extract conditions for csd cmputation per condition:
                    conditions =  list(epochs_combined.event_id.keys())

                    # Suppress warning about wavelet length.

                    for condition in conditions:

                        # csd calculation post stimulus over the desired frequency range per condition, save and add to report
                        csd, csd_mean = compute_csd.compute_csd(epochs_combined, condition, config.freq_bands, config.post_stim_time) 
                        output_tests.test_csd(csd)
                        output_tests.test_csd(csd_mean)

                    # csd calculation of baseline over the desired frequency range, save and add to report. (calculates csd baseline for the last 
                    # condition in loop, we assume that all conditions have same baseline activity)
                    csd_baseline, csd_baseline_mean = compute_csd.compute_csd(epochs, condition, config.freq_bands, config.baseline_time, is_base_line=True)
                    output_tests.test_csd(csd_baseline)
                    output_tests.test_csd(csd_baseline_mean)
                    
                    # compute tfrs for desired contrast of conditions, over the frequencies in freqs and save:
                    freqs = np.arange(8, 24, 2)
                    
                    tfr_pres = tfr_psd_analyses.compute_tfr_contrast(epochs=epochs, freqs=freqs, con1=('pres_1', config.pres_1), 
                    con2=('pres_2', config.pres_2))
                    output_tests.test_tfr(tfr_pres, freqs)


                    tfr_food = tfr_psd_analyses.compute_tfr_contrast(epochs=epochs,  freqs=freqs, con1=('food',config.food), 
                    con2=('nonfood',config.nonfood))
                    output_tests.test_tfr(tfr_food, freqs)

                    # compute psd (power spectral density) over the desired frequencies, times and channels:
                    psd =  tfr_psd_analyses.compute_psd(evoked_instance=evoked, fmin=config.freq_bands[0][0], fmax=config.freq_bands[-1][-1], tmin=config.baseline_time[0], tmax=config.post_stim_time[1], picks='meg')
                    output_tests.test_psd(psd)

                    report = mne.Report(title=f"report for {subject_num}")
                    
                    # add plots of the above computations to a report of the subject:
                    add_to_report.add_to_report(report, subject_num)

                    # save the report with added plots to h5 (if the report needs to be changed later) and to html (for report viewing):
                    report.save(config.h5_report_path, overwrite=True)
                    report.save(config.html_report_path, overwrite=True)

                except Exception as e:
                    print("An error occured:", e)
                    traceback.print_exc()


            else:
                raise FileNotFoundError(f"The path {folder} doesn't exist")

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
    print("Run finished")

