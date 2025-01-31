# Import necessary libraries
import pytest
from conftest import *  # Just imported it manually to ensure

### ===== Test Configuration Import ===== ###
def test_imports():
    assert fwd_path, "fwd_path is None"
    assert fwd_r_path, "fwd_r_path is None"
    assert trans_path, "trans_path is None"

# Valid Test: Ensure that the function works with correct inputs
@pytest.mark.parametrize("sub_idx, meg_val, surface_val", [
    (0, "sensors", "white"),
])
def test_plot_source_space_valid(sub_idx, meg_val, surface_val):
    plot_source_space(sub_idx, meg_val, surface_val)

# Invalid Test: Ensure that the function raises an error for invalid subject index
def test_plot_source_space_invalid_sub_idx():
    with pytest.raises(IndexError):
        plot_source_space(sub_idx=99, meg_val='sensors', surface_val='white')