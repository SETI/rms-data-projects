##########################################################################################
# jnojir_status_index.py
##########################################################################################
"""\
This program re-formats the content of a JNOJIR "status" CSV index file in a standard,
consistent format for the RMS node's PDS3 holdings/metadata tree.

To use:
    > python jnojir_status_index.py path/to/status_index.csv ...

The output file is written into the metadata tree with the correct
subdirectory and name. If a file of that name is already present and there is no backup,
the existing file is renamed with the ending "-backup.tab".

This program does not correct any information that is incorrect in the existing index!
It also does not write a label.
"""

import glob
import os
import pathlib
import pdsparser
import pdstemplate
import re
import shutil
import sys

# This is a regular expression selecting the volume ID out of the directory path
VOLUME_ID_REGEX = re.compile(r'(.*?)(JNOJIR_\d\d\d\d)')

# The number of characters in each column, excluding quotes
LENGTHS = [11, 39, 14, 14, 16, 7, 9, 9, 3, 5, 9, 5, 11, 4, 21, 9, 6, 5, 5, 3, 3,
           1, 1, 14, 18, 4, 2, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6,
           6, 6, 6, 6, 6, 1, 5, 8, 1]
TYPES = 'ccffccccififcccciiiiiiiccciifiiiiiiiiiiiffffffffiifi'

VOLUME_ID                    = 0
FILE_SPECIFICATION_NAME      = 1
TIME_TM                      = 2
TIME_SCI_HK                  = 3
COMMAND_FILE_NAME            = 4
ACQ_NAME                     = 5
TARGET                       = 6
LAMP                         = 7
LAMP_GAIN_CURRENT_1          = 8
LAMP_GAIN_CURRENT_1_mA       = 9
LAMP_GAIN_CURRENT_2          = 10
LAMP_GAIN_CURRENT_2_mA       = 11
DETECTORS                    = 12
LINK                         = 13
FRAME_TYPE                   = 14
MODE                         = 15
COUNTER                      = 16
ACQ_NUMBER                   = 17
ACQ_COUNT                    = 18
ACQ_REPETITION               = 19
ACQ_DURATION                 = 20
SUBFRAME_NUMBER              = 21
SUBFRAME_TYPE                = 22
COMP_STATUS                  = 23
EN_DIS_SUB                   = 24
BKG_RN                       = 25
BKG_REPETITION               = 26
TEXPO                        = 27
TEXPO_sec                    = 28
TDELAY                       = 29
DET_TEMP                     = 30
S_TELESCOPE_MIRROR_TEMP      = 31
S_SLIT_TEMP                  = 32
S_SC_IF_TEMP                 = 33
S_COLD_RADIATOR_TEMP         = 34
S_SPECTROMETER_MIRROR_TEMP   = 35
M_MOTOR_TS                   = 36
M_CAL_SOURCE_TEMP            = 37
M_DIFFUSER_CAL_TEMP          = 38
DET_TEMP_K                   = 39
S_TELESCOPE_MIRROR_TEMP_K    = 40
S_SLIT_TEMP_K                = 41
S_SC_IF_TEMP_K               = 42
S_COLD_RADIATOR_TEMP_K       = 43
S_SPECTROMETER_MIRROR_TEMP_K = 44
M_MOTOR_TS_K                 = 45
M_CAL_SOURCE_TEMP_K          = 46
M_DIFFUSER_CAL_TEMP_K        = 47
NADIR_OFFSET_SIGN            = 48
NADIR_OFFSET                 = 49
NADIR_OFFSET_deg             = 50
EXTRA_COLUMN                 = 51

