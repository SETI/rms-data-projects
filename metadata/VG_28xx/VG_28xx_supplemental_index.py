################################################################################
# vg_28xx_supplement.py: Generates all supplemental indices for Voyager ring
# profiles.
#
# Usage:
#   python vg_28xx_supplement.py .../holdings/volumes/VG_28xx*/VG_2801 ...
################################################################################

import numpy as np
import os, sys
import pdsparser

############################################
# Method to define prefix text for table
############################################

def volume_and_filespec(root, name):
    """Returns the volume_id and file_specification_name for a label file.
    """

    ivol = root.rindex("VG_28")
    volume_id = root[ivol:ivol+7]
    dir_path = root[ivol+8:]

    file_spec = "%s/%s" % (dir_path, name)
    file_spec = (file_spec + 54*" ")[:54]
    return (volume_id, file_spec)

############################################

OCCULTATION_TYPES = {
    'VG_2801': 'STELLAR',
    'VG_2802': 'STELLAR',
    'VG_2803': 'RADIO',
    'VG_2810': 'REFLECTANCE',
}

WAVELENGTH_BANDS = {
    'VG_2801': ('UV', 'N/A'),
    'VG_2802': ('UV', 'N/A'),
    'VG_2803': None,
    'VG_2810': ('VISUAL', 'N/A'),
}

EARTH_RECEIVED_TIMES = {
    'C3493405.IMQ': '1980-11-12T17:14:09',
    'C3493409.IMQ': '1980-11-12T17:17:21',
    'C3493413.IMQ': '1980-11-12T17:20:33',
    'C3493417.IMQ': '1980-11-12T17:23:45',
    'C3493421.IMQ': '1980-11-12T17:26:57',
    'C3493425.IMQ': '1980-11-12T17:30:09',
    'C3493429.IMQ': '1980-11-12T17:33:21',
    'C3493433.IMQ': '1980-11-12T17:36:33',
    'C3493437.IMQ': '1980-11-12T17:39:45',
    'C3493441.IMQ': '1980-11-12T17:42:57',
    'C3493445.IMQ': '1980-11-12T17:46:09',
    'C3493449.IMQ': '1980-11-12T17:49:21',
    'C3493453.IMQ': '1980-11-12T17:52:33',
    'C3493457.IMQ': '1980-11-12T17:55:45',
    'C3493501.IMQ': '1980-11-12T17:58:57',
    'C3493505.IMQ': '1980-11-12T18:02:09',
    'C3493509.IMQ': '1980-11-12T18:05:21',
    'C3493513.IMQ': '1980-11-12T18:08:33',
    'C3493517.IMQ': '1980-11-12T18:11:45',
    'C3493535.IMQ': '1980-11-12T18:26:09',
    'C3493539.IMQ': '1980-11-12T18:29:21',
    'C3493543.IMQ': '1980-11-12T18:32:33',
    'C3493549.IMQ': '1980-11-12T18:37:21',
    'C3493553.IMQ': '1980-11-12T18:40:33',
    'C4399346.IMQ': '1981-08-25T19:21:42',
    'C4399350.IMQ': '1981-08-25T19:24:54',
    'C4399354.IMQ': '1981-08-25T19:28:06',
    'C4399358.IMQ': '1981-08-25T19:31:18',
    'C4399402.IMQ': '1981-08-25T19:34:30',
    'C4399406.IMQ': '1981-08-25T19:37:42',
    'C4399410.IMQ': '1981-08-25T19:40:54',
    'C4399416.IMQ': '1981-08-25T19:45:42',
    'C4399420.IMQ': '1981-08-25T19:48:54',
    'C4399424.IMQ': '1981-08-25T19:52:06',
    'C4399428.IMQ': '1981-08-25T19:55:18',
    'C4399432.IMQ': '1981-08-25T19:58:30',
    'C4399436.IMQ': '1981-08-25T20:01:42',
    'C4399440.IMQ': '1981-08-25T20:04:54',
    'C4399444.IMQ': '1981-08-25T20:08:06',
    'C4399450.IMQ': '1981-08-25T20:12:54',
    'C4399454.IMQ': '1981-08-25T20:16:06',
    'C4399458.IMQ': '1981-08-25T20:19:18',
    'C4399502.IMQ': '1981-08-25T20:22:30',
    'C4399506.IMQ': '1981-08-25T20:25:42',
}

