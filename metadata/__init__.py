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

    TEMPLATES_DIR (str): Directory containing the geometry templates.

    NULL (str): Backplane key NULL value.

"""
################################################################################
import sys
import config
import argparse
import numpy as np
import fortranformat as ff
import oops

from pathlib import Path
from pdstemplate import PdsTemplate
from .fancyindex import FancyIndex

###############################
# Define constants
###############################
_metadata = sys.modules[__name__]
BODY_DIR = Path(_metadata.__file__).parent / 'body'
TEMPLATES_DIR = Path(_metadata.__file__).parent / 'templates'
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

################################################################################
# Preprocessor Directive Functions
#
#  index_support.make_index() runs a preprocoessing step on the label templates
#  to resolve the column names.  The preprocessor also parses directives of the
#  form $<DIRECTIVE>{<arg>}, whose functionalities are defined here in 
#  functions of the form _directive_<directive>(lines, lnum, <arg>).
################################################################################

#===============================================================================
def _directive_insert(lines: list, lnum: int, filename: str):
    """Defines the INSERT directive, which replaces the directive with the
    contents of the named file.

    Args:
        lines   (list): Lines comprising the input label.
        lnum     (int): Line number at which this directive was encountered.
        filename (str): Name of file containing the lines to insert.
 
    Returns:
        NamedTuple (lines (list), lnum (int)): 
            lines   (list): Lines comprising the output label.
            lnum     (int): Line number in output label at which processing 
                            is to continue.
            .
    """

    # Read file
    insert_lines = read_txt_file(filename)       

    # Insert into label
    lines = lines[0:lnum] + insert_lines + lines[lnum+1:]
    lnum += len(insert_lines)-1

    return(lines, lnum)

#===============================================================================
def process_directives(lines: list):
    """Parses label directives of the form $<DIRECTIVE>{<arg>}.  Directives must 
    appear at the start of a line.

    Args:
        lines   (list): Lines comprising the input label.
 
    Returns:   
        str: Lines comprising the output label.

    """

    # List of accepted directives.  Define new directivs by adding to this list
    # and adding a directive function above.
    directives = ['INSERT']

    lnum = 0
    for line in lines:
        for directive in directives:
        
            # test for directive pattern at start of line: $<directive>{
            pattern = '$' + directive + '{'
            if line.startswith(pattern):
                try:
                    arg = line.split('{')[1].split('}')[0]
                except:
                    raise SyntaxError(line)

                # call directive function
                fn = globals()['_directive_' + directive.lower()]
                (lines, lnum) = fn(lines, lnum, arg)
        lnum += 1

    return lines

################################################################################
# Utility functions
################################################################################

#===============================================================================
def download(outdir: str, url: str, patterns: str, first=False):
    """Download remote tree to local machine.

    Args:
        outdir    (str): Top directory of local output tree.
        url       (str): URL pointing to the top directry of the remote input 
                         tree.
        patterns (list): Glob patterns to match in remote tree.
        first    (bool): If True, the function returns after the first 
                         pattern that produces any matches.

    Returns:
        int: Index of succesful pattern if first==True, or -1.

    Todo:
        Detect whether a tar.gz files exists and download and untar in
        local tree instead of walking the remote tree.  Would be much more
        efficient.

    """

    outdir = Path(outdir)

    # Determine instrument collection and instrument ids
    p = Path('.') 
    curdir = p.absolute()               # e.g., /rms-data-projects/metadata/hosts/GO_xxxx
    collection = curdir.name            # e.g., GO_0XXX, COISS_XXXX

    # Determine collection directory
    coldir = outdir / collection
    colurl = url + '/' + collection

    # Copy tree from URL
    print('Indexing...')
    F = FancyIndex(colurl, recursive=True)

    print('Transferring files...')
    match = False
    for i in range(len(patterns)):
        try:
            F.walk(pattern=patterns[i], dest=coldir)
            match = True
            from IPython import embed; print('++*+*+*+*+*+++++++'); embed()
        except:
            pass

        if match:
            if first:
                return i

    return -1

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
def force_crlf(lines):

    new_lines = []
    for line in lines:
        if len(line) < 2 or line[-2] !=  '\r':
            new_line = line.replace('\n', '\r\n')
        else:
            new_line = line
        new_lines.append(new_line)

    return new_lines

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
        path   (str): Path to split.
        string (str): Search string.  The path is split at the first occurrence
                      and the search string is omitted.

    Returns:
        NamedTuple (lines (str), lnum (int)): 
            lines   (list): Lines comprising the output label.
            lnum     (int): Line number in output label at which processing 
                            is to continue.

    Todo:
        Place this function in a general utility package.

    """
    parts = path.parts
    i = parts.index(string)
    return (Path('').joinpath(*parts[0:i]), Path('').joinpath(*parts[i+1:]))

