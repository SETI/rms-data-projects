##########################################################################################
# NHxxMV_index.py
##########################################################################################
"""\
This program re-formats the content of a NHxxMV index file in a standard, consistent
format for the RMS node's PDS3 holdings/metadata tree.

To use:
    > python [--nomerge] NHxxMV_index.py path/to/index.tab ...

Afterward, it labels the new index file, regenerates the cumulative index, and labels the
new cumulative index.

If the "--nomerge" option is specified, the PATH_NAME and FILE_NAME columns will be
preserved; otherwise, they will be merged into a single columne FILE_SPECIFICATION_NAME.

This program does not correct any information that is incorrect in the existing index!
"""

import glob
import os
import pathlib
import pdstemplate
import re
import shutil
import sys

# This is a regular expression selecting the volume ID out of the directory path
VOLUME_ID_REGEX = re.compile(r'(.*?)(NH[A-Z][A-Z0-9]MV_[12]001)')

# Indices of the columns
VOLUME_ID                     = 0
PATH_NAME                     = 1
FILE_NAME                     = 2
DATA_SET_ID                   = 3
PRODUCT_ID                    = 4
PRODUCT_CREATION_TIME         = 5
REDUCTION_LEVEL               = 6
SPACECRAFT_CLOCK_START_COUNT  = 7
SPACECRAFT_CLOCK_STOP_COUNT   = 8
START_TIME                    = 9
STOP_TIME                     = 10
TARGET_NAME                   = 11
INSTRUMENT_HOST               = 12
INSTRUMENT_ID                 = 13
INSTRUMENT_NAME               = 14
TELEMETRY_APPLICATION_ID      = 15

# The number of characters in each string
LENGTHS = [11, 21, 31, 43, 27, 19, 10, 18, 18, 23, 23, 28, 12, 6 , 61, 7]

# Matches the mis-valued TARGET_NAME fields
JUPITER_MOON_TARGET = re.compile(r'J\d (.*)')

def fix_target(target):

    # Fix Jupiter moon targets
    match = JUPITER_MOON_TARGET.fullmatch(target)
    if match:
        return match.group(1)

    # "M 7" -> "M7"
    if target == 'M 7':
        return 'M7'

    return target


def write_nhxxmv_index(filepath, merge_filespec):

    # Read the input index
    with open(filepath) as f:
        recs = f.readlines()

    # Identify the volume ID from the directory path
    prefix, volume_id = VOLUME_ID_REGEX.match(filepath).groups()

    # Identify the output file and optional backup
    output_file = (prefix.replace('volumes', 'metadata') + volume_id + '/'
                   + volume_id + '_index.tab')
    backup_file = output_file[:-4] + '-backup.tab'

    # Create a parent directory if necessary
    parent = os.path.split(output_file)[0]
    os.makedirs(parent, exist_ok=True)

    # Make a backup if necessary
    if os.path.exists(output_file) and not os.path.exists(backup_file):
        shutil.move(output_file, backup_file)

    # Open the output file
    f = open(output_file, 'wb')     # use binary write to suppress <cr><lf> handling

    # Loop through the records...
    start_time = '9999-99-99'
    stop_time = '0000-00-00'
    data_set_id = ''
    volume_id = ''
    for irec, rec in enumerate(recs):

        # Interpret the record as Python values (they're all quoted)
        values = list(eval(rec))

        # Convert file path to lower case
        values[PATH_NAME] = values[PATH_NAME].lower()
        values[FILE_NAME] = values[FILE_NAME].lower()

        # PRODUCT_CREATION_TIME is really just a date
        if values[PRODUCT_CREATION_TIME].endswith('T00:00:00'):
            values[PRODUCT_CREATION_TIME] = values[PRODUCT_CREATION_TIME][:-9]

        # Fix Jupiter moon targets, "M 7" -> "M7"
        values[TARGET_NAME] = fix_target(values[TARGET_NAME])

        # Check index values
        if 'N/A' not in values[START_TIME]:
            start_time = min(start_time, values[START_TIME])
            stop_time  = max(stop_time,  values[START_TIME])
        if 'N/A' not in values[STOP_TIME]:
            start_time = min(start_time, values[STOP_TIME])
            stop_time  = max(stop_time,  values[STOP_TIME])
        data_set_id = values[DATA_SET_ID]
        volume_id = values[VOLUME_ID]

        # Adjust all string lengths and check
        for k, v in enumerate(values):
            values[k] = v.rstrip().ljust(LENGTHS[k])
            if len(values[k]) != LENGTHS[k]:
                print(f'Length overflow in record {irec}, column {k}: {values[k]!r}')
                f.close()

                # If a backup file exists, copy it back
                if os.path.exists(backup_file):
                    shutil.copy(backup_file, output_file)

                sys.exit(1)

        # Merge the FILE_SPECIFICATION_NAME if necessary
        if merge_filespec:
            values = values[:1] + [values[PATH_NAME] + values[FILE_NAME]] + values[3:]

        # Merge this back into a single record
        new_rec = '"' + '","'.join(values) + '"\r\n'

        # Write the new record
        f.write(new_rec.encode('latin-1'))

    # Close and label the output file
    f.close()
    info = {'start_time': start_time,
            'stop_time': stop_time,
            'data_set_id': data_set_id,
            'volume_id': volume_id,
            'merge_filespec': merge_filespec}
    label_nhxxmv_index(output_file, info)

    return output_file


