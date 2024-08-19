##########################################################################################
# textkernel/_PREDEFINED_FRAME_INFO.py
#
# _PREDEFINED_FRAME_INFO is a dictionary keyed by frame ID and frame name, which returns a
# named tuple ("name", "idcode", "center") containing the name, frame ID, and body ID of
# the frame center.
#
# At startup, this  content is read from the SPICE toolkit source file "zzfdat.f".
#
# The subdirectory SPICE_N0067 contains the two source files zzidmap.f and zzfdat.f from
# version 67 of SPICE toolkit in FORTRAN. The former defines standard bodies and the
# latter defines standard frames.
#
# Each release of the toolkit adds new standard bodies and frames. Upon the release of
# version 68, create a new subdirectory "SPICE_N0068" and copy the updated versions of
# these two source files into it. This routine automatically checks for the latest SPICE
# subdirectory and loads the source from there, ensuring that the dictionary content will
# be up to date, while also allowing us to keep track of the change history.
##########################################################################################

import pathlib
import re
import sys

from collections import namedtuple
FrameInfo = namedtuple('FrameInfo', ['name', 'idcode', 'center'])

# Get the path to the latest FORTRAN source file zzfdat.f
tk_root_dir = pathlib.Path(sys.modules['textkernel'].__file__).parent
source_dirs = list(tk_root_dir.glob('SPICE_N????'))
source_dirs.sort()
zzfdat = source_dirs[-1] / 'zzfdat.f'

with zzfdat.open(encoding='latin8') as f:
    recs = f.readlines()

# Extract every NAME/IDCODE/CENTER set
regex = re.compile(r" +(NAME|IDCODE|CENTER) *\((.*)\) *= *(.*)", re.I)

name_dict   = {}
idcode_dict = {}
center_dict = {}
dicts = {'NAME': name_dict, 'IDCODE': idcode_dict, 'CENTER': center_dict}

for rec in recs:
    rec = rec.rstrip()

    match = regex.fullmatch(rec)
    if match:
        dictname = match.group(1).upper()
        key = match.group(2).replace(' ', '').upper()

        try:
            value = eval(match.group(3))
        except Exception:
            continue

        dicts[dictname][key] = value

# Save the info keyed by frame name, frame ID, and center body ID
_PREDEFINED_FRAME_INFO = {}

for key in name_dict:
    name = name_dict[key]
    if key not in idcode_dict or key not in center_dict:    # pragma: no branch
        continue                                            # pragma: no cover

    idcode = idcode_dict[key]
    center = center_dict[key]
    info = FrameInfo(name, idcode, center)

    _PREDEFINED_FRAME_INFO[name] = info
    _PREDEFINED_FRAME_INFO[idcode] = info

    # The center body ID always maps to the first/lowest frame ID
    if center in _PREDEFINED_FRAME_INFO:
        if idcode > _PREDEFINED_FRAME_INFO[center].idcode:  # pragma: no branch
            continue

    _PREDEFINED_FRAME_INFO[center] = info

##########################################################################################
