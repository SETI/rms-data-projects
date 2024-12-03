################################################################################
# index_support.py - Tools for generating geometric index files
################################################################################
import os, time
import glob as glb
import fortranformat as ff
import pdsparser
import fnmatch
import warnings
import hosts.pds3 as pds3

import metadata as meta
import config
import pdstable

from pathlib     import Path
from pdslabelbot import PdsLabelBot

################################################################################
# Built-in key functions
################################################################################

#===============================================================================
def key__volume_id(label_path, label_dict):
    """Key function for VOLUME_ID.   The return value will appear in the index
    file under VOLUME_ID.

    Args:
        label_path (str): Path to the PDS label.
        label_dict (dict): Dictionary containing the PDS label fields.

    Returns:
        str: Volume ID
    """
    return config.get_volume_id(label_path)

#===============================================================================
def key__file_specification_name(label_path, label_dict):
    """Key function for FILE_SPECIFICATION_NAME.  The return value will appear in
    the index file under FILE_SPECIFICATION_NAME.

    Args:
        label_path (str): Path to the PDS label.
        label_dict (dict): Dictionary containing the PDS label fields.

    Returns:
        str: File Specification name.
    """
    return meta.get_volume_subdir(label_path)
    

################################################################################
# internal functions
################################################################################

#===============================================================================
def _format_value(value, format):
    """Format a single value using a Fortran format code.

    Args:
        value (str): Value to format.
        format (str): FORTRAN_style format code.

    Returns:
        str: formatted value.
    """
    
    # format value
    line = ff.FortranRecordWriter('(' + format + ')')
    line = line.write([value])
    result = line.strip().ljust(len(line))                 # Left justify

    # add double quotes to string formats
    if format[0] == 'A':
        result = '"' + result + '"'
    
    return result

#===============================================================================
def _format_parms(format):
    """Determine len and type corresopnding to a given FORTRAN format code..

    Args:
        format (str): FORTRAN_style format code.
        
    Returns:
        NamedTuple (width (int), data_type (str)): 
            width     (int): Number of bytes required for a formatted value, 
                      including any quotes.
            data_type (str): Data type corresponding to the format code.

    """
    
    data_types = {'A':'CHARACTER', 
                  'E':'ASCII_REAL', 
                  'F':'ASCII_REAL', 
                  'I':'ASCII_INTEGER'}
    try:
        f = _format_value('0', format)
    except TypeError:
        f = _format_value(0, format)

    width = len(f)
    data_type = data_types[format[0]]
    
    return (width, data_type)

#===============================================================================
def _format_column(column_stub, value, count=None):
    """Format a column.

    Args:
        column_stub (list): Preprocessed column stub. 
        value 
        count

    Returns:
        str: Formatted value.
    """

    # Get value parameters
    name = column_stub['NAME']
    format = column_stub['FORMAT'].strip('"')
    (width, data_type) =  _format_parms(format)
    if not count:
        count = int(column_stub['ITEMS']) if 'ITEMS' in column_stub.keys() else 1

    # Split multiple elements into individual columns and process recursively
    if count > 1:
        if not isinstance(value, (list,tuple)):
           value = count * [value]
        assert len(value) == count

        fmt_list = []
        for item in value:
            result = _format_column(column_stub, item, count=1) 
            fmt_list.append(result)
        return ','.join(fmt_list)

    # Clean up strings
    if isinstance(value, str):
        value = value.strip()
        value = value.replace('\n', ' ')
        while ('  ' in value):
            value = value.replace('  ', ' ')
        value = value.replace('"', '')

    # Format the value
    try:
        result = _format_value(value, format)
    except TypeError:
        print("**** WARNING: Invalid format: ", name, value, format)
        result = width * "*"

    if len(result) > width:
        print("**** WARNING: No second format: ", name, value, format, result)

    # Validate the formatted value
    try:
        test = eval(result)
    except Exception:
        print('Format error for %s: %s' % (name, value))

    return result

#===============================================================================
def _get_null_value(column_stub):
    """Determine the null value for a column.

    Args:
        column_stub (dict): Column stub dictionary.

    Returns:
        str|float: Null value.
    """

    # List of accepted Null keywords
    nullkeys = ['NULL_CONSTANT', 'UNKNOWN_CONSTANT', 'NOT_APPLICABLE_CONSTANT']

    # Check for a known null key in column stub
    nullval = None
    for key in nullkeys:
        if key in column_stub.keys():
            nullval = column_stub[key]
        
    # Convert to numeric type if no quotes
    if nullval and not nullval.startswith('"'):
        nullval = float(nullval)

    return nullval

#===============================================================================
def _index_one_value(column_stub, label_path, label_dict):
    """Determine value for one row of one column.

    Args:
        column_stub (dict): Column stub dictionary.
        label_path (str): Path to the PDS label.
        label_dict (dict): Dictionary containing the PDS label fields.

    Returns:
        str: Determined value.
    """

    # Determine null value
    nullval = _get_null_value(column_stub)

    # Check for built-in key function
    key = column_stub['NAME']
    fn_name = 'key__' + key.lower()
    try:
        fn = globals()[fn_name]
        value = fn(label_path, label_dict)

    # Check for key function in index_config module
    except KeyError:
        try:
            fn = getattr(config, fn_name)
            value = fn(label_path, label_dict)

        # If no key function, just take the value from the label
        except AttributeError:
            value = label_dict[key] if key in label_dict else nullval

    # If a key function returned None, insert a NULL value.
    if value is None:
        value = nullval

    assert value is not None, 'Null constant needed for %s.' % column_stub['NAME']
    return value

