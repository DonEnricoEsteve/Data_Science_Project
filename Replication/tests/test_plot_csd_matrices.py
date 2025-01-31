# Import necessary libraries
import pytest
from conftest import *  # Just imported it manually to ensure

### ===== Test Configuration Import ===== ###
def test_imports():
    assert epo_path, "epo_path is None"
    assert csd_path, "csd_path is None"

### ===== Test Valid Inputs ===== ###
@pytest.mark.parametrize("cond, sub_idx, mode_val, meg_val", [
    ("face", 0, "csd", "grad"),
    ("scrambled", 0, "coh", "grad"),
])
def test_plot_csd_valid(cond, sub_idx, mode_val, meg_val):
    plot_csd_matrices(cond, sub_idx, mode_val, meg_val)
    assert plt.gcf(), "No figure was generated."

### ===== Test One Invalid Input ===== ###
def test_plot_csd_invalid():
    with pytest.raises(ValueError):
        plot_csd_matrices("invalid_condition", 0, "csd", "grad")