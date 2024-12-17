################################################################################
# config.py for GLL SSI
#
#  Host-specific utilites and key functions.
#
################################################################################
import os, sys, traceback
import julian
import vicar
import warnings

from pathlib import Path

import oops
import hosts.galileo.ssi as ssi
import metadata as meta


SCLK_BASES = [16777215,91,10,8]
SAMPLING = 8                        # pixel sampling density

ssi.initialize()
################################################################################
# SCLK-dependent mission-specific data.
################################################################################
SYSTEMS_TABLE = [
#      SCLK_START range (inclusive)   SYSTEM      SECONDARIES
    (('00180626.00', '00190641.00'), 'VENUS',     []),
    (('00594697.00', '00623035.00'), 'EARTH',     []), 
#    (('00997579.45', '01073185.13'), 'GASPRA',    []), 
    (('01645330.00', '01663247.00'), 'EARTH',     []), 
#    (('02025307.00', '02025628.00'), 'IDA',       []), 
#    (('03464059.00', '06475387.00'), 'JUPITER',   ['IO', 'EUROPA', 'GANYMEDE', 'CALLISTO']) ]
    (('03464059.00', '06475387.00'), 'JUPITER',   []) ]


############################################
# Construct the meshgrids
############################################
## TODO: this should be obtainable from the host module
MODE_SIZES  = {"FULL":1,
               "HMA": 1,
               "HIM": 1,
               "IM8": 1,
               "HCA": 1,
               "IM4": 1,
               "XCM": 1,
               "HCM": 1,
               "HCJ": 1,
               "HIS": 2,
               "AI8": 2}

BORDER = 25         # in units of full-size SSI pixels
NAC_PIXEL = 6.0e-6  # approximate full-size SSI pixel in units of radians
EXPAND = BORDER * NAC_PIXEL

MESHGRIDS = {}
for mode in MODE_SIZES.keys():
    pixel_wrt_full = MODE_SIZES[mode]
    pixels = 800 / MODE_SIZES[mode]

    # Define sampling of FOV
    origin = -float(BORDER) / pixel_wrt_full
    limit = pixels - origin

    # Revise the sampling to be exact
    samples = int((limit - origin) / SAMPLING + 0.999)
    under = (limit - origin) / samples

    # Construct the meshgrid
    limit += 0.0001
    meshgrid = oops.Meshgrid.for_fov(ssi.SSI.fovs[mode], origin,
                                     undersample=under, limit=limit, swap=True)
    MESHGRIDS[mode] = meshgrid

MESHGRID_KEY = 'TELEMETRY_FORMAT_ID'

#===============================================================================
def meshgrid(snapshot):
    """Returns the meshgrid given the dictionary derived from the
    SSI index file.
    """
    return MESHGRIDS[snapshot.dict['TELEMETRY_FORMAT_ID']]


################################################################################
# Utilities
################################################################################

#===============================================================================
def get_volume_id(label_path):
    """Edit this function to determine the volume ID for this collection
       using the label path when there is no observation or label available.

    Inputs:
        label_path      Path to the PDS label.
    """
    top = 'GO_0xxx'
    return meta.splitpath(label_path, top)[1].parts[0]

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

#===============================================================================
def _spacecraft_clock_start_count_from_label(label_path, label_dict):
    """Function for SPACECRAFT_CLOCK_START_COUNT using the SPACECRAFT_CLOCK_START_COUNT
       field.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_START_COUNT.
    """
    start_count = label_dict['SPACECRAFT_CLOCK_START_COUNT']
    start_fields = meta.sclk_split_count(start_count)
    return meta.sclk_format_count(start_fields, 'nnnnnnnn:nn:n:n')

#===============================================================================
def _spacecraft_clock_stop_count_from_label(label_path, label_dict):
    """Function for SPACECRAFT_CLOCK_STOP_COUNT using the SPACECRAFT_CLOCK_START_COUNT

       The stop count is computed by adding the exposure time (in ticks)
       to the SPACECRAFT_CLOCK_START_COUNT field.  THe exposure time is rounded
       up to the next tick.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_STOP_COUNT.
    """
    start_count = label_dict['SPACECRAFT_CLOCK_START_COUNT']
    start_fields = meta.sclk_split_count(start_count)

    exposure = label_dict['EXPOSURE_DURATION'] / 1000
    exposure_ticks = exposure*120
    exposure_fields,over = meta.rebase(exposure_ticks, SCLK_BASES, ceil=True)

    stop_fields = meta.add_by_base(start_fields, exposure_fields, SCLK_BASES)
    return meta.sclk_format_count(stop_fields[1:], 'nnnnnnnn:nn:n:n')


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
    image_path = label_path.with_suffix('.IMG') 

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
    start_time = julian.iso_from_tai(start_tai, digits=6, suffix='Z')

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
    stop_time = julian.iso_from_tai(stop_tai, digits=6, suffix='Z')

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
    return _spacecraft_clock_start_count_from_label(label_path, label_dict)

#===============================================================================
def key__spacecraft_clock_stop_count(label_path, label_dict):
    """Key function for SPACECRAFT_CLOCK_STOP_COUNT.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_STOP_COUNT.
    """
    return _spacecraft_clock_stop_count_from_label(label_path, label_dict)

#===============================================================================
def key__image_start_time(label_path, label_dict):
    """Key function for IMAGE_START_TIME.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_START_COUNT.
    """
    return _spacecraft_time(label_path, label_dict, stop=False)

#===============================================================================
def key__image_stop_time(label_path, label_dict):
    """Key function for IMAGE_STOP_TIME.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_START_COUNT.
    """
    return _spacecraft_time(label_path, label_dict, stop=True)

################################################################################


############################################
# SSI geometry functions
############################################

from_index = ssi.from_index

#===============================================================================
def target_name(dict):
    """Returns the target name from the snapshot's dictionary. If the given
    name is "SKY", it checks the CIMS ID and the TARGET_DESC for something
    different."""

    return  dict["TARGET_NAME"]

    target = dict["TARGET_NAME"]
    if target != "SKY": return target

    id = dict["OBSERVATION_ID"]
    abbrev = id[id.index("_"):][4:6]

    if abbrev == "SK":
        desc = dict["TARGET_DESC"]
        if desc in MOON_NAMES:
            return desc

    try:
        return columns.CIMS_TARGET_ABBREVIATIONS[abbrev]
    except KeyError:
        return target

#===============================================================================
def cleanup():
    """Cleanup function for geometry code.  This function is called after
       the geometry table and labels are written, before exiting."""
    pass
################################################################################