#===============================================================================
def replace(tree, placeholder, name):
    """Return a copy of the tree of objects, with each occurrence of the
    placeholder string replaced by the given name.

    Args:
        tree        (list): List contining the tree. 
        placeholder  (str): Placeholder to replace
        name         (str): Replacement string.

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
    """Return a dictionary of copies of the tree of objects, where each
    dictionary entry is keyed by a name in the list and returns a copy of the 
    tree using that name as the replacement.

    Args:
        tree        (list): List contining the tree. 
        placeholder  (str): Placeholder to replace
        name        (list): List of replacement strings.

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
    vol_glob = parts[0] + '_' + id_glob

    return vol_glob

#===============================================================================
def get_cumulative_dir(input_tree):
    """Determine the cumulative index directory.

    Args:
        col (str): Collection name, e.g., GO_xxxx.

    Returns:
        Path: Cumulative index directory.

    """
    return input_tree / Path(input_tree.name.replace('x','9'))

#===============================================================================
def add_by_base(x_digits, y_digits, bases):           ### move to utilities
    import math

    result = [0]*(len(bases)+1)
    for i, (x_digit, y_digit, base) in \
        enumerate(zip(reversed(x_digits), reversed(y_digits), reversed(bases))):
        result[i] += (x_digit + y_digit) % base
        result[i+1] += (x_digit + y_digit) // base
    return list(reversed(result))

#===============================================================================
def read_txt_file(filename):           ### move to utilities
    f = open(filename)
    lines = f.readlines()
    f.close()
    return lines

#===============================================================================
def write_txt_file(filename, lines, append=False):        ### move to utilities

    mode = 'a' if append else 'w'
    f = open(filename, mode)
    for line in lines:
        f.write(line)
    f.close()

#===============================================================================
def rebase(x, bases, ceil=False):           ### move to utilities
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
def sclk_to_ticks(count, bases):
    # Get fields
    fields = sclk_split_count(count)

    # Compute ticks
    ticks = fields[-1]
    for i in range(len(fields)-1):
        ticks += fields[i]*bases[i+1]

    return ticks
    
#===============================================================================
def convert_systems_table(table, bases):

    new_table = []
    for item in table:
        new_table.append(
            ((sclk_to_ticks(item[0][0], bases), 
              sclk_to_ticks(item[0][1], bases)),
              item[1], item[2]))

    return new_table

#===============================================================================
def get_system(table, sclk, bases):
    # Could default to using checking Hill radii of each planet with the table 
    # as an override.

    sclk_ticks = sclk_to_ticks(sclk, bases)
    for row in table:
        sclks = row[0]
        if sclk_ticks >= sclks[0] and sclk_ticks <= sclks[1]:
            return (row[1], row[2])
    return (None, None)

#===============================================================================
def _range_of_n_angles(n, prob=0.1, tests=100000):
    """Used to study the statistics of n randomly chosen angles.

    For a set of n randomly chosen angles 0-360, return the range such that the
    likelihood of all n angles falling within this range of one another has the
    given probability. Base this on the specified number of tests.

    Args:
        n (int): Xxx
        prob (float, optional): Xxx
        tests (int, optional): Xxx

    Returns:
        xxx: xxx
    """
    #### This function is not used.  It should be removed and placed in a 
    #### utility library.

    max_diffs = []
    for k in range(tests):
        values = np.random.rand(n) * 360.
        values = np.sort(values % 360)
        diffs = np.empty(values.size)
        diffs[:-1] = values[1:] - values[:-1]
        diffs[-1]  = values[0] + 360. - values[-1]
        max_diffs.append(diffs.max())

    max_diffs = np.sort(max_diffs)
    cutoff = int((1.-prob) * tests + 0.5)
    return 360. - max_diffs[cutoff]

