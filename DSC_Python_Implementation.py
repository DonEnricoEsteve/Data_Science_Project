"""importations of libraries"""

try:   
    import numpy as np
    import os
    import mne
    import glob
    from config import *
    import warnings
    from mne.time_frequency import csd_morlet
    import traceback
    from pymatreader import read_mat

# in case one of the modules is not installed or can not be found by python using the system variables:
except ModuleNotFoundError as e :
    print(" An error occured:", e)


class EmptyVariable(Exception):
    """
    Exception raised for an error when an empty variabe that is supposed to have some value is detected .
    recieves the variable name (str) and the message (str) to be printed.
    
    """
    # variable name is optional
    def __init__(self, message: str, variable_name=None):
        super().__init__(message)
        self.variable = variable_name
        self.message = message

    def __str__(self):
        # message returned in case a variable name is given by user and otherwise
        if self.variable==None:
            return f"{self.message}"
        else:
            return f"{self.message} (Variable: {self.variable})" 
        

def convert_mat_to_dict(file_name: os.PathLike):

    """
    
    Recieves:
    * file_name: path to mat file for conversion. 
    
    Function:
    * Converts mat files from v. 7.3 to dictionaries and deals with possible exceptions.

    Returns: 
    * dict_from_mat: dictionary (if conversion was not successful, an exception occured, dict_from_mat = {})

    Notes:
    * For the following code to work the mat file should include epoched data.
        
    """
        
    try:
        # using read_mat from pymatreader module, convert a v. 7.3 mat file to a dictionary
        dict_from_mat = read_mat(file_name)

    except NameError as e:
        print(" An error occured:", e)

    except FileNotFoundError as e:
        print(" An error occured:", e)

    except OSError as e:
        print(" An error occured:", e)
    
    except PermissionError as e:
        print(" An error occured:", e)

    except Exception as e:
        print(" An error occured:", e)
        traceback.print_exc()
        
    # finally returns dict_mat, if dict_mat doesn't exist (fail in conversion), return an empty dictionary
    finally:
        if 'dict_from_mat' not in locals(): 
            dict_from_mat = {}
        return dict_from_mat


def remove_oddball_trials(data: np.ndarray, events_code: np.ndarray, oddball_id: int):

    """ 
    
    Recieves:
    * data: numpy ndarray, shape (trials, channels, time points).
    * events_code: numpy ndarray of type int, shape (1, trials), contains unique code for each stimuls.
    * odball_id: integer, code of the odball stimulus.

    Function:
    * Removes all trials coressponding to oddball stimulus id.

    Reutrns:
    * data: numpy ndarray shape (trials, channels, time points), after oddball trial removal.
    * events_code: numpy ndarray of type int, shape (1, trials), after oddball id removal.
    
    """
    
    try:
        # check if the events_code length matches the number of trials in the data:
        if not len(data) == len(events_code):
            raise ValueError ("The number of trials in data is not equal to the number of trials in events_code")
        
        oddball_idx = np.where(events_code == oddball_id)[0]  # using [0] to extract the indices array of the oddball stimulus,
        # those are the indices of the trials in data corresponding to the oddball stimulus

        # because odball stimuli are expected to appear in the events_code array, raise an error of EmptyVariable
        if len(oddball_idx) == 0:
            print("no odball stimuli were found")
            raise EmptyVariable("an empty variable was detected", 'oddball_idx') 

        # Remove odball code from events_code + oddball trials from data
        events_code_removed = np.delete(events_code, oddball_idx)
        data_removed = np.delete(data, oddball_idx, axis=0)  # axis=0 --> remove odball from data rows (trials)
    
    except ValueError as e:
        print(" An error occured:", e) 

    except TypeError as e:
        print(" An error occured:", e) 

    except EmptyVariable as e:
        print(" An error occured:", e) 

    except Exception as e:
         print(" An error occured:", e)

    # finally return data_removed, if data_removed doesn't exist (an exception occured during the process), return an empty ndarray
    finally:
        if 'data_removed' not in locals():
            data_removed = np.empty(0)
        return data_removed, events_code_removed


