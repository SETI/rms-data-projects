################################################################################
# covims_supplement.py: Generates all supplemental indices for Cassini VIMS
#
# Usage:
#   python COVIMS_supplement.py .../holdings/volumes/COVIMS/COVIMS_00xx ...
################################################################################

import numpy as np
import os, sys
import pdsparser

############################################
# Method to define prefix text for table
############################################

def volume_and_filespec(root, name):
    """Returns the volume_id and file_specification_name for a VIMS label file.
    """

    ivol = root.rindex("COVIMS_00")
    volume_id = root[ivol:ivol+11]
    dir_path = root[ivol+12:ivol+48]

    if len(dir_path) > ivol + 48:
        raise ValueError("Illegal directory path: ", dir_path)

    file_spec = "%s/%-22s" % (dir_path, name)
    return (volume_id, file_spec)

############################################

def index_one_file(root, name, supplement):

    COLUMNS = [
        ("MISSION_PHASE_NAME"           , 1, 30, '"%-28s"', None,    'UNK'),
        ("PRODUCT_VERSION_TYPE"         , 1, 13, '"%-11s"', None,    'UNK'),
        ("FLIGHT_SOFTWARE_VERSION_ID"   , 1,  5, '"%-3s"' , None,    'UNK'),
        ("SOFTWARE_VERSION_ID"          , 1, 22, '"%-20s"', None,    'UNK'),
        ("TARGET_DESC"                  , 1, 30, '"%-28s"', None,    'UNK'),
        ("IMAGE_OBSERVATION_TYPE"       ,-3, 13, '"%-11s"', None,    'N/A'),
        ("NATIVE_START_TIME"            , 1, 18, '"%-16s"', None,    'UNK'),
        ("NATIVE_STOP_TIME"             , 1, 18, '"%-16s"', None,    'UNK'),
        ("HOUSEKEEPING_CLOCK_COUNT"     , 1, 15, '"%-13s"', None,    'UNK'),
        ("PRODUCT_CREATION_TIME"        , 1, 19, '"%-17s"', None,    'UNK'),
        ("COMMAND_FILE_NAME"            , 1, 43, '"%-41s"', None,    'UNK'),
        ("COMMAND_SEQUENCE_NUMBER"      , 1,  3, '%3d'    , None,    -99  ),
        ("EARTH_RECEIVED_START_TIME"    , 1, 23, '"%-21s"', None,    'UNK'),
        ("EARTH_RECEIVED_STOP_TIME"     , 1, 23, '"%-21s"', None,    'UNK'),
        ("MISSING_PACKET_FLAG"          , 1,  5, '"%-3s"' , None,    'UNK'),
        ("DESCRIPTION"                  , 1, 95, '"%-93s"', None,    'N/A'),
        ("PARAMETER_SET_ID"             , 1, 36, '"%-34s"', None,    'UNK'),
        ("SEQUENCE_TITLE"               , 1, 31, '"%-29s"', None,    'UNK'),
        ("TELEMETRY_FORMAT_ID"          , 1, 12, '"%-10s"', None,    'UNK'),
#         ("DATA_REGION"                  , 1,  5, '"%-3s"' , None,    'UNK'),
        ("OVERWRITTEN_CHANNEL_FLAG"     , 1,  5, '"%-3s"' , None,    'UNK'),
        ("INTERFRAME_DELAY_DURATION"    , 1,  7, '%7.1f'  , None,    -999.),
        ("COMPRESSOR_ID"                , 1,  3, '%3d'    , None,    -99  ),
        ("INST_CMPRS_NAME"              , 1,  9, '"%-7s"' , None,    'UNK'),
        ("INST_CMPRS_RATIO"             , 1, 11, '%11.6f' , '%11.3f',-999.),
        ("DATA_BUFFER_STATE_FLAG"       , 1, 10, '"%-8s"' , None,    'UNK'),
        ("INSTRUMENT_DATA_RATE"         , 1, 11, '%11.6f' , None,    -999.),
        ("MISSING_PIXELS"               , 1,  7, '%7d'    , None,    -99  ),
        ("POWER_STATE_FLAG"             , 2,  5, '"%-3s"' , None,    'UNK'),
        ("GAIN_MODE_ID"                 , 2,  6, '"%-4s"' , None,    'N/A'),
        ("BACKGROUND_SAMPLING_MODE_ID"  ,-2, 10, '"%-8s"' , None,    'N/A'),
        ("X_OFFSET"                     , 1,  3, '%3d'    , None,    -99  ),
        ("Z_OFFSET"                     , 1,  3, '%3d'    , None,    -99  ),
        ("OFFSET_FLAG"                  , 1,  5, '"%-3s"' , None,    'UNK'),
        ("SNAPSHOT_MODE_FLAG"           , 1,  5, '"%-3s"' , None,    'UNK'),
        ("PACKING_FLAG"                 , 1,  5, '"%-3s"' , None,    'UNK'),
        ("DETECTOR_TEMPERATURE"         , 3, 10, '%10.6f' , "%10.5f",-999.),
        ("OPTICS_TEMPERATURE"           , 3, 10, '%10.6f' , "%10.5f",-999.),
        ("BIAS_STATE_ID"                , 1,  6, '"%-4s"' , None,    'UNK'),
        ("SCAN_MODE_ID"                 , 1,  7, '"%-5s"' , None,    'UNK'),
        ("SHUTTER_STATE_FLAG"           , 1, 10, '"%-8s"' , None,    'UNK'),
        ("INTEGRATION_DELAY_FLAG"       , 1, 10, '"%-8s"' , None,    'UNK'),
        ("INTERLINE_DELAY_DURATION"     , 1,  7, '%7.1f'  , None,    -99. ),
        ("BACKGROUND_SAMPLING_FREQUENCY", 1,  3, '%3d'    , None,    -99  ),
        ("INSTRUMENT_TEMPERATURE"       , 2, 10, '%10.6f' , "%10.5f",-999.),
        ("FAST_HK_ITEM_NAME"            ,-4, 29, '"%-27s"', None,    'N/A'),
        ("FAST_HK_PICKUP_RATE"          , 1,  3, '%3d'    , None,    -99  ),
        ("ANTIBLOOMING_STATE_FLAG"      , 1,  5, '"%-3s"' , None,    'UNK')]

    (volume_id, file_spec) = volume_and_filespec(root, name)
    supplement.write('"%s","%s"' % (volume_id, file_spec))

    # Read the PDS3 label and the ISIS2 header, fixing known syntax errors
    with open(os.path.join(root, name)) as f:
        label_text = f.read()

    # Add missing quotes around N/A in many labels
    label_text = label_text.replace('" N/A"', ' "N/A"')
    label_text = label_text.replace(' N/A', ' "N/A"')
    label_text = label_text.replace('(N/A', '("N/A"')
    label_text = label_text.replace(',N/A', ',"N/A"')

    # Handle multi-line comments
    recs = label_text.split('\n')
    changed = False
    for k,rec in enumerate(recs):
        if '/*' in rec and '*/' not in rec:
            recs[k] = rec[:-2] + '*/' + rec[-2:]
            changed = True
        if '*/' in rec and '/*' not in rec:
            recs[k] = '/*' + rec
            changed = True

    if changed:
        label_text = '\n'.join(recs)

    label_text = label_text.replace('\r','') # pyparsing is not set up for <CR>

    label = pdsparser.PdsLabel.from_string(label_text).as_dict()

    test = label['IMAGE_OBSERVATION_TYPE']
    if isinstance(test, list):
        if len(test) == 0:
            label['IMAGE_OBSERVATION_TYPE'] = 'UNK'
        elif len(test) == 1:
            label['IMAGE_OBSERVATION_TYPE'] = test[0]
        else:
            pass

    # strip ".000" from time
    label['PRODUCT_CREATION_TIME'] = label['PRODUCT_CREATION_TIME'][:17]

    for info in COLUMNS:
        supplement.write("," + format_col(label[info[0]], *info))

    supplement.write('\r\n')

def format_col(value, name, count, width, fmt0, fmt1, nullval):

    if count < 0:
        if not isinstance(value, list):
            value = [value]

        count = -count
        while len(value) < count:
            value.append(nullval)

    if count > 1:
        if not isinstance(value, (list,tuple)):
            assert value in ("N/A", "UNK")
            value = count * ["N/A"]
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

ivol = input_dir.rfind('COVIMS_')
volname = input_dir[ivol:ivol+11]

prefix = os.path.join(output_dir, volname)
data_dir = os.path.join(input_dir, 'data')

print prefix + "_supplemental_index.tab"
supplement = open(prefix + "_supplemental_index.tab", "w")

# Walk the directory tree...
for (root, dirs, files) in os.walk(data_dir):
  for name in files:

    # Ignore any file that is not a label
    if not name.lower().endswith(".lbl"): continue

    print '    ', root, name
    index_one_file(root, name, supplement)

# Close all files
supplement.close()

################################################################################