# This is a tabulation of range_of_n_angles(N) for N in the range 0-1000
# We have 90% confidence that, if the N angles fall within this range, then the
# points do not sample a full 360 degrees of longitude.
NINETY_PERCENT_RANGE_DEGREES = np.array([
    0.000,   0.000,  18.000,  65.682, 105.260, 135.335, 158.717, 177.366, 192.527, 205.134,
  215.648, 225.089, 232.935, 239.913, 246.178, 251.693, 256.834, 261.349, 265.279, 269.092,
  272.471, 275.603, 278.550, 281.247, 283.765, 286.168, 288.339, 290.340, 292.325, 294.165,
  295.864, 297.473, 298.976, 300.490, 301.843, 303.207, 304.438, 305.556, 306.733, 307.824,
  308.847, 309.884, 310.841, 311.734, 312.588, 313.447, 314.264, 315.094, 315.822, 316.550,
  317.261, 317.970, 318.580, 319.220, 319.836, 320.457, 321.044, 321.560, 322.104, 322.608,
  323.119, 323.788, 324.007, 324.891, 325.153, 325.444, 325.846, 326.399, 326.476, 327.109,
  327.315, 327.836, 328.114, 328.482, 328.806, 329.285, 329.764, 329.890, 330.145, 330.617,
  330.905, 331.254, 331.386, 331.701, 332.006, 332.473, 332.484, 332.936, 333.199, 333.220,
  333.744, 333.740, 334.021, 334.347, 334.438, 334.794, 335.075, 335.232, 335.284, 335.611,
  335.909, 335.903, 336.214, 336.544, 336.682, 336.804, 336.868, 337.071, 337.370, 337.528,
  337.688, 337.753, 337.782, 338.255, 338.482, 338.519, 338.627, 338.681, 339.024, 339.043,
  339.346, 339.397, 339.602, 339.700, 339.894, 340.027, 340.092, 340.214, 340.468, 340.584,
  340.538, 340.687, 340.808, 341.034, 340.884, 341.211, 341.394, 341.394, 341.682, 341.751,
  341.812, 341.898, 342.161, 342.244, 342.359, 342.342, 342.426, 342.572, 342.702, 342.626,
  342.873, 343.100, 342.874, 343.032, 343.311, 343.285, 343.471, 343.518, 343.663, 343.694,
  343.727, 343.811, 344.054, 344.033, 344.099, 344.076, 344.212, 344.280, 344.473, 344.431,
  344.579, 344.582, 344.826, 344.849, 344.979, 344.987, 344.990, 345.085, 345.126, 345.149,
  345.264, 345.381, 345.464, 345.579, 345.546, 345.668, 345.718, 345.778, 345.800, 345.889,
  346.031, 345.977, 346.119, 346.129, 346.240, 346.259, 346.308, 346.400, 346.372, 346.454,
  346.527, 346.679, 346.624, 346.738, 346.772, 346.873, 346.938, 346.972, 347.079, 347.084,
  347.144, 347.174, 347.195, 347.298, 347.348, 347.385, 347.464, 347.477, 347.494, 347.526,
  347.618, 347.618, 347.743, 347.709, 347.852, 347.849, 347.970, 347.891, 348.000, 348.009,
  348.070, 348.135, 348.163, 348.210, 348.183, 348.348, 348.448, 348.324, 348.471, 348.483,
  348.515, 348.584, 348.621, 348.644, 348.651, 348.800, 348.774, 348.882, 348.885, 348.911,
  348.823, 348.969, 348.892, 348.970, 349.010, 349.121, 349.142, 349.193, 349.185, 349.329,
  349.318, 349.306, 349.408, 349.338, 349.416, 349.480, 349.479, 349.514, 349.616, 349.652,
  349.652, 349.621, 349.718, 349.735, 349.698, 349.778, 349.743, 349.888, 349.903, 349.864,
  349.951, 349.985, 349.937, 350.090, 350.021, 350.043, 350.226, 350.148, 350.174, 350.273,
  350.259, 350.245, 350.319, 350.264, 350.412, 350.421, 350.456, 350.414, 350.506, 350.563,
  350.593, 350.557, 350.614, 350.621, 350.620, 350.701, 350.669, 350.734, 350.754, 350.773,
  350.878, 350.850, 350.896, 350.863, 350.884, 350.942, 350.934, 351.004, 350.975, 351.065,
  351.036, 351.082, 351.087, 351.130, 351.167, 351.172, 351.161, 351.213, 351.284, 351.262,
  351.201, 351.353, 351.349, 351.336, 351.372, 351.395, 351.425, 351.426, 351.492, 351.507,
  351.555, 351.588, 351.578, 351.581, 351.631, 351.598, 351.621, 351.619, 351.692, 351.672,
  351.766, 351.699, 351.733, 351.759, 351.733, 351.830, 351.862, 351.907, 351.885, 351.869,
  351.982, 351.935, 351.999, 351.965, 352.035, 351.998, 352.025, 352.090, 352.072, 352.087,
  352.087, 352.122, 352.164, 352.123, 352.163, 352.143, 352.175, 352.218, 352.223, 352.352,
  352.307, 352.345, 352.352, 352.355, 352.346, 352.399, 352.362, 352.364, 352.445, 352.496,
  352.473, 352.485, 352.467, 352.530, 352.562, 352.551, 352.609, 352.619, 352.548, 352.652,
  352.612, 352.653, 352.671, 352.702, 352.767, 352.699, 352.759, 352.734, 352.752, 352.769,
  352.798, 352.759, 352.800, 352.862, 352.890, 352.900, 352.864, 352.949, 352.938, 352.921,
  352.975, 352.972, 352.977, 353.005, 352.975, 353.040, 352.997, 353.078, 353.059, 353.064,
  353.019, 353.110, 353.101, 353.141, 353.196, 353.161, 353.200, 353.176, 353.199, 353.178,
  353.252, 353.253, 353.271, 353.284, 353.272, 353.286, 353.321, 353.322, 353.331, 353.322,
  353.396, 353.328, 353.389, 353.370, 353.368, 353.411, 353.410, 353.460, 353.409, 353.483,
  353.475, 353.515, 353.497, 353.492, 353.573, 353.586, 353.509, 353.601, 353.585, 353.590,
  353.578, 353.574, 353.618, 353.645, 353.608, 353.674, 353.692, 353.696, 353.684, 353.697,
  353.701, 353.728, 353.733, 353.765, 353.785, 353.782, 353.777, 353.810, 353.779, 353.788,
  353.782, 353.835, 353.859, 353.864, 353.868, 353.875, 353.883, 353.922, 353.929, 353.952,
  353.937, 353.948, 353.981, 353.971, 353.933, 353.988, 354.019, 354.054, 354.000, 354.025,
  354.053, 354.067, 354.051, 354.050, 354.071, 354.076, 354.163, 354.124, 354.113, 354.122,
  354.145, 354.173, 354.168, 354.187, 354.199, 354.210, 354.252, 354.224, 354.232, 354.238,
  354.235, 354.219, 354.254, 354.283, 354.275, 354.265, 354.289, 354.317, 354.341, 354.318,
  354.366, 354.338, 354.330, 354.403, 354.339, 354.399, 354.377, 354.389, 354.405, 354.435,
  354.422, 354.420, 354.454, 354.463, 354.486, 354.481, 354.462, 354.485, 354.461, 354.508,
  354.520, 354.522, 354.513, 354.560, 354.523, 354.534, 354.585, 354.553, 354.572, 354.562,
  354.600, 354.564, 354.596, 354.642, 354.603, 354.625, 354.621, 354.640, 354.670, 354.661,
  354.686, 354.655, 354.701, 354.674, 354.680, 354.699, 354.731, 354.732, 354.742, 354.741,
  354.778, 354.776, 354.768, 354.767, 354.792, 354.820, 354.778, 354.798, 354.828, 354.844,
  354.826, 354.854, 354.850, 354.835, 354.868, 354.870, 354.888, 354.905, 354.871, 354.911,
  354.898, 354.902, 354.901, 354.974, 354.943, 354.951, 354.938, 354.973, 354.968, 354.979,
  354.997, 354.989, 355.002, 355.006, 355.038, 355.027, 355.043, 355.051, 354.994, 355.045,
  355.048, 355.048, 355.048, 355.059, 355.043, 355.104, 355.091, 355.122, 355.120, 355.099,
  355.099, 355.123, 355.155, 355.150, 355.118, 355.152, 355.176, 355.190, 355.124, 355.175,
  355.197, 355.170, 355.184, 355.256, 355.212, 355.236, 355.227, 355.221, 355.213, 355.260,
  355.277, 355.257, 355.278, 355.261, 355.280, 355.256, 355.309, 355.314, 355.290, 355.308,
  355.307, 355.331, 355.315, 355.336, 355.323, 355.335, 355.349, 355.376, 355.341, 355.400,
  355.357, 355.350, 355.366, 355.379, 355.398, 355.374, 355.409, 355.422, 355.406, 355.433,
  355.447, 355.447, 355.426, 355.459, 355.452, 355.475, 355.456, 355.471, 355.494, 355.496,
  355.483, 355.505, 355.495, 355.478, 355.517, 355.518, 355.530, 355.538, 355.551, 355.530,
  355.535, 355.572, 355.569, 355.543, 355.589, 355.555, 355.607, 355.586, 355.634, 355.578,
  355.604, 355.624, 355.616, 355.610, 355.629, 355.643, 355.629, 355.630, 355.634, 355.649,
  355.677, 355.650, 355.679, 355.658, 355.657, 355.690, 355.703, 355.686, 355.703, 355.694,
  355.714, 355.742, 355.729, 355.705, 355.721, 355.712, 355.741, 355.736, 355.768, 355.781,
  355.727, 355.758, 355.771, 355.794, 355.774, 355.794, 355.789, 355.772, 355.783, 355.807,
  355.804, 355.807, 355.828, 355.822, 355.838, 355.836, 355.820, 355.841, 355.840, 355.851,
  355.840, 355.857, 355.859, 355.889, 355.873, 355.887, 355.896, 355.876, 355.896, 355.936,
  355.896, 355.891, 355.934, 355.940, 355.934, 355.918, 355.927, 355.935, 355.921, 355.950,
  355.976, 355.998, 355.955, 355.937, 355.963, 355.984, 355.979, 355.969, 355.991, 355.980,
  355.994, 355.972, 355.999, 355.995, 355.989, 356.010, 356.025, 355.989, 356.038, 356.045,
  356.026, 356.042, 356.054, 356.038, 356.073, 356.058, 356.067, 356.074, 356.063, 356.077,
  356.091, 356.087, 356.116, 356.089, 356.103, 356.096, 356.124, 356.106, 356.126, 356.109,
  356.127, 356.101, 356.120, 356.132, 356.133, 356.141, 356.153, 356.162, 356.143, 356.142,
  356.167, 356.192, 356.168, 356.176, 356.170, 356.189, 356.167, 356.194, 356.188, 356.190,
  356.201, 356.189, 356.219, 356.216, 356.235, 356.233, 356.224, 356.218, 356.225, 356.257,
  356.248, 356.240, 356.244, 356.237, 356.261, 356.267, 356.293, 356.262, 356.275, 356.286,
  356.292, 356.293, 356.287, 356.306, 356.307, 356.297, 356.306, 356.300, 356.333, 356.310,
  356.329, 356.338, 356.302, 356.337, 356.314, 356.330, 356.336, 356.348, 356.335, 356.361,
  356.355, 356.377, 356.350, 356.389, 356.352, 356.380, 356.366, 356.378, 356.396, 356.382,
  356.402, 356.374, 356.381, 356.402, 356.406, 356.414, 356.390, 356.430, 356.424, 356.428,
  356.429, 356.440, 356.445, 356.441, 356.450, 356.463, 356.461, 356.439, 356.448, 356.462,
  356.451, 356.479, 356.471, 356.449, 356.495, 356.476, 356.486, 356.473, 356.479, 356.518,
  356.494, 356.492, 356.507, 356.494, 356.509, 356.513, 356.544, 356.509, 356.511, 356.504,
  356.517, 356.541, 356.526, 356.527, 356.542, 356.536, 356.553, 356.548, 356.553, 356.537,
  356.534, 356.557, 356.587, 356.563, 356.583, 356.588, 356.593, 356.582, 356.611, 356.583,
  356.589, 356.604, 356.585, 356.569, 356.598, 356.615, 356.598, 356.620, 356.624, 356.624,
  356.620, 356.625, 356.644, 356.627, 356.630, 356.651, 356.637, 356.640, 356.666, 356.651,
  356.661, 356.664, 356.679, 356.655, 356.638, 356.659, 356.674, 356.681, 356.672, 356.675,
  356.677, 356.687, 356.691, 356.685, 356.701, 356.712, 356.701, 356.696, 356.703, 356.717,
])