def index_one_file(root, name, supplement):

    COLUMNS = [
        ("DATA_SET_ID"                  , 1, 35, '"%-33s"', None,    'N/A'),
        ("PRODUCT_CREATION_TIME"        , 1, 21, '"%-19s"', None,    'N/A'),
        ("SPACECRAFT_NAME"              , 1, 11, '"%-9s"' , None,    'N/A'),
        ("INSTRUMENT_ID"                , 1, 10, '"%-8s"' , None,    'N/A'),
        ("OCCULTATION_TYPE"             , 1, 13, '"%-11s"', None,    'N/A'),
        ("PLANETARY_OCCULTATION_FLAG"   , 1,  3, '"%-1s"' , None,    'N'  ),
        ("WAVELENGTH_BAND"              , 2,  8, '"%-6s"' , None,    'N/A'),
        ("WAVELENGTH"                   ,-2, 11, '%11.4f' , None,    -99. ),
        ("EARTH_RECEIVED_START_TIME"    , 1, 25, '"%-23s"', None,    'UNK'),
        ("EARTH_RECEIVED_STOP_TIME"     , 1, 25, '"%-23s"', None,    'UNK'),
        ("RING_EVENT_START_TIME"        , 1, 25, '"%-23s"', None,    'N/A'),
        ("RING_EVENT_STOP_TIME"         , 1, 25, '"%-23s"', None,    'N/A'),
        ("MINIMUM_RING_RADIUS"          , 1, 12, '%12.5f' , None,    -99. ),
        ("MAXIMUM_RING_RADIUS"          , 1, 12, '%12.5f' , None,    -99. ),
        ("RADIAL_RESOLUTION"            ,-2,  7, '%7.3f'  , None,    -99. ),
        ("INCIDENCE_ANGLE"              , 1, 10, '%10.6f' , None,    -99. ),
        ("EMISSION_ANGLE"               ,-2,  6, '%6.2f'  , None,    -99. ),
        ("PHASE_ANGLE"                  ,-2,  6, '%6.2f'  , None,    -99. ),
        ("RECEIVER_HOST_NAME"           , 1, 11, '"%-9s"' , None,    'N/A'),
        ("SIGNAL_SOURCE_NAME"           , 2, 11, '"%-9s"' , None,    'N/A'),
        ("TEMPORAL_SAMPLING_INTERVAL"   , 1,  6, '%6.2f'  , None,    -99. ),
]

    (volume_id, file_spec) = volume_and_filespec(root, name)
    supplement.write('"%s","%s"' % (volume_id, file_spec))

    if name.endswith('.LBL'):
        label = pdsparser.PdsLabel.from_file(os.path.join(root, name)).as_dict()
    elif name.endswith('.IMQ'):

        start_ert = EARTH_RECEIVED_TIMES[name]
        hh = int(start_ert[11:13])
        mm = int(start_ert[14:16])
        ss = int(start_ert[17:19])
        ss += 3 * 48
        carry = ss//60
        ss -= carry * 60
        mm += carry
        carry = mm//60
        mm -= carry * 60
        hh += carry
        stop_ert = start_ert[:11] + '%02d:%02d:%02d' % (hh,mm,ss)

        label = {
            'SPACECRAFT_NAME': 'VOYAGER 1' if name.startswith('C3') else 'VOYAGER 2',
            'INSTRUMENT_ID': 'ISSN',
            'EARTH_RECEIVED_START_TIME': start_ert,
            'EARTH_RECEIVED_STOP_TIME': stop_ert,
        }

    if 'SPICE' not in root:
        label['WAVELENGTH_BAND']  = WAVELENGTH_BANDS[volume_id]
        label['RECEIVER_HOST_NAME'] = label['SPACECRAFT_NAME']
        label['OCCULTATION_TYPE'] = OCCULTATION_TYPES[volume_id]

        if 'STAR_NAME' in label:
            label['SIGNAL_SOURCE_NAME'] = label['STAR_NAME']

    if 'IMAGES' in root and name.startswith('C'):
        label['WAVELENGTH_BAND'] = ('VISUAL', 'N/A')
        label['WAVELENGTH'] = (0.28, 0.64)

    if 'INCIDENCE_ANGLE' in label:
        if 'EMISSION_ANGLE' not in label:
            formatted = '%6.2f' % (180. - label['INCIDENCE_ANGLE'])
            label['EMISSION_ANGLE'] = float(formatted)
        if 'PHASE_ANGLE' not in label:
            label['PHASE_ANGLE'] = 180.

    if volume_id == 'VG_2801':
        if 'INSTRUMENT_MODE_ID' in label:
            if 'OC1' in label['INSTRUMENT_MODE_ID']:
                label['TEMPORAL_SAMPLING_INTERVAL'] = 0.01
            elif 'GS3' in label['INSTRUMENT_MODE_ID']:
                label['TEMPORAL_SAMPLING_INTERVAL'] = 0.6

    if volume_id == 'VG_2802':
        if 'SPICE' not in root:
            label['TEMPORAL_SAMPLING_INTERVAL'] = 0.32

        if 'MINIMUM_WAVELENGTH' in label:
            label['WAVELENGTH'] = (label['MINIMUM_WAVELENGTH'],
                                   label['MAXIMUM_WAVELENGTH'])

    if volume_id == 'VG_2803':
        if 'SPICE' in root:
            label['WAVELENGTH_BAND'] = 'N/A'
        elif name[5] == 'X':
            label['WAVELENGTH_BAND'] = 'X-BAND'
            if 'WAVELENGTH' not in label:
                label['WAVELENGTH'] = 35625.9810
        elif name[5] == 'S':
            label['WAVELENGTH_BAND'] = 'S-BAND'
            if 'WAVELENGTH' not in label:
                label['WAVELENGTH'] = 130628.5950
        elif name[5] == 'B':
            label['WAVELENGTH_BAND'] = ('X-BAND', 'S-BAND')
            label['WAVELENGTH'] = -99.
        else:
            raise ValueError('Unrecognized RSS band: ' + name)

        if 'RADIAL_SAMPLING_INTERVAL' in label:
            label['RADIAL_RESOLUTION'] = label['RADIAL_SAMPLING_INTERVAL']

        if 'SPICE' not in root:
            label['SIGNAL_SOURCE_NAME'] = label['SPACECRAFT_NAME']

        if name.startswith('RS'):
            label['RECEIVER_HOST_NAME'] = 'DSN-63'
            if ('INCIDENCE_ANGLE' not in label and 'DATA' in root):
                label['INCIDENCE_ANGLE'] = 84.0746
                label['EMISSION_ANGLE'] = 180. - 84.07
                label['PHASE_ANGLE'] = 180

        elif name.startswith('RU'):
            label['RECEIVER_HOST_NAME'] = 'DSN-43'
        else:
            label['RECEIVER_HOST_NAME'] = 'N/A'

    if volume_id == 'VG_2810':
        label['WAVELENGTH'] = (0.28, 0.64)

        if name.startswith('IS1_'):
            label['PHASE_ANGLE'] = (45.01, 48.21)
            label['EMISSION_ANGLE'] = (99.11, 104.64)
        elif name.startswith('IS2_'):
            label['PHASE_ANGLE'] = (45.74, 48.16)
            label['EMISSION_ANGLE'] = (66.22, 67.08)

        label['SIGNAL_SOURCE_NAME'] = 'RINGS'
        label['DATA_SET_ID'] = 'VG1/VG2-SR-ISS-4-PROFILES-V1.0'

    for info in COLUMNS:
        key = info[0]
        if key in label:
            value = label[key]
        else:
            value = info[-1]

        supplement.write("," + format_col(value, *info))

    supplement.write('\r\n')

