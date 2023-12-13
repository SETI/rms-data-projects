################################################################################
# index_config.py for GLL SSI
#
#  Host-specific utilites and key functions.
#
################################################################################
import os


################################################################################
# Utilities
################################################################################

#===============================================================================
def get_volume_id(label_path):
    """Edit this function to determine the volume ID for this collection.

    Inputs:
        label_path      Path to the PDS label.
    """
    top = 'GO_0xxx'
    return label_path.split(top)[1].split('/')[1]


################################################################################
# Key functions
################################################################################

#===============================================================================
def key__test_column(label_path, label_dict):
    """Sample key function for a hypothetical keyword named TEST_COLUMN.  
    
    Inputs:
        label_path        Path to the PDS label.
        label_dict        Dictionary containing the PDS label fields.

    The return value will appear in the index file under TEST_COLUMN.
    """
    return 'xxxxxxx'