#===============================================================================
def _ninety_percent_gap_degrees(n):
    """For n samples, return the approximate number of degrees for the largest
    gap in coverage providing 90% confidence that the angular coverage is not
    actually complete.

    Args:
        n (int): Number of samples.

    Returns:
        xxx: xxx
    """

    # Below 1000, use the tabulation
    if n < 1000:
        return 360. - NINETY_PERCENT_RANGE_DEGREES[n]

    # Otherwise, this empirical fit does a good job
    return 1808. * n**(-0.912)

#===============================================================================
def _get_range_mod360(values, alt_format=None):
    """Returns the minimum and maximum values in the array, allowing for the
    possibility that the numeric range wraps around from 360 to 0.

    Args:
        values (xxx): The set of values for which to determine the range.
        alt_format (str, optional):
            "-180" to return values in the range (-180,180) rather
            than (0,360).

    Returns:
        xxx: xxx
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


################################################################################
# Argument parsers
################################################################################

#===============================================================================
def get_common_args(host=None):

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

#===============================================================================
def get_index_args(host=None, type=None):

    # Get parser with common args
    parser = get_common_args(host=host)

    # Add parser for index args
    gr = parser.add_argument_group('Index Arguments')
    gr.add_argument('--type', '-t', type=str, metavar='type', 
                    default=type, 
                    help='''Type of index file to create, e.g., 
                            "supplemental".''')

    # Return parser
    return parser

#===============================================================================
def get_geometry_args(host=None, selection=None, exclude=None):

    # Get parser with common args
    parser = get_common_args(host=host)

    # Add parser for index args
    gr = parser.add_argument_group('Geometry Arguments')
    gr.add_argument('--selection', '-s', type=str, metavar='selection',
                    default=selection, 
                    help=''' A string containing:
                             "S" to generate summary files;
                             "D" to generate detailed files.''')
    gr.add_argument('--exclude', '-e', nargs='*', type=str, metavar='exclude',
                    default=exclude, 
                    help='''List of volumes to exclude.''')

    # Return parser
    return parser


################################################################################
# Label functions
################################################################################

#===============================================================================
def parse_block(lines, head=0, *,
                 start_token='OBJECT=COLUMN', end_token='END_OBJECT=COLUMN'):
    """Extract a block of lines between two tokens.

    Args:
        lines (list): List of strings.
        head (list, optional): Line at which to start search.  Default: 0.
        start_token (str, optional): Block start token.  Default: 'OBJECT=COLUMN'.
        end_token (str, optional): Block end token.  Default: END_OBJECT=COLUMN'.

    Returns:
        NamedTuple (block (list), head (int), tail (int)):
            block   (list): List of strings in the first detected block.
            head     (int): Line number of the start of the block.
            tail     (int): Line number of the end of the block.
    """   

    tail = -1
    block = []
    for i in range(head,len(lines)):
        line = lines[i]
        if line.replace(' ', '').startswith(start_token):
            head = i
            tail = head
            for line in lines[i:]:
                tail += 1
                block.append(line)
                if line.replace(' ', '').startswith(end_token):
                    break
            if block:
                break

    return (block, head, tail)

#===============================================================================
def format_value(value, format):
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
def format_parms(format):
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
        f = format_value('0', format)
    except TypeError:
        f = format_value(0, format)

    width = len(f)
    data_type = data_types[format[0]]
    
    return (width, data_type)

#===============================================================================
def format_column(value, *, 
                       name=None, 
                       count=None, 
                       nbytes=None, 
                       width=None, 
                       format=None, 
                       nullval=None, 
                       data_type=None, 
                       description=None):
    """Format a column.

    Args:
        value (str): Value to format.
        name (str, optional): Column name. Default: None.
        count (int, optional): Number of items, if array. Default: None.
        nbytes (int, optional): Number of bytes in the value  Default: None.
        width (int, optional):
            Number of bytes required for a formatted value,
            including any quotes. Default: None.
        format (str, optional): FORTRAN format code. Default: None.
        nullval (str, optional): Value to use for a null value. Default: None.
        data_type (str, optional): Data type. Default: None.
        description (str, optional): Column description. Default: None.

    Returns:
        str: Formatted value.
    """

    # Split multiple elements into individual columns
    if count > 1:
        if not isinstance(value, (list,tuple)):
            assert value == nullval
            value = count * [nullval]
        else:
            assert len(value) == count

        fmt_list = []
        for item in value:
            result = format_column(item, name=name, 
                                       count=1, 
                                       nbytes=nbytes, 
                                       width=width, 
                                       format=format, 
                                       nullval=nullval, 
                                       data_type=None, 
                                       description=description)
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
        result = format_value(value, format)
    except TypeError:
        print("**** WARNING: Invalid format: ", name, value, format)
        result = width * "*"

    if len(result) > width:
        print("**** WARNING: No second format: ", name, value, format, result)

    # Validate the formatted value
    try:
        test = eval(result)
    except Exception:
        print("**** WARNING: Eval failure: ", name, value, result)
        test = nullval
    else:
        if isinstance(test, str):
            test = test.rstrip()

# Values change when reformatted to a larger width, which is desired behavior
#    if test != value and test != nullval and test != str(value):
#        print("**** WARNING: Value has changed: ", name, value, format, result)

    return result

#===============================================================================
def process_columns(column_stubs):
    """Convert column description info into more useful form.
    
    Args:
       column_stubs (list): Preprocessed column stubs. 
        
    Returns:
        dict: Column descriptions.
    """
#xxx Unknown docstring format
 
    nullvals = ['NULL_CONSTANT', 'UNKNOWN_CONSTANT', 'NOT_APPLICABLE_CONSTANT']

    # Convert each column
    column_dicts = {}
    for column_stub in column_stubs:
        name = column_stub['NAME']
        column_dict = {'name':name}
        
        column_dict['format'] = column_stub['FORMAT'].strip('"')
        (width, data_type) =  format_parms(column_dict['format'])

        column_dict['count'] = int(column_stub['ITEMS']) if 'ITEMS' in column_stub.keys() else 1

        column_dict['width'] = width

        column_dict['data_type'] = data_type

        column_dict['nullval'] = None
        for nullval in nullvals:
            if nullval in column_stub.keys():
                column_dict['nullval'] = column_stub[nullval]
            
        if column_dict['nullval'] and not column_dict['nullval'].startswith('"'):
            column_dict['nullval'] = float(column_dict['nullval'])

        column_dict['description'] = column_stub['DESCRIPTION'] if 'DESCRIPTION' in column_stub.keys() else ''
        
        column_dict['nbytes'] = width-2 if data_type == 'CHARACTER' else width
#        column_dict['nbytes'] = width-1 if data_type == 'CHARACTER' else width

        column_dicts[name] = column_dict

    return column_dicts

#===============================================================================
def parse_column(lines):
    """Parse a column description into a dictionary.

    Args:
        lines (list): Column description.

    Returns:
        dict: Column dictionary.
    """   
    
    column_dict = {}
    for line in lines:
        line = line.replace(' ', '')
        kv = line.split('=')
        if len(kv) == 2:
            column_dict[kv[0]] = kv[1].strip()
    return column_dict

#===============================================================================
def parse_columns(lines):
    """Parse all column descriptions into a list of dictionaries.

    Args:
        lines (list): PDS label.

    Returns:
        list: Column dictionaries.
    """

    column_stubs = []
    head = 0
    while(True):
    
        # Get the current block
        block, head, tail = parse_block(lines, head)
        if block == []:
            break
            
        # Append the column dictionary 
        column_stubs.append(parse_column(block))

        # Advance the read head
        head += len(block)

    return column_stubs

#===============================================================================
def parse_template(template_path):
    """Create column descriptions from a label template.

    Args:
        template_path (str): Path to label template.

    Returns:
        NamedTuple (lines (list), lnum (int)): 
            lines   (list): Lines comprising the label template.
            dicts   (list): Column description dictionaries.
    """

    # Read template
    template_lines = read_txt_file(template_path)
    template_lines = force_crlf(template_lines)

    # Parse any directives in the columns
    template_lines = preprocess_template(template_lines)

    # Parse into column dictionaries
    column_stubs = parse_columns(template_lines)
    column_dicts = process_columns(column_stubs)
    return (template_lines, column_dicts)

#===============================================================================
def make_label(template_path, input_dir, output_dir, type=''):
    """Creates a label for a given index table.

    Args:
        template_path (str): Path to label template.
        input_dir (str): Directory containing the volume.
        output_dir (str): Directory in which to write the label file.
        type (str, optional):
            Qualifying string identifying the type of index
            file to create, e.g., 'supplemental'.

    Returns:
        None
    """

    # Get filenames
    vol_id = config.get_volume_id(input_dir)
    index_name = get_index_name(input_dir, vol_id, type) 

    index_filename = Path(index_name + '.tab')
    label_filename = Path(index_name + '.lbl')

    index_path = output_dir/index_filename
    label_path = output_dir/label_filename

    # Read the data file
    index_lines = read_txt_file(index_path)
    index_lines = force_crlf(index_lines)

    # Validate the data file
    recs = len(index_lines)
    linelen = len(index_lines[0])

    # Get the volume_id
    volume_id = config.get_volume_id(input_dir)
    
    # Get the columns
    (template_lines, column_dicts) = parse_template(template_path)

    # Populate the standard PdsTemplate field dictionary
    fields = {'TYPE'            : type.upper(),
              'INDEX_FILENAME'  : index_filename,
#              'RECORD_BYTES'    : linelen+1,
              'RECORD_BYTES'    : linelen,
              'FILE_RECORDS'    : recs,
              'ROWS'            : recs,
              'COLUMNS'         : len(column_dicts),
#              'ROW_BYTES'       : linelen+1 }  
              'ROW_BYTES'       : linelen }  

    # Add column-specific fields
    pos = 1
    line = index_lines[0]
    for name in column_dicts:
        column_dict = column_dicts[name]
        
        count = column_dict['count']
        nbytes = column_dict['nbytes']
        width = column_dict['width']
        data_type = column_dict['data_type']

        item_bytes = nbytes

        fields[name + '_START_BYTE'] = pos+1 if data_type == 'CHARACTER' else pos
        fields[name + '_BYTES'] = item_bytes
        fields[name + '_DATA_TYPE'] = data_type

        total_width = width
        if count>1:
            total_width = nbytes*count + (count-1)
            bytes = total_width
            if data_type == 'CHARACTER':
                total_width += 2*count
                bytes = total_width - 2
            fields[name + '_BYTES'] = bytes
            fields[name + '_ITEM_BYTES'] = item_bytes
            fields[name + '_ITEM_OFFSET'] = nbytes + 1
            if data_type == 'CHARACTER':
                fields[name + '_ITEM_OFFSET'] += 2

        pos = pos + total_width + 1

    # Add host-specific fields
    fields['VOLUME_ID'] = volume_id

    # Process the template
    template = PdsTemplate('', content=template_lines)
    template.write(fields, label_path.as_posix())

#===============================================================================
def preprocess_template(lines):
    """Initial parse of the column descriptions handling preprocessor
    directives and using PdsTemplate to create the directive names for
    building the final label.

    Args:
        lines (list): Label template.

    Returns:
        list: Pre-processed label template.
    """

    # Handle preprocessor directives
    lines = process_directives(lines)

    # Parse each column description with PdsTemplate
    head = 0
    while(True):

        # Get the current block
        block, head, tail = parse_block(lines, head)
        if block == []:
            break

        # Parse the block
        T = PdsTemplate('_', content=block)
        content = T.generate({})
#        block = content.split('\n')[0:-1]
#        block = [line + '\n' for line in block]
        block = content.split('\n')[0:-1]
        block = [line + '\n' for line in block]

        # Re-insert into template
        lines = lines[0:head] + block + lines[tail:]

        # Advance the read head
        head += len(block)

    return lines

################################################################################


############################################
# Define geometry parameters
############################################
column_files = list(BODY_DIR.glob('COLUMNS_*.py'))
for file in column_files:
    exec(open(file).read())

