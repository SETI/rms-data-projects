#!/usr/bin/env python
################################################################################
# Syntax:
#   cisscal_label.py path [path...]
#
# Creates a new PDS3 label for every calibrated image in the directory tree.
# The label for the uncalibrated image, must reside in the same directory.
#
# Calibrated images must end in either ".IMG.cal" or "_CALIB.IMG". Images ending
# in ".IMG.cal" are renamed.
################################################################################

import sys
import os
import re

################################################################################
# Methods for updating a Cassini ISS PDS3 label
################################################################################

def find_object_in_label(records, name):
    """Record indices of an object in the label."""

    match1 = 'OBJECT = ' + name + '\r\n'
    match2 = 'END_' + match1

    found = False
    for k1 in range(len(records)):
        if records[k1] == match1:
            found = True
            break

    if not found:
        raise ValueError('Object ' + name  + ' not found')

    for k2 in range(k1+1, len(records)):
        if records[k2] == match2: break

    return (k1,k2+1)

def replace_in_label(records, name, value, obj=None):
    """Replace value of a label parameter, optionally within a specific
    object."""

    # Default is to check every record, can be overridden by object index limits
    if obj:
        limits = find_object_in_label(records, obj)
    else:
        limits = (0, len(records))

    # Define regular expression to match parameter name
    if name[0] == '^':
        regex = re.compile(' *\\' + name + ' *=')
    else:
        regex = re.compile(' *' + name + ' *=')

    # Search and replace
    for k in range(*limits):
        record = records[k]
        if regex.match(record) is None: continue
        parts = record.split('=')
        records[k] = parts[0] + '= ' + value + '\r\n'
        return

    raise ValueError('Label parameter ' + name + ' not found')

def replace_pair_in_label(records, name, newname, value, obj=None):
    """Replace name and value of a label parameter, optionally within a specific
    object."""

    # Default is to check every record, can be overridden by object index limits
    if obj:
        limits = find_object_in_label(records, obj)
    else:
        limits = (0, len(records))

    # Define regular expression to match parameter name
    if name[0] == '^':
        regex = re.compile(' *\\' + name + ' *=')
    else:
        regex = re.compile(' *' + name + ' *=')

    # Search and replace
    for k in range(*limits):
        record = records[k]
        if regex.match(record) is None: continue
        parts = record.split('=')
        records[k] = parts[0] + '= ' + value + '\r\n'
        records[k] = records[k].replace(name, newname)

        return

    raise ValueError('Label parameter ' + name + ' not found')

def remove_from_label(records, name, obj=None):
    """Remove a parameter from the label, optionally within a specific
    object."""

    # Default is to check every record, can be overridden by object index limits
    if obj:
        limits = find_object_in_label(records, obj)
    else:
        limits = (0, len(records))

    # Define regular expression to match parameter name
    if name[0] == '^':
        regex = re.compile(' *\\' + name + ' *=')
    else:
        regex = re.compile(' *' + name + ' *=')

    # Search and remove
    for k in range(*limits):
        record = records[k]
        if regex.match(record) is None: continue
        del records[k]
        return

    raise ValueError('Label parameter ' + name + ' not found')

def remove_object_from_label(records, name):
    """Remove an object from the label."""

    # Default is to check every record, can be overridden by object index limits
    (k1, k2) = find_object_in_label(records, name)
    del records[k1:k2]

################################################################################
# Procedure to write a PDS3 label for a calibrated ISS image
################################################################################

pair_regex = re.compile(r' *([_A-Z]+)=([.0-9]+|\'[^\']*\'|\(.*?\))')
comma_delim_regex = re.compile(r' *([^\(]+?|[^\(]+\(.*?\)),')

months = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12',
}

