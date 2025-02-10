import os
import numpy as np
import mne
from tests import input_validation_tests
from . import create_events_for_epochs, extract_from_dict, remove_oddball_trials
from beartype import beartype

@beartype
def convert_mat_to_dict(file_name: str|os.PathLike) -> dict:
    """
    
    Recieves:
    * file_name: path to mat file for conversion. 
    
    Function:
    * Converts mat files from v. 7.3 to dictionaries and deals with possible exceptions.

    Returns: 
    * dict_from_mat: dictionary 

    Notes:
    * For the following code to work the mat file should include epoched data.
        
    """
    import traceback
    from pymatreader import read_mat

    try:
        input_validation_tests.file_exists(file_name) 

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:

        try:    
            # using read_mat from pymatreader module, convert a v. 7.3 mat file to a dictionary
            dict_from_mat = read_mat(file_name)

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
            
    return dict_from_mat


@beartype
def convert_dict_to_epochs(sub_dict: dict, mne_info: mne.Info) -> tuple[mne.EpochsArray, mne.EvokedArray]:

    """

    Recieves:
    * sub_dict: subject dictionary with the already epoched data that was converted from mat file, with fields:['datafinalLow']['trial'], ['datafinalLow']['trialinfo'], 
    ['datafinalLow']['grad']['label'], ['datafinalLow']['fsample'].  
    * mne_info: instance of mne.Info class

    Function:
    * Converts dictionary to MNE epochs array, averages it to compute the evoked response and saves the epochs and evoked instances.

    Reutrns:
    * epochs: mne.EpochsArray instance
    * evoked: mne.Evoked instance

    """
    from src import config
    from tests import input_validation_tests
    import traceback

    # try:

    #     input_validation_tests.sub_dict(sub_dict)
        

    # except Exception as e:
    #     print("An error occured:", e)
    #     traceback.print_exc()


    try:      
        # variables imported from config.py:

        tmin = config.baseline_time[0] # starting point of baseline (-0.3 in our case) 

        baseline = config.baseline_time # tuple for baseline time (-0.3,0)

        oddball_id = config.oddball_id # int of code for oddball stimulus


        data, events_code,_,_ = extract_from_dict.extract(sub_dict)

        # Identify and remove oddball trials
        data, events_code =  remove_oddball_trials.remove(data, events_code, oddball_id)

        events = create_events_for_epochs.create(events_code)

        # Create the epochs instance:
        epochs = mne.EpochsArray(data, mne_info, events=events, tmin=tmin, event_id=config.event_ids,
            reject=None, flat=None, reject_tmin=None, reject_tmax=None,
            baseline=baseline, proj=True, on_missing='raise', metadata=None,
            selection=None, drop_log=None, raw_sfreq=None, verbose=None)
        
        # average epochs to get a general evoked response to all visual stimuli
        evoked = epochs.average()

                        
        # save the epochs array and evoked in the current subject's folder:
        epochs.save(config.epochs_path)
        evoked.save(config.evoked_path)

    except Exception as e:
        print(" An error occured:", e)
        traceback.print_exc()

    return epochs, evoked   


@beartype
def convert_mat_to_epochs(file_name: str|os.PathLike, mne_info: mne.Info = None) -> tuple[mne.EpochsArray, mne.evoked.Evoked]:

    """
    Recieves:
    * file_name: mat file path to convert to an mne.EpochsArray instance
    * info: mne.Info instance, if info is not given a manual info is created (the manuall info doesn't contain sensor positions)

    Function:
    * Convert mat structure to an EpochsArray instance and average to get evoked response

    Reutrns:
    * epochs: mne.EpochsArray instance
    * evoked: mne.Evoked instance

    """

    from src import config
    from mat_to_epochs_conversion import create_info
    import traceback
    from tests import input_validation_tests
    
    try: 

        input_validation_tests.file_exists(file_name)
        
    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
    else:

        try:

            sub_dict = convert_mat_to_dict(file_name)

            if mne_info is None:
                mne_info = create_info.create_mne_info(sub_dict)
                
            epochs, evoked = convert_dict_to_epochs(sub_dict, mne_info)

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
            
    return epochs, evoked
