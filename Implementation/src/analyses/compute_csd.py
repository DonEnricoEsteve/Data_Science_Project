import numpy as np
import mne
from beartype import beartype
import traceback
from src import  config
from mne.time_frequency import csd_morlet
from tests import input_validation_tests
import warnings
warnings.simplefilter('ignore') #supress morlet wavelet warnings about length of wave
from src import config

@beartype
def compute_csd(epochs_instance: mne.EpochsArray, condition:str, freq_bands: list[tuple[int, int]], time_range: tuple[float,float], is_base_line=False) \
    -> tuple[mne.time_frequency.CrossSpectralDensity, mne.time_frequency.CrossSpectralDensity]:
    """
    Recieves:
    * epochs_instance: mne.EpochsArray.
    * condition: str, the event_id key present in epochs_instance that corresponds to the experimental condition.
    * freq_bands: list of tuples(1,2) containing the lower an upper bound for each frequency band.
    * time_range: tuple, post stimulus / baseline time range.

    Function:
    * Calculate the cross spectral density for all channels in epochs through the set frequencies for the whole time range.
      for a specific epochs condition using morlet wavelet.  

    Returns:
    * csd: CrossSpectralDensity instance, the cross spectral density calculated.

    """


    # vaidate input values 
    try:
        input_validation_tests.compute_csd(freq_bands=freq_bands, time_range=time_range)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:
        try:
        # set the time and frequency range for csd calculation (whole time and frequency range):
            tmin = min(time_range)
            tmax = max(time_range)

            fmin = freq_bands[0][0]
            fmax = freq_bands[-1][1]

            frequencies = np.arange(fmin, fmax + 1, 2) # calculate the csd for the frequencies in the frequency range with a 2Hz step

            # Remove the mean during the time interval for which we compute the CSD
            epochs_baselined = epochs_instance[condition].apply_baseline((tmin, tmax)) 

            # # extracts the epochs data for a single condition, the condition in which we desire to compute the csd.
            # epochs_for_csd = epochs_instance[condition]
            
            # Compute CSD for the desired time interval and frequencies
            csd = csd_morlet(epochs_baselined, frequencies=frequencies, tmin=tmin,
                            tmax=tmax, decim=20, n_jobs=-1, verbose=True)
            
            # average csds over frequency bands, each frequency band is a tuple (f[0], f[1])
            csd_mean = csd.mean([f[0] for f in freq_bands], [f[1] for f in freq_bands])

            if is_base_line==True:
                condition = 'baseline'
            # save original and mean csd:
            csd.save(config.get_csd_path(condition)) 
            csd_mean.save(config.get_csd_mean_path(condition))

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()

    return csd, csd_mean