NHXXMV_ORDER = {'LA':0, 'JU':1, 'PC':2, 'PE':3, 'KC':4, 'KE':5, 'K2':6}

def write_nhxxmv_cum_index(filepath, merge_filespec):

    # Identify the directory path
    prefix, volume_id = VOLUME_ID_REGEX.match(filepath).groups()
    prefix = prefix.replace('volumes', 'metadata')
    group = volume_id[7]        # '1' or '2'

    # Identify the output file and optional backup
    index_pattern = prefix + f'NH??MV_{group}001/NH??MV_{group}001_index.tab'
    output_file = prefix + f'NHxxMV_{group}999/NHxxMV_{group}999_index.tab'

    index_files = glob.glob(index_pattern)
    index_files.sort(key=lambda k: NHXXMV_ORDER[os.path.basename(k)[2:4]])

    # Make a backup if necessary
    backup_file = output_file[:-4] + '-backup.tab'
    if os.path.exists(output_file) and not os.path.exists(backup_file):
        shutil.move(output_file, backup_file)

    # Create a parent directory if necessary
    parent = os.path.split(output_file)[0]
    os.makedirs(parent, exist_ok=True)

    # Open the output file
    f = open(output_file, 'wb')

    # Loop through the records...
    for file in index_files:
        content = pathlib.Path(file).read_bytes()
        f.write(content)

    # Close and label the output file
    f.close()
    label_nhxxmv_index(output_file, {'merge_filespec': merge_filespec})

    return output_file


def label_nhxxmv_index(index_file, info):

    label_path = index_file[:-4] + '.lbl'
    backup_label = index_file[:-4] + '-backup.lbl'
    if os.path.exists(label_path):
        shutil.move(label_path, backup_label)

    program_path = sys.modules['__main__'].__file__
    template_path = os.path.split(program_path)[0] + '/NHxxMV_index_template.txt'
    template = pdstemplate.PdsTemplate(template_path)
    template.write(info, label_path)

##########################################################################################

if __name__ == '__main__':

    merge_filespec = True
    if '--nomerge' in sys.argv:
        merge_filespec = False
        sys.argv.remove('--nomerge')

    # Process indices; keep track of output index files
    index_files = []
    for filepath in sys.argv[1:]:
        print('\n' + filepath)
        index_file = write_nhxxmv_index(filepath, merge_filespec)
        index_files.append(index_file)

    # Generate cumulative indices by group, if necessary
    saved = {1: False, 2: False}
    for index_file in index_files:
        group = 1 if 'MV_1' in index_file else 2
        if saved[group]:
            continue
        print(f'\nmerging MHxxMV_{group}999_index_template.tab')
        write_nhxxmv_cum_index(index_file, merge_filespec)
        saved[group] = True

##########################################################################################
