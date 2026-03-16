#!/usr/bin/env python
################################################################################
# coiss_production.py: Generates all geometry indices for Cassini ISS at Saturn
#
# Syntax:
#   python coiss_production.py COISS/COISS_2xxx/index/index.lbl
################################################################################

import oops
import oops.inst.cassini.iss as iss
import numpy as np
import os, sys, traceback
import cspyce

import metadata as meta

iss.initialize()

PREFIX = '/Users/mark/Desktop/CK-cruise/'
cspyce.furnsh(PREFIX + '97288_98002rc.bc')
cspyce.furnsh(PREFIX + '98002_98091rc.bc')
cspyce.furnsh(PREFIX + '98091_98185rc.bc')
cspyce.furnsh(PREFIX + '98185_98279rc.bc')
cspyce.furnsh(PREFIX + '98279_99001rc.bc')
cspyce.furnsh(PREFIX + '99001_99093rc.bc')
cspyce.furnsh(PREFIX + '99093_99182rc.bc')
cspyce.furnsh(PREFIX + '99182_99274rc.bc')
cspyce.furnsh(PREFIX + '99274_00001rc.bc')
cspyce.furnsh(PREFIX + '00001_00092rc.bc')
cspyce.furnsh(PREFIX + '00092_00183rc.bc')
cspyce.furnsh(PREFIX + '00183_00275rc.bc')
cspyce.furnsh(PREFIX + '00275_01001rc.bc')
cspyce.furnsh(PREFIX + '01001_01091rc.bc')
cspyce.furnsh(PREFIX + '01091_01182rc.bc')
cspyce.furnsh(PREFIX + '01182_01274rc.bc')
cspyce.furnsh(PREFIX + '01274_02001rc.bc')
cspyce.furnsh(PREFIX + '02001_02091rc.bc')
cspyce.furnsh(PREFIX + '02091_02182rc.bc')
cspyce.furnsh(PREFIX + '02182_02274rc.bc')
cspyce.furnsh(PREFIX + '02274_03001rc.bc')
cspyce.furnsh(PREFIX + '03001_03091rc.bc')
cspyce.furnsh(PREFIX + '03091_03182rc.bc')
cspyce.furnsh(PREFIX + '03182_03274rc.bc')
cspyce.furnsh(PREFIX + '03274_04001rc.bc')

cspyce.furnsh('/Resources/SPICE/General/PCK/pck00010_edit_v01.tpc')

############################################
# Key parameters of run
############################################

execfile("COLUMNS_SATURN_v1.py")   # define the columns, tiles, etc.

SAMPLING = 8                        # pixel sampling density
SELECTION = "S"                     # summary files only

############################################
# Construct the meshgrid for each ISS FOV
############################################

PIXEL_SIZES = {"NAC":1, "WAC":10}
MODE_SIZES  = {"FULL":1, "SUM2":2, "SUM4":4}

BORDER = 25         # in units of full-size NAC pixels
NAC_PIXEL = 6.0e-6  # approximate full-size NAC pixel in units of radians
EXPAND = BORDER * NAC_PIXEL

MESHGRIDS = {}
for camera in PIXEL_SIZES.keys():
  for mode in MODE_SIZES.keys():
    pixel_wrt_nac = MODE_SIZES[mode] * PIXEL_SIZES[camera]
    pixels = 1024 / MODE_SIZES[mode]

    # Define sampling of FOV
    origin = -float(BORDER) / pixel_wrt_nac
    limit = pixels - origin

    # Revise the sampling to be exact
    samples = int((limit - origin) / SAMPLING + 0.999)
    under = (limit - origin) / samples

    # Construct the meshgrid
    limit += 0.0001
    meshgrid = oops.Meshgrid.for_fov(iss.ISS.fovs[(camera,mode,True)], origin,
                                     undersample=under, limit=limit, swap=True)
    MESHGRIDS[(camera,mode)] = meshgrid

############################################
# ISS metadata functions
############################################

def ring_observation_id(dict):
    """Returns the ring observation ID given the dictionary derived from the
    ISS index file.
    """

    filename = dict["FILE_NAME"]
    return PLANET[0] + "/IMG/CO/ISS/" + filename[1:11] + "/" + filename[0]

def target_name(dict):
    """Returns the target name from the snapshot's dictionary. If the given
    name is "SKY", it checks the CIMS ID and the TARGET_DESC for something
    different."""

    target = dict["TARGET_NAME"]
    if target != "SKY": return target

    id = dict["OBSERVATION_ID"]
    try:
        abbrev = id[id.index("_"):][4:6]

        if abbrev == "SK":
            desc = dict["TARGET_DESC"]
            if desc in MOON_NAMES:
                return desc

        return CIMS_TARGET_ABBREVIATIONS[abbrev]

    except (IndexError, ValueError, KeyError):
        return target

