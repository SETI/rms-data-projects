#!/usr/bin/env python
################################################################################
# COUVIS_metadata.py: Generates all geometry indices for Cassini UVIS
################################################################################

import oops
import oops.inst.cassini.uvis as uvis
import numpy as np
import pyparsing
import os, sys, traceback, warnings, logging

import metadata as meta

uvis.initialize()

execfile("COLUMNS_SATURN_v1.py")

SELECTION = "S"         # summary files only
MAX_TIMESTEPS = 1000

PREFIX = ""             # global variable to hold record prefix string

############################################
# Prepare to log warning messages
############################################

logging.basicConfig(level=logging.INFO)

def log_warnings(message, category, filename, lineno, file=None):
    global PREFIX
    print "**** WARNING: " + str(message)
    warning_file.write(PREFIX + "  " + str(message) + "\n")

old_showwarning = warnings.showwarning
warnings.showwarning = log_warnings

############################################
# Method to determine ring_observation_id
############################################

def ring_observation_id(filename):
    """Returns the ring observation ID given the name of the UVIS label file.
    """

    i20 = filename.index("20")      # The year always starts with 20
    detector = filename[:i20]
    year   = filename[i20+0:i20+4]
    doy    = filename[i20+5:i20+8]
    hour   = filename[i20+9:i20+11]
    minute = filename[i20+12:i20+14]

    # Check for a seconds field
    second = filename[i20+15:i20+17]
    has_seconds = (second != 'LB')

    if has_seconds:
        return "S/CO/UVIS/%4s-%3sT%2s-%2s-%2s/%-4s" % (year, doy, hour, minute,
                                                       second, detector)
    else:
        return "S/CO/UVIS/%4s-%3sT%2s-%2s/%-4s   " % (year, doy, hour, minute,
                                                      detector)

############################################
# Method to define prefix text for table
############################################

def volume_and_filespec(root, name):
    """Returns the volume_id and file_specification_name for a UVIS label file.
    """

    ivol = root.rindex("COUVIS_0")
    volume_id = root[ivol:ivol+11]
    dir_path = root[ivol+12:ivol+26]

    if len(dir_path) > ivol + 26:
        raise ValueError("Illegal directory path: ", dir_path)

    file_spec = "%s/%-25s" % (dir_path, name)
    return (volume_id, file_spec)

############################################

