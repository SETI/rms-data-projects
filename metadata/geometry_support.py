################################################################################
# geometry_support.py - Tools for generating geometric geometry files
################################################################################
import oops
import numpy as np
import os, traceback, time
import warnings
import fnmatch
import pdstable, pdsparser
from pdslabelbot import PdsLabelBot

import metadata as meta
import config

from pathlib import Path


################################################################################
# FORMAT_DICT tuples are:
#
#   (flag, number_of_values, column_width, standard_format, overflow_format,
#    null_value)
#
# where...
#
#   flag = "RAD" = convert values from radians to degrees;
#        = "360" = convert to degrees, with 360-deg periodicity;
#        = ""    = do not modify value.
#
# Adding a column:
#   1. Update format dictionary below as needed
#   2. Run GO_xxxx_geometry.py
#   3. Update label template:
#       a. Update RECORD_BYTES (= .tab last line number + 2)
#       b. Update ROW_BYTES (= RECORD_BYTES)
#       c. Update COLUMNS
#       d. Add column description(s) in label template(s)
#          - Update COLUMN_NUMBER
#          - Update START_BYTE (= table character # after comma + 1)
#       e. Run make_label.py
#          **** check other tables for any new columns resulting from step 1.
#   4. Update unit tests
#   
################################################################################
FORMAT_DICT = {
    "right_ascension"           : ("360", 2, 10, "%10.6f", "%10.5f", -999.),
    "center_right_ascension"    : ("360", 2, 10, "%10.6f", "%10.5f", -999.),
    "declination"               : ("DEG", 2, 10, "%10.6f", "%10.5f", -999.),
    "center_declination"        : ("DEG", 2, 10, "%10.6f", "%10.5f", -999.),

    "distance"                  : ("",    2, 12, "%12.3f", "%12.5e", -999.),
    "center_distance"           : ("",    2, 12, "%12.3f", "%12.5e", -999.),

    "event_time"                : ("",    2, 16, "%16.3f", "%16.9e",    0.),

    "ring_radius"               : ("",    2, 12, "%12.3f", "%12.5e", -999.),
    "ansa_radius"               : ("",    2, 12, "%12.3f", "%12.5e", -999.),

    "altitude"                  : ("",    2, 12, "%12.3f", "%12.5e", -9.99e9),
    "ansa_altitude"             : ("",    2, 12, "%12.3f", "%12.5e", -9.99e9),

    "resolution"                : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "finest_resolution"         : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "coarsest_resolution"       : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "ring_radial_resolution"    : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "ansa_radial_resolution"    : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "ansa_vertical_resolution"  : ("",    2, 10, "%10.5f", "%10.4e", -999.),
    "center_resolution"         : ("",    2, 10, "%10.5f", "%10.4e", -999.),

    "ring_angular_resolution"   : ("DEG", 2, 10, "%8.5f",  "%8.4f",  -999.),

    "longitude"                 : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_longitude"            : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_azimuth"              : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ansa_longitude"            : ("360", 2,  8, "%8.3f",  None,     -999.),
    "sub_solar_longitude"       : ("360", 2,  8, "%8.3f",  None,     -999.),
    "sub_observer_longitude"    : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_sub_solar_longitude"  : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_sub_observer_longitude"
                                : ("360", 2,  8, "%8.3f",  None,     -999.),

    "latitude"                  : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "sub_solar_latitude"        : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "sub_observer_latitude"     : ("DEG", 2,  8, "%8.3f",  None,     -999.),

    "phase_angle"               : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_phase_angle"        : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "incidence_angle"           : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_incidence_angle"      : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_incidence_angle"    : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_center_incidence_angle":("DEG", 2,  8, "%8.3f",  None,     -999.),
    "emission_angle"            : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_emission_angle"       : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_emission_angle"     : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_center_emission_angle": ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_elevation"            : ("DEG", 2,  8, "%8.3f",  None,     -999.),

    "where_inside_shadow"       : ("",    2,  1, "%1d",    None,        0 ),
    "where_in_front"            : ("",    2,  1, "%1d",    None,        0 ),
    "where_in_back"             : ("",    2,  1, "%1d",    None,        0 ),
    "where_antisunward"         : ("",    2,  1, "%1d",    None,        0 )}

