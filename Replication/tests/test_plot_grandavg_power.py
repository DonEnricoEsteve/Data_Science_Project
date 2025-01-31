# Import necessary libraries
import pytest
from conftest import *  # Just imported it manually to ensure

### ===== Test Valid Inputs ===== ###
@pytest.mark.parametrize("cond, views_val, hemi_val", [
    ("contrast", "med", "split"),
])
def test_plot_grandavg_power_valid(cond, views_val, hemi_val):
    plot_grandavg_power(cond=cond, views_val=views_val, hemi_val=hemi_val)

    # Check if the plot is generated (i.e., no exception was raised)
    assert plt.gcf(), "No figure was generated."

### ===== Test Invalid Condition ===== ###
def test_plot_grandavg_power_invalid_cond():
    with pytest.raises(ValueError) as e:
        plot_grandavg_power(cond="invalid_condition", views_val="med", hemi_val="split")