import numpy as np
from beartype import beartype
from numpy.typing import NDArray

@beartype
def create(events_code: NDArray[np.integer]) -> NDArray[np.integer]:
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

    from tests import input_validation_tests
    import traceback

    try:

        input_validation_tests.create_events_for_epochs(events_code)
        

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:
        try:
                # Create event onset and preceding event arrays for the 3D events structure required in MNE epochs class:

                # Because data is already epoched, every epoch will get a different integer to be treated as a different event.
                event_onset = np.arange(len(events_code), dtype=int) 
                event_precede = np.zeros(len(events_code), dtype=int)
                
                # Stack the event info into the correct shape and structure for an epochs array input (1st col: onset, 2nd col: preceding, 3rd col: events_code)
                events = np.vstack((event_onset, event_precede, events_code)).T
        
        except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()

    return events    