ALT_FORMAT_DICT = {
    ("longitude",      "-180")  : ("-180", 2, 8, "%8.3f",  None,     -999.),
    ("ring_longitude", "-180")  : ("-180", 2, 8, "%8.3f",  None,     -999.),
    ("sub_longitude",  "-180")  : ("-180", 2, 8, "%8.3f",  None,     -999.)}

################################################################################
# General functions for writing geometry files
################################################################################
SYSTEMS_TABLE = meta.convert_systems_table(config.SYSTEMS_TABLE, config.SCLK_BASES)

#===============================================================================
def _write_table(filename, rows, system=None, qualifier=None):
    if rows == []:
        return

    # Write table
    print("Writing:", filename)
    meta.write_txt_file(filename, rows)

    # Write label
    table_type = ''
    if qualifier:
        table_type = qualifier + '_geometry'
    meta._make_label(filename, system=system, table_type=table_type)

#===============================================================================
def _write_tables(table, prefix, desc='summary', qualifier=None):

    if type(table) == dict:
        for system in table.keys():
            if qualifier:
                filename = Path(prefix + "_%s.%s_%s.tab" % (system.lower(), qualifier, desc))
                _write_table(filename, table[system], system=system, qualifier=qualifier)
            else:
                filename = Path(prefix + "_%s_%s.tab" % (system.lower(), desc))
                _write_table(filename, table[system], qualifier=qualifier)
    else:
            filename = Path(prefix + "_%s_%s.tab" % (qualifier, desc))
            _write_table(filename, table, qualifier=qualifier)

#===============================================================================
def _add_record(prefixes, backplane, column_descs, 
                  system=None, target=None, name_length=0,
                  tiles=[], tiling_min=100,
                  blocker=None, ignore_shadows=False, 
                  start_index=1, allow_zero_rows=False, no_mask=False, 
                  no_body=False):
    """Generates the geometry and writes rows of a file, given a list of column
    descriptions.

    The tiles argument supports detailed listings where a geometric region is
    broken down into separate subregions. If the tiles argument is empty (which
    is the default), then this routine writes a summary file.

    If the tiles argument is not empty, then the routine writes a detailed file,
    which generally contains one record for each non-empty subregion. The tiles
    argument must be a list of boolean backplane keys, each equal to True for
    the pixels within the subregion. An additional column is added before the
    geometry columns, containing the index value of the associated tile.

    The first backplane in the list is treated differently. It should evaluate
    to an area roughly equal to the union of all the other backplanes. It is
    used to ensure that tiling is suppressed when the region to be tiled is too
    small. If the number of meshgrid samples that are equal to True in this
    backplane is smaller than the limit specified by argument tiling_min, then
    no detailed record is written.

    In a summary listing, this routine writes one record per call, even if all
    values are null. In a detailed listing, only records associated with
    non-empty regions of the meshgrid are written.

    Args:
        prefixes (list):
            A list of the strings to appear at the beginning of the
            line, up to and including the file specification name. Each
            individual string should already be enclosed in quotes.
        backplane (xxx): Backplane for the observation.
        column_descs (list): A list of column descriptions.
        system (str, optional): Name of system, uppercase, e.g., "SATURN".
        target (str, optional): Optionally, the target name to write into the record.
        name_length (int, optional):
            The character width of a column to contain body names.
            If zero (which is the default), then no name is
            written into the record.
        tiles (list, optional):
            An optional list of boolean backplane keys, used to
            support the generation of detailed tabulations instead
            of summary tabulations. See details above.
        tiling_min (int, optional):
            The lower limit on the number of meshgrid points in a
            region before that region is subdivided into tiles.
        blocker (str, optional):
            The name of one body that may be able to block or shadow
            other bodies.
        ignore_shadows (bool, optional):
            True to ignore any mask constraints applicable to
            shadowing or to the sunlit faces of surfaces.
        start_index (int, optional): Index to use for first subregion. Default 1.
        allow_zero_rows (bool, optional):
            True to allow the function to return no rows. If False,
            a row filled with null values will be returned if
            necessary.
        no_body (bool, optional): True to suppress body prefixes.
    """
