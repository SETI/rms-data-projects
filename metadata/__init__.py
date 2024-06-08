import sys

from pathlib import Path
from .fancyindex import FancyIndex


###############################
# Define constants
###############################
metadata = sys.modules[__name__]
COLUMNS_PATH = Path(metadata.__file__).parent / 'columns'
TEMPLATES_PATH = Path(metadata.__file__).parent / 'templates'

NULL = "null"                   # Indicates a suppressed backplane calculation


###############################
# Functions
###############################

#===============================================================================
def _directive_insert(lines, lnum, filename):

    # Read file
    f = open(filename, 'r')
    insert_lines = f.readlines()
    f.close()

    # Insert into label
    lines = lines[0:lnum] + insert_lines + lines[lnum+1:]
    lnum += len(insert_lines)

    return(lines, lnum)

#===============================================================================
def preprocess_label(lines):
    """Return a copy of the tree of objects, with each occurrence of the
    placeholder string replaced by the given name."""

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

#===============================================================================
def download(outdir, url, patterns):
    """Download data to local machine."""

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
    for pattern in patterns:
        F.walk(pattern=pattern, dest=coldir)

#===============================================================================
def splitpath(path, string):                    ## move to utilities
    """Split a path at a given string."""

    parts = path.parts
    i = parts.index(string)
    return (Path('').joinpath(*parts[0:i]), Path('').joinpath(*parts[i+1:]))

#===============================================================================
def replace(tree, placeholder, name):
    """Return a copy of the tree of objects, with each occurrence of the
    placeholder string replaced by the given name."""

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
    tree using that name as the replacement."""

    dict = {}
    for name in names:
        dict[name] = replace(tree, placeholder, name)

    return dict

#===============================================================================
def get_volume_glob(col):
    """Build appropriate glob strign for this volume.

    Inputs:
        col      collection name, e.g., GO_xxxx.
    """
    parts = col.rsplit('_', 1)
    id = parts[1]
    id_glob = id.replace('x','[0-9]')
    vol_glob = parts[0] + '_' + id_glob

    return vol_glob

################################################################################

