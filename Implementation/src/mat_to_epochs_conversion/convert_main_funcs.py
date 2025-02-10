import os
import numpy as np
import mne

def convert_mat_to_dict(file_name: str|os.PathLike) -> dict|None:
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
    import traceback
    from pymatreader import read_mat

    try:
        #validate input type:
        if not isinstance(file_name, (str, os.PathLike)):
            raise TypeError("file_name should be a directory to a mat file in str or PathLike format, input from another type was given")

    except Exception as e:
         print("An error occured:", e)
         traceback.print_exc()
    
    else:
            
        try:
            if os.path.exists(file_name):
                # using read_mat from pymatreader module, convert a v. 7.3 mat file to a dictionary
                dict_from_mat = read_mat(file_name)

            else:
                raise FileNotFoundError()

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
            
    #returns dict_mat, if dict_mat doesn't exist (fail in conversion), return None
    if 'dict_from_mat' not in locals(): 
        dict_from_mat = None
    return dict_from_mat


def extract_from_dict(sub_dict: dict) -> tuple[np.ndarray|None, np.ndarray|None, list[str]|None, float|None]:

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
    
    from tests import input_validation
    import traceback

    try:
        
        input_validation.validation_func['extract_from_dict'](sub_dict)

    except ValueError as e:
        print("An error occured:")
        print("sub_dict has missing keys or incorrect types of values, check dictionary or change extract_from_dict function")
        
    except Exception as e:
        print("An error occured:", e)

    else:
        try:
            # Extract data and trial info
            data = sub_dict.get("data").get("trial") 
            events_code = np.array(sub_dict.get("data").get("trialinfo")[:, 0], dtype=int) # convert from float to int
            ch_names = sub_dict.get("data").get("label")
            sfreq = sub_dict.get("data").get("fsample")

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    #return data, events_code, ch_names, sfreq , if one of the variables doesn't exist (an exception occured during the process), return an empty variable / 0.
    if 'data' not in locals():
        data = None

    if 'events_code' not in locals():
        events_code = None

    if 'ch_names' not in locals():
        ch_names = None

    if 'sfreq' not in locals():
        sfreq = None

    return data, events_code, ch_names, sfreq


def remove_oddball_trials(data: np.ndarray, events_code: np.ndarray, oddball_id: int) -> tuple[np.ndarray|None, np.ndarray|None]:

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
    from tests import input_validation
    import traceback

    try:
        input_validation.validation_func['remove_oddball_trials'](data, events_code, oddball_id)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()


    else:
        try:
            
            oddball_idx = np.where(events_code == oddball_id)[0]  # using [0] to extract the indices array of the oddball stimulus,
            # those are the indices of the trials in data corresponding to the oddball stimulus

            # Remove odball code from events_code + oddball trials from data
            events_code_removed = np.delete(events_code, oddball_idx)
            data_removed = np.delete(data, oddball_idx, axis=0)  # axis=0 --> remove odball from data rows (trials)
    
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()


    #return data_removed, if data_removed doesn't exist (an exception occured during the process), return an empty ndarray
    if 'data_removed' not in locals():
        data_removed = None
    if 'events_code_removed' not in locals():
        events_code_removed = None  

    return data_removed, events_code_removed


def create_events_for_epochs(events_code: np.ndarray) -> np.ndarray|None:
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

    from tests import input_validation
    import traceback

    try:

        input_validation.validation_func['create_events_for_epochs'](events_code)
        

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:
        try:
                # Create event onset and preceding event arrays for the 3D events structure required in MNE epochs class:
                event_onset = np.arange(len(events_code), dtype=int)
                event_precede = np.zeros(len(events_code), dtype=int)
                
                # Stack the event info into the correct shape and structure for an epochs array input (onset, preceding, events_code)
                events = np.vstack((event_onset, event_precede, events_code)).T
        
        except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()

    if 'events' not in locals():
            events = None
    return events    


def convert_dict_to_epochs(sub_dict: dict, mne_info: mne.Info) -> tuple[mne.EpochsArray|None, mne.EvokedArray|None]:

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
    from src import config
    from tests import input_validation
    import traceback

    try:

        input_validation.validation_func['convert_dict_to_epochs'](sub_dict, mne_info)
        

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:
        try:      
            # variables imported from config.py:

            tmin = config.baseline_time[0] # starting point of baseline (-0.3 in our case) 

            baseline = config.baseline_time # tuple for baseline time (-0.3,0)

            oddball_id = oddball_id # int of code for oddball stimulus


            data, events_code = extract_from_dict(sub_dict)

            # Identify and remove oddball trials
            data, events_code =  remove_oddball_trials(data, events_code, oddball_id)

            events = create_events_for_epochs(events_code)

            # Create the epochs instance:
            epochs = mne.EpochsArray(data, mne_info, events=events, tmin=tmin, event_id=config.event_ids,
                reject=None, flat=None, reject_tmin=None, reject_tmax=None,
                baseline=baseline, proj=True, on_missing='raise', metadata=None,
                selection=None, drop_log=None, raw_sfreq=None, verbose=None)
            evoked = epochs.average()

                            
            # save the epochs arrays in the current subject's folder:
            epochs.save(config.epochs_path, overwrite=True)
            evoked.save(config.evoked_path, overwrite=True)

        except Exception as e:
            print(" An error occured:", e)
            traceback.print_exc()

    #returns epochs, if epochs doesn't exist due to exception, return an empty dictionary
    if 'epochs' not in locals():
        epochs = None
    if 'evoked' not in locals():
        evoked = None
    return epochs, evoked   


def convert_mat_to_epochs(file_name: os.PathLike, info = None) -> tuple[mne.EpochsArray|None, mne.evoked.Evoked|None]:

    """
    Recieves:
    * file_name: mat file path to convert to an mne.EpochsArray instance
    * info: mne.Info instance, if info is not given a manual info is created (the manuall info doesn't contain sensor positions)

    Function:
    * Convert mat structure to an EpochsArray instance.

    Reutrns:
    * epochs: EpochsArray instance, or an empty dictionary in case of exception

    """

    from src import config
    from mat_to_epochs_conversion import create_info
    import traceback
    from tests import input_validation
    
    try: 

        input_validation.validation_func['convert_mat_to_epochs'](file_name, info)
        
    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:

        try:

            if not os.path.exists(file_name):
                raise FileNotFoundError(f"The file: {file_name}, doesn't exist.")
            

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

        else: 

            try:
                sub_dict = convert_mat_to_dict(file_name)

                if info is None:
                    mne_info = create_info.create_mne_info(sub_dict)
                    
                epochs, evoked = convert_dict_to_epochs(sub_dict, mne_info)

            except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()
            
    
    #returns epochs and evoked, if doesn't exist due to exception, return None
    if 'epochs' not in locals():
        epochs = None
    if 'evoked' not in locals():
        evoked = None
    return epochs, evoked