#xxx Insert "*"?

    # Prepare the rows
    rows = _prep_rows(prefixes, backplane, blocker, column_descs,
                      system, target, name_length,
                      tiles, tiling_min, ignore_shadows,
                      start_index, allow_zero_rows, no_mask=no_mask, 
                      no_body=no_body)

    # Append the complete rows to the output
    lines = []
    for row in rows:
        line = row[0]
        for column in row[1:]:
            line += ','
            line += column

        # Always use PDS-style line termination
        line += '\r\n'
        lines.append(line)

    return lines

#===============================================================================
def _append_body_prefix(prefix_columns, body, length):

    if body is None:
        entry = '"' + length * ' ' + '"'
    else:
        lbody = len(body)
        if lbody > length:
            entry  = '"' + body[:length] + '"'
        else:
            entry  = '"' + body + (length - lbody) * ' ' + '"'

    prefix_columns.append(entry)

#===============================================================================
def _prep_rows(prefixes, backplane, blocker, column_descs,
               system=None, target=None, name_length=0,
               tiles=[], tiling_min=100, ignore_shadows=False,
               start_index=1, allow_zero_rows=False, no_mask=False, 
               no_body=False):
    """Generates the geometry and returns a list of lists of strings. The inner
    list contains string representations for each column in one row of the
    output file. These will be concatenated with commas between them and written
    to the file. The outer list contains one list for each output row. The
    number of output rows can be zero or more.

    The tiles argument supports detailed listings where a geometric region is
    broken down into separate subregions. If the tiles argument is empty (which
    is the default), then this routine writes a summary file.

    If the tiles argument is not empty, then the routine writes a detailed file,
    which generally contains one record for each non-empty subregion. The tiles
    argument must be a list of boolean backplane keys, each equal to True for
    the pixels within the subregion. An additional column is added before the
    geometry columns, containing the index value of the associated tile.

    The first backplane in the list is treated differently. It should evaluate
    to an area roughly equal to the union of all the other backplanes. It is
    used as an overlay to all subsequent tiles.

    In a summary listing, this routine writes one record per call, even if all
    values are null. In a detailed listing, only records associated with
    non-empty regions of the meshgrid are written.

    Args:
        prefixes (list):
            A list of the strings to appear at the beginning of the
            line, up to and including the file specification name. Each
            individual string should already be enclosed in quotes.
        backplane (xxx): Backplane for the observation.
        blocker (str):
            The name of one body that may be able to block or shadow
            other bodies.
        column_descs (list): A list of column descriptions.
        system (str): Name of systembody, uppercase, e.g., "SATURN".
        target (str, optional): Optionally, the target name to write into the record.
        name_length (int, optional):
            The character width of a column to contain body names.
            If zero (which is the default), then no name is
            written into the record.
        tiles (list, optional):
            An optional list of boolean backplane keys, used to
            support the generation of detailed tabulations instead
            of summary tabulations. See details above.
        tiling_min (int, optional):
            The lower limit on the number of meshgrid points in a
            region before that region is subdivided into tiles.
        ignore_shadows (bool, optional):
            True to ignore any mask constraints applicable to
            shadowing or to the sunlit faces of surfaces.
        start_index (int, optional): Index to use for first subregion. Default 1.
        allow_zero_rows (bool, optional):
            True to allow the function to return no rows. If False,
            a row filled with null values will be returned if
            necessary.
        no_mask (bool, optional): True to suppress the use of a mask.
        no_body (bool, optional): True to suppress body prefixes.

    Returns:
        xxx: xxx
    """
