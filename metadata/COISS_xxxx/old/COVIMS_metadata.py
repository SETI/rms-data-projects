################################################################################
# COVIMS_metadata.py: Generates all geometry indices for Cassini VIMS
#
# 8/20/12 MRS - Version 1 created
# 1/3/13 MRS - Revised:
#   - Each output line begins with a volume ID and file specification path
#     before the ring_observation_id.
#   - Output lines that do not complete are always completely suppressed.
#   - A more sophisticated algorithm is used to determine the target name.
#   - Within numeric precision, numbers are identical to those in the first
#     production run.
################################################################################

import oops
import oops.inst.cassini.vims as vims
import numpy as np
import pyparsing
import os, sys, traceback

import metadata as meta

vims.initialize()

execfile("COLUMNS_SATURN_v1.py")

SELECTION = "S"         # summary files only
IGNORED_PHASE_NAMES = ("INSTRUMENT CHECKOUT 1",
                       "VENUS 2 ENCOUNTER",
                       "EARTH ENCOUNTER",
                       "HIGH GAIN ANTENNA TRANSITION",
                       "INSTRUMENT CHECKOUT 2",
                       "EARTH-JUPITER CRUISE",
                       "CRUISE SCIENCE")

############################################
# Method to determine ring_observation_id and target
############################################

def ring_observation_id(filename):
    """Returns the ring observation ID given the name of the VIMS label file,
    up to but not including the final "VIS" or "IR".
    """

    sclk = filename[1:11]
    index = filename.find("_", 12)

    if index >= 0:
        suffix = "." + filename[index+1:index+4]
    else:
        suffix = ""

    return "S/CUBE/CO/VIMS/" + sclk + suffix + "/"

def target_name(dict):
    """Returns the target name from the snapshot's dictionary. If the given
    name is "SKY", it checks the CIMS ID and the TARGET_DESC for something
    different."""

    target = dict["TARGET_NAME"]
    if target != "SKY": return target

    id = dict["OBSERVATION_ID"]
    abbrev = id[id.index("_"):][4:6]

    if abbrev == "SK":
        desc = dict["TARGET_DESC"]
        if desc in MOON_NAMES:
            return desc

    try:
        return CIMS_TARGET_ABBREVIATIONS[abbrev]
    except KeyError:
        return target

############################################

# Currently unused
def meshgrid_and_times(obs, oversample=6, extend=1.5):
    """Returns a meshgrid object and time array that oversamples and extends the
    dimensions of the field of view of a VIMS observation.

    Input:
        obs             the VIMS observation object to for which to generate a
                        meshgrid and a time array.
        oversample      the factor by which to oversample the field of view, in
                        units of the full-resolution VIMS pixel size.
        extend          the number of pixels by which to extend the field of
                        view, in units of the oversampled pixel.

    Return:             (mesgrid, time)
    """

    shrinkage = {("IR",  "NORMAL"): (1,1),
                 ("IR",  "HI-RES"): (2,1),
                 ("IR",  "UNDER" ): (2,1),
                 ("VIS", "NORMAL"): (1,1),
                 ("VIS", "HI-RES"): (3,3)}

    assert obs.instrument == "VIMS"

    (ushrink,vshrink) = shrinkage[(obs.detector, obs.sampling)]

    oversample = float(oversample)
    undersample = (ushrink, vshrink)

    ustep = ushrink / oversample
    vstep = vshrink / oversample

    origin = (-extend * ustep, -extend * vstep)

    limit = (obs.fov.uv_shape.vals[0] + extend * ustep,
             obs.fov.uv_shape.vals[1] + extend * vstep)

    meshgrid = oops.Meshgrid.for_fov(obs.fov, origin, undersample, oversample,
                                     limit, swap=True)

    time = obs.uvt(obs.fov.nearest_uv(meshgrid.uv).swapxy())[1]

    return (meshgrid, time)

############################################

