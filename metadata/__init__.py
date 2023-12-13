import os, sys


###############################
# Define constants
###############################
metadata = sys.modules[__name__]
COLUMNS_PATH = os.path.join(os.path.dirname(metadata.__file__), 'columns')
TEMPLATES_PATH = os.path.join(os.path.dirname(metadata.__file__), 'templates')

NULL = "null"                   # Indicates a suppressed backplane calculation


###############################
# Functions
###############################

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

