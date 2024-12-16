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
from pdstemplate import PdsTemplate
from pdstemplate.pds3table import Pds3Table, pds3_table_preprocessor

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
# Index class
################################################################################
class Index():
    """Class describing an index for a single volume.
    """

    #===========================================================================
    def __init__(self, input_dir, output_dir, *, 
                    type='', glob=None):
        """Constructor for a Index object.

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
        """

        # Save inputs
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.type = type
        self.glob = glob

        # Get volume id from label
        self.volume_id = config.get_volume_id(self.input_dir)

        # Get relevant filenames and paths
        primary_index_name = meta.get_index_name(self.input_dir, self.volume_id, None)
        index_name = meta.get_index_name(self.input_dir, self.volume_id, self.type) 
        template_name = meta.get_template_name(self.type)         # assumes top dir is pwd
        self.index_path = self.output_dir/(index_name + '.tab')

        # If the index name is the same as the primary inxex name,
        # then this is the primary index.
        create_primary = index_name == primary_index_name

        # This assumes that the primary index file has been copied from viewmaster 
        if not create_primary:
            self.primary_index_path = self.output_dir/(primary_index_name + '.lbl')
            if not self.primary_index_path.exists():
                warnings.warn('Primary index file not found: %s.  Skipping' % primary_index_path)
                return

        # Extract relevent fields from the template
        template_path = Path('./templates/')/(template_name + '.lbl')
        label_name = meta.get_index_name(self.input_dir, self.volume_id, self.type) 
        label_path = self.output_dir / Path(label_name + '.lbl')

        template = meta.read_txt_file(template_path, as_string=True)
        pds3_table = Pds3Table(label_path, template, validate=False, numbers=True, formats=True)
        self.column_stubs = Index._get_column_values(pds3_table)

        # If there is a primary file, read it and build the file list
        if not create_primary:
            table = pdstable.PdsTable(self.primary_index_path)
            primary_row_dicts = table.dicts_by_row()
            self.files = [Path(primary_row_dict['FILE_SPECIFICATION_NAME']) \
                                   for primary_row_dict in primary_row_dicts]

            for i in range(len(self.files)): 
                self.files[i] = self.input_dir/self.files[i].with_suffix('.LBL') 

        # Otherwise, build the file list from the directory tree
        else:
            self.files = [f for f in input_dir.rglob('*.LBL')]

        # Initialize the index
        self.content = []

    #===========================================================================
    def _create(self):
        """Creates the index file for a single volume.

        Args: None
        Returns: None.
        """

        # Open the output file; create dir if necessary
        self.output_dir.mkdir(exist_ok=True)

        # Build the index
        for file in self.files:
            name = file.name
            root = file.parent

            # Match the glob pattern
            file = fnmatch.filter([name], self.glob)[0]
            if file == []:
             continue

            # Print volume ID and subpath
            subdir = meta.get_volume_subdir(root)
            print('    ', self.volume_id, subdir/name)

            # Make the index for this file
            self._index_one_file(root, file)

        # Write index 
        if self.content:
            meta.write_txt_file(self.index_path, self.content)

        # Create the label
        meta.make_label(self.index_path, table_type=self.type)
 
    #===============================================================================
    def _index_one_file(self, root, name):
        """Write a single index file entry.

        Args:
            root (str): Top of the directory tree containing the volume.
            name (str): Name of PDS label.

        Returns:
            None.
        """

        # Read the PDS3 label
        path = root/name
        label = pds3.get_label(path.as_posix())

        # Write columns
        first = True
        line = ''
        for column_stub in self.column_stubs:
            if not column_stub:
                continue

            # Get the value
            value = Index._index_one_value(column_stub, path, label)

            # Write the value into the index
            if not first:
                line += ","

            fvalue = Index._format_column(column_stub, value)
            line += fvalue

            first = False

        self.content += [line]

    #===============================================================================
    @staticmethod
    def _index_one_value(column_stub, label_path, label_dict):
        """Determine value for one row of one column.

        Args:
            column_stub (dict): Column stub dictionary.
            label_path (str): Path to the PDS label.
            label_dict (dict): Dictionary containing the PDS label fields.

        Returns:
            str: Determined value.
        """
        nullval = column_stub['NULL_CONSTANT']

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
    @staticmethod
    def _get_column_values(pds3_table):
        """Build a list of column stubs.

        Args:
            pds3_table (Pds3Tabel): Object defining the table.

        Returns:
            list: Dictionaries containing relevant keyword values for each column.
        """
        column_stubs = []
        colnum = 1
        while True:
            try:
                name = pds3_table.old_lookup('NAME', colnum)
            except IndexError:
                break

            column_stubs += [ 
                {'NAME'          : name, 
                 'FORMAT'        : pds3_table.old_lookup('FORMAT', colnum),
                 'ITEMS'         : pds3_table.old_lookup('ITEMS', colnum),
                 'NULL_CONSTANT' : Index._get_null_value(pds3_table, colnum)} ]

            colnum += 1

        return column_stubs

    #===============================================================================
    @staticmethod
    def _get_null_value(pds3_table, colnum):
        """Determine the null value for a column.

        Args:
            pds3_table (Pds3Tabel): Object defining the table.
            column (int): Column number.

        Returns:
            str|float: Null value.
        """

        # List of accepted Null keywords
        nullkeys = ['NULL_CONSTANT', 
                    'UNKNOWN_CONSTANT', 
                    'INVALID_CONSTANT', 
                    'MISSING_CONSTANT', 
                    'NOT_APPLICABLE_CONSTANT']

        # Check for a known null key in column stub
        nullval = None
        for key in nullkeys:
            if nullval := pds3_table.old_lookup(key, colnum):
                continue
        
        return nullval

    #===============================================================================
    @staticmethod
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
    @staticmethod
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
            f = Index._format_value('0', format)
        except TypeError:
            f = Index._format_value(0, format)

        width = len(f)
        data_type = data_types[format[0]]
    
        return (width, data_type)

    #===============================================================================
    @staticmethod
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
        (width, data_type) =  Index._format_parms(format)
        if not count:
            count = column_stub['ITEMS'] if column_stub['ITEMS'] else 1

        # Split multiple elements into individual columns and process recursively
        if count > 1:
            if not isinstance(value, (list,tuple)):
               value = count * [value]
            assert len(value) == count

            fmt_list = []
            for item in value:
                result = Index._format_column(column_stub, item, count=1) 
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
            result = Index._format_value(value, format)
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

################################################################################
# external functions
################################################################################

#===============================================================================
def make_index(input_tree, output_tree, *, type='', glob=None, volume=None):
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
        # __skip directory will not be scanned, so it's safe for test results
        if '__skip' in root.as_posix():
            continue

        # Sort directories for convenience
        dirs.sort()
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

                index = Index(indir, outdir, 
                              type=type, 
                              glob=glob)
                index._create()

################################################################################