def format_col(value, name, count, width, fmt0, fmt1, nullval):

    if count == -2:
        if not isinstance(value, (list,tuple)):
            value = [value, value]
        count = 2

    if count > 1:
        if isinstance(value, set):
            value = list(value)
            print('SET!')

        if not isinstance(value, (list,tuple)):
            value = [value] + (count-1) * [nullval]
        else:
            assert len(value) == count

        fmt_list = []
        for item in value:
            result = format_col(item, name, 1, width, fmt0, fmt1, nullval)
            fmt_list.append(result)

        return ",".join(fmt_list)

    if value in ("N/A", "UNK") and not isinstance(nullval, str):
        value = nullval

    if isinstance(value, str):
        value = value.strip()
        value = value.replace('\n', ' ')
        while ('  ' in value):
            value = value.replace('  ', ' ')

    try:
        result = fmt0 % value
    except TypeError:
        print "**** WARNING: Invalid format: ", name, value, fmt0
        result = width * "*"

    if len(result) > width:
        if fmt1 is None:
            print "**** WARNING: No second format: ", name, value, fmt0, result
        else:
            result = fmt1 % value
            if len(result) > width:
                print "**** WARNING: Value too wide: ", name, value, fmt1

    try:
        test = eval(result)
    except Exception:
        print "**** WARNING: Eval failure: ", name, value, result
        test = nullval
    else:
        if isinstance(test, str):
            test = test.rstrip()

    if test != value and test != nullval and test != str(value):
        print "**** WARNING: Value has changed: ", name, value, fmt0, fmt1, result

    return result

############################################
# Finally, generate the indices...
############################################

input_dir = sys.argv[1]
output_dir = sys.argv[2]

ivol = input_dir.rfind('VG_28')
volname = input_dir[ivol:ivol+7]

prefix = os.path.join(output_dir, volname)

print prefix + "_supplemental_index.tab"
supplement = open(prefix + "_supplemental_index.tab", "w")

# Walk the directory tree...
for (root, dirs, files) in os.walk(input_dir):

  if 'CATALOG' in root: continue
  if 'DOCUMENT' in root: continue
  if 'INDEX' in root: continue
  if 'SOFTWARE' in root: continue

  for name in files:

    # Ignore any file that is not a label
    if name.endswith(".LBL") or name.endswith(".IMQ"):
        print '    ', root, name
        index_one_file(root, name, supplement)

# Close all files
supplement.close()

################################################################################