# The format definition of each float
FORMATS = {
    TIME_TM                     : '%14.4f',
    TIME_SCI_HK                 : '%14.4f',
    LAMP_GAIN_CURRENT_1_mA      : '%5.1f',
    LAMP_GAIN_CURRENT_2_mA      : '%5.1f',
    TEXPO_sec                   : '%5.3f',
    DET_TEMP_K                  : '%6.2f',
    S_TELESCOPE_MIRROR_TEMP_K   : '%6.2f',
    S_SLIT_TEMP_K               : '%6.2f',
    S_SC_IF_TEMP_K              : '%6.2f',
    S_COLD_RADIATOR_TEMP_K      : '%6.2f',
    S_SPECTROMETER_MIRROR_TEMP_K: '%6.2f',
    M_MOTOR_TS_K                : '%6.2f',
    M_CAL_SOURCE_TEMP_K         : '%6.2f',
    M_DIFFUSER_CAL_TEMP_K       : '%6.2f',
    NADIR_OFFSET_deg            : '%8.4f',
}


def write_jnojir_status_index(filepath):

    # Read the input index
    with open(filepath) as f:
        recs = f.readlines()

    # Identify the volume ID from the directory path
    prefix, volume_id = VOLUME_ID_REGEX.match(filepath).groups()

    # Identify the output file and optional backup
    output_file = (prefix.replace('volumes', 'metadata') + volume_id + '/'
                   + volume_id + '_status_index.tab')
    backup_file = output_file[:-4] + '-backup.tab'

    # Check the delivered INDEX.TAB vs. a pre-existing metadata file
    index_is_original = filepath.upper().endswith('.CSV')
    if index_is_original:
        recs = recs[1:]     # skip header

    # Create a parent directory if necessary
    parent = os.path.split(output_file)[0]
    os.makedirs(parent, exist_ok=True)

    # Make a backup if necessary
    if os.path.exists(output_file) and not os.path.exists(backup_file):
        shutil.move(output_file, backup_file)

    # Open the output file
    f = open(output_file, 'wb')     # use binary write to suppress <cr><lf> handling

    # Loop through the records...
    for irec, rec in enumerate(recs):

        # If this is an original CSV, quote the filespec and put the volume ID in front
        if index_is_original:
            icomma = rec.index(',')
            rec = '"' + volume_id + '","' + rec[:icomma] + '"' + rec[icomma:]

        values = list(eval(rec))

        # Convert FILE_NAME to FILE_SPECIFICATION_NAME
        values[FILE_SPECIFICATION_NAME] = 'DATA/' + values[FILE_SPECIFICATION_NAME]

        # These errors appear starting in JNOJIR_1047
        for icol in (M_DIFFUSER_CAL_TEMP_K, S_SLIT_TEMP_K, S_SC_IF_TEMP_K,
                     S_COLD_RADIATOR_TEMP_K, M_CAL_SOURCE_TEMP_K):
            if values[icol] == 9999:
                values[icol] = -1.

        if values[FILE_SPECIFICATION_NAME].endswith('.IMG'):
            prev_time_sci_hk = values[TIME_SCI_HK]

        if values[TIME_SCI_HK] > 3000000000.:
            print(f'TIME_SCI_HK corrected in record {irec+1}: {prev_time_sci_hk}')
            values[TIME_SCI_HK] = prev_time_sci_hk

        # Adjust all string lengths and check
        failed = False
        for k, v in enumerate(values):
            length = LENGTHS[k]
            if k in FORMATS:
                v = -1 if v == 'N/A' else v
                values[k] = FORMATS[k] % v
            elif TYPES[k] == 'i':
                v = -1 if v == 'N/A' else v
                values[k] = f'%{length}d' % v
            else:
                values[k] = '"' + v.rstrip().ljust(length) + '"'
                length += 2

            if len(values[k]) != length:
                print(f'Length overflow in record {irec+1}, column {k+1}: {values[k]!r}')
                print(values)
                failed = True
                break

        # Last value is ignored
        if values[-1] != '0':
            print(f'Last column is not zero in record {irec+1}: {values[-1]!r}')
