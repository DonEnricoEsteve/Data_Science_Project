import mne

def combine_epochs(epochs: mne.EpochsArray, old_event_ids: dict, new_event_ids: dict)-> mne.EpochsArray|None:
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

    import mne
    import traceback
    import numpy as np
    from src import config
    from tests import input_validation

    epochs_combined = None

    try:

        input_validation.validation_func["combine_epochs"](epochs, old_event_ids, new_event_ids)
        

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()
        
    else:
        try:
            old_event_ids = list(old_event_ids.keys())
            num_keys_combined = len(old_event_ids)/len(new_event_ids)

            # goes through new event_ids and assignes a new event id for every triplet of old event ids and returns a new epochs array with combined
            # event ids
            for i in np.arange(len(new_event_ids)):
                epochs_combined = mne.epochs.combine_event_ids(epochs, 
                old_event_ids[num_keys_combined*i:num_keys_combined*i+num_keys_combined] , 
                {list(new_event_ids.keys())[i]: list(new_event_ids.values())[i]}, copy=True)

            epochs_combined.save(config.epochs_combined_path, overwrite = True)
        
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    return epochs_combined
