"""
Author: Mohit Mayank

Load and return dataset
"""

# imports
import os
import pandas as pd

# data load and return function
def load_network_data(__edge_filename__, __node_filename__, filter_conections_threshold=10):
    """Load the first book of the Got Dataset

    Parameters
    -----------
    filter_conections_threshold: int
        keep the connections in GoT dataset with weights greater than this threshold 
    """
    # resolve path
    this_dir, _ = os.path.split(__file__)

    # load the edge and node data
    edge_df = pd.read_csv(os.path.join(this_dir, __edge_filename__))
    node_df = pd.read_csv(os.path.join(this_dir, __node_filename__))

    # return
    return edge_df, node_df