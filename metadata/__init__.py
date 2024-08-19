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

from pathlib import Path
from .fancyindex import FancyIndex

###############################
# Define constants
###############################
_metadata = sys.modules[__name__]
BODY_DIR = Path(_metadata.__file__).parent / 'body'
TEMPLATES_DIR = Path(_metadata.__file__).parent / 'templates'
NULL = "null"

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
    f = open(filename, 'r')
    insert_lines = f.readlines()
    f.close()

    # Insert into label
    lines = lines[0:lnum] + insert_lines + lines[lnum+1:]
    lnum += len(insert_lines)

    return(lines, lnum)

#===============================================================================
def process_diectives(lines: list):
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

        elif leaf == placeholder:
            new_tree.append(name)

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

################################################################################