def process_file(root, name, index, files, selection="S"):

    # Don't abort if cspice throws a runtime error
    try:

        (volume_id, file_spec) = volume_and_filespec(root, name)

        roid = ring_observation_id(name)
        logstr = "%s  %4d/%4d  %s" % (volume_id, index, files, roid)
        print logstr,
        terminated_print = False

        i20 = name.index("20")
        year = int(name[i20:i20+4])
        if year < 2004:
            print "skipped"
            return
 
        prefixes = ['"' + volume_id + '"',
                    '"' + file_spec + '"',
                    '"' + roid + '"']

        # Create the observation object
        obs = uvis.from_file(os.path.join(root,name), enclose=True)

        # Get the target
        target = obs.dict["TARGET_NAME"].upper()
        if target in TRANSLATIONS.keys():
            target = TRANSLATIONS[target]

        print " " + target
        terminated_print = True

        # Create the backplane
        cad = obs.cadence

        if cad.steps <= MAX_TIMESTEPS:
            steps = cad.steps
            tstride = cad.tstride
        else:
            steps = MAX_TIMESTEPS
            tstride = (cad.time[1] - cad.time[0]) / steps

        time_vals = cad.tstart + tstride * np.arange(0.5, steps)

        if len(obs.shape) > 1:
            time = oops.Scalar(time_vals[:,np.newaxis])
        else:
            time = oops.Scalar(time_vals)

        backplane = oops.Backplane(obs, time=time)

        # Catch SPICE NOFRAMECONNECT exceptions before going any further
        ignore = backplane.right_ascension()

        # Define a list of moon names and the blocker moon
        if target in SYSTEM_NAMES and target != PLANET:
            blocker = target
            moon_names = [target]
        else:
            blocker = None
            moon_names = []

        # Write the summary files for the rings and for the planet
        if "S" in selection:
            meta.write_record(prefixes, backplane, blocker,
                              ring_summary, RING_SUMMARY_COLUMNS,
                              PLANET, ignore_shadows=True)

            meta.write_record(prefixes, backplane, blocker,
                              planet_summary, PLANET_SUMMARY_COLUMNS,
                              PLANET, moon=PLANET,
                              moon_length=NAME_LENGTH,
                              ignore_shadows=True)

        # Write the detailed files for the rings and for the planet
        if "D" in selection:
            meta.write_record(prefixes, backplane, blocker,
                              ring_detailed, RING_DETAILED_COLUMNS,
                              PLANET, tiles=RING_TILES,
                              ignore_shadows=True)

            meta.write_record(prefixes, backplane, blocker,
                              planet_detailed, PLANET_DETAILED_COLUMNS,
                              PLANET, moon=PLANET,
                              moon_length=NAME_LENGTH,
                              tiles=PLANET_TILES,
                              ignore_shadows=True)

        # Write the moon files
        for name in moon_names:
            if "S" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  moon_summary, MOON_SUMMARY_DICT[name],
                                  PLANET, moon=name,
                                  moon_length=NAME_LENGTH,
                                  ignore_shadows=True)

            if "D" in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  moon_detailed, MOON_DETAILED_DICT[name],
                                  PLANET, moon=name,
                                  moon_length=NAME_LENGTH,
                                  tiles=MOON_TILE_DICT[name],
                                  ignore_shadows=True)

    # A RuntimeError is probably caused by missing spice data. There is
    # probably nothing we can do.
    except RuntimeError as e:

        if "NOFRAMECONNECT" in str(e):
            print "**** SPICE(NOFRAMECONNECT)"
            noframe_file.write(PREFIX + "\n")
        else:
            if not terminated_print: print
            print e

            error_file.write(40*"*" + "\n" + logstr + "\n")
            error_file.write(str(e))
            error_file.write("\n\n")

    # Other kinds of errors are genuine bugs. For now, we just log the
    # problem, and jump over the image; we can deal with it later.
    except (AssertionError, AttributeError, IndexError, KeyError,
            LookupError, TypeError, ValueError, ZeroDivisionError,
            pyparsing.ParseException):

        if not terminated_print: print

        traceback.print_exc()
        error_file.write(40*"*" + "\n" + logstr + "\n")
        error_file.write(traceback.format_exc())
        error_file.write("\n\n")

############################################
# Finally, generate the indices...
############################################

input_dir = sys.argv[1]
output_dir = sys.argv[2]

ivol = input_dir.rfind('COUVIS_')
volname = input_dir[ivol:ivol+11]

prefix = os.path.join(output_dir, volname)
data_dir = os.path.join(input_dir, 'data')

# Walk the directory tree, counting files to process
count = 0
for root, dirs, files in os.walk(data_dir):
  for name in files:

    # Ignore any file that is not a VIMS file label
    if not name.lower().endswith(".lbl"): continue
    if len(name) > 6 and "20" not in name[3:6]: continue

    count += 1

error_filename   = prefix + "_errors.txt"
warning_filename = prefix + "_warnings.txt"
noframe_filename = prefix + "_noframeconnect.txt"

error_file   = open(error_filename,   "w")
warning_file = open(warning_filename, "w")
noframe_file = open(noframe_filename, "w")

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

    # Ignore any file that is not a UVIS file label
    if not name.lower().endswith(".lbl"): continue
    if len(name) > 6 and "20" not in name[3:6]: continue

    index += 1
    process_file(root, name, index, count, selection=SELECTION)

# Close all files
error_file.close()
warning_file.close()
noframe_file.close()

if os.path.getsize(error_filename) == 0: os.remove(error_filename)
if os.path.getsize(warning_filename) == 0: os.remove(warning_filename)
if os.path.getsize(noframe_filename) == 0: os.remove(noframe_filename)

if "S" in SELECTION:
    ring_summary.close()
    planet_summary.close()
    moon_summary.close()

if "D" in SELECTION:
    ring_detailed.close()
    planet_detailed.close()
    moon_detailed.close()

################################################################################

