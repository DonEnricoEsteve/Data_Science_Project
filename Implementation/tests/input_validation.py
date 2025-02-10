
import mne
import numpy as np
from src import config
import os
from cerberus import Validator
import numbers

def validate_input_compute_csd(epochs_instance: mne.EpochsArray, condition:str, freq_bands: list, time_range: tuple):

    if not isinstance(epochs_instance, mne.EpochsArray):
        raise TypeError("TypeError: epochs_instance should be of type mne.EpochsArray")
    
    if not isinstance(condition, str):
        raise TypeError("TypeError: condition should be a string.")


    if not isinstance(freq_bands, list):
        raise TypeError("TypeError: freq_bands should be a list of 2 entry tuples with numeric entries.")

    elif not all(isinstance(item, tuple) for item in freq_bands):
        raise TypeError("TypeError: freq_bands should be a list of 2 entry tuples with numeric entries.")
    
    elif all(len(item) != 2 for item in freq_bands):
        raise ValueError("Value: freq_bands should be a list of 2 entry tuples with numeric entries.")
    
    elif not all(isinstance([item[0], item[1]], numbers.Real) for item in freq_bands):
        raise TypeError("TypeError: freq_bands should be a list of 2 entry tuples with numeric entries.")
    
    elif not all(item[0]<item[1] for item in freq_bands):
        raise ValueError("first entry should be smaller than second entry in freq_bands tuples")


    if not isinstance(time_range, tuple):
        raise TypeError("time_range should be a tuple with two entries")
    
    elif len(time_range) != 2:
        raise ValueError("time_range should be a tuple with two entries")
    
    elif max(time_range) > max(config.post_stim_time) or min(time_range) > min(config.baseline_time):
        raise ValueError(f"maximum and minimum of time_range can't extend the timerange of epochs: \
                        {config.baseline_time}-{config.post_stim_time}. \n See config.py and convert_dict_to_epochs \
                            function.")

def validate_input_compute_tfr_contrast(epochs: mne.EpochsArray, freqs: np.ndarray, con1: tuple, con2: tuple):
    
    if not isinstance(epochs, mne.EpochsArray):
        raise TypeError(f"epochs shpould be an mne.EpochsArray instance, an input  from another type was given. \n")
    
    if len(freqs) == 0:
        raise ValueError(f"freqs should be an np.ndarray with at list one entry")
    
    elif not isinstance(freqs, np.ndarray) and not np.issubdtype(freqs.dtype, np.number):
        raise TypeError(f"freqs should be a numerical ndarray, another input type was given.\n")
    
    elif max(freqs)>config.freq_bands[-1][-1]:
        raise ValueError(f"the max frequency in freqs can't be above 30Hz, data was low pass filtered up till 30Hz. \n")
    
    if not isinstance(con1, tuple) or not isinstance(con2, tuple):
        raise TypeError(f"con1 and con2 should be tuples. Another input type was given.\n")
    
    elif len(con1) != 2 or len(con2) != 2:
        raise ValueError(f"con1 and con2 should be tuples in length 2. \n ")
    
    elif not isinstance(con1[0], str) or not isinstance(con2[0]):
        raise TypeError(f"First entry in con1 and con2 tuples should be a string, wrong input type was given. \n")
    
    elif len(con1[0])==0 or len(con2[0])==0:
        raise ValueError("con1[0] and con2[0] can't be empty strings.")
    
    elif not isinstance(con1[1], list) or not isinstance(con2[1], list) :
        raise TypeError(f"Second entry in con1 and con2 tuples should be a list, wrong iput type was given. \n")

    elif len(con1[1])==0 or len(con2[1])==0:
        raise ValueError(f"con1[1] and con2[1] can't be empty lists")

    elif not all(isinstance(item, str) for item in con1[1]) or not all(isinstance(item, str) for item in con2[1]):
            raise TypeError(f"Second entry in con1 and con2 tuples should be a list of strings, \n \
                not all entries in list are strings.")

    elif not set(con1[1]).issubset(epochs.event_id.keys()) or  not set(con2[1]).issubset(epochs.event_id.keys()):
        raise ValueError(f"con1[1] and con2[1] should be lists with names of keys contained in epochs. \n \
                            con1[1] or con2[1] strings are not in epochs.event_id.keys()")

def validate_input_combine_epochs(epochs: mne.EpochsArray, old_event_ids: dict, new_event_ids: dict):
        
        # search for input type errors
        if not isinstance(epochs, mne.EpochsArray):
            raise TypeError("epochs should be an mne.EpochsArray instance, got input of another type")
        
        if not isinstance(old_event_ids, dict):
            raise TypeError("old_event_ids should be a dict, got input of another type")
        
        elif not len(old_event_ids)>0:
            raise ValueError("old_event_ids is an empty dict. No empty dictionaries allowed as input.")

        elif not set(old_event_ids.keys()).issubset(epochs.event_id.keys()):
            raise ValueError("some or all given old_event_ids keys are not found in epochs.event_id.keys().")
        
        if not isinstance(new_event_ids, dict):
            raise TypeError("new_event_ids should be a dict, got input of another type")
        
        elif not len(new_event_ids)>0:
            raise ValueError("new_event_ids is an empty dict. No empty dictionaries allowed as input.")      
        
        if len(old_event_ids) <= len(new_event_ids):
            raise ValueError("Length of new_event_ids must be shorter than of old_event_ids, \n \
                    to combine old event ids into the new ones.")
        
        elif len(old_event_ids)%len(new_event_ids) != 0:
            raise ValueError("""old_event_ids must be divisible by new_event_ids, \n 
                    the function takes every (# old_event_ids \ # new_event_ids) old event ids \n 
                    and combines them to a single new event id""")