#xxx Insert "*"?

    # Handle option for multiple tile sets
    if type(tiles) == tuple:
        rows = []
        local_index = start_index
        for tile in tiles:
            new_rows = _prep_rows(prefixes, backplane, blocker, column_descs,
                                  system, target, name_length,
                                  tile, tiling_min, ignore_shadows,
                                  local_index, allow_zero_rows=True)
            rows += new_rows
            local_index += len(tile) - 1

        if rows or allow_zero_rows:
            return rows

        return _prep_rows(prefixes, backplane, blocker, column_descs,
                          system, target, name_length,
                          [], tiling_min, ignore_shadows,
                          start_index, allow_zero_rows=False)

    # Handle a single set of tiles
    if tiles:
        global_area = backplane.evaluate(tiles[0]).vals
        subregion_masks = [np.logical_not(global_area)]

        if global_area.sum() < tiling_min:
            tiles = []
        else:
            for tile in tiles[1:]:
                mask = backplane.evaluate(tile).vals & global_area
                subregion_masks.append(np.logical_not(mask))
    else:
        subregion_masks = []

    # Initialize the list of rows
    rows = []

    # Create all the needed pixel masks
    excluded_mask_dict = {}
    if not no_mask:
        for column_desc in column_descs:
            event_key = column_desc[0]
            mask_desc = column_desc[1]
            mask_target = event_key[1]

            key = (mask_target,) + mask_desc
            if key in excluded_mask_dict: continue

            excluded_mask_dict[key] = \
                _construct_excluded_mask(backplane, mask_target, system, mask_desc,
                                         blocker, ignore_shadows)
    # Initialize the list of rows

    # Interpret the subregion list
    if tiles:
        indices = range(1,len(tiles))
    else:
        indices = [0]

    # For each subregion...
    for indx in indices:

        # Skip a subregion if it will be empty
        if indx != 0 and np.all(subregion_masks[indx]): continue

        # Initialize the list of columns
        prefix_columns = list(prefixes) # make a copy

        # Append the target and system name as needed
        if not no_body:
            _append_body_prefix(prefix_columns, system, name_length)
            if target is not None:
                _append_body_prefix(prefix_columns, target, name_length)

        # Insert the subregion index
        if subregion_masks:
            prefix_columns.append('%2d' % (indx + start_index - 1))

        # Append the backplane columns
        data_columns = []
        nothing_found = True

        # For each column...
        for column_desc in column_descs:
            event_key = column_desc[0]
            mask_desc = column_desc[1]

            # Fill in the backplane array
            if event_key[1] == meta.NULL:
                values = oops.Scalar(0., True)
            else:
                values = backplane.evaluate(event_key)

            # Make a shallow copy and apply the new masks
            if excluded_mask_dict != {}:
                target = event_key[1]
                excluded = excluded_mask_dict[(target,) + mask_desc]
                values = values.mask_where(excluded)
                if len(subregion_masks) > 1:
                    values = values.mask_where(subregion_masks[indx])
                elif len(subregion_masks) == 1:
                    values = values.mask_where(subregion_masks[0])

            if not np.all(values.mask):
                nothing_found = False

            # Write the column using the specified format
            if len(column_desc) > 2:
                format = ALT_FORMAT_DICT[(event_key[0], column_desc[2])]
            else:
                format = FORMAT_DICT[event_key[0]]

            data_columns.append(_formatted_column(values, format))

        # Save the row if it was completed
        if len(data_columns) < len(column_descs): continue # hopeless error
        if nothing_found and (indx > 0 or allow_zero_rows): continue
        rows.append(prefix_columns + data_columns)

    # Return something if we can
    if rows or allow_zero_rows:
        return rows

    return _prep_rows(prefixes, backplane, blocker, column_descs,
                      system, target, name_length,
                      [], 0, ignore_shadows, start_index,
                      allow_zero_rows=False)