def extract_from_dict(sub_dict: dict):
 
    """
    
    Recieves:
    * sub_dict: subject dictionary with the data that was converted from mat file, with fields:['data']['trial'], ['data']['trialinfo'], 
    ['data']['grad']['label'], ['data']['fsample'].
    
    Function:
    * Extracts relevant data from the dictionary for the following steps.

    Returns: 
    * data: ndarray of shape (trials, channels, time points). 
    * events_code: ndarray of shape (1, trials), stores the integers corresponding to the condition tested in each trial, 
    * ch_names: list of length 246, first 246 channel (sensor) names as a  (all "good" magnometers, the bad and reference channels are excluded).
    * s_freq: int, sampling frequency.

     """

    try:
        # Extract data and trial info
        data = sub_dict.get("data").get("trial") 
        events_code = np.array(sub_dict.get("data").get("trialinfo")[:, 0], dtype=int) # convert from float to int
        ch_names = sub_dict.get("data").get("grad").get("label")[0:246]
        sfreq = sub_dict.get("data").get("fsample")
        

    except AttributeError as e:
       print("An error occured:", e) 

    except ValueError as e:
        print("An error occured:", e)
    
    except TypeError as e:
        print("An error occured:", e)
    
    except KeyError as e:
        print("An error occured:", e)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
     # finally return data, events_code, ch_names, sfreq , if one of the variables doesn't exist (an exception occured during the process), return an empty variable / 0.
    finally:
        if 'data' not in locals():
            data = np.empty(0)

        if 'events_code' not in locals():
            events_code = np.empty(0)

        if 'ch_names' not in locals():
            ch_names = []

        if 'sfreq' not in locals():
            sfreq = 0

        return data, events_code, ch_names, sfreq
    

def create_events_for_epochs(events_code: np.ndarray):
        """
        Recieves:
        * events_code: numpy ndarray of integers with the code for each condition

        Function:
        * Creates an events (trials, 3) numpy ndarray.
          First column: The first column contains the event onset, because data already epoched - 
          np.arange(len(events_code), dtype=int), onset time should be different otherwise events is not valid input to EpochsArray.
          Second column: The second column contains the signal value of the immediately preceding sample, 
          and reflects the fact that event arrays sometimes originate from analog voltage channels.
          In most cases it is all zeros and can be ignored.
          Third column: events code for each trial according to condition.

        Reutrns:
        * events: 3D array with events ready to be input in mne.EpochsArray

        """
        try:
                # Create event onset and preceding event arrays for the 3D events structure required in MNE epochs class:
                event_onset = np.arange(len(events_code), dtype=int)
                event_precede = np.zeros(len(events_code), dtype=int)
                
                # Stack the event info into the correct shape and structure for an epochs array input (onset, preceding, events_code)
                events = np.vstack((event_onset, event_precede, events_code)).T
        
        except NameError as e:
                print("An error occured:", e)
        except TypeError as e:
                print("An error occured:", e)
        except ValueError as e:
                print("An error occured:", e)
        except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()
                
        finally:
                if 'events' not in locals():
                        events = np.empty(0)
                return events



