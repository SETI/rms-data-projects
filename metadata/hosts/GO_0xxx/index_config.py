################################################################################
# index_config.py for GLL SSI
#
#  Host-specific utilites and key functions.
#
################################################################################
import os
import julian
import cspyce

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
def __event_tai(label_path, label_dict, stop=False):
    """Utility function for start/stop times.  FOR GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under START_TIME.
    """
    # get IMAGE_TIME; pass though any NULL value
    image_time = label_dict['IMAGE_TIME']
    try:
        image_tai = julian.tai_from_iso(image_time)
    except:
        return image_time

    # compute offset from IMAGE_TIME
    exposure = label_dict['EXPOSURE_DURATION'] / 1000
    sign = 2*(int(stop)-0.5)
    
    # offset to requested time
    return image_tai + sign*0.5*exposure

#===============================================================================
def key__start_time(label_path, label_dict):
    """Key function for START_TIME.  FOR GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under START_TIME.
    """
    return julian.iso_from_tai(__event_tai(label_path, label_dict), 
                               digits=3, suffix='Z')

#===============================================================================
def key__stop_time(label_path, label_dict):
    """Key function for STOP_TIME.  FOR GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under START_TIME.
    """
    return julian.iso_from_tai(__event_tai(label_path, label_dict, stop=True),
                               digits=3, suffix='Z')

#===============================================================================
def key__spacecraft_stop_count(label_path, label_dict):
    """Key function for SPACECRAFT_STOP_COUNT.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under START_TIME.
    """
    # get stop time
    from IPython import embed; print('+++++++++++++'); embed()
    cspyce.furnsh('leapseconds.ker')
    cspyce.furnsh('mk00062a.tsc')
    stop_et = julian.tdb_from_tai(__event_tai(label_path, label_dict, stop=False))
    stopdp =  cspyce.sce2c(-77, stop_et)
#    cspyce.scfmt(-77, stopdp)

################################################################################

