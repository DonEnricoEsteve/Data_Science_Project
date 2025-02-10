import numpy as np
from beartype import beartype
from numpy.typing import NDArray
from tests import input_validation_tests
import traceback

@beartype
def extract(sub_dict: dict) -> tuple[NDArray[np.floating], NDArray[np.integer], list[str], float]:

    """
    
    Recieves:
    * sub_dict: subject dictionary with the data that was converted from mat file, with fields:['datafinalLow']['trial'], ['datafinalLow']['trialinfo'], 
    ['datafinalLow']['grad']['label'], ['datafinalLow']['fsample'].
    
    Function:
    * Extracts relevant data from the dictionary for the following steps.

    Returns: 
    * data: ndarray of shape (trials, channels, time points). 
    * events_code: ndarray of shape (1, trials), stores the integers corresponding to the condition tested in each trial, 
    * ch_names: list of length 246, first 246 channel (sensor) names as a  (all "good" magnometers, the bad and reference channels are excluded).
    * s_freq: int, sampling frequency.

     """
    

    try:
        
        input_validation_tests.sub_dict(sub_dict)

    except ValueError as e:
        print("An error occured:")
        print("sub_dict has missing keys or incorrect types of values, check dictionary or change extract_from_dict function")
        traceback.print_exc()

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
    
    else:
        try:
            # Extract data, events_code(the special id for each experimental condition), channel names and sampling frequency
            data = np.array(sub_dict["datafinalLow"]["trial"])
            events_code = np.array(sub_dict["datafinalLow"]["trialinfo"][:, 0], dtype=int) # convert from float to int
            ch_names = sub_dict["datafinalLow"]["label"]
            sfreq = sub_dict["datafinalLow"]["fsample"]

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    return data, events_code, ch_names, sfreq