def convert_dict_to_epochs(sub_dict: dict, mne_info):

    """

    Recieves:
    * sub_dict: subject dictionary with the already epoched data that was converted from mat file, with fields:['data']['trial'], ['data']['trialinfo'], 
    ['data']['grad']['label'], ['data']['fsample'].  
    * mne_info: instance of mne.Info class

    Function:
    * Converts dictionary to MNE epochs array.

    Reutrns:
    * MNE epochs array, or an empty dictionary in case of an exception

    """

    try:

        # variables imported from config.py:

        tmin = baseline_time[0] # starting point of baseline (-0.3 in our case) 

        baseline = baseline_time # tuple for baseline time (-0.3,0)

        oddball_id = oddball_id # int of code for oddball stimulus


        data, events_code = extract_from_dict(sub_dict)

        if len(data) == 0:
            raise EmptyVariable("an empty variable was detected","data")
        
        if len(events_code) == 0:
            raise EmptyVariable("an empty variable was detected","events_code")
        

        # Identify and remove oddball trials
        data, events_code =  remove_oddball_trials(data, events_code, oddball_id)

        if len(data)==0:
            raise EmptyVariable("an empty variable was detected","data")
        
        if len(events_code) == 0:
            raise EmptyVariable("an empty variable was detected","events_code")
        
        
        events = create_events_for_epochs(events_code)

        # Create the epochs instance:
        epochs = mne.EpochsArray(data, mne_info, events=events, tmin=tmin, event_id=event_ids,
            reject=None, flat=None, reject_tmin=None, reject_tmax=None,
            baseline=baseline, proj=True, on_missing='raise', metadata=None,
            selection=None, drop_log=None, raw_sfreq=None, verbose=None)

    except NameError as e:
        print("an error has occured:", e)

    except EmptyVariable as e:
        print("an error has occured:", e)
        traceback.print_exc()

    except ValueError as e:
        print(" An error occured:", e)

    except TypeError as e:
        print(" An error occured:", e)

    except Exception as e:
        print(" An error occured:", e)
        traceback.print_exc()
    
    # finally returns epochs, if epochs doesn't exist due to exception, return an empty dictionary
    finally:
        if epochs not in locals():
            epochs = {}
        return epochs


def create_mne_info(sub_dict: dict):
    """
    Recieves:
    * sub_dict: dictionary with fields ['data']['trial'], ['data']['trialinfo'], 
    ['data']['grad']['label'], ['data']['fsample'].  

    Function:
    * Creates a manual mne.Info instance with info: channel names, channel_types, sampling frequency

    Returns:
    * mne_info: an instance of mne.Info object, or an empty dictionary in case of an exception.

    """

    try:
        _, _, ch_names, sfreq = extract_from_dict(sub_dict)
        ch_types = np.array(246 * ['mag']) # create 246 'mag' channel types relating to the 246 extracted channel names in extract_from_dict channels 
        mne_info = mne.create_info(ch_names, sfreq, ch_types, verbose=None)
    
    
    except KeyError as e:
        print(" An error occured:", e)
    
    except TypeError as e:
        print(" An error occured:", e)

    except ValueError as e:
        print(" An error occured:", e)

    except AttributeError as e:
        print(" An error occured:", e)

    except Exception as e:
        print(" An error occured:", e)
    
    # finally returns mne_info, if doesn't exist due to exception, return an empty dictionary
    finally:
        if mne_info not in locals():
            mne_info = {}
        return mne_info


def combine_epochs(epochs, old_event_ids: dict, new_event_ids: dict):
    """
    Recieves:
    * epochs: mne epochs array instance
    * old_event_ids: dictionary in length of the number of conditions (18 in our case), must be divisible by 3.
      contains condition names as keys and the integer code for each conditio as values.
    * new_event_ids: dictionary in the length of the new number of conditions. must be in length - no. old conditions / 3.
      contains condition names as keys and the integer code for each conditio as values.

    Function:
    * Combines all conditions of same semantic category (food, positive, neutral) and repetition (presentation 1 and 2), 
    disregarding the lag (short, medium, long)

    Returns:
    * epochs_combined: mne.EpochsArray instance, with events categorized to the new conditions.

    Notes: 
    * A specific order of the conditions in old_event_ids and new_even_ids is required.
    """
    try:
        old_event_ids = list(old_event_ids.keys())

        # goes through new event_ids and assignes a new event id for every triplet of old event ids and returns a new epochs array with combined
        # event ids
        for i in np.arange(len(new_event_ids)):
            epochs_combined = mne.epochs.combine_event_ids(epochs, old_event_ids[3*i:3*i+3] , {list(new_event_ids.keys())[i]: list(new_event_ids.values())[i]}, copy=False)
    
    except TypeError as e:
        print("An error occured:", e)

    except ValueError as e:
        print("An error occured:", e)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
        
    finally:
        if 'epochs_combined' not in locals():
            epochs_combined = {}
        return epochs_combined