def process_file(root, name, index, files, selection="S"):

    # Get the volume ID
    temp = root.upper()
    volume_id = '"' + temp[temp.index("COVIMS_00"):][:11] + '"'

    # Create the file specification name
    temp = os.path.join(root, name)
    temp = temp[temp.index("/data/"):][1:]
    filespec = '"%-57s"' % temp

    # Create the prefix for the ring_observation_id
    roid_prefix = ring_observation_id(name)
    logstr = "%4d/%4d  %s" % (index, files, roid_prefix)

    # Don't abort if cspice throws a runtime error
    try:

    # Create observations (vis,ir)
        observations = vims.from_file(os.path.join(root,name))

        # For each detector...
        for obs in observations:

            # Ignore empty VIMS channels
            if obs is None: continue

            # Ignore certain mission phases
            if obs.dict["MISSION_PHASE_NAME"] in IGNORED_PHASE_NAMES:
                return

            # Write lines to the output files if necessary
            roid = "%-33s" % (roid_prefix + obs.detector)

            # Get the target
            target = target_name(obs.dict)
            if target in TRANSLATIONS.keys():
                target = TRANSLATIONS[target]

            # Create the backplane
            # (meshgrid, times) = meshgrid_and_times(obs)
            # backplane = oops.Backplane(obs, meshgrid, times)
            backplane = oops.Backplane(obs)

            # Print a log of progress. This records where errors occurred
            logstr = "%s  %4d/%4d  %s %s" % (volume_id[1:-1], index, files,
                                             roid, target)
            print logstr

            prefixes = [volume_id, filespec, '"' + roid + '"']

            # Inventory the bodies in the FOV (including targeted irregulars)
            if (target not in SYSTEM_NAMES and oops.Body.exists(target) and \
                target != 'SUN'):
                    body_names = SYSTEM_NAMES + [target]
            else:
                    body_names = SYSTEM_NAMES

            try:
                inventory_names = obs.inventory(body_names, expand=0.)

                # Write a record into the inventory file
                inventory_file.write(",".join(prefixes))
                for name in inventory_names:
                    inventory_file.write(',"' + name + '"')

                inventory_file.write("\r\n")    # Use <CR><LF> line termination

            except NotImplementedError:
                inventory_names = SYSTEM_NAMES

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
            if target in moon_names and target not in MOON_SUMMARY_DICT:
                MOON_SUMMARY_DICT[target] = meta.replace(MOON_SUMMARY_COLUMNS,
                                                         MOONX, target)
                MOON_DETAILED_DICT[target] = meta.replace(MOON_DETAILED_COLUMNS,
                                                          MOONX, target)
                MOON_TILE_DICT[target] = meta.replace(MOON_TILES, MOONX, target)

            # Write the summary files for the rings and for the planet
            if "S" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_summary, RING_SUMMARY_COLUMNS,
                                  PLANET)

                meta.write_record(prefixes, backplane, blocker,
                                  planet_summary, PLANET_SUMMARY_COLUMNS,
                                  PLANET, moon=PLANET,
                                  moon_length=NAME_LENGTH)

            # Write the detailed files for the rings and for the planet
            if "D" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_detailed, RING_DETAILED_COLUMNS,
                                  PLANET,
                                  tiles=RING_TILES, tiling_min=10)

                meta.write_record(prefixes, backplane, blocker,
                                  planet_detailed, PLANET_DETAILED_COLUMNS,
                                  PLANET, moon=PLANET,
                                  moon_length=NAME_LENGTH,
                                  tiles=PLANET_TILES, tiling_min=10)

            # Write the moon files
            for name in moon_names:

                # ...but skip tiny moons with no intercepts
                if name != target:
                    mask = backplane.where_intercepted(name)
                    if not mask.any(): continue

                if "S" in selection:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_summary, MOON_SUMMARY_DICT[name],
                                      PLANET, moon=name,
                                      moon_length=NAME_LENGTH)

                if "D" in selection:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_detailed, MOON_DETAILED_DICT[name],
                                      PLANET, moon=name,
                                      moon_length=NAME_LENGTH,
                                      tiles=MOON_TILE_DICT[name], tiling_min=10)

    # A RuntimeError is probably caused by missing spice data. There is
    # probably nothing we can do.
    except RuntimeError as e:

        if logstr.endswith("/"): print logstr
        print e
        log_file.write(40*"*" + "\n" + logstr + "\n")
        log_file.write(str(e))
        log_file.write("\n\n")

    # Other kinds of errors are genuine bugs. For now, we just log the
    # problem, and jump over the image; we can deal with it later.
    except (AssertionError, AttributeError, IndexError, KeyError,
            LookupError, TypeError, ValueError, ZeroDivisionError,
            pyparsing.ParseException):

        if logstr.endswith("/"): print logstr
        traceback.print_exc()
        log_file.write(40*"*" + "\n" + logstr + "\n")
        log_file.write(traceback.format_exc())
        log_file.write("\n\n")

############################################
# Finally, generate the indices...
############################################

input_dir = sys.argv[1]
output_dir = sys.argv[2]

ivol = input_dir.rfind('COVIMS_')
volname = input_dir[ivol:ivol+11]

prefix = os.path.join(output_dir, volname)
data_dir = os.path.join(input_dir, 'data')

# Walk the directory tree, counting files to process
count = 0
for root, dirs, files in os.walk(data_dir):
  for name in files:

    # Ignore any file that is not a VIMS file label
    if not name.lower().endswith(".lbl"): continue
    if not name.lower().startswith("v"): continue

    count += 1

# Open the output files
log_file = open(prefix + "_log.txt", "w")
inventory_file = open(prefix + "_inventory.tab", "w")

if "S" in SELECTION:
    ring_summary   = open(prefix + "_ring_summary.tab", "w")
    planet_summary = open(prefix + "_saturn_summary.tab", "w")
    moon_summary   = open(prefix + "_moon_summary.tab", "w")

if "D" in SELECTION:
    ring_detailed   = open(prefix + "_ring_detailed.tab", "w")
    planet_detailed = open(prefix + "_saturn_detailed.tab", "w")
    moon_detailed   = open(prefix + "_moon_detailed.tab", "w")

# Walk the directory tree...
index = 0
for root, dirs, files in os.walk(data_dir):
  for name in files:

    # Ignore any file that is not a VIMS file label
    if not name.lower().endswith(".lbl"): continue
    if not name.lower().startswith("v"): continue

    index += 1
    process_file(root, name, index, count, selection=SELECTION)

# Close all files
log_file.close()
inventory_file.close()

if "S" in SELECTION:
    ring_summary.close()
    planet_summary.close()
    moon_summary.close()

if "D" in SELECTION:
    ring_detailed.close()
    planet_detailed.close()
    moon_detailed.close()

################################################################################

