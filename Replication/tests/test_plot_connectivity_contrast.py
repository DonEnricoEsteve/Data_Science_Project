# Import necessary libraries
import pytest
from conftest import *  # Just imported it manually to ensure

### ===== Test Valid Inputs ===== ###
@pytest.mark.parametrize("summary_val, hemi_val", [
    ("degree", "both"),
    ("degree", "lh"),
    ("degree", "rh"),
])
def test_plot_connectivity_contrast_valid(summary_val, hemi_val):
    try:
        plot_connectivity_contrast(summary_val=summary_val, hemi_val=hemi_val)
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {e}")

### ===== Test Invalid Condition: Invalid Summary Value ===== ###
def test_plot_connectivity_contrast_invalid_summary():
    with pytest.raises(ValueError):
        plot_connectivity_contrast(summary_val="invalid_summary", hemi_val="both")