#===============================================================================
def _construct_excluded_mask(backplane, target, system, mask_desc,
                             blocker=None, ignore_shadows=True):
    """Return a mask using the specified target, maskers and shadowers to
    indicate excluded pixels.

    Args:
        backplane (xxx): The backplane defining the target surface.
        target (str): The name of the target surface.
        system (str): Name of system, e.g., "SATURN".
        mask_desc (masker, shadower, face), where:
            Masker      a string identifying what surfaces can obscure the
            target. It is a concatenation of:
            "P" to let the planet obscure the target;
            "R" to let the rings obscure the target;
            "M" to let the blocker body obscure the target.
            shadower    a string identifying what surfaces can shadow the
            target. It is a string containing:
            "P" to let the planet shadow the target;
            "R" to let the rings shadow the target;
            "M" to let the blocker body shadow the target.
            face        a string identifying which face(s) of the surface to
            include:
            "D" to include only the day side of the target;
            "N" to include only the night side of the target;
            ""  to include both faces of the target.
        blocker (str, optional):
            Optionally, the name of the body to use for any "M"
            codes that appear in the mask_desc.
        ignore_shadows (bool, optional):
            True to ignore any shadower or face constraints; default
            is False.
        system (str): Name of system, e.g., "SATURN".

    Returns:
        xxx: xxx
    """
#xxx Insert "*"?

    # Do not let a body block itself
    if target == blocker:
        blocker = None

    # Generate the new mask, with True means included
    if type(target) == str:
        system_name = target.split(':')[0]
        if not oops.Body.exists(system_name):
            return True

    (masker, shadower, face) = mask_desc

    excluded = np.zeros(backplane.shape, dtype='bool')

    # Handle maskers
    if "R" in masker and system == "SATURN":
        excluded |= backplane.where_in_back(target, "SATURN_MAIN_RINGS").vals

    if "P" in masker:
        excluded |= backplane.where_in_back(target, system).vals
        if system == "PLUTO":
            excluded |= backplane.where_in_back(target, "CHARON").vals

    if "M" in masker and blocker is not None:
        excluded |= backplane.where_in_back(target, blocker).vals

    if not ignore_shadows:

      # Handle shadowers
      if "R" in shadower and system == "SATURN":
        excluded |= backplane.where_inside_shadow(target, "SATURN_MAIN_RINGS").vals

      if "P" in shadower:
        excluded |= backplane.where_inside_shadow(target, system).vals
        if system == "PLUTO":
            excluded |= backplane.where_inside_shadow(target, "CHARON").vals

      if "M" in shadower and blocker is not None:
        excluded |= backplane.where_inside_shadow(target, blocker).vals

      # Handle face selection
      if "D" in face:
        excluded |= backplane.where_antisunward(target).vals

      if "N" in face:
        excluded |= backplane.where_sunward(target).vals

#!!!!
# This function does does not handle gridless backplanes properly.  This
# code fixes that, but the core problem should be fixed before this point.
    if np.any(excluded):
        return excluded
    if np.all(excluded):
        return True
    return False


