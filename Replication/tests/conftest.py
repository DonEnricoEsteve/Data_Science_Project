# Import necessary libraries
import sys
import os
import pytest
import mne
import importlib
import matplotlib.pyplot as plt

# Add the Replication/src directory to the Python path so it can find the config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from replication_config import *
from plot_replicated_files import *