def create_CSD(epochs_instance, condition:str, freq_bands: list, time_range: tuple):
    """
    Recieves:
    * epochs_instance: mne.EpochsArray.
    * condition: str, the event_id key present in epochs_instance that corresponds to the experimental condition.
    * freq_bands: list of tuples(1,2) containing the lower an upper bound for each frequency band.
    * time_range: tuple, baseline time range ((-0.3,0) for our case).

    Function:
    * Calculate the cross spectral density for all channels in epochs through the set frequencies for the whole time range.
      for a specific epochs condition using morlet wavelet.  

    Returns:
    * csd: CrossSpectralDensity instance, the cross spectral density calculated.

    """
    # Suppress warning about wavelet length.
    warnings.simplefilter('ignore')

    try:
    # set the time and frequency range for csd calculation (whole time and frequency range):
        tmin = time_range[0]
        tmax = time_range[1]

        fmin = freq_bands[0][0]
        fmax = freq_bands[-1][1]

        frequencies = np.arange(fmin, fmax + 1, 2) # calculate the csd for the frequencies in the frequency range with a 2Hz step

        # epochs_baselined = epochs_instance[condition].apply_baseline((csd_tmin, csd_tmax)) # see what yields without and with baseline

        # extracts the epochs data for a single condition, the condition in which we desire to compute the csd.
        epochs_for_csd = epochs_instance[condition]
        
        # Compute CSD for the desired time interval and frequencies
        csd = csd_morlet(epochs_for_csd, frequencies=frequencies, tmin=tmin,
                        tmax=tmax, decim=20, n_jobs=-1, verbose=True)
        
    except NameError as e:
        print("An error occured:", e)

    except ValueError as e:
        print("An error has occured:", e)

    except TypeError as e:
        print("An error has occured:", e)

    except KeyError as e:
        print(" An error occured:", e)
    
    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    finally:
        if 'csd' not in locals():
            csd = np.empty(0)
        return csd


def convert_mat_to_epochs(file_name: os.PathLike, info = None):

    """
    Recieves:
    * file_name: mat file path to convert to an mne.EpochsArray instance
    * info: mne.Info instance, if info is not given a manual info is created (the manuall info doesn't contain sensor positions)

    Function:
    * Convert mat structure to an EpochsArray instance.

    Reutrns:
    * epochs: EpochsArray instance, or an empty dictionary in case of exception

    """

    if os.path.exists(file_name):
        
        try:
            sub_dict = convert_mat_to_dict(file_name)

            if info == None:
                mne_info = create_mne_info(sub_dict)
                
            epochs = convert_dict_to_epochs(sub_dict, mne_info)

            if len(epochs)==0:
                raise EmptyVariable("an empty variable was detected","epochs")

        except EmptyVariable as e:
            print("An error occured:", e)

        except TypeError as e:
            print("An error occured:", e)
        
        except OSError as e:
            print("An error occured:", e)

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
        
    else:
        raise FileNotFoundError
    
    if 'epochs' not in locals():
        epochs = {}
    
    return epochs


def save_csds_add_to_report(csd, condition: str, subject_num: str, report):

    """
    
    Recieves: 
    * csd: mne Cross Spectral Density instance for a specific condition
    * condition: condition name for reporting purposes
    * subject_num: subject number as a string for reporting purposes
    * report: mne Report instance 

    Function:
    * calculates the mean csd over the desired frequency bands for the desired condition 
    and saves the original csd for the condition, plus the mean csd.
    Adds figures to report: csd per each frequency (in initial csd calculation), mean csd over frequency bands, mean csd in coherence mode.

    Returns:
    * None

    """

    try:
        
        # average csds over frequency bands, each frequency band is a tuple (f[0], f[1])
        csd_mean = csd.mean([f[0] for f in freq_bands], [f[1] for f in freq_bands])

        # save original and mean csd:
        csd.save(f"csd_{condition}.h5") 
        csd_mean.save(f"csd_mean_{condition}.h5")

        # add csd plots to the report in the subject/CSD section, replace if a figure with this title exists in the same section:
        report.add_figure(csd.plot(show=False), title= f"CSD matrices for {condition}", section=f"{subject_num}/CSD", replace=True)
        report.add_figure(csd_mean.plot(show=False), title= f"CSD mean matrices for {condition}", section=f"{subject_num}/CSD", replace=True)
        report.add_figure(csd_mean.plot(mode='coh', show=False), title= f"Coherence mean matrices for {condition}", section=f"{subject_num}/CSD", replace=True)
        
    except NameError as e:
        print("An error occured:", e)

    except AttributeError as e:
        print("An error occured:", e)

    except TypeError as e:
        print("An error occured:", e)
        
    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    


