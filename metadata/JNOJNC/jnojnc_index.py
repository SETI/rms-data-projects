##########################################################################################
# jnojnc_index.py
##########################################################################################
"""\
This program re-formats the content of a JNOJNC index file in a standard, consistent
format for the RMS node's PDS3 holdings/metadata tree.

To use:
    > python jnojnc_index.py path/to/index.tab ...

The file path can point to either an original INDEX.TAB file or to a v1.0 index in the
metadata tree. The output file is written into the metadata tree with the correct
subdirectory and name. If a file of that name is already present and there is no backup,
the existing file is renamed with the ending "-backup.tab".

Afterward, it labels the new index file, regenerates the cumulative index, and labels the
new cumulative index.

This program does not correct any information that is incorrect in the existing index!
"""

import glob
import os
import pathlib
import pdstemplate
import re
import shutil
import sys

# This is a regular expression that matches any time field with an optional leading '"'
ISODATE_REGEX = re.compile(r'("?20\d\d-\d+-?\d*T?\d*:?\d*:?\d*\.?\d*)')

# This is a regular expression selecting the volume ID out of the directory path
VOLUME_ID_REGEX = re.compile(r'(.*?)(JNOJNC_\d\d\d\d)')

# Indices of the columns
VOLUME_ID                 = 0
STANDARD_DATA_PRODUCT_ID  = 1
DATA_SET_ID               = 2
PRODUCT_ID                = 3
START_TIME                = 4
STOP_TIME                 = 5
PROCESSING_LEVEL_ID       = 6
RATIONALE_DESC            = 7
SOLAR_DISTANCE            = 8
SPACECRAFT_ALTITUDE       = 9
SUB_SPACECRAFT_LATITUDE   = 10
SUB_SPACECRAFT_LONGITUDE  = 11
TARGET_NAME               = 12
FILE_SPECIFICATION_NAME   = 13
PRODUCT_CREATION_TIME     = 14
PRODUCT_LABEL_MD5CHECKSUM = 15

# The number of characters in each column (excluding quotes on strings)
LENGTHS = [11, 11, 29, 25, 23, 23, 1, 140, 10, 10, 8, 8, 11, 55, 19, 32]
RECORD_LENGTH = 457

# The format definition of each float
FORMATS = {
    SOLAR_DISTANCE          : '%10.4e',
    SPACECRAFT_ALTITUDE     : '%10.1f',
    SUB_SPACECRAFT_LATITUDE : '%8.4f',
    SUB_SPACECRAFT_LONGITUDE: '%8.4f',
}


def write_jnojnc_index(filepath):

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
    for irec, rec in enumerate(recs):

        # Because the time fields are un-quoted, we need to quote them before the next
        # step. The result of re.split() alternates between the non-dates and the dates.
        parts = ISODATE_REGEX.split(rec)
        for k, part in enumerate(parts):
            if k % 2 == 1:
                if part[0] != '"':      # if not already quoted
                    parts[k] = '"' + part + '"'
        rec = ''.join(parts)

        # Remove all occurrences of "<km>"
        rec = rec.replace('<km>', '')

        # Now we can interpret the record as Python values
        values = list(eval(rec))

        # Remove extra zero from VOLUME_ID if necessary
        volume_id = values[VOLUME_ID]
        if len(volume_id) == 12:
            values[VOLUME_ID] = volume_id[:7] + volume_id[-4:]

        # If the three of the four floating-point columns are zero, they should be
        # NOT_APPLICABLE_CONSTANT
        if values[SPACECRAFT_ALTITUDE:SPACECRAFT_ALTITUDE+3] == [0, 0, 0]:
            values[SPACECRAFT_ALTITUDE] = -1.e32
            values[SUB_SPACECRAFT_LATITUDE] = -1.e32
            values[SUB_SPACECRAFT_LONGITUDE] = -1.e32

        # "SPACE" isn't a target!
        if values[TARGET_NAME].rstrip() == 'SPACE':
            values[TARGET_NAME] = 'N/A'

        # Format all columns
        for k, v in enumerate(values):
            if v == -1.e32:
                value = '-1.e32'.rjust(LENGTHS[k])
            elif isinstance(v, float):
                value = FORMATS[k] % v
            else:
                value = '"' + v.rstrip().ljust(LENGTHS[k]) + '"'
            values[k] = value

        # Move FILE_SPECIFICATION_NAME to second column
        filespec = values.pop(FILE_SPECIFICATION_NAME)
        values.insert(1, filespec)

        # Merge this back into a single record
        new_rec = ','.join(values) + '\r\n'

        # A length error probably indicates length overflow of a string-valued column
        if len(new_rec) != RECORD_LENGTH:
            print('Length error!')
            print(irec, values)
            f.close()

            # If a backup file exists, copy it back
            if os.path.exists(backup_file):
                shutil.copy(backup_file, output_file)

            sys.exit(1)

        # Write the new record
        f.write(new_rec.encode('latin8'))

    # Close and label the output file
    f.close()
    label_jnojnc_index(output_file)

    return output_file


def write_jnojnc_cum_index(index_file):

    # Identify the directory path
    prefix, _ = VOLUME_ID_REGEX.match(index_file).groups()  # up to volume ID

    # Identify the output file and optional backup
    index_pattern = prefix + 'JNOJNC_0???/JNOJNC_0???_index.tab'
    output_file = prefix + 'JNOJNC_0999/JNOJNC_0999_index.tab'

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
    label_jnojnc_index(output_file)


def label_jnojnc_index(index_file):

    label_path = index_file[:-4] + '.lbl'
    backup_label = index_file[:-4] + '-backup.lbl'
    if os.path.exists(label_path):
        shutil.move(label_path, backup_label)

    program_path = sys.modules['__main__'].__file__
    template_path = os.path.split(program_path)[0] + '/JNOJNC_0xxx_index_template.lbl'
    template = pdstemplate.PdsTemplate(template_path)
    template.write({}, label_path)

##########################################################################################

if __name__ == '__main__':

    for filepath in sys.argv[1:]:
        print(filepath)
        index_file = write_jnojnc_index(filepath)

    print('merging JNOJNC_0xxx_index_template.tab')
    write_jnojnc_cum_index(index_file)

##########################################################################################
