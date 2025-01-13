################################################################################
""" PDS metadata generation package.

Utilities to generate index and geometry tables and their corresponding PDS3
labels.  Each line of the table contains metadata for a single data file 
(e.g. image).  

Index files contain descriptive information about the data product like 
observation times, exposures, instrument modes and settings, etc.  Index file 
entries are taken from the label for the data product by default, but may 
instead be derived from label quantities by defining the appropriate 
configuration function in the config.py for the specific host.  

Raw index files are provided by each project, with varying levels of compliance.
The project-supplied index files are modified to produce the corrected index 
files that can be used with the host from_index() method.  This package is 
intended to produce supplemetnal index files, which add columns to the corrected
index file.  Supplemental index files are just index files with specual names,
so this package can generate any kind of index file.  Supplemental index files
can be provded as arguments to from_index() create a merged dicionary.

Index files are used as input to OPUS, and are available via viewmaster to be 
downloaded by PDS users

Geometry files tabulate the values of geometrc quantites for each data file
derived from SPICE using the information in the index file or from the PDS3 
label using OOPS.  The purpose of the geometry files is to provide input
to OPUS and they are not available to PDS users [[right?]]

The procedure for generating metadata table is as follows:

 1. Create a directory for the new host collection under the hosts/ subdirectory, 
    e.g., GO_0xxx, COISS_xxxx, etc.

 2. Copy the python files from an existing host directory and rename them 
    according to the new collection.  You should have four files:

     <collection>_index.py
     <collection>_geometry.py
     index_config.py
     geometry_config.py

 3. Create a templates/ subdirectory and copy the label templates from an 
    exsting host, and rename accordingly, yielding:

     templates/<collection>_supplmental_index.lbl
     templates/host_defs.lbl

 4. Edit the supplmental template according to the instructions in that file.

 5. Edit the host_defs file to decsribe the new host.

 6. Edit <collection>_index.py and <collection>_geometry.py by replacing the old
    collection names with that of the new host and modifying the arguments to
    make_index() and process_index() accordingly.

 7. Generate the supplemental index using <collection>_index.py:

    7.1. Point $RMS_METADATA and $RMS_VOLUMES to the top of the local metadata 
         and volume trees respectively., e.g.,

          $ RMS_METADATA = ~/SETI/RMS/metadata_test
          $ RMS_VOLUMES = ~/SETI/RMS/holdings/volumes

    7.2. From the host directory (e.g., rms-data-projects/metadata/hosts/GO_0xxx),
         run download.sh to create and populate the metadata and volume trees:

          $ python ../download.py $RMS_METADATA $RMS_VOLUMES

    7.3. Create a template for the supplemental label, e.g.: rms-data-projects/
         hosts/GO_0xxx/templates/GO_0xxx_index_supplemental.lbl

    7.4  Run the script to generate the supplemental files in that tree:

          $ python <collection>_index.py $RMS_VOLUMES/<collection>/ $RMS_METADATA/<collection>/ [volume id]

 8. Generate the geometry files using <collection>_geometry.py:

          $ python <collection>_geometry.py $RMS_METADATA/<collection>/ $RMS_METADATA/<collection>/ [volume id]

Attributes:
    COLUMNS_DIR (str): Directory containing the columns definitions files.

    GLOBAL_TEMPLATE_PATH (str): Directory containing the geometry templates.

    NULL (str): Backplane key NULL value.

"""
################################################################################
import sys, os
import config
import argparse
import numpy as np
import time
import fnmatch
import pdstable, pdsparser
import oops

from pathlib                import Path
from filecache              import FCPath
from pdstemplate            import PdsTemplate
from pdstemplate.pds3table  import pds3_table_preprocessor
from pdslogger              import PdsLogger, LoggerError

###############################
# Define constants
###############################
_metadata = sys.modules[__name__]
COLUMN_DIR = Path(_metadata.__file__).parent / 'column'
GLOBAL_TEMPLATE_PATH = Path(_metadata.__file__).parent / 'templates'
NULL = "null"
BODYX = "bodyx"                     # Placeholder for an arbitrary body to be 
                                    # filled in by replacement_dict()

################################################################################
# Create a list of body IDs
################################################################################
PLANET_NAMES = [
    'MERCURY', 
    'VENUS', 
    'EARTH', 
    'MARS', 
    'JUPITER', 
    'SATURN', 
    'URANUS', 
    'NEPTUNE', 
    'PLUTO'
]