def topomap_GFP_psd_plot_report(epochs, report, subject_num: str="default"):
    """
    Recieves:
    * epochs: mne.EpochsArray instance.
    * subject_num: the subject number as str for reporting purposes, if not provided subject_num="default"
    * reoprt: mne.Report instance

    Function:
    * Calculate and plot Global Field Power and Power Spectral Density over all epochs.
    * Plot topo-plots for evoked array according to condition 
    
    Returns: 
    * None

    """
    try:
        # average epochs array of a subject for each condition in the epochs array -> create evoked array for each condition 
        evoked_list = [epochs[condition].average() for condition in epochs.event_id.keys()]

        # add to report a general topo-plot over all the trial time and frequencies for each evoked instance (per condition) of a subject
        for evoked, condition in zip(evoked_list, epochs.event_id.keys()):
            report.add_figure(evoked.plot_topomap(show=False), title= f"topo-plots for {condition}", section=f"{subject_num}/general_topo-plot", replace=True)

        # add to report a plot of the Global Field Power of the evoked array (averages epochs across all conditions) for a subject  
        report.add_figure(epochs.average().plot_image(titles=f"Global Field Power for {subject_num}", show=False),title= f"Global Field Power", 
        section=f"{subject_num}/GFP", replace=True)

        # add to report a plot of the power spectral density over the whole trial range (-0.3, 0.8), in 2-30Hz  
        report.add_figure(epochs.compute_psd(method='multitaper', fmin=2, fmax=30, tmin=baseline_time[0], tmax=post_stim_time[1], picks=['meg']).average().plot(), 
        title= f"Power Spectral Density", section=f"{subject_num}/PSD", replace=True)

    except NameError as e:
        print("An error occured:", e)

    except KeyError as e:
        print("An error occured:", e)

    except AttributeError as e:
        print("An error occured:", e)

    except TypeError as e:
        print("An error occured:", e)

    except ValueError as e:
        print("An error occured:", e)

    except Exception as e:
        print("An error occured:", e)


def extract_raw_info(folder_directory: os.PathLike):
    """

    Recieves:
    * folder_directory: directory to the folder where the raw MEG bti recording is saved

    Function:
    * reads and extracts info from raw MEG bti recording

    Returns:
    * mne.Info instance

    """

    try:
        # redirect to the folder
        os.chdir(folder_directory) 

        # glob.glob returns a list of the paths with the desired pattern, return the first and only object in the list
        raw_path = glob.glob(f"*1Hz")[0] 

        # read raw object
        raw = mne.io.read_raw_bti(raw_path, rename_channels=False)

        # drop all bad channels and reference channels (leaves 246 channels)
        raw.drop_channels(['A247','A248','TRIGGER','RESPONSE','MLzA','MLyA','MLzaA','MLyaA','MLxA','MLxaA','MRzA','MRxA','MRzaA','MRxaA','MRyA',
                'MCzA','MRyaA','MCzaA','MCyA','GzxA','MCyaA','MCxA','MCxaA','GyyA','GzyA','GxxA','GyxA','UACurrent','X1','X3','X5','X2','X4','X6'])
        
        # extracts only info from raw object
        raw_info = raw.info

    except FileNotFoundError as e:
        print("An error occured:", e)
        
    except OSError as e:
        print("An error occured:", e)

    except PermissionError as e:
        print("An error occured:", e)

    except NameError as e:
        print("An error occured:", e)

    except AttributeError as  e:
        print("An error occured:", e)

    except TypeError as e:
        print("An error occured:", e)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
    finally:
        if 'raw_info' not in locals():
            raw_info = {}
        return raw_info
    

