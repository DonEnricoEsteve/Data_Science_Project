import mne
from src import config
import numpy as np
from numpy.typing import NDArray
from beartype import beartype

#output validation functions, functions validate correct values for global variables in main.py which contain the outputs of the functions used in the script.

@beartype
def test_subject_num(subject_num: str):
    """
    Function: validates correct subject_num string.
    
    """
    import fnmatch
    assert fnmatch.fnmatch(subject_num, "subject_*")

@beartype
def test_raw_info(raw_info: mne.Info):
    """

    Function: validates existance of sensor locations in raw_info.
    
    """
    assert len(raw_info['chs'][0]['loc']) != 0

@beartype
def test_epochs_combined(epochs_combined: mne.EpochsArray):  
    """
    
    Function: validates event id keys in epochs combined equal new_event_ids keys as set in config.py.
    
    """
    assert epochs_combined.event_id.keys() == config.new_event_ids.keys()

@beartype
def test_csd(csd: mne.time_frequency.CrossSpectralDensity):
    """
    
    Function: validates the number of channels that the  cross spectral density calculated for is the number of channels set in config.py.

    """
    assert csd.n_channels == config.channels_number

@beartype
def test_tfr(tfr: mne.time_frequency.AverageTFR, freqs: NDArray):
    """
    
    Function: asserts tfr data shape is correct according to the channel number and time points defined in config.py and the number of frequencies the tfr was calculated for.
    
    """

    assert tfr.get_data().shape == (config.channels_number, len(freqs), config.time_points)

@beartype   
def test_psd(psd: mne.time_frequency.Spectrum):
    """
    
    Function: asserts that power spectral density was calculated for all desired channels, as the number of channels defined in condig.py.

    """
    assert len(psd.ch_names) == config.channels_number

    
    