bodies = []
for planet in PLANET_NAMES:
    bod = oops.Body.lookup(planet)
    bodies += [bod]
    bodies += bod.select_children("REGULAR")
BODIES = {body.name: body for body in bodies}

NAME_LENGTH = 12

# Maintain a list of translations for target names
TRANSLATIONS = {}

##########################################################################################
# Logger management
##########################################################################################

# Define the global logger with streamlined output, no handlers so printing to stdout
_LOGGER = PdsLogger.get_logger('metadata', timestamps=False, digits=0, lognames=False,
                               pid=False, indent=True, blanklines=False, level='info')

#===============================================================================
def get_logger():
    """The global PdsLogger for the metadata tools."""
    return _LOGGER

################################################################################
# Utility functions
################################################################################

#===============================================================================
def get_index_name(dir, vol_id, type):
    """Determine the name of the index file.

    Args:
        dir (str): Top dir for volume.
        vol_id (str): Volume ID.
        type (tstr): Index type.

    Returns:
        str: Index name.
    """   

    # Name starts with volume id
    dir = dir.absolute()
    name = vol_id

    # Add type if given
    if type:
        name += '_' + type

    name += '_index'

    return name

#===============================================================================
def get_template_name(type):
    """Determine the name of the label template.

    Args:
        type (str): Index type.

    Returns:
        str: Index name.
    """   

    # Name starts with collection id
    dir = Path.cwd()
    name = dir.name

    # Add type if given
    if type:
        name += '_' + type

    name += '_index'

    return name

#===============================================================================
def splitpath(path: str, string: str):
    """Split a path at a given string.

    Args:
        path (str): Path to split.
        string (str): 
            Search string. The path is split at the first occurrence and the search 
            string is omitted.

    Returns:
        NamedTuple (lines (list), lnum (int)): 
            lines: Lines comprising the output label.
            lnum: Line number in output label at which processing 
                        is to continue.

    Todo:
        Place this function in a general utility package.

    """
    parts = path.parts
    i = parts.index(string)
    return (Path('').joinpath(*parts[0:i]), Path('').joinpath(*parts[i+1:]))

#===============================================================================
def get_volume_subdir(path):
    """Determine the Subdirectory of an input file relative to the volume dir.

    Args:
        path (str): Input path or directory.

    Returns:
        str: Final directory in tree.
    """
    return splitpath(path, config.get_volume_id(path))[1]

#===============================================================================
def replace(tree, placeholder, name):
    """Return a copy of the tree of objects, with each occurrence of the
    placeholder string replaced by the given name.

    Args:
        tree (list): List contining the tree. 
        placeholder (str): Placeholder to replace
        name (str): Replacement string.

    Returns:
        list: New tree with placeholder replaced by name.

    """

    new_tree = []
    for leaf in tree:
        if type(leaf) in (tuple, list):
            new_tree.append(replace(leaf, placeholder, name))

        elif type(leaf) == str and leaf.find(placeholder) != -1:
            new_tree.append(leaf.replace(placeholder, name))

        else:
            new_tree.append(leaf)

    if type(tree) == tuple:
        return tuple(new_tree)
    else:
        return new_tree

#===============================================================================
def replacement_dict(tree, placeholder, names):
    """Create a dictionary of copies of the tree of objects, where each
    dictionary entry is keyed by a name in the list and returns a copy of the 
    tree using that name as the replacement.

    Args:
        tree (list): List contining the tree. 
        placeholder (str): Placeholder to replace
        name (list): List of replacement strings.

    Returns:
        dict: New dictionary.

    """

    dict = {}
    for name in names:
        dict[name] = replace(tree, placeholder, name)

    return dict

#===============================================================================
def get_volume_glob(col):
    """Build a glob string to match all volumes in a collection.

    Args:
        col (str): Collection name, e.g., GO_xxxx.

    Returns:
        str: Glob string.

    """
    parts = col.rsplit('_', 1)
    id = parts[1]
    id_glob = id.replace('x','[0-9]')
    volume_glob = parts[0] + '_' + id_glob

    return volume_glob

#===============================================================================
def add_by_base(x_digits, y_digits, bases):           ### move to utilities
    """Add numbers represented using the specified bases.

    Args:
        x_digits (list): Digits (int) representing the first operand.
        y_digits (list): Digits (int) representing the second operand.
        bases (list): Bases (int) for each position.

    Returns:
        list: Digits (int) representing the result.

    """
    import math

    result = [0]*(len(bases)+1)
    for i, (x_digit, y_digit, base) in \
        enumerate(zip(reversed(x_digits), reversed(y_digits), reversed(bases))):
        result[i] += (x_digit + y_digit) % base
        result[i+1] += (x_digit + y_digit) // base
    return list(reversed(result))

