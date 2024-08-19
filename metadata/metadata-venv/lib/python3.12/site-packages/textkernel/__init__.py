##########################################################################################
# textkernel/__init__.py
##########################################################################################
"""
This is a set of routines for parsing SPICE text kernels. This module implements the
complete syntax specification as discussed in the SPICE Kernel Required Reading document,
"kernel.req": https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html

The `textkernel` module provides two functions for reading text kernels:

- `from_text`: Given a string representing the contents of a text kernel, return a
  dictionary of the values found.
- `from_file`: Given the path to a text kernel, read the contents and return a dictionary
  of the values found.

and two functions for manipulating text kernels:

- `continued_value`: Interpret a list of strings as one or more continued strings.
- `update_dict`: Merge the contents of two text kernel dictionaries, preserving nested
  values.
"""

__all__ = ['from_text', 'from_file', 'continued_value', 'update_dict']

import pathlib
import re

from textkernel._DATA_GRAMMAR          import _DATA_GRAMMAR
from textkernel._NAME_GRAMMAR          import _NAME_GRAMMAR
from textkernel._PREDEFINED_BODY_INFO  import _PREDEFINED_BODY_INFO
from textkernel._PREDEFINED_FRAME_INFO import _PREDEFINED_FRAME_INFO

try:
    from ._version import __version__
except ImportError:  # pragma: nocover
    __version__ = 'Version unspecified'


# Regular expressions to match \\begindata and \\begintext sections. These must be alone
# on a line. NOTE: There's really only one backslash in front of the "b", but two are
# needed in the Python source code because a single backslash indicates an escape.
_BEGINDATA = re.compile(r'\n[ \t]*\\begindata[ \t]*\r?\n', re.S)
_BEGINTEXT = re.compile(r'\n[ \t]*\\begintext[ \t]*\r?\n', re.S)


