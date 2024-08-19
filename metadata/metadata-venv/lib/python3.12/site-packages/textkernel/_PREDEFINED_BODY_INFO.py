##########################################################################################
# textkernel/_PREDEFINED_BODY_INFO.py
#
# _PREDEFINED_BODY_INFO is a dictionary keyed by body ID and body name, which returns a
# named tuple ("name", "idcode") containing the name and ID of the body.
#
# This content is read from the SPICE toolkit source file "zzidmap.f".
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
BodyInfo = namedtuple('BodyInfo', ['name', 'idcode'])

# Get the path to the latest FORTRAN source file zzidmap.f
tk_root_dir = pathlib.Path(sys.modules['textkernel'].__file__).parent
source_dirs = list(tk_root_dir.glob('SPICE_N????'))
source_dirs.sort()
zzidmap = source_dirs[-1] / 'zzidmap.f'

with zzidmap.open(encoding='latin8') as f:
    recs = f.readlines()

# Extract every BODCOD/BODNAM pair
regex = re.compile(r" +(BLTNAM|BLTCOD)\((.*)\) *= *(.*)", re.I)

bltnam_dict = {}
bltcod_dict = {}
dicts = {'BLTNAM': bltnam_dict, 'BLTCOD': bltcod_dict}

for rec in recs:
    rec = rec.rstrip()

    match = regex.fullmatch(rec)
    if match:
        dictname = match.group(1).upper()
        key = match.group(2).replace(' ', '').upper()

        try:
            value = eval(match.group(3))
        except Exception:                       # pragma: no cover
            continue

        dicts[dictname][key] = value

# Save the info keyed by body name and body ID
_PREDEFINED_BODY_INFO = {}

for key in bltnam_dict:
    name = bltnam_dict[key]
    if key not in bltcod_dict:
        continue                                # pragma: no cover

    idcode = bltcod_dict[key]
    info = BodyInfo(name, idcode)

    _PREDEFINED_BODY_INFO[name] = info
    _PREDEFINED_BODY_INFO[idcode] = info

##########################################################################################
