import os, mne
# in case a raw object exists:
def extract_raw_info(folder_directory: os.PathLike) -> mne.Info|None:
    """

    Recieves:
    * folder_directory: directory to the folder where the raw MEG bti recording is saved

    Function:
    * reads and extracts info from raw MEG bti recording

    Returns:
    * mne.Info instance

    """
    import traceback, glob
    from src import config

    try:
        if not isinstance(folder_directory, (str, os.PathLike)):
            raise TypeError("folder_directory should be a directory in a str or PathLike format containing raw MEG bti file, \n \
                 input from another type was given")

    except TypeError as e:
        print("Type Error:", e)
        traceback.print_exc()


    else:
        try:
            if os.path.exists(folder_directory):
                # redirect to the folder
                os.chdir(folder_directory) 

                # glob.glob returns a list of the paths with the desired pattern, return the first and only object in the list
                raw_path = glob.glob(f"*1Hz")[0] 

                print(raw_path)

                # read raw object
                raw = mne.io.read_raw_bti(raw_path, rename_channels=False)

                # drop all bad channels and reference channels (leaves 246 channels)
                raw.drop_channels(config.bad_ch_names)
                
                # extracts only info from raw object
                raw_info = raw.info
            
            else: 
                raise FileNotFoundError(f"Directory {folder_directory} doesn't exist.")
            
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
    
    #returns raw_info, if doesn't exist due to exception, return an empty dictionary
    if 'raw_info' not in locals():
        raw_info = None
    return raw_info


#in case a raw object doesn't exist - manual creation of mne.Info:
def create_mne_info(sub_dict: dict) -> mne.Info|None:
    """
    Recieves:
    * sub_dict: dictionary with fields ['data']['trial'], ['data']['trialinfo'], 
    ['data']['grad']['label'], ['data']['fsample'].  

    Function:
    * Creates a manual mne.Info instance with info: channel names, channel_types, sampling frequency

    Returns:
    * mne_info: an instance of mne.Info object, or an empty dictionary in case of an exception.

    """

    import numpy as np
    from src import config
    from mat_to_epochs_conversion.convert_main_funcs import extract_from_dict
    import traceback

    try:
        #validate input type:
        if not isinstance(sub_dict, dict):
            raise TypeError("sub_dict should be a dictionary, another input type was recieved")
    
    except Exception as e:
        print("An error has occured:", e)

    else:
        try:
            _, _, ch_names, sfreq = extract_from_dict(sub_dict)
            ch_types = np.array(config.channels_number * ['mag']) # create 246 'mag' channel types relating to the 246 extracted channel names in extract_from_dict channels 
            mne_info = mne.create_info(ch_names, sfreq, ch_types, verbose=None)
        
        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    #returns mne_info, if doesn't exist due to exception, return None
    if mne_info not in locals():
        mne_info = None
    return mne_info