#===============================================================================
def _formatted_column(values, format):
    """Returns one formatted column (or a pair of columns) as a string.

    Args:
        values (xxx): A Scalar of values with its applied mask.
        format (xxx):
            A tuple (flag, number_of_values, column_width,
            standard_format, overflow_format, null_value),
            describing the format to use. Here...
            flag              "DEG" implies that the values should be converted
            from radians to degrees; "360" implies that the
            values should be converted to a range of degrees,
            allowing for ranges that cross from 360 to 0.
            number_of_values  1 yields the mean value
            2 yields the minimium and maximum values
            column_width      Total width of the formatted string.
            standard_format   Desired format code for the field.
            overflow_format   Format code if field overflows the standard_format
            length.
            null_value        Value to indicate NULL.

    Returns:
        xxx: xxx
    """

    # Interpret the format
    (flag, number_of_values, column_width,
     standard_format, overflow_format, null_value) = format

    # Convert from radians to degrees if necessary
    if flag in ("DEG","360","-180"):
        values = values * oops.DPR

    # Create a list of the numeric values for this column
    if number_of_values == 1:
        meanval = values.mean().as_builtin()
        if type(meanval) == oops.Scalar and meanval.mask:
            results = [null_value]
        else:
            results = [meanval]

    elif np.all(values.mask):
        results = [null_value, null_value]

    elif flag == "360":
        results = meta._get_range_mod360(values)

    elif flag == "-180":
        results = meta._get_range_mod360(values, alt_format=flag)

    else:
        results = [values.min().as_builtin(), values.max().as_builtin()]

    # Write the formatted value(s)
    strings = []
    for number in results:
        error_message = ""

        if np.isnan(number):
            warnings.warn("NaN encountered")
            number = null_value

        if np.isinf(number):
            warnings.warn("infinity encountered")
            number = null_value

        string = standard_format % number

        if len(string) > column_width:
            string = overflow_format % number

            if len(string) > column_width:
                number = min(max(-9.99e99, number), 9.99e99)
                string99 = overflow_format % number

                if len(string99) > column_width:
                    error_message = "column overflow: " + string
                else:
                    warnings.warn("column overflow: " + string +
                                  " clipped to " + string99)
                    string = string99

                string = string[:column_width]

        strings.append(string)

        if error_message != "":
            raise RuntimeError(error_message)

    return ",".join(strings)

#===============================================================================
def _add_records(system, table, dicts, body_names, dat):

    # Add sky columns
    table['sky'] += _add_record(dat['prefixes'], dat['backplane'], dicts['sky'],
                                blocker=dat['blocker'], system=system, 
                                name_length=meta.NAME_LENGTH, no_body=True)

    # Add rings and system primary body
    if system:
        if dat['rings_present']:
            table['ring'] += \
                _add_record(dat['prefixes'], dat['backplane'],
                            dicts['ring'][system], blocker=dat['blocker'], 
                            system=system, name_length=meta.NAME_LENGTH)

        table['body'] += \
            _add_record(dat['prefixes'], dat['backplane'],
                        dicts['body'][system], blocker=dat['blocker'], 
                        system=system, target=system, name_length=meta.NAME_LENGTH)

    # Add other bodies
    for name in body_names:
        if name != system:
            table['body'] += \
                _add_record(dat['prefixes'], dat['backplane'], 
                            dicts['body'][name], 
                            blocker=dat['blocker'], system=system, 
                            target=name, name_length=meta.NAME_LENGTH)
#        if dat['rings_present']:
#            table['ring'][name] += _add_record(dat['prefixes'], dat['backplane'], 
#                                                dicts['ring'][name], 
#                                                    target=name+'-ring', name_length=meta.NAME_LENGTH,
#                                                    no_mask=True)

#===============================================================================
def _process_one_index(indir, outdir, logdir,
                       selection='', exclude=None, glob=None):
    """Process the index file for a single volume and write a selection of
    geometry files.

    Args:
        indir (Path): Directory containing the volume.
        outdir (Path): Directory in which to write the geometry files.
        logdir (Path): Directory in which to write the log files.
        selection (str, optional):
            A string containing...
            "S" to generate summary files;
            "D" to generate detailed files;
            set of columns in the old geometry files).
        exclude (list, optional): List of volumes to exclude.
        glob (str, optional): Glob pattern for index files.
    """