def from_text(text, tkdict=None, *, commented=True, contin=''):
    """
    Parse a string as the contents of a text kernel and return a dict of values found.

    Args:
        text (str): The contents as a SPICE text kernel. It can be represented as a single
            string with embedded newlines or as a list of strings.
        tkdict (dict, optional): An optional starting dictionary. If provided, the new
            content is merged into the one provided; otherwise, a new dictionary is
            returned.
        commented (bool, optional): True if the kernel text contains comments delimited
            by `\\\\begintext` and `\\\\begindata`.
        contin (str, optional): Optional sequence of characters indicating that a string
            is "continued", meaning that its value should be concatenated with the
            next string in the list. See the rules for continued strings here:
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#Additional%20Text%20Kernel%20Syntax%20Rules

            If a text kernel uses multiple different continuation sequences (which
            is exceedingly unlikely), you can only specify one sequence here; use
            continued_value() to interpret the values of other continued strings.
            The default value is "+" for all metakernels.

    Returns:
        dict: A dictionary containing all the parameters in the given string.

        The returned dictionary is keyed by all the parameter names (on the left
        side of an equal sign) in the text kernel, and each associated
        dictionary value is that found on the right side. Values are Python
        ints, floats, strings, datetime objects, or lists of one or more of
        these.

        For convenience, the returned dictionary adds additional, "hierarchical"
        keys that provide alternative access to the same values. Hierarchical
        keys are substrings from the original parameter name, which return a
        sub-dictionary keyed by part or all of the remainder of that parameter
        name.

        - Parameter names with a slash are split apart as if they represented
          components of a file directory tree, so these are equivalent:

          - tkdict["DELTET/EB"] == tkdict["DELTET"]["EB"]

        - When a body or frame ID is embedded inside a parameter name, it is extracted,
          converted to integer, and used as a piece of the hierarchy, making these
          equivalent:

          - tkdict["BODY399_POLE_RA"] == tkdict["BODY"][399]["POLE_RA"]
          - tkdict["SCLK01_MODULI_32"] == tkdict["SCLK"][-32]["01_MODULI"]

          Leading and trailing underscores before and after the embedded numeric ID are
          stripped from the hierarchical keys, as you can see in the examples above.

        - When the name associated with a body or frame ID is known, that name can be
          used in the place of the integer ID:

          - tkdict["BODY"][399] == tkdict["BODY"]["EARTH"]
          - tkdict["FRAME"][10013] == tkdict["FRAME"]["IAU_EARTH"]
          - tkdict["SCLK"][-32] == tkdict["SCLK"]["VOYAGER 2"]

        - If a frame is associated with a particular central body, the body's ID can also
          be used in place of the frame's ID:

          - tkdict["FRAME"][399] == tkdict["FRAME"]["IAU_EARTH"]

        - Note that the "BODY" and "FRAME" dictionaries also have an additional entry
          keyed by "ID", which returns the associated integer ID:

          - tkdict["FRAME"][623]["ID"] = 623
          - tkdict["FRAME"]["IAU_SUTTUNGR"]["ID"] = 623

          This ensures that you can look up a body or frame by name and readily obtain its
          ID.
    """

    tkdict_is_new = (tkdict is None)
    if tkdict_is_new:
        tkdict = {}

    if not isinstance(text, str):
        text = '\n'.join(text)

    # Fill in the default continuation character if this is a metakernel
    if not contin and 'KERNELS_TO_LOAD' in text:
        contin = '+'

    # Pre-process commented text
    if commented:
        parts = _BEGINDATA.split(text)[1:] + ['']    # blank at end restores final newline
        parts = [_BEGINTEXT.split(p)[0] for p in parts]
        text = '\n'.join(parts)

    # Parse
    parsed = _DATA_GRAMMAR.parse_string(text).as_list()

    # Track new sub-dictionaries and new name/ID pairs
    indices = []         # a list of tuples (before-text, idcode or name)

    new_body_names = []  # a list of new tuples NAIF_BODY_NAME values
    new_body_codes = []  # a list of new tuples NAIF_BODY_CODE values

    # Insert each value into the dictionary
    for (name, op, value) in parsed:

        # Catch new name/idcode pairs (before merging lists)
        if name == 'NAIF_BODY_NAME':
            new_body_names += value if isinstance(value, list) else [value]

        if name == 'NAIF_BODY_CODE':
            new_body_codes += value if isinstance(value, list) else [value]

        # Merge continued strings if necessary; any other value is returned as is
        value = continued_value(value, contin)

        # Merge list with previous value if operator is "+="
        if op == '+=':
            if not isinstance(value, list):
                value = [value]

            if name in tkdict:
                old_value = tkdict[name]
                if isinstance(old_value, list):
                    value = old_value + value
                else:
                    value = [old_value] + value

        # Insert into the dictionary under the full name
        tkdict[name] = value

        # Identify the alternative names
        parsed_name = _NAME_GRAMMAR.parse_string(name).as_list()[0]

        # Unless it's a nested or indexed name, we're done
        if isinstance(parsed_name, str):
            continue

        # Put the nested or indexed value into a sub-dictionary
        subdict = tkdict
        for subname in parsed_name[:-1]:
            subdict = subdict.setdefault(subname, {})

            # Keep track of indexed sub-dictionaries
            if isinstance(parsed_name, tuple):
                indices.append(parsed_name[:2])

        subdict[parsed_name[-1]] = value

    # Key any pre-existing sub-dictionaries by a new name
    if new_body_codes and not tkdict_is_new:

        # For each sub-dictionary...
        for (key, subdict) in tkdict.items():
            if not isinstance(subdict, dict):
                continue

            # ... if the idcode is a key, use the name as a key as well
            for k, idcode in enumerate(new_body_codes):
                if idcode in subdict:
                    subdict[new_body_names[k]] = subdict[idcode]

    # Key any new indexed sub-dictionaries by name(s) as well as ID
    for (prefix, key) in indices:
        prefix_dict = tkdict[prefix]
        prefix_subdict = prefix_dict[key]

        allkeys = [key]

        # Determine whether this is a body or a frame; get predefined values if any
        if prefix in ('BODY', 'OBJECT', 'SCLK'):
            bf_key = 'BODY'
            (name, idcode) = _PREDEFINED_BODY_INFO.get(key, ('', 0))
        else:
            bf_key = 'FRAME'
            (name, idcode, center) = _PREDEFINED_FRAME_INFO.get(key, ('', 0, 0))

        # See if this already has an associated ID and name
        bf_dict = tkdict.setdefault(bf_key, {})     # tkdict['BODY'] or tkdict['FRAME']
        bf_subdict = bf_dict.setdefault(key, {})
        allkeys.append(bf_subdict.get('NAME', ''))
        allkeys.append(bf_subdict.get('ID', 0))

        # Include the pre-defined values if any
        allkeys += [name, idcode]

        # This gets the body name in some "rocks" files. Example:
        #   OBJECT_65040_FRAME = 'IAU_S12_2004'
        # implies name='S12_2004'
        if bf_key == 'BODY':
            frame_name = prefix_subdict.get('FRAME', '')
            if frame_name.startswith('IAU_'):
                allkeys.append(frame_name[4:])

        # This is how the name is embedded in some instrument kernels
        if bf_key == 'FRAME' and 'INS' in tkdict:
            try:
                allkeys.append(tkdict['INS'][key]['FOV_FRAME'])
            except KeyError:                                        # pragma: no cover
                pass

        # Remove duplicate, blank, and zero keys
        newkeys = []
        for k in allkeys:
            if k and k not in newkeys:
                newkeys.append(k)

        allkeys = newkeys

        # Identify the first ID and the first name
        idcodes = [k for k in allkeys if isinstance(k, int)]
        first_id = idcodes[0] if idcodes else 0

        names = [k for k in allkeys if isinstance(k, str)]
        first_name = names[0] if names else ''

        # Make sure each "BODY"/"FRAME" dictionary has an entry for the ID and NAME
        if first_id and 'ID' not in bf_subdict:
            bf_subdict['ID'] = first_id

        if first_name and 'NAME' not in bf_subdict:
            bf_subdict['NAME'] = first_name

        # Insert additional dictionary keys
        for k in allkeys[1:]:       # first item in thelist is the current key
            bf_dict[k] = bf_subdict
            prefix_dict[k] = prefix_subdict

        # We're done with body IDs
        if bf_key == 'BODY':
            continue

        # Identify the frame center
        if not center:
            center = bf_subdict.get('CENTER', 0)

        # We can derive the center ID from the frame ID for instruments
        if not center and isinstance(key, int):
            center = -((-key) // 1000)
            if not (0 > center > -1000):
                center = 0                                          # pragma: no cover

        if center and 'CENTER' not in bf_subdict:
            bf_subdict['CENTER'] = center

    # Insert a "FRAME" dictionary key for each unique body center ID
    frame_dict = tkdict.get('FRAME', {})
    frame_ids = {}          # center ID -> list of frame IDs
    for frame_subdict in frame_dict.values():
        if 'CENTER' in frame_subdict:                               # pragma: no branch
            center_id = frame_subdict['CENTER']
            frame_ids.setdefault(center_id, []).append(frame_subdict['ID'])

    for center_id, frame_id_list in frame_ids.items():
        if len(frame_id_list) == 1 and center_id not in frame_dict:
            frame_dict[center_id] = frame_dict[frame_id_list[0]]    # pragma: no cover

    return tkdict


def from_file(path, tkdict=None, *, contin=''):
    """
    Parse the contents of a text kernel, returning a dict of the values found.

    Args:
        path (str or Path): The path to a kernel file as a string or `pathlib.Path`.
        tkdict (dict, optional): An optional starting dictionary. If provided, the new
            content is merged into the one provided; otherwise, a new dictionary is
            returned.
        contin (str, optional): Optional sequence of characters indicating that a string
            is "continued", meaning that its value should be concatenated with the
            next string in the list. See the rules for continued strings here:
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#Additional%20Text%20Kernel%20Syntax%20Rules

            If a text kernel uses multiple different continuation sequences (which
            is exceedingly unlikely), you can only specify one sequence here; use
            continued_value() to interpret the values of other continued strings.
            The default value is "+" for all metakernels.

    Returns:
        dict: A dictionary containing all the parameters in the given string.

        The returned dictionary is keyed by all the parameter names (on the left
        side of an equal sign) in the text kernel, and each associated
        dictionary value is that found on the right side. Values are Python
        ints, floats, strings, datetime objects, or lists of one or more of
        these.

        For convenience, the returned dictionary adds additional, "hierarchical"
        keys that provide alternative access to the same values. Hierarchical
        keys are substrings from the original parameter name, which return a
        sub-dictionary keyed by part or all of the remainder of that parameter
        name.

        - Parameter names with a slash are split apart as if they represented
          components of a file directory tree, so these are equivalent:

          - tkdict["DELTET/EB"] == tkdict["DELTET"]["EB"]

        - When a body or frame ID is embedded inside a parameter name, it is extracted,
          converted to integer, and used as a piece of the hierarchy, making these
          equivalent:

          - tkdict["BODY399_POLE_RA"] == tkdict["BODY"][399]["POLE_RA"]
          - tkdict["SCLK01_MODULI_32"] == tkdict["SCLK"][-32]["01_MODULI"]

          Leading and trailing underscores before and after the embedded numeric ID are
          stripped from the hierarchical keys, as you can see in the examples above.

        - When the name associated with a body or frame ID is known, that name can be
          used in the place of the integer ID:

          - tkdict["BODY"][399] == tkdict["BODY"]["EARTH"]
          - tkdict["FRAME"][10013] == tkdict["FRAME"]["IAU_EARTH"]
          - tkdict["SCLK"][-32] == tkdict["SCLK"]["VOYAGER 2"]

        - If a frame is associated with a particular central body, the body's ID can also
          be used in place of the frame's ID:

          - tkdict["FRAME"][399] == tkdict["FRAME"]["IAU_EARTH"]

        - Note that the "BODY" and "FRAME" dictionaries also have an additional entry
          keyed by "ID", which returns the associated integer ID:

          - tkdict["FRAME"][623]["ID"] = 623
          - tkdict["FRAME"]["IAU_SUTTUNGR"]["ID"] = 623

          This ensures that you can look up a body or frame by name and readily obtain its
          ID.
    """

    text = pathlib.Path(path).read_text(encoding='latin8')
    return from_text(text, tkdict=tkdict, commented=True, contin=contin)


##########################################################################################
# Kernel dictionary management
##########################################################################################

def continued_value(value, contin='+'):
    """Interpret a list of strings as one or more continued strings.

    Use this function if you did not specify the string's continuation sequence when you
    created the dictionary.

    Args:
        value (Any): A value from a text kernel.
        contin (str, optional): A sequence of characters indicating that a string is
            "continued", meaning that its value should be concatenated with the next
            string in the list. See the rules for continued strings here:
            https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html#Additional%20Text%20Kernel%20Syntax%20Rules

    Returns:
        Any: The same value after the continuation sequence has been applied.

        If the list now contains only a single value, that string is returned
        instead of a list containing the string.

        If any other type of value is given as input, that value is returned as is.
    """

    if not contin:
        return value

    if not isinstance(value, list):
        return value

    newlist = [value[0]]
    merged = False
    for item in value[1:]:
        if isinstance(item, str) and isinstance(newlist[-1], str):
            stripped = newlist[-1].rstrip()
            if stripped.endswith(contin):
                newlist[-1] = stripped[:-len(contin)] + item
                merged = True
                continue

        newlist.append(item)

    # If a list was not modified, return the original in case this matters
    if not merged:
        return value

    # If the new list contains a single merged string, just return the string
    if len(newlist) == 1:
        return newlist[0]

    return newlist


def update_dict(tkdict, newdict):
    """Merge the contents of two text kernel dictionaries, preserving nested values.

    Values in the new dictionary take precedence.

    The returned dictionary is the same as what one would get by reading the first text
    kernel and then using its return value as the `tkdict` input when reading the second
    text kernel.

    Args:
        tkdict (dict): A text kernel dictionary.
        newdict (dict): A second text kernel dictionary.

    Returns:
        dict: The input `tkdict`, updated with the contents of `newdict`.
    """

    def alt_dict_keys(d):
        """Create a dict that maps each key to its alt keys including itself."""

        alt_keys = {}
        keys_for_dict_id = {}
        for key, value in d.items():
            if isinstance(value, dict):
                dict_id = id(value)
                keys_for_dict_id.setdefault(dict_id, set()).add(key)

        for alt_key_set in keys_for_dict_id.values():
            for key in alt_key_set:
                alt_keys[key] = alt_key_set

        return alt_keys

    # Use NAIF_BODY_CODE/NAME to define new keys
    new_body_codes = newdict.get('NAIF_BODY_CODE', [])
    if new_body_codes:
        new_body_names = newdict.get('NAIF_BODY_NAME', [])
        for key, subdict in tkdict.items():
            if not isinstance(subdict, dict):
                continue
            for k, idcode in enumerate(new_body_codes):
                if idcode in subdict:
                    subdict[new_body_names[k]] = subdict[idcode]

    # Identify each dictionary's alternative keys
    new_dict_keys = alt_dict_keys(newdict)
    old_dict_keys = alt_dict_keys(tkdict)

    # Copy/merge dictionary items
    keys_handled = set()
    for key, new_value in newdict.items():

        # Merge dictionaries
        if isinstance(new_value, dict):
            if key in keys_handled:
                continue

            old_keys = old_dict_keys.get(key, set())
            new_keys = new_dict_keys[key] - old_keys
            if old_keys:
                old_key = list(old_keys)[0]
                updated = update_dict(tkdict[old_key], new_value)
            else:
                updated = new_value

            for key in new_keys:
                tkdict[key] = updated

            keys_handled |= new_keys
            continue

        # Insert new values
        if key not in tkdict:
            tkdict[key] = new_value
            continue

        # Leave identical values alone
        tk_value = tkdict[key]
        if tk_value == new_value:
            continue

        # Otherwise, convert to list if necessary and concatenate
        concat  = tk_value  if isinstance(tk_value,  list) else [tk_value]
        concat += new_value if isinstance(new_value, list) else [new_value]
        tkdict[key] = concat

    return tkdict

##########################################################################################