def validate_input_create_events_for_epochs(events_code: np.ndarray):
        
        if not isinstance(events_code, np.ndarray):
             raise TypeError("events_code should be an np.ndarray, got an input from anoter type")
        
        #validate input subtype
        elif not np.issubdtype(events_code.dtype, np.integer):
            raise TypeError("events_code should be an array of integers")
        
        #validate input size
        elif events_code.ndim != 1:
            raise ValueError("events_code should be a 1D numpy array, an incorrect input dimension was given")

def validate_input_remove_oddball_trials(data: np.ndarray, events_code: np.ndarray, oddball_id: int):
            
    if not isinstance(data, np.ndarray):
        raise TypeError("data should be an np.ndarray, another input type was given")

    if not isinstance(events_code, np.ndarray):
        raise TypeError("events_code should be an np.ndarray, another input type was given")
    
    if not isinstance(oddball_id, int):
        raise TypeError("oddball_id should be an int, another input type was given")

    if not data.shape != (config.trial_number, config.channels_number, config.time_points):
        raise ValueError("Shape of data is incorrect, should be: \n \
                (trial_number, channels_number, time_points) \n \
                see config.py")

    # check if the events_code length matches the number of trials in the data:
    if not len(data) == len(events_code):
        raise ValueError("data and events_code have non matching number of trials")
    
    if np.where(events_code == oddball_id)[0].size == 0:
        raise ValueError(f"{oddball_id} was not found in events_cpde, no oddball to remove")
            
def validate_input_extract_from_dict(sub_dict: dict):
    #validate input type:
        if not isinstance(sub_dict, dict):
            raise TypeError("sub_dict should be a dictionary, another input type was recieved")
        
        else:
            #validate key existence and values type in dict:
                    
            v = Validator(config.sub_dict_schema)

            if v.validate(sub_dict) is False:
                raise ValueError("sub_dict has missing/mismatching keys and wrong value types \n \
                compared to sub_dict_schema, see config.py.\n", v.error)
            
            else:

                if sub_dict["data"]["trial"].shape != (config.trial_number, config.channels_number, config.time_points):
                    raise ValueError("Shape of sub_dict['data']['trial'] is incorrect, should be: \n \
                           (trial_number, channels_number, time_points) \n \
                          see config.py")
                
                if len(sub_dict["data"]["trialinfo"][:, 0]) != config.trial_number:
                    raise ValueError('Length of sub_dict["data"]["trialinfo"][:, 0] is incorrect,\n \
                          should be: (trial_number) , see config.py.')
                
                if len(sub_dict["data"]["trial"]) != len(sub_dict["data"]["trialinfo"][:, 0]):
                    raise ValueError('sub_dict["data"]["trial"] and sub_dict["data"]["trialinfo"] mismatch in first dimension, \n \
                          should have matching number of trials')
                
                if  sub_dict["data"]["label"].ndim != 1 or len(sub_dict.get("data").get("label")) != config.channels_number:
                    raise ValueError('Dimension or length of sub_dict["data"]["label"] is incorrect, \n \
                          should be 1D array in the length of channels_number, see config.py')

def validate_input_convert_dict_to_epochs(sub_dict: dict, mne_info: mne.Info):        
    
    if not isinstance(sub_dict, dict):
        raise TypeError("sub_dict should be a dictionary, another input type was given")

    if not isinstance(mne_info, mne.Info):
        raise TypeError("mne_info should be an mne.Info, another input type was given")

def validate_input_convert_mat_to_epochs(file_name: os.PathLike, info = None):
    
    v = Validator(config.sub_dict_schema)

    if not isinstance(file_name,(str,os.PathLike)):
        raise TypeError("file_name should be a directory to a mat file in str or PathLike format, input from another type was given")
    
    if info is not None and not isinstance(info, mne.Info):
        raise TypeError("info should be an mne.Info instance, input of another type was given")


validation_func = {'compute_csd': validate_input_compute_csd, 'compute_tfr_contrast': validate_input_compute_tfr_contrast, 
                   'combine_epochs': validate_input_combine_epochs, 'create_events_for_epochs': validate_input_create_events_for_epochs,
                   'remove_oddball_trials':validate_input_remove_oddball_trials, 'extract_from_dict': validate_input_extract_from_dict,
                   'convert_dict_to_epochs': validate_input_convert_dict_to_epochs, 'convert_mat_to_epochs':validate_input_convert_mat_to_epochs}