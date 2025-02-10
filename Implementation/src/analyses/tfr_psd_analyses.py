import mne
import numpy as np


def compute_tfr_contrast(epochs: mne.EpochsArray, freqs: np.ndarray, con1: tuple, con2: tuple)\
    -> mne.time_frequency.AverageTFR|None:
    """

    Recieves:
    * epochs: mne.EpochsArray object
    * freqs: 1D-array, a range of numbers defining the start, end, and step frequencies.
    * con1: tuple, tuple[0] - name of first combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * con2: tuple, tuple[0] - name of second combined condition to contrast, 
      tuple[1] - a list of str of the name of conditions present in epochs combined under the same new condition -> tuple[0]
    * report: mne.Report instance

    Funtion:
    * Add plots of Time-Frequency Representation (TFR) of the contrast (con1-con2) between two conditions.

    Returns: 
    * Time-Frequency Representation (TFR) for the epochs (con1-con2) contrast.

    """
    import traceback
    from src import config
    from tests import input_validation

    # input handling
    try:

        input_validation.validation_func['compute_tfr_contrast'](epochs, freqs, con1, con2)

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
            evo_contrast = mne.EvokedArray(contrast, info, tmin=epochs_con_1.tmin)

            # Compute TFR
            try:
                tfr_contrast = evo_contrast.compute_tfr(method='morlet', tmin=config.baseline_time[0], tmax=config.post_stim_time[1], freqs=freqs)

                tfr_contrast.save(config.get_tfr_contrast_path(con1, con2))

            except ValueError as e:
                print(f"Error in computing the TFR: {e}\nAdjust the frequency range. freqs=(8, 24, 2) works best!")

            except Exception as e:
                print("An error occured:", e)
                traceback.print_exc()

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()
        
    if 'tfr_contrast' not in locals():
        tfr_contrast = None
    return tfr_contrast


def psd(evoked_instance: mne.evoked.Evoked)-> mne.time_frequency.Spectrum:
    from src import config
    import traceback
    
    try:
        if not isinstance(evoked_instance, mne.evoked.Evoked):
            raise TypeError("evoked_instance should be an mne.evoked.Evoked instance, wrong input type was given.")
        
    except TypeError as e:
        print("An error occured:", e)

    else:
        try:

            psd = evoked_instance.compute_psd(method='morlet', fmin=2, fmax=30, tmin=config.baseline_time[0], tmax=config.post_stim_time[1], picks=['meg'])
            psd.save(config.psd_path)

        except Exception as e:
            print("An error occured:", e)
            traceback.print_exc()


    if 'psd' not in locals():
        psd = None
    return psd