#xxx Insert "*"?


    # Handle exclusions
    if exclude is not None:
        for item in exclude:
            if item in indir.parts:
                return

    # Check for supplemental index
    index_filenames = list(indir.glob(glob))
    if len(index_filenames) == 0:
        return
    if len(index_filenames) > 1:
        raise RuntimeError('Mulitple index files found in %s.' % indir)

    index_filename = index_filenames[0]
    ext = index_filename.suffix
    volume_id = config.get_volume_id(indir)
    supplemental_index_name = meta.get_index_name(indir, volume_id, 'supplemental')
    supplemental_index_filename = indir.joinpath(supplemental_index_name+ext)
    if not supplemental_index_filename.exists():
        supplemental_index_filename = None

    # Get observations
    observations = config.from_index(index_filename, supplemental_index_filename)
    records = len(observations)

    # Open output files
    prefix = outdir.joinpath(volume_id).as_posix()

    logdir.mkdir(exist_ok=True)
    log_filename = logdir / Path(volume_id + "_log.txt")

    inventory_filename = Path(prefix + "_inventory.csv")

    body_summary_filename = Path(prefix + "_body_summary.tab")
    body_detailed_filename = Path(prefix + "_body_detailed.tab")

    log_file = open(log_filename, "w")
    inventory_file = open(inventory_filename, "w")
    
    print("Log file: " + log_file.name)
    print("Inventory file: " + inventory_file.name)

    # Set up the datatables
    tables = {
        'summary' : {
            'sky'    : [],
            'ring'   : [],
            'body'   : [],
        },
        'detailed' : {
            'sky'    : [],
            'ring'   : [],
            'body'   : []
        }
    }

    # Loop through the observations...
    count = 0
    for i in range(records):
        if count >= 5: continue            #####Remove Before Launch#######
        observation = observations[i]

        # Determine system, if any
        sclk = observation.dict["SPACECRAFT_CLOCK_START_COUNT"] + '' 
        system, secondaries = meta.get_system(SYSTEMS_TABLE, sclk, config.SCLK_BASES)

        # Set up planet-based geometry
        dat = {
            'rings_present' : None,
            'blocker'       : None
        }

        dicts = {
            'summary' : {
                'sky'    : meta.SKY_COLUMNS,
                'ring'   : meta.RING_SUMMARY_DICT,
                'body'   : meta.BODY_SUMMARY_DICT,
            },
            'detailed' : {
                'sky'    : meta.SKY_COLUMNS,
                'ring'   : meta.RING_DETAILED_DICT,
                'body'   : meta.BODY_DETAILED_DICT
            }
        }

        if system:
            dat['rings_present'] = meta.BODIES[system].ring_frame is not None    
            ring_tile_dict = meta.RING_TILE_DICT[system]
            body_tile_dict = meta.BODY_TILE_DICT[system]

        # Determine target
        target = config.target_name(observation.dict)
        if target in meta.TRANSLATIONS.keys():
            target = meta.TRANSLATIONS[target]

        # Create the record prefix
        volume_id = observation.dict["VOLUME_ID"]
        filespec = observation.dict["FILE_SPECIFICATION_NAME"]
        dat['prefixes'] = ['"' + volume_id + '"',
                           '"%-32s"' % filespec.replace(".IMG", ".LBL")]

        # Create the backplane
        meshgrid = config.meshgrid(observation)
        dat['backplane'] = oops.backplane.Backplane(observation, meshgrid)

        # Print a log of progress. This records where errors occurred
        logstr = "%s  %4d/%4d  %s" % (volume_id, i+1, records, target)
        print(logstr)

        # Don't abort if cspice throws a runtime error
        try:
            body_names = meta.BODIES.keys()
            if target not in meta.BODIES and oops.Body.exists(target):
                body_names += [target]

            # Inventory the bodies in the FOV (including targeted irregulars)
            if body_names:
                body_names = observation.inventory(body_names, expand=config.EXPAND, cache=False)

            # Add any secondaries to body_names
            if secondaries:
                body_names += secondaries

            # Write a record into the inventory file
            inventory_file.write(",".join(dat['prefixes']))
            for name in body_names:
                inventory_file.write(',"' + name + '"')
            inventory_file.write("\r\n")    # Use <CR><LF> line termination

            if system:
                # Define a blocker body, if any
                if target in body_names:
                    dat['blocker'] = target

                # Add an irregular moon to the dictionaries if necessary
                if target in body_names and target not in dicts['summary']['body'].keys():
                    dicts['summary']['body'][target] = meta.replace(meta.BODY_SUMMARY_COLUMNS,
                                                             meta.BODYX, target)
                    dicts['detailed']['body'][target] = meta.replace(meta.BODY_DETAILED_COLUMNS,
                                                              meta.BODYX, target)
                    body_tile_dict[target] = meta.replace(meta.BODY_TILES, meta.BODYX, target)

            # Update the summary tables
            if "S" in selection:
                _add_records(system, tables['summary'], dicts['summary'], body_names, dat)

            # Update the detailed tables
            if "D" in selection:
                _add_records(system, tables['detailed'], dicts['detailed'], body_names, dat)

            count += 1

        # A RuntimeError is probably caused by missing spice data. There is
        # probably nothing we can do.
        except RuntimeError as e:
            print(e)
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

    # Write tables and make labels 
    meta._make_label(inventory_filename)

    if "S" in selection:
        _write_tables(tables['summary']['sky'], prefix, qualifier='sky')
        _write_tables(tables['summary']['ring'], prefix, qualifier='ring')
        _write_tables(tables['summary']['body'], prefix, qualifier='body')
    if "D" in selection:
        _write_tables(tables['detailed']['sky'], prefix, desc='detailed', qualifier='sky')
        _write_tables(tables['detailed']['ring'], prefix, desc='detailed', qualifier='ring')
        _write_tables(tables['detailed']['body'], prefix, qualifier='body')

    # Clean up
    config.cleanup() 

     