def compute_plot_TFR_contrast_report(epochs, subject_num: str, freqs: np.ndarray, con1: tuple, con2: tuple, report):
    """

    Recieves:
    * epochs: mne.EpochsArray object
    * freqs: 1D-array, a range of numbers defining the start, end, and step frequencies.
    * con1: tuple, tuple[0] - name of first combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * con2: tuple, tuple[0] - name of second combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * report: mne.Report instance

    Funtion:
    * Add plots of Time-Frequency Representation (TFR) of the contrast (con1-con2) between two conditions.

    Returns: 
    * Time-Frequency Representation (TFR) for the epochs (con1-con2) contrast.

    """
    try:
        # Duplicate the epochs and work with the copy
        epochs_copy = epochs.copy()

        # Take the average within each condition
        epochs_con_1 = epochs_copy[con1[1]].average()
        epochs_con_2 = epochs_copy[con2[1]].average()

        # Subtract the data (assuming the data shapes are the same)
        contrast = epochs_con_1.data - epochs_con_2.data

        # Create a new info object, assuming the same channels and info as the original EvokedArrays
        info = epochs_con_1.info 

        # Create a new Evoked object with the contrast data
        evo_contrast = mne.EvokedArray(contrast, info, tmin=epochs_con_1.tmin)

        # Compute TFR
        try:
            tfr = evo_contrast.compute_tfr(method='multitaper', tmin=baseline_time[0], tmax=post_stim_time[1], freqs=freqs)
        except ValueError as e:
            print(f"Error in computing the TFR: {e}\nAdjust the frequency range. freqs=(8, 24, 2) works best!")

        # add to report: Plot TFR - Plot TFRs as two-dimensional time-frequency images
        # Perform baseline correction by subtracting the mean baseline power (‘mean’)
        report.add_figure(tfr.plot(combine='mean', baseline=baseline_time, title=f"Contrast ({con1[0]} - {con2[0]})"),
        title= f"TFR plot Contrast", section=f"{subject_num}/TFR", replace=True)

        # frequency bands created based on freqs input, with a 4Hz interval for each band (except the last) 
        freqs_for_new_freq_bands = np.arrange(freqs[0], freqs[-1]+1, 4) # np.ndarray

        # itterate over frequencies and time frames(list of tuples from config.py): 
        for time_range in time_frames:

            for i,freq in enumerate(freqs_for_new_freq_bands):
                
                # if reached to last frequency in numpy array -> no more fmin-fmax pairs to go over 
                if i == len(freqs_for_new_freq_bands)-1:
                    break

                fmin, fmax = freq, freqs_for_new_freq_bands[i+1]

                tmin, tmax = time_range[0], time_range[1]

                # Plot TFR topomap - Plot topographic maps of specific time-frequency intervals of TFR data
                report.add_figure(tfr.plot_topomap(size=8, mode='mean', fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax, baseline=baseline_time), title=f"TFR topo-plot Contrast({con1[0]} - {con2[0]}, 
                {fmin}-{fmax}Hz, {tmin}-{tmax}s)", section=f"{subject_num}/TFR", replace=True)

        # Plot TFR joint - Plot TFRs as a two-dimensional image with topomap peak activation overall times and frequencies:
        report.add_figure(tfr.plot_joint(combine='mean', baseline=baseline_time, title=f"TFR + topo-plot Contrast ({con1[0]} - {con2[0]})"),
        title= f"TFR + topo-plot Contrast ({con1[0]} - {con2[0]})", 
        section=f"{subject_num}/TFR", replace=True)

    except NameError as e:
        print("An error occured:", e)
        
    except AttributeError as e:
        print("An error occured:", e)

    except TypeError as e:
        print("An error occured:", e)

    except ValueError as e:
        print("An error occured:", e)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
    finally:
        if 'tfr' not in locals():
            tfr = np.empty(0)
        return tfr
    


"""

Itterate over all subjects folders, convert mat files of epoched data to EpochsArray instances, combine epochs
to the desired conditions and save the two epochs arrays to fif files.
Analyse epochs_combined data using CSD, TFR, GFP, PSD and topo plots. 

Subjects foldes must contain only one mat file that contains the epoched data and one raw MEG bti recording.

"""
report = mne.Report(title="DS project report")

