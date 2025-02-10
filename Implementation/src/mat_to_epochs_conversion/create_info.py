import os, mne
from tests import output_tests
import traceback, glob
from src import config
from tests import input_validation_tests
from beartype import beartype

@beartype
# in case a raw object exists:
def extract_raw_info(folder_directory: str|os.PathLike) -> mne.Info:
    """

    Recieves:
    * folder_directory: directory to the folder where the raw MEG bti recording is saved

    Function:
    * reads and extracts info from raw MEG bti recording

    Returns:
    * raw_info: mne.Info instance

    """
    try:
        
        input_validation_tests.file_exists(folder_directory)

        # redirect to the folder
        os.chdir(folder_directory) 

        # glob.glob returns a list of the paths with the desired pattern, return the first and only object in the list
        raw_path = glob.glob(f"*1Hz")[0] 

        print(raw_path)

        # read raw object
        raw = mne.io.read_raw_bti(raw_path, rename_channels=False)

        # drop all bad channels and reference channels (leaves 246 channels)
        raw.drop_channels(config.bad_ch_names)
        
        # extracts info from raw object
        raw_info = raw.info
            
            
    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    return raw_info


@beartype
#in case a raw object doesn't exist - manual creation of mne.Info:
def create_mne_info(sub_dict: dict) -> mne.Info:
    """
    Recieves:
    * sub_dict: dictionary with fields ['datafinalLow']['trial'], ['datafinalLow']['trialinfo'], 
    ['datafinalLow']['grad']['label'], ['datafinalLow']['fsample'].  

    Function:
    * Creates a manual mne.Info instance with info: channel names, channel_types, sampling frequency

    Returns:
    * mne_info: mne.Info instance

    """

    import numpy as np
    from src import config
    from mat_to_epochs_conversion.convert_main_funcs import extract_from_dict
    import traceback

    try:
       
       input_validation_tests.sub_dict(sub_dict)
    
    except Exception as e:
        print("An error has occured:", e)
        traceback.print_exc()

    else:
        try:
            _, _, ch_names, sfreq = extract_from_dict(sub_dict) #ec=xtracts from the dictionary that has the epoched data the channel names and sampling frequency.
            ch_types = np.array(config.channels_number * ['mag']) # create 246 'mag' channel types relating to the 246 extracted channel names in extract_from_dict channels 
            mne_info = mne.create_info(ch_names, sfreq, ch_types, verbose=None)  
        
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    return mne_info


