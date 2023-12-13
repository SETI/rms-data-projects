import oops
import hosts.galileo.ssi as ssi
import numpy as np
import os, sys, traceback

import metadata as meta

ssi.initialize()

############################################
# Key parameters of run
############################################
exec(open(os.path.join(meta.COLUMNS_PATH, "COLUMNS_JUPITER.py")).read())

SAMPLING = 8                        # pixel sampling density
#SELECTION = "S"                     # summary files only

############################################
# Construct the meshgrid 
############################################

## TODO: this should be obtainable from the host module
MODE_SIZES  = {"FULL":1,
               "HMA": 1,
               "HIM": 1,
               "IM8": 1,
               "HCA": 1,
               "IM4": 1,
               "XCM": 1,
               "HCM": 1,
               "HCJ": 1,
               "HIS": 2,
               "AI8": 2}

BORDER = 25         # in units of full-size SSI pixels
NAC_PIXEL = 6.0e-6  # approximate full-size SSI pixel in units of radians
EXPAND = BORDER * NAC_PIXEL

MESHGRIDS = {}
for mode in MODE_SIZES.keys():
    pixel_wrt_full = MODE_SIZES[mode]
    pixels = 800 / MODE_SIZES[mode]

    # Define sampling of FOV
    origin = -float(BORDER) / pixel_wrt_full
    limit = pixels - origin

    # Revise the sampling to be exact
    samples = int((limit - origin) / SAMPLING + 0.999)
    under = (limit - origin) / samples

    # Construct the meshgrid
    limit += 0.0001
    meshgrid = oops.Meshgrid.for_fov(ssi.SSI.fovs[mode], origin,
                                     undersample=under, limit=limit, swap=True)
    MESHGRIDS[mode] = meshgrid


############################################
# SSI geometry functions
############################################

from_index = ssi.from_index

#===============================================================================
def ring_observation_id(dict):
    """Returns the ring observation ID given the dictionary derived from the
    SSI index file.
    """

    _,filename = os.path.split(dict["FILE_SPECIFICATION_NAME"])
##### TODO: no idea whether this is correct
    return "J/IMG/GO/SSI/" + filename[:11]

#===============================================================================
def target_name(dict):
    """Returns the target name from the snapshot's dictionary. If the given
    name is "SKY", it checks the CIMS ID and the TARGET_DESC for something
    different."""

    return  dict["TARGET_NAME"]


    target = dict["TARGET_NAME"]
    if target != "SKY": return target

    id = dict["OBSERVATION_ID"]
    abbrev = id[id.index("_"):][4:6]

    if abbrev == "SK":
        desc = dict["TARGET_DESC"]
        if desc in MOON_NAMES:
            return desc

    try:
        return columns.CIMS_TARGET_ABBREVIATIONS[abbrev]
    except KeyError:
        return target