try:
    directory = subject_directory_pattern # directory pattern for itterating over subject folders

    # itterate over all subjects folders
    for folder in glob.iglob(directory): 

        if os.path.exists(folder): # the subject folder that contains the mat file with epoched data and the raw MEG recordings per subject

            try:  
                subject_num = folder.split("SUBS_DIR\\", 1)[1]

                os.chdir(folder)
                
                raw_info = extract_raw_info(folder)
                if len(raw_info)==0:
                    raise EmptyVariable("an empty variable was detected", "raw_info")
                
                # recieves a file path to the mat file, glob.glob returns a list of all paths found with the pattern.
                # [0] for returning the first and only element in the list.
                epochs = convert_mat_to_epochs(glob.glob(mat_file_path_pattern)[0], info=raw_info) 
                if len(epochs)==0:
                    raise EmptyVariable("an empty variable was detected", "epochs")
                
                # combine epochs by new conditions (new_event_ids):
                epochs_combined = combine_epochs(epochs, event_ids, new_event_ids)
                if len(epochs_combined)==0:
                    raise EmptyVariable("an empty variable was detected", "epochs_combined")
                
                # save the epochs arrays in the current subject's folder:
                save_in_path = os.path.join(folder, f"conds_epo.fif")
                save_in_path_combined = os.path.join(folder, f"combined_conds_epo.fif")
                epochs.save(save_in_path, overwrite=True)
                epochs_combined.save(save_in_path_combined, overwrite = True)

                # extract conditions for csd cmputation per condition:
                conditions =  list(epochs_combined.event_id.keys())
                if len(conditions)==0:
                    raise EmptyVariable("an empty variable was detected", "conditions")

                for condition in conditions:

                    # csd calculation post stimulus over the desired frequency range per condition, save and add to report
                    csd = create_CSD(epochs_combined, condition, freq_bands, post_stim_time) 
                    if len(csd)==0:
                        raise EmptyVariable("an empty variable was detected", "csd")
                    save_csds_add_to_report(csd, condition, subject_num, report)

                # csd calculation of baseline over the desired frequency range, save and add to report. (calculates csd baseline for the last 
                # condition in loop, we assume that all conditions have same baseline activity)
                csd_baseline = create_CSD(epochs, condition, freq_bands, baseline_time)
                if len(csd_baseline)==0:
                    raise EmptyVariable("an empty variable was detected", "csd_baseline")
                save_csds_add_to_report(csd_baseline, 'baseline', subject_num, report)
                
                # compute, plot and add to report GFP, PSD and general topo-plots
                topomap_GFP_psd_plot_report(epochs_combined, subject_num, report)

                # compute and plot TFR and TFR topo-plots over desired contrast of conditions, over the frequencies in freqs, save to report
                tfr = compute_plot_TFR_contrast_report(epochs=epochs, subject_num=subject_num, freqs=np.arange(8, 24, 2), con1=('pres_1', pres_1), 
                con2=('pres_2', pres_2), report=report)
                if len(tfr)==0:
                    raise EmptyVariable("an empty variable was detected", "tfr_presentation")

                tfr = compute_plot_TFR_contrast_report(epochs=epochs, subject_num=subject_num, freqs=np.arange(8, 24, 2), con1=('food',food), 
                con2=('nonfood',nonfood), report=report)
                if len(tfr)==0:
                    raise EmptyVariable("an empty variable was detected", "tfr_food")

                report.save(h5_report_path)
                report.save(html_report_path)

            except IndexError as e:
                print("An error occured:", e)

            except EmptyVariable as e:
                print("An error occured:", e)

            except OSError as e:
                print("An error occured:", e)

            except NameError as e:
                print("An error occured:", e)

            except PermissionError as e:
                print("An error occured:", e)
            
            except TypeError as e:
                print("An error occured:", e)

            except AttributeError as e:
                print("An error occured:", e)
            
            except Exception as e:
                print("An error occured:", e)


        else:
            raise FileNotFoundError
        
except NameError as e:
    print(" An error occured:", e)

  

