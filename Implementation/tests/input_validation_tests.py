
import mne
import numpy as np
from src import config
import os
import numbers
from numpy.typing import NDArray
from beartype import beartype

# input validation functions:


@beartype
def file_exists(file_name: str|os.PathLike):
    """
    
    Function: asserts correct values of inputs to file_exists function
    
    """
    # add validation of existing file 
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"The file: {file_name}, doesn't exist.")

@beartype
def compute_csd(freq_bands: list[tuple[int, int]], time_range: tuple[float, float]):
    """

    Function: asserts correct values of inputs to compute_csd function
    
    """
    
    if not all(item[0]<item[1] for item in freq_bands):
        raise ValueError("first entry should be smaller than second entry in freq_bands tuples")
    
    if max(time_range) > max(config.post_stim_time) or min(time_range) < min(config.baseline_time):
        raise ValueError(f"maximum and minimum of time_range can't extend the timerange of epochs:{config.baseline_time}-{config.post_stim_time}. See config.py and convert_dict_to_epochs function.")

@beartype
def compute_tfr_contrast(epochs: mne.EpochsArray, freqs: NDArray, con1: tuple[str, list[str]], con2: tuple[str, list[str]]):
    """
    
    Function: asserts correct values of inputs to ompute_tfr_contrast function
    
    """

    if len(freqs) == 0:
        raise ValueError(f"freqs should be an np.ndarray with at list one entry")

    elif max(freqs)>config.freq_bands[-1][-1]:
        raise ValueError(f"the max frequency in freqs can't be above 30Hz, data was low pass filtered up till 30Hz. \n")

    if len(con1[0])==0 or len(con2[0])==0:
        raise ValueError("con1[0] and con2[0] can't be empty strings.")
    
    if len(con1[1])==0 or len(con2[1])==0:
        raise ValueError(f"con1[1] and con2[1] can't be empty lists")

    if not set(con1[1]).issubset(epochs.event_id.keys()) or  not set(con2[1]).issubset(epochs.event_id.keys()):
        raise ValueError("con1[1] and con2[1] should be lists with names of keys contained in epochs. \n con1[1] or con2[1] strings are not in epochs.event_id.keys()")


@beartype
def combine_epochs(epochs: mne.EpochsArray, old_event_ids: dict, _new_event_ids: dict):
    """
    
    Function: asserts correct values of inputs to compute_tfr_contrast function
    
    """

    if not len(old_event_ids)>0:
        raise ValueError("old_event_ids is an empty dict. No empty dictionaries allowed as input.")

    if not set(old_event_ids.keys()).issubset(epochs.event_id.keys()):
        raise ValueError("some or all given old_event_ids keys are not found in epochs.event_id.keys().")

    if not len(_new_event_ids)>0:
        raise ValueError("new_event_ids is an empty dict. No empty dictionaries allowed as input.")      
    
    if len(old_event_ids) <= len(_new_event_ids):
        raise ValueError("Length of new_event_ids must be shorter than of old_event_ids, \n to combine old event ids into the new ones.")
    
    elif len(old_event_ids)%len(_new_event_ids) != 0:
        raise ValueError("""old_event_ids must be divisible by new_event_ids,
                the function takes every (# old_event_id / # new_event_ids) old event ids
                    and combines them to a single new event id""")

@beartype
def create_events_for_epochs(events_code: NDArray[np.integer]):
    """
    
    Function: asserts correct values of inputs to create_events_for_epochs function
    
    """
        
    #validate input size
    if events_code.ndim != 1:
        raise ValueError("events_code should be a 1D numpy array, an incorrect input dimension was given")

@beartype
def remove_oddball_trials(data: NDArray[np.floating], events_code: NDArray[np.integer], oddball_id: int):
    """
    
    Function: asserts correct values of inputs to remove_oddball_trials function
    
    """

    #trial number (1st dimension of data) varies for each participant, that's why we exclude it 
    if data.shape[1:3] != (config.channels_number, config.time_points):
        raise ValueError("Shape of data is incorrect, should be: \n (trial_number, channels_number, time_points) \n see config.py")

    # check if the events_code length matches the number of trials in the data:
    if not len(data) == len(events_code):
        raise ValueError("data and events_code have non matching number of trials")
    
    if np.where(events_code == oddball_id)[0].size == 0:
        raise ValueError(f"{oddball_id} was not found in events_cpde, no oddball to remove")

@beartype            
def sub_dict(sub_dict: dict):
    """
    
    Function: asserts correct values of inputs to sub_dict function
    
    """
            
    #validate key existence and values type in dict:
    if len(list(filter(lambda x: type(x) != np.ndarray, sub_dict["datafinalLow"]["trial"][:]))) != 0:
        raise TypeError("sub_dict['datafinalLow']['trial'] should be an np.ndarray of dtype float")
        
    if not isinstance(sub_dict["datafinalLow"]["trialinfo"][:, 0], np.ndarray) or sub_dict["datafinalLow"]["trialinfo"][:, 0].dtype != np.int32:
        raise TypeError('sub_dict["datafinalLow"]["trialinfo"][:, 0] should be an np.ndarray of dtype int')
    
    if not isinstance(sub_dict["datafinalLow"]["fsample"], float):
        raise TypeError(f'datafinalLow"]["fsample"] should be of type float')
    
    if not isinstance(sub_dict["datafinalLow"]["label"], list) or not all(isinstance(entery, str) for entery in sub_dict["datafinalLow"]["label"]):
        raise TypeError(f'sub_dict["datafinalLow"]["label"] should be a list of strings')

    #trial number (1st dimension of ["datafinalLow"]["trial"]) varies for each participant, that's why we exclude it 
    if np.array(sub_dict["datafinalLow"]["trial"]).shape[1:3] != (config.channels_number, config.time_points):
        raise ValueError("Shape of sub_dict['datafinalLow']['trial'] is incorrect, should be: \n (trial_number, channels_number, time_points) \n see config.py")
    
    if len(sub_dict["datafinalLow"]["trial"]) != len(sub_dict["datafinalLow"]["trialinfo"][:, 0]):
        raise ValueError(f'sub_dict["datafinalLow"]["trial"] and sub_dict["datafinalLow"]["trialinfo"] mismatch in first dimension, \n should have matching number of trials')
    
    if np.array(sub_dict["datafinalLow"]["label"]).ndim != 1 or len(sub_dict.get("datafinalLow").get("label")) != config.channels_number:
        raise ValueError(f'Dimension or length of sub_dict["datafinalLow"]["label"] is incorrect, \n should be 1D array in the length of channels_number, see config.py')




