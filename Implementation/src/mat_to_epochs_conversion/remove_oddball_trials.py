import numpy as np
from beartype import beartype
from numpy.typing import NDArray

@beartype
def remove(data: NDArray[np.floating], events_code: NDArray[np.integer], oddball_id: int) -> tuple[NDArray[np.floating], NDArray[np.integer]]:

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
    from tests import input_validation_tests
    import traceback

    try:
        input_validation_tests.remove_oddball_trials(data, events_code, oddball_id)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()


    else:

        try:

            # using [0] to extract the indices array of the oddball stimulus,
            # those are the indices of the trials in data corresponding to the oddball stimulus
            oddball_idx = np.where(events_code == oddball_id)[0] 

            # Remove odball code from events_code + oddball trials from data
            events_code_removed = np.delete(events_code, oddball_idx)
            data_removed = np.delete(data, oddball_idx, axis=0)  # axis=0 --> remove odball from data rows (trials)
    
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc() 

    return data_removed, events_code_removed