def process_index(input_filename, selection="S"):
    """Process one index file and write a selection of metadata files.

    Input:
        input_filename  the name of the label for an ISS index file.
        selection       a string containing...
                            "S" to generate summary files;
                            "D" to generate detailed files;
                            "T" to generate a test file (which matches the
                                set of columns in the old geometry files).
    """

    snapshots = iss.from_index(input_filename)
    volume_id = snapshots[0].dict["VOLUME_ID"]

    records = len(snapshots)

    # Open the output files
    (path, filename) = os.path.split(input_filename)
    path = path.replace("/index", "")
    path = path.replace("/INDEX", "")

    prefix = path + "/" + volume_id
    log_file = open(prefix + "_log.txt", "w")
    inventory_file = open(prefix + "_inventory.tab", "w")

    if "S" in selection:
        ring_summary   = open(prefix + "_ring_summary.tab", "w")
        planet_summary = open(prefix + "_%s_summary.tab" % PLANET.lower(), "w")
        moon_summary   = open(prefix + "_moon_summary.tab", "w")

    if "D" in selection:
        ring_detailed   = open(prefix + "_ring_detailed.tab", "w")
        planet_detailed = open(prefix + "_%s_detailed.tab" % PLANET.lower(),"w")
        moon_detailed   = open(prefix + "_moon_detailed.tab", "w")

    if "T" in selection:
        test_summary = open(prefix + "_test_summary.tab", "w")

    # Loop through the snapshots...

    for i in range(records):
        snapshot = snapshots[i]

        target = target_name(snapshot.dict)
        if target in TRANSLATIONS.keys():
            target = TRANSLATIONS[target]

        # Don't abort if cspice throws a runtime error
        try:

            # Create the record prefix
            volume_id = snapshot.dict["VOLUME_ID"]
            filespec = snapshot.dict["FILE_SPECIFICATION_NAME"]
            roid = ring_observation_id(snapshot.dict)
            prefixes = ['"' + volume_id + '"',
                        '"%-45s"' % filespec.replace(".IMG", ".LBL"),
                        '"' + roid + '"']

            # Create the backplane
            meshgrid = MESHGRIDS[(snapshot.detector, snapshot.sampling)]
            backplane = oops.Backplane(snapshot, meshgrid)

            # Print a log of progress. This records where errors occurred
            logstr = "%s  %4d/%4d  %s  %s" % (volume_id, i+1, records, roid,
                                              target)
            print logstr

            # Inventory the bodies in the FOV (including targeted irregulars)
            if target not in SYSTEM_NAMES and oops.Body.exists(target):
                body_names = SYSTEM_NAMES + [target]
            else:
                body_names = SYSTEM_NAMES

            inventory_names = snapshot.inventory(body_names, expand=EXPAND)

            # Write a record into the inventory file
            inventory_file.write(",".join(prefixes))
            for name in inventory_names:
                inventory_file.write(',"' + name + '"')

            inventory_file.write("\r\n")    # Use <CR><LF> line termination

            # Convert the inventory into a list of moon names
            if len(inventory_names) > 0 and inventory_names[0] == PLANET:
                moon_names = inventory_names[1:]
            else:
                moon_names = inventory_names

            # Define a blocker moon, if any
            if target in moon_names:
                blocker = target
            else:
                blocker = None

            # Add an irregular moon to the dictionaries if necessary
            if target in moon_names and target not in MOON_SUMMARY_DICT.keys():
                MOON_SUMMARY_DICT[target] = meta.replace(MOON_SUMMARY_COLUMNS,
                                                         MOONX, target)
                MOON_DETAILED_DICT[target] = meta.replace(MOON_DETAILED_COLUMNS,
                                                          MOONX, target)
                MOON_TILE_DICT[target] = meta.replace(MOON_TILES, MOONX, target)

            # Write the summary files
            if "S" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_summary, RING_SUMMARY_COLUMNS,
                                  PLANET)

                meta.write_record(prefixes, backplane, blocker,
                                  planet_summary, PLANET_SUMMARY_COLUMNS,
                                  PLANET, moon=PLANET,
                                  moon_length=NAME_LENGTH)

                for name in moon_names:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_summary, MOON_SUMMARY_DICT[name],
                                      PLANET, moon=name,
                                      moon_length=NAME_LENGTH)

            # Write the detailed files
            if "D" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_detailed, RING_DETAILED_COLUMNS,
                                  PLANET, tiles=(RING_TILES,OUTER_RING_TILES))

                meta.write_record(prefixes, backplane, blocker,
                                  planet_detailed, PLANET_DETAILED_COLUMNS,
                                  PLANET, moon=PLANET,
                                  moon_length=NAME_LENGTH,
                                  tiles=PLANET_TILES)

                for name in moon_names:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_detailed, MOON_DETAILED_DICT[name],
                                      PLANET, moon=name,
                                      moon_length=NAME_LENGTH,
                                      tiles=MOON_TILE_DICT[name])

            # Write the test metadata file
            if "T" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  test_summary, TEST_SUMMARY_COLUMNS, PLANET)

        # A RuntimeError is probably caused by missing spice data. There is
        # probably nothing we can do.
        except (RuntimeError, IOError) as e:

            print e
            log_file.write(40*"*" + "\n" + logstr + "\n")
            log_file.write(str(e))
            log_file.write("\n\n")

        # Other kinds of errors are genuine bugs. For now, we just log the
        # problem, and jump over the image; we can deal with it later.
        except (AssertionError, AttributeError, IndexError, KeyError,
                LookupError, TypeError, ValueError):

            traceback.print_exc()
            log_file.write(40*"*" + "\n" + logstr + "\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n\n")

    # Close all files
    log_file.close()
    inventory_file.close()

    if "S" in selection:
        ring_summary.close()
        planet_summary.close()
        moon_summary.close()

    if "D" in selection:
        ring_detailed.close()
        planet_detailed.close()
        moon_detailed.close()

    if "T" in selection:
        test_summary.close()

############################################
# Finally, generate the indices...
############################################

for input_filename in sys.argv[1:]:
    process_index(input_filename, selection=SELECTION)

################################################################################