#           failed = True           # Turns out it is occasionally 1 instead of 0

        if failed:
            f.close()

            # If a backup file exists, copy it back
            if os.path.exists(backup_file):
                shutil.copy(backup_file, output_file)

            sys.exit(1)

        # Merge this back into a single record
        new_rec = ','.join(values[:-1]) + '\r\n'

        # Write the new record
        f.write(new_rec.encode('latin-1'))

    # Close and label the output file
    f.close()
    label_jnojir_status_index(filepath, output_file)

    return output_file


def write_jnojir_cum_status_index(filepath):

    # Identify the directory path
    prefix, volume_id = VOLUME_ID_REGEX.match(filepath).groups()
    prefix = prefix.replace('volumes', 'metadata')
    group = volume_id[:8]       # 'JNOJIR_1' or 'JNOJIR_2'

    # Identify the output file and optional backup
    index_pattern = f'{prefix}{group}???/{group}???_status_index.tab'
    output_file   = f'{prefix}{group}999/{group}999_status_index.tab'

    index_files = glob.glob(index_pattern)
    index_files.sort()
    if output_file in index_files:          # don't copy self!
        index_files.remove(output_file)

    # Make a backup if necessary
    backup_file = output_file[:-4] + '-backup.tab'
    if os.path.exists(output_file) and not os.path.exists(backup_file):
        shutil.move(output_file, backup_file)

    # Open the output file
    f = open(output_file, 'wb')

    # Loop through the records...
    for file in index_files:
        content = pathlib.Path(file).read_bytes()
        f.write(content)

    # Close and label the output file
    f.close()
    label_jnojir_status_index(filepath, output_file)

    return output_file


def label_jnojir_status_index(source_file, index_file):

    # Read old label if present
    source_label = source_file[:-4] + '.LBL'
    if os.path.exists(source_label):
        with open(source_file[:-4] + '.LBL') as f:
            recs = f.readlines()

        # Strip out bad lines
        recs = [rec for rec in recs if rec.strip() != 'by double quotes*/']

        # Get content as dictionary
        content = ''.join(recs)
        label_dict = pdsparser.PdsLabel.from_string(content).as_dict()

        # Convert lists back to "{}" notation
        for key, value in label_dict.items():
            if isinstance(value, list):
                value = str(value).replace('[', '{').replace(']', '}').replace("'", '"')
                label_dict[key] = value

        # Don't let the PDS3 FILE_RECORDS attribute override the built-in
        # PdsTemplate function of the same name.
        del(label_dict['FILE_RECORDS'])

        # Attribute missing from the first indices
        if 'COMMAND_FILE_NAME' not in label_dict:
            label_dict['COMMAND_FILE_NAME'] = "'N/A'"

        label_dict['old_label'] = source_label
    else:
        label_dict = {}

    # Make label backup if necessary
    label_path = index_file[:-4] + '.lbl'
    backup_label = index_file[:-4] + '-backup.lbl'
    if os.path.exists(label_path):
        shutil.move(label_path, backup_label)

    # Find the template and use it
    program_path = sys.modules['__main__'].__file__
    template_path = (os.path.split(program_path)[0]
                     + '/JNOJIR_xxxx_status_index_template.txt')
    template = pdstemplate.PdsTemplate(template_path)
    template.write(label_dict, label_path)

##########################################################################################

if __name__ == '__main__':

    # Process indices; keep track of output index files
    index_files = []
    for filepath in sys.argv[1:]:
        print(filepath)
        index_file = write_jnojir_status_index(filepath)
        index_files.append(index_file)

    # Generate cumulative indices by group, if necessary
    saved = {1: False, 2: False}
    for index_file in index_files:
        group = 1 if '/JNOJIR_1' in index_file else 2
        if saved[group]:
            continue
        print(f'merging JNOJIR_{group}999_index_template.tab')
        write_jnojir_cum_status_index(index_file)
        saved[group] = True

##########################################################################################