################################################################################
# external functions
################################################################################

#===============================================================================
def process_index(input_tree, output_tree, *,
                  selection='', exclude=None, glob=None, 
                  volume=None, new_only=False):
    """Creates geometry files for a collection of volumes.

    Args:
        input_tree (Path): Root of the tree containing the volumes.
        output_tree (Path): Root of the tree in which the output files are
            written in the same directory structure as in the input tree.
        selection (str, optional):
            A string containing...
            "S" to generate summary files;
            "D" to generate detailed files;
            "T" to generate a test file (which matches the
            set of columns in the old geometry files).
        exclude (list, optional): List of volumes to exclude.
        glob (str, optional): Glob pattern for index files.
        volume (str, optional): If given, only this volume is processed.
        new_only (bool): If True, only volumes that contain no output files are 
                         processed.  Overridden if volumeinput provided.
    """

    if volume:
        new_only = False

    input_tree = Path(input_tree) 
    output_tree = Path(output_tree) 

    # Build volume glob
    vol_glob = meta.get_volume_glob(input_tree.name)

    # Walk the input tree, making indexes for each found volume
    logdir = None
    for root, dirs, files in input_tree.walk():
        # __skip directory will not be scanned, so it's safe for test results
        if '__skip' in root.as_posix():
            continue

        # Sort directories for convenience
        dirs.sort()
        root = Path(root)

        if not logdir:
            logdir = root / 'logs'

        # Determine notional set and volume
        parts = root.parts
        set = parts[-2]
        vol = parts[-1]

        # Proceed only if this root is a volume
        if fnmatch.filter([vol], vol_glob):
            if not volume or vol == volume:
                # Set up input and output directories
                indir = root
                if output_tree.parts[-1] != set: 
                    outdir = output_tree.joinpath(set)
                outdir = output_tree.joinpath(vol)

                # Check whether this volume has already been processed
                if new_only & (list(outdir.glob('*_inventory.csv')) != []):
                    continue

                # Process this volumne
                _process_one_index(indir, outdir, logdir,
                                   selection=selection, 
                                   exclude=exclude, 
                                   glob=glob)

################################################################################