def cisscal_label(calimage, rawlabel):

    # Read the VICAR header
    with open(calimage,'rb') as f:
        header = f.read(40)
        assert header.startswith('LBLSIZE='), calimage + ' is not a VICAR file'

        header = header[len('LBLSIZE='):]
        lblsize = int(header.split(' ')[0])

        f.seek(0)
        header = f.read(lblsize)

    header = header.rstrip(chr(0))

    # Interpret into a list of tuples and a dict
    header_pairs = pair_regex.findall(header)
    header_pairs = [(n,eval(v)) for (n,v) in header_pairs]
    header_dict = dict(header_pairs)

    # Read old PDS label
    with open(rawlabel) as f:
        records = f.readlines()

    # Update PDS3 label
    replace_in_label(records, 'RECORD_BYTES', str(header_dict['LBLSIZE']))
    replace_in_label(records, 'FILE_RECORDS', str(header_dict['NL'] + 1))

    # Remove TELEMETRY_TABLE object
    remove_from_label(records, '^TELEMETRY_TABLE')
    remove_object_from_label(records, 'TELEMETRY_TABLE')

    # Remove LINE_PREFIX_TABLE object
    remove_from_label(records, '^LINE_PREFIX_TABLE')
    remove_object_from_label(records, 'LINE_PREFIX_TABLE')

    # VALID_MAXIMUM is no longer applicable
    remove_from_label(records, 'VALID_MAXIMUM')

    # Update IMAGE_HEADER object
    basename = os.path.basename(calimage)
    replace_in_label(records, '^IMAGE_HEADER', '("' + basename + '",1)')

    replace_pair_in_label(records, ' BYTES', 'BYTES',
                                   str(header_dict['LBLSIZE']),
                                   'IMAGE_HEADER')
    replace_pair_in_label(records, '^DESCRIPTION', 'DESCRIPTION',
                                   '"Original VICAR2 header, updated by CISSCAL."',
                                   'IMAGE_HEADER')

    # Update IMAGE object
    replace_in_label(records, '^IMAGE', '("' + basename + '",2)')
    replace_in_label(records, 'SAMPLE_TYPE', 'PC_REAL', 'IMAGE')
    replace_in_label(records, 'SAMPLE_BITS', '32', 'IMAGE')
    remove_from_label(records, 'LINE_PREFIX_BYTES', 'IMAGE')

    # Replace DESCRIPTION and PRODUCT_CREATION_TIME
    cisscal_task = ''
    for k in range(len(header_pairs)):
        (name,value) = header_pairs[k]
        if name == 'TASK' and value.startswith('CISSCAL'):
            cisscal_task = value
            break

    assert cisscal_task != '', 'CISSCAL task not found in VICAR header'

    # Skip the user
    k += 1
    assert header_pairs[k][0] == 'USER', 'CISSCAL USER not found'

    # Replace the PRODUCTION_CREATION_TIME
    k += 1
    assert header_pairs[k][0] == 'DAT_TIM', 'CISSCAL DAT_TIM not found'

    # Example: DAT_TIM='Thu Oct 16 08:22:08 2003'
    value = header_pairs[k][1]
    date = value[-4:] + '-' + months[value[4:7]] + '-' + value[8:10] + 'T' + \
           value[11:19]
    replace_in_label(records, 'PRODUCT_CREATION_TIME', date)

    k += 1

    # For CISSCAL 3.6 and earlier
    if header_pairs[k][0] == 'PROCESSING_HISTORY_TEXT':
        value = header_pairs[k][1]
        info = comma_delim_regex.findall(value.rstrip() + ',')

    # For CISSCAL 3.8 and later
    else:
        info = [n + ' = ' + repr(v) for (n,v) in header_pairs[k:]]

    # Cleanup
    info = [i.replace('/Data/Cassini-ISS/CALIB/','') for i in info]
    info = [i.replace(', parameter file',',\r\n    parameter file')
            for i in info]
    info = [i.replace('; ',';\r\n    ') for i in info]

    desc_list = ['"', 'Calibrated using ' + cisscal_task + ':'] + \
                ['  ' + i for i in info] + ['"']
    replace_in_label(records, 'DESCRIPTION', '\r\n'.join(desc_list))

    # Write label file
    outfile = calimage[:-4] + '.LBL'
    f = open(outfile, 'w')
    f.writelines(records)
    f.close()

################################################################################
# Main program
################################################################################

for arg in sys.argv[1:]:

  for (path, dirs, files) in os.walk(arg):
    for file in files:
        abspath = os.path.join(path, file)

        if abspath.endswith('.IMG.cal'):
            newname = abspath[:-8] + '_CALIB.IMG'
            os.rename(abspath, newname)
            abspath = newname

        if abspath.endswith('_CALIB.IMG'):
            rawlabel = abspath[:-10] + '.LBL'
            cisscal_label(abspath, rawlabel)
            print abspath[:-4] + '.LBL'



