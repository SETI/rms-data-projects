################################################################################
# index_config.py for GLL SSI
#
#  Host-specific utilites and key functions.
#
################################################################################
import os
import julian
import vicar
import cspyce
import warnings

from pathlib import Path
import metadata as meta

cspyce.furnsh('leapseconds.ker')
cspyce.furnsh('mk00062a.tsc')


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
    return meta.splitpath(label_path, top)[1].parts[0]

#===============================================================================
def _spacecraft_clock_count(label_path, label_dict, stop=False):
    """Utility function for SCLK times.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.
        stop              If False, the start count is returned.

    Output: the requested clock count.
    """
    tai = _event_tai(label_path, label_dict, stop=stop)
    if tai == 'UNK':
        return tai

    et = julian.tdb_from_tai(tai)

    dp =  cspyce.sce2c(-77, et)
    return cspyce.scdecd(-77, dp)

#===============================================================================
def _event_tai(label_path, label_dict, stop=False):
    """Utility function for start/stop times.  FOR GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.
        stop              If False, the start time is returned.

    Output: the requested TAI time.
    """
    # get IMAGE_TIME; pass though any NULL value
    image_time = label_dict['IMAGE_TIME']
    if image_time == 'UNK':
        return image_time
    image_tai = julian.tai_from_iso(image_time)

    # compute offset from IMAGE_TIME
    exposure = label_dict['EXPOSURE_DURATION'] / 1000
    sign = 2*(int(stop)-0.5)
    
    # offset to requested time
    return image_tai + sign*0.5*exposure


################################################################################
# Key functions
################################################################################

#===============================================================================
def key__product_creation_time(label_path, label_dict):
    """Key function for PRODUCT_CREATION_TIME.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under PRODUCT_CREATION_TIME.
    """
    # Get path for VICAR image
    image_path = Path(os.path.splitext(label_path.as_posix())[0] + '.IMG')
#xx    image_path = label_path.removesuffix.with_suffix('.img'))   # Doesn't work in 3.8

    # Read the VICAR label and take the latest DAT_TIM value
    try:
        viclab = vicar.VicarLabel.from_file(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(image_path)
    except vicar.VicarError as err:
        warnings.warn(f'VICAR error in file {image_path}, PRODUCT_CREATION_TIME cannot be determined: {err}', RuntimeWarning)
        return None

    pct = viclab['DAT_TIM', -1]

    # Convert to ISO format
    pct = pct[20:] + pct[3:20]

    return julian.iso_from_tai(
                julian.tai_from_day_sec(
                *julian.day_sec_in_strings(pct, first=True)), digits=3, suffix='Z')

#===============================================================================
def key__start_time(label_path, label_dict):
    """Key function for START_TIME.  For GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under START_TIME.
    """
    # get start tai; pass though any NULL value
    start_tai = _event_tai(label_path, label_dict)
    if start_tai == 'UNK':
        return start_tai
    start_time = julian.iso_from_tai(start_tai, digits=3, suffix='Z')

    return start_time

#===============================================================================
def key__stop_time(label_path, label_dict):
    """Key function for STOP_TIME.  For GOSSI, IMAGE_TIME refers to
    the center of the exposure.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under STOP_TIME.
    """
    stop_tai = _event_tai(label_path, label_dict, stop=True)
    if stop_tai == 'UNK':
        return stop_tai
    stop_time = julian.iso_from_tai(stop_tai, digits=3, suffix='Z')

    return stop_time

#===============================================================================
def key__spacecraft_clock_start_count(label_path, label_dict):
    """Key function for SPACECRAFT_CLOCK_START_COUNT.  Note this
       definition supercedes that in the default index file.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_START_COUNT.
    """
    return _spacecraft_clock_count(label_path, label_dict, stop=False)

#===============================================================================
def key__spacecraft_clock_stop_count(label_path, label_dict):
    """Key function for SPACECRAFT_CLOCK_STOP_COUNT.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_STOP_COUNT.
    """
    return _spacecraft_clock_count(label_path, label_dict, stop=True)

################################################################################