#===============================================================================
def read_txt_file(filespec, as_string=False, terminator='\r\n'):           ### move to utilities
    """Read a text file.

    Args:
        filespec (str or Path): Path to the file to read.  Environment variables are expanded.
        as_string (bool, optional): 
            If True, the result is return as a string using the specified terminator.
        terminator (str): Terminator to use for string return.

    Returns:
        list (as_string==False): Lines of the file with no terminators.
        str (as_string==True): Lines of the file concatenated using the specified terminator. 

    """

    # Expand environment variables and resolve to absolute path
    filespec = Path(os.path.expandvars(filespec)).resolve()
    filespec = FCPath(filespec)

    # Read the file
    content = filespec.read_text(encoding='utf-8', newline=terminator)    
    if as_string:
        return content

    # Split into list of lines with no terminator
    content = content.split('\n')
    if content[-1] == '':
        content = content[:-1]
    content = [c.rstrip('\r\n') for c in content]
    
    return content

#===============================================================================
def write_txt_file(filespec, content, terminator='\r\n'):        ### move to utilities
    """Write a text file.

    Args:
        filespec (str or Path): Path to the file to write.
        content (str or list): 
            Text to write.  If list, each element is a line that will be terminated
            using the specified terminator.  If string, existing terminators are 
            replaced with the specified terminator.
        terminator (str): Desired line terminator.

    Returns:
        None
    """

    # Expand environment variables and resolve to absolute path
    filespec = Path(os.path.expandvars(filespec)).resolve()
    filespec = FCPath(filespec)

    # Determine terminator
    if terminator is None:
        if isinstance(content, list):
            crlf = content[0].endswith('\r\n')
        else:
            crlf = content.endswith('\r\n')
        terminator = '\r\n' if crlf else '\n'

    # Split into list of lines with no terminator
    if not isinstance(content, list):
        content = content.split('\n')
    content = [c.rstrip('\r\n') for c in content]

    # Reconstitute with correct terminator
    content = terminator.join(content) + terminator

    # Write file
    filespec.write_text(content, encoding='utf-8')

#===============================================================================
def rebase(x, bases, ceil=False):           ### move to utilities
    """Convert a decimal number to a different base.

    Args:
        x (int): Number to convert.
        bases (list): Base (int) to use for each decimal place.

    Returns:
        NamedTuple (digits (list), over (int)): 
            digits: Digits (int) in the new base.
            overflow: 
                Remaining quantity, if any, exceeding the maximum value that can be
                represented by the given bases.
    """
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
def sclk_split_count(count, delim=None):
    """Parse a spacecraft clock count into a list.

    Args:
        count (str): Number to convert.
        delim (str): 
            Field delimiter to use. If None, all non-alphanumeric characters are
            treated as delimiters.
        

    Returns:
        list: Fields (int) of the given spacecraft clock count.
    """

    # Replace all non-alphanumerics with default delimiter if non given
    if delim is None:
        delim = '.'
        delims = list(set([c for c in count if not c.isalnum()]))
        table = {ord(d): ord(delim) for d in delims}
        count = count.translate(table) 

    # Split the count string
    fields = list(map(int, (count.split(delim))))
    fields = fields + [0,0,0,0]
    
    return fields[0:4]

#===============================================================================
def sclk_format_count(fields, format):
    """Construct a spacecraft clock count from a list of fields.

    Args:
        fields (list): Fields (int) the spacecraft clock count.
        format (str): 
            Template indicating the fields widths and delimiters.  Alphanumeric 
            characters indicate field digits, non-alphanumeric characters indicate
            field delimiters. Example: 'nnnnnnnn:nn:n.n'.

    Returns:
        int: Spacecraft clock count.
    """

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
def sclk_to_ticks(sclk, bases):
    """Convert spacecraft clock count string to ticks.

    Args:
        sclk (list): Spacecraft clock count string.
        bases (list): Base (int) to use for each decimal place.

    Returns:
        int: Spacecraft clock ticks.
    """

    # Get fields
    fields = sclk_split_count(sclk)

    # Compute ticks
    ticks = fields[-1]
    for i in range(len(fields)-1):
        ticks += fields[i]*bases[i+1]

    return ticks
    