#===============================================================================
def _index_one_file(root, name, index, column_stubs):
    """Write a single index file entry.

    Args:
        root (str): Top of the directory tree containing the volume.
        name (str): Name of PDS label.
        index ([[]]): Open descriptor for the index file.
        column_stubs (list): List of preprocessed column stubs.

    Returns:
        None.
    """

    # Read the PDS3 label
    path = root/name
    label = pds3.get_label(path.as_posix())

    # Write columns
    first = True
    for column_stub in column_stubs:

        # Get the value
        value = _index_one_value(column_stub, path, label)

        # Write the value into the index
        if not first:
            index.write(",")

        fvalue = _format_column(column_stub, value)
        index.write(fvalue)

        first = False

    index.write('\r\n')

#===============================================================================
def _make_one_index(input_dir, output_dir, *, type='', glob=None, no_table=False):
    """Creates index file for a single volume.

    Args:
        input_dir (str):
            Directory containing the volume, specifically the
            data labels.
        output_dir (str):
            Directory in which to find the "updated" index file
            (e.g., <volume>_index.tab, and in which to write the
            new index files.
        type (str, optional):
            Qualifying string identifying the type of index file
            to create, e.g., 'supplemental'.
        glob (str, optional): Glob pattern for index files.
        no_table (bool, optional): If True, do not produce a table, just a label.

    Returns:
    : None.
    """

    if not no_table:
        # Get index and template filenames
        vol_id = config.get_volume_id(input_dir)
        primary_index_name = meta.get_index_name(input_dir, vol_id, None)
        index_name = meta.get_index_name(input_dir, vol_id, type) 
        template_name = meta.get_template_name(type)         # assumes top dir is pwd

        create_primary = index_name == primary_index_name

        # This assumes that the primary index file has been copied from the 
        if not create_primary:
            primary_index_path = output_dir/(primary_index_name + '.lbl')
            if not primary_index_path.exists():
                warnings.warn('Primary index file not found: %s.  Skipping' % primary_index_path)
                return

        index_path = output_dir/(index_name + '.tab')
        template_path = Path('./templates/')/(template_name + '.lbl')

        # Process the template
        T = PdsLabelBot(template_path)
        T.generate() 
        column_stubs = T.column_stubs

        # Walk the directory tree...

        # Open the output file; create dir if necessary
        output_dir.mkdir(exist_ok=True)
        index = open(index_path, 'w')

        # If there is a primary file, read it and build the file list
        if not create_primary:
            table = pdstable.PdsTable(primary_index_path)
            primary_row_dicts = table.dicts_by_row()
            files = [Path(primary_row_dict['FILE_SPECIFICATION_NAME']) \
                        for primary_row_dict in primary_row_dicts]

            for i in range(len(files)): 
                files[i] = input_dir/files[i].with_suffix('.LBL') 

        # Otherwise, build the file list from the directory tree
        else:
            files = [f for f in input_dir.rglob('*.LBL')]

        # Build the index
        for file in files:
            name = file.name
            root = file.parent

            # Match the glob pattern
            file = fnmatch.filter([name], glob)[0]
            if file == []:
                continue

            # Print volume ID and subpath
            subdir = meta.get_volume_subdir(root)
            volume_id = config.get_volume_id(input_dir)
            print('    ', volume_id, subdir/name)

            # Make the index for this file
            _index_one_file(root, file, index, column_stubs)

        # Close index file and make label if the index exists
        try:
            index.close()
        except:
            pass

    # Create the label
    meta._make_label(index_path, table_type=type)

################################################################################
# external functions
################################################################################

#===============================================================================
def make_index(input_tree, output_tree, *, type='', glob=None, volume=None, no_table=False):
    """Creates index files for a collection of volumes.

    Args:
        input_tree (str): Root of the tree containing the volumes.
        output_tree (str):
            Root of the tree in which the output files are
            written in the same directory structure as in the
            input tree.
        type (str, optional):
            Qualifying string identifying the type of index file
            to create, e.g., 'supplemental'.
        glob (str, optional): Glob pattern for index files.
        volume (str, optional): If given, only this volume is processed.
        no_table (bool, optional): If True, do not produce a table, just a label.

    Returns:
    : None.
    """
#xxx Unknown arg name: input
#xxx Unknown arg name: output

    input_tree = Path(input_tree) 
    output_tree = Path(output_tree) 

    # Build volume glob
    vol_glob = meta.get_volume_glob(input_tree.name)

    # Walk the input tree, making indexes for each found volume
    for root, dirs, files in input_tree.walk():
        root = Path(root)

        # Determine notional set and volume
        parts = root.parts
        set = parts[-2]
        vol = parts[-1]

        # Test whether this root is a volume
        if fnmatch.filter([vol], vol_glob):
            if not volume or vol == volume:
                indir = root
                if output_tree.parts[-1] != set: 
                    outdir = output_tree/set
                outdir = output_tree/vol
                _make_one_index(indir, outdir, 
                                type=type, 
                                glob=glob, 
                                no_table=no_table)

################################################################################

