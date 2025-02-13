# Define the __all__ variable

__all__ = ["convert_mat_to_dict", "convert_dict_to_epochs", "convert_mat_to_epochs", \
    "create_events_for_epochs", "extract_from_dict", "remove_oddball_trials", "combine_epochs", \
       "create_mne_info", "extract_raw_info"]

# Import the submodules
from mat_to_epochs_conversion.convert_main_funcs import convert_mat_to_dict, convert_dict_to_epochs, convert_mat_to_epochs
from mat_to_epochs_conversion.create_events_for_epochs import create
from mat_to_epochs_conversion.extract_from_dict import extract
from mat_to_epochs_conversion.remove_oddball_trials import remove
from mat_to_epochs_conversion.combine_epochs import combine_epochs
from mat_to_epochs_conversion.create_info import create_mne_info, extract_raw_info