#===============================================================================
def convert_systems_table(table, bases):
    """Convert systems tables SCLK count string to ticks.

    Args:
        table (list): Systems table.
        bases (list): Base (int) to use for each decimal place.

    Returns:
        list: Converted Systems table containing ticks instead of strings.
    """
    new_table = []
    for item in table:
        new_table.append(
            ((sclk_to_ticks(item[0][0], bases), 
              sclk_to_ticks(item[0][1], bases)),
              item[1], item[2]))

    return new_table

#===============================================================================
def get_system(table, sclk, bases):
    """Use converted systems table to determine the system for a given spacecraft 
    clock count.

    Args:
        table (list): Converted systems table containing sclk ticks instead of strings.
        sclk (str): Spacecraft clock string corresponding to the observation time.
        bases (list): Base (int) to use for each decimal place.

    Returns:
        NamedTuple (system (str), secondaries (list)): 
            system: Name of the system corresponding to the given SCLK value.
            secondaries: 
                Names of any secondaries for this system.
    """
    sclk_ticks = sclk_to_ticks(sclk, bases)
    for row in table:
        sclks = row[0]
        if sclk_ticks >= sclks[0] and sclk_ticks <= sclks[1]:
            return (row[1], row[2])
    return (None, None)

#===============================================================================
def _ninety_percent_gap_degrees(n):
    """For n samples, determine the approximate number of degrees for the largest
    gap in coverage providing 90% confidence that the angular coverage is not
    actually complete.

    Args:
        n (int): Number of samples.

    Returns:
        float: Estimated number of degrees.
    """

    # Below 1000, use the tabulation
    if n < 1000:
        return 360. - NINETY_PERCENT_RANGE_DEGREES[n]

    # Otherwise, this empirical fit does a good job
    return 1808. * n**(-0.912)

#===============================================================================
def _get_range_mod360(values, alt_format=None):
    """Determines the minimum and maximum values in the array, allowing for the
    possibility that the numeric range wraps around from 360 to 0.

    Args:
        values (list or np.array): The set of values for which to determine the range.
        alt_format (str, optional):
            "-180" to return values in the range (-180,180) rather
            than (0,360).

    Returns:
        list: Minimum and maximum values in the cyclic array.
    """

    # Check for use of negative values
    use_minus_180 = (alt_format == "-180")

    complete_coverage = [-180.,180.] if use_minus_180 else [0.,360.]

    # Flatten the set of values
    values = np.asarray(values.flatten().vals)

    # With only one value, we know nothing
    if values.size <= 1:
#        return complete_coverage
        return [values, values]

    # Locate the largest gap in coverage
    values = np.sort(values % 360)
    diffs = np.empty(values.size)
    diffs[:-1] = values[1:] - values[:-1]
    diffs[-1]  = values[0] + 360. - values[-1]

    # Locate the largest gap and use it to define the range
    gap_index = np.argmax(diffs)
    diff_max  = diffs[gap_index]
    range_mod360 = [values[(gap_index + 1) % values.size], values[gap_index]]

    # Convert to range -180 to 180 if necessary
    if use_minus_180:
        (lower, upper) = range_mod360
        lower = (lower + 180.) % 360. - 180.
        upper = (upper + 180.) % 360. - 180.
        range_mod360 = [lower, upper]

    # We want 90% confidence that the coverage is not complete. Otherwise,
    # return the complete range
    if diff_max >= _ninety_percent_gap_degrees(values.size):
        return range_mod360
    else:
        return complete_coverage

#===============================================================================
def get_common_args(host=None):
    """Common argument parser for metadata tools.

        Args:
            host (str): Host name e.g. 'GOISS'.

         Returns:
            argparser.ArgumentParser : 
                Parser containing the common argument specifications.
   """
    # Define parser
    parser = argparse.ArgumentParser(
                    description='Metadata generation utility%s.'
                                % ('' if not host else
                                   ' for host ' + host))

    # Generate parser
    gr = parser.add_argument_group('Common Arguments')
    gr.add_argument('input_tree', type=str, metavar='input_tree',
                    help='''File path to the top to tree containing the 
                            volume files.''')
    gr.add_argument('output_tree', type=str, metavar='output_tree',
                    help='''File path to the top to tree in which to place the 
                            volume files.''')
    gr.add_argument('volume', type=str, nargs='?', metavar='volume',
                    help='''If given, only this volume is processed.''')

    # Return parser
    return parser

############################################
# Define geometry parameters
############################################
column_files = list(COLUMN_DIR.glob('COLUMNS_*.py'))
for file in column_files:
    exec(open(file).read())

################################################################################