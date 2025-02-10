import mne
import numpy as np
from beartype import beartype
from numpy.typing import NDArray
from src import config
import traceback
from tests import input_validation_tests

@beartype
def compute_tfr_contrast(epochs: mne.EpochsArray, freqs: NDArray, con1: tuple, con2: tuple)\
    -> mne.time_frequency.AverageTFR:
    """

    Recieves:
    * epochs: mne.EpochsArray object
    * freqs: 1D-array, a range of numbers defining the start, end, and step frequencies.
    * con1: tuple, tuple[0] - name of first combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * con2: tuple, tuple[0] - name of second combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * report: mne.Report instance

    Function:
    * Compute Time-Frequency Representation (TFR) of the contrast (con1-con2) between two conditions and save it to the current directory.

    Returns: 
    * Time-Frequency Representation (TFR) for the epochs (con1-con2) contrast.

    """

    # input testing
    try:

        input_validation_tests.compute_tfr_contrast(epochs, freqs, con1, con2)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    else:
        try:
            # Duplicate the epochs and work with the copy
            epochs_copy = epochs.copy()

            # Take the average within each condition
            epochs_con_1 = epochs_copy[con1[1]].average()
            epochs_con_2 = epochs_copy[con2[1]].average()

            # Subtract the data (assuming the data shapes are the same)
            contrast = epochs_con_1.data - epochs_con_2.data

            # Create a new info object, assuming the same channels and info as the original EvokedArrays
            info = epochs_con_1.info 

            # Create a new Evoked object with the contrast data
            # Note: baselining is preformed in the spectrum and topo-map plots in add_to_report.py and that's why it's not included here
            evo_contrast = mne.EvokedArray(contrast, info, tmin=epochs_con_1.tmin)
            
            # Compute TFR
            try:
                tfr_contrast = evo_contrast.compute_tfr(method='multitaper', tmin=config.baseline_time[0], tmax=config.post_stim_time[1], freqs=freqs)

                tfr_contrast.save(config.get_tfr_contrast_path(con1, con2))
                traceback.print_exc()
                
            except ValueError as e:
                print(f"Error in computing the TFR: {e}\nAdjust the frequency range. freqs=(8, 24, 2) works best!")

            except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
        
    return tfr_contrast


@beartype
def compute_psd(evoked_instance: mne.Evoked, fmin: int, fmax: int, tmin: float, tmax: float, picks: str|list[str])-> mne.time_frequency.Spectrum:
    """
    Recieves:
    * evoked_instance: mne.Evoked object
    * fmin: float, the minimal frequency for power spectral density computation
    * fmax: float, the maximal frequency for power spectral density computation
    * tmin: float, the starting point for power spectral density computation
    * tmax: float, the end point for power spectral density computation
    * picks: the type/names of channels to compute psd for.

    Function:
    * Compute the Power Spectral Density (PSD) for the channels provided in picks and save it to the current directory. 

    Returns: 
    * The Power Spectral Density for all picked channels.

    """

    try:


        psd = evoked_instance.compute_psd(method='multitaper', fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax, picks=picks)

        psd.save(config.psd_path)

    except Exception as e:
        print("An error occured:", e)
        traceback.print_exc()

    return psd

