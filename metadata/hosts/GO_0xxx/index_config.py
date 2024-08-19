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
def _add_by_base(x_digits, y_digits, bases):           ### move to utilities
    import math

    result = [0]*(len(bases)+1)
    for i, (x_digit, y_digit, base) in \
        enumerate(zip(reversed(x_digits), reversed(y_digits), reversed(bases))):
        result[i] += (x_digit + y_digit) % base
        result[i+1] += (x_digit + y_digit) // base
    return list(reversed(result))

#===============================================================================
def _rebase(x, bases, ceil=False):           ### move to utilities
    import math

    digits = []
    for base in reversed(bases):
        digit = x % base
        if not ceil:
            digit = int(digit)
        else:
            digit = math.ceil(digit)
        digits.append(digit)

        x //= base
    return (list(reversed(digits)),x)

#===============================================================================
def _sclk_split_count(count, delim='.'):
    fields = list(map(int, (count.split(delim))))
    fields = fields + [0,0,0,0]
    return fields[0:4]

#===============================================================================
def _sclk_format_count(fields, format):

    # Get delimiters
    delims = [c for c in format if not c.isalnum()] + ['']

    # Get field formats (i.e. field widths)
    f = "".join([s if s.isalnum() else '/' for s in format])
    formats = f.split('/')
    widths = [len(f) for f in formats]

    # Build count string
    count = ''
    for delim, width, field in zip(delims, widths, fields):
        s = f'{field}'
        count += '0'*(width-len(s)) + s + delim

    return count

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
def _spacecraft_time(label_path, label_dict, stop=False):
    """Utility function for start/stop times.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.
        stop              If False, the start time is returned.

    Output: the requested clock count.
    """
    tai = _event_tai(label_path, label_dict, stop=stop)
    if tai == 'UNK':
        return tai

    et = julian.tdb_from_tai(tai)

    return cspyce.scdecd(-77, et)

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
def _spacecraft_clock_start_count_from_image_time(label_path, label_dict):
    """Function for SPACECRAFT_CLOCK_START_COUNT using the IMAGE_TIME field.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_START_COUNT.
    """
    return _spacecraft_clock_count(label_path, label_dict, stop=False)

#===============================================================================
def _spacecraft_clock_stop_count_from_image_time(label_path, label_dict):
    """Function for SPACECRAFT_CLOCK_STOP_COUNT using the IMAGE_TIME field.

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_STOP_COUNT.
    """
    return _spacecraft_clock_count(label_path, label_dict, stop=True)

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
    start_fields = _sclk_split_count(start_count)
    return _sclk_format_count(start_fields, 'nnnnnnnn:nn:n:n')

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
    start_fields = _sclk_split_count(start_count)

    exposure = label_dict['EXPOSURE_DURATION'] / 1000
    exposure_ticks = exposure*120
    exposure_fields,over = _rebase(exposure_ticks, [16777215,91,10,8], ceil=True)

    stop_fields = _add_by_base(start_fields, exposure_fields, [16777215,91,10,8])
    return _sclk_format_count(stop_fields[1:], 'nnnnnnnn:nn:n:n')


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
#    return _spacecraft_clock_start_count_from_image_time(label_path, label_dict)
    return _spacecraft_clock_start_count_from_label(label_path, label_dict)

#===============================================================================
def key__spacecraft_clock_stop_count(label_path, label_dict):
    """Key function for SPACECRAFT_CLOCK_STOP_COUNT.  

    Inputs:
        label_path        path to the PDS label.
        label_dict        dictionary containing the PDS label fields.

    The return value will appear in the index file under SPACECRAFT_CLOCK_STOP_COUNT.
    """
#    return _spacecraft_clock_stop_count_from_image_time(label_path, label_dict)
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

