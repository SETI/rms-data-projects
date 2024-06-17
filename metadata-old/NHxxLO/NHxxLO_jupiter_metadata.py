################################################################################
# lorri_production_jupiter.py: Generates all geometry indices for the LORRI
#                              Jupiter data.
#
# Syntax:
#  python lorri_production_jupiter.py path/to/NHJULO_2001_supplemental_index.lbl
################################################################################

import oops
import oops.inst.nh.lorri as lorri
import numpy as np
import os, sys, traceback

import metadata_jupiter as meta

PLANET = 'JUPITER'

import cspice
cspice.furnsh('/Resources/SPICE/General/PCK/pck00010_edit_v01.tpc')
# This reload last overrides some bug that produces this error message:
# SPICE(INSUFFICIENTANGLES) -- TISBOD: Insufficient number of nutation/precession angles for body 599 at time 2.8472754946623E+07.

############################################
# Key parameters of run
############################################

execfile('COLUMNS_JUPITER.py')  # define the columns, tiles, etc.

SAMPLING = 8                # pixel sampling density
SELECTION = 'S'             # summary files only

############################################
# Construct the meshgrid for each LORRI FOV
############################################

BORDER = 32         # in units of full-size LORRI pixels
PIXEL_FOV = 4.96e-6 # approximate full-size pixel in units of radians
PIXELS = 1024 + 2 * BORDER
EXPAND = BORDER * PIXEL_FOV

FOV_1x1 = oops.fov.FlatFOV((PIXEL_FOV,-PIXEL_FOV), (PIXELS,PIXELS))
FOV_4x4 = oops.fov.FlatFOV((PIXEL_FOV*4,-PIXEL_FOV*4), (PIXELS/4,PIXELS/4))

MESHGRIDS = {}
MESHGRIDS['1x1'] = oops.Meshgrid.for_fov(FOV_1x1, undersample=SAMPLING,
                                                  swap=True)
MESHGRIDS['4x4'] = oops.Meshgrid.for_fov(FOV_4x4, undersample=SAMPLING/4,
                                                  swap=True)

############################################
# LORRI metadata functions
############################################

def ring_observation_id(dict):
    """Returns the ring observation ID given the dictionary derived from the
    supplemental index file.
    """

    return PLANET[0] + '/IMG/NH/LORRI/' + dict['PRODUCT_ID'][4:14]

def target_name(dict):
    """Returns the target name from the snapshot's dictionary."""

    return dict['TARGET_NAME']

def process_index(input_filename, selection='S'):
    """Process one index file and write a selection of metadata files.

    Input:
        input_filename  the name of the label for a LORRI supplemental index
                        file.
        selection       a string containing...
                            'S' to generate summary files;
                            'D' to generate detailed files;
    """

    snapshots = lorri.from_index(input_filename)
    volume_id = snapshots[0].dict['VOLUME_ID']

    records = len(snapshots)

    # Open the output files
    (path, filename) = os.path.split(input_filename)
    path = path.replace('/index', '')
    path = path.replace('/INDEX', '')

    prefix = path + '/' + volume_id
    log_file = open(prefix + '_log.txt', 'w')
    inventory_file = open(prefix + '_inventory.tab', 'w')

    if 'S' in selection:
        ring_summary   = open(prefix + '_ring_summary.tab', 'w')
        planet_summary = open(prefix + '_jupiter_summary.tab', 'w')
        moon_summary   = open(prefix + '_moon_summary.tab', 'w')

    if 'D' in selection:
        ring_detailed   = open(prefix + '_ring_detailed.tab', 'w')
        planet_detailed = open(prefix + '_jupiter_detailed.tab', 'w')
        moon_detailed   = open(prefix + '_moon_detailed.tab', 'w')

    # Loop through the snapshots...

    for i in range(records):
        snapshot = snapshots[i]
        target = target_name(snapshot.dict)

        # Don't abort if cspice throws a runtime error
        try:

            # Create the record prefix
            volume_id = snapshot.dict['VOLUME_ID']
            filespec = snapshot.dict['FILE_SPECIFICATION_NAME'].lower()
            roid = ring_observation_id(snapshot.dict)
            prefixes = ['"' + volume_id + '"',
                        '"%-52s"' % filespec,
                        '"' + roid + '"']

            # Create the backplane
            meshgrid = MESHGRIDS[snapshot.dict['BINNING_MODE']]
            backplane = oops.Backplane(snapshot, meshgrid)

            # Print a log of progress. This records where errors occurred
            logstr = '%s  %4d/%4d  %s  %s' % (volume_id, i+1, records, roid,
                                              target)
            print logstr

            # Inventory the bodies in the FOV (including targeted irregulars)
            if target not in SYSTEM_NAMES and oops.Body.exists(target):
                body_names = SYSTEM_NAMES + [target]
            else:
                body_names = SYSTEM_NAMES

            inventory_names = snapshot.inventory(body_names, expand=EXPAND)

            # Write a record into the inventory file
            inventory_file.write(','.join(prefixes))
            for name in inventory_names:
                inventory_file.write(',"' + name + '"')

            inventory_file.write('\r\n')    # Use <CR><LF> line termination

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
            if 'S' in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_summary, RING_SUMMARY_COLUMNS)

                meta.write_record(prefixes, backplane, blocker,
                                  planet_summary, PLANET_SUMMARY_COLUMNS,
                                  moon=PLANET, moon_length=NAME_LENGTH)

                for name in moon_names:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_summary, MOON_SUMMARY_DICT[name],
                                      moon=name, moon_length=NAME_LENGTH)

            # Write the detailed files
            if 'D' in selection:
                meta.write_record(prefixes, backplane, blocker,
                                  ring_detailed, RING_DETAILED_COLUMNS,
                                  tiles=RING_TILES)

                meta.write_record(prefixes, backplane, blocker,
                                  planet_detailed, PLANET_DETAILED_COLUMNS,
                                  moon=PLANET, moon_length=NAME_LENGTH,
                                  tiles=PLANET_TILES)

                for name in moon_names:
                    meta.write_record(prefixes, backplane, blocker,
                                      moon_detailed, MOON_DETAILED_DICT[name],
                                      moon=name, moon_length=NAME_LENGTH,
                                      tiles=MOON_TILE_DICT[name])

        # A RuntimeError is probably caused by missing spice data. There is
        # probably nothing we can do.
        except RuntimeError as e:

            print e
            log_file.write(40*'*' + '\n' + logstr + '\n')
            log_file.write(str(e))
            log_file.write('\n\n')

        # Other kinds of errors are genuine bugs. For now, we just log the
        # problem, and jump over the image; we can deal with it later.
        except (AssertionError, AttributeError, IndexError, KeyError,
                LookupError, TypeError, ValueError):

            traceback.print_exc()
            log_file.write(40*'*' + '\n' + logstr + '\n')
            log_file.write(traceback.format_exc())
            log_file.write('\n\n')

    # Close all files
    log_file.close()
    inventory_file.close()

    if 'S' in selection:
        ring_summary.close()
        planet_summary.close()
        moon_summary.close()

    if 'D' in selection:
        ring_detailed.close()
        planet_detailed.close()
        moon_detailed.close()

############################################
# Finally, generate the indices...
############################################

for input_filename in sys.argv[1:]:
    process_index(input_filename, selection=SELECTION)

################################################################################
