################################################################################
# geometry_support.py - Tools for generating geometric geometry files
################################################################################
import oops
import numpy as np
import os, traceback, time
import warnings
import fnmatch

import metadata as meta
import geometry_config as config
import metadata.index_support as idx

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

#===============================================================================
def _write_record(prefixes, backplane, blocker, outfile, column_descs, planet,
                  moon=None, moon_length=0,
                  tiles=[], tiling_min=100,
                  ignore_shadows=False, start_index=1, allow_zero_rows=False):
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

    In a summmary listing, this routine writes one record per call, even if all
    values are null. In a detailed listing, only records associated with
    non-empty regions of the meshgrid are written.

    Input:
        prefixes        a list of the strings to appear at the beginning of the
                        line, up to and including the ring observation ID. Each
                        individual string should already be enclosed in quotes.
        backplane       backplane for the observation.
        blocker         the name of one moon that may be able to block or shadow
                        other bodies.
        outfile         the output file, already open.
        column_descs    a list of column descriptions.
        planet          name of planet, uppercase, e.g., "SATURN".
        moon            optionally, the moon name to write into the record.
        moon_length     the character width of a column to contain moon names.
                        If zero (which is the default), then no moon name is
                        written into the record.
        tiles           an optional list of boolean backplane keys, used to
                        support the generation of detailed tabulations instead
                        of summary tabulations. See details above.
        tiling_min      the lower limit on the number of meshgrid points in a
                        region before that region is subdivided into tiles.
        ignore_shadows  True to ignore any mask constraints applicable to
                        shadowing or to the sunlit faces of surfaces.
        start_index     index to use for first subregion. Default 1.
        allow_zero_rows True to allow the function to return no rows. If False,
                        a row filled with null values will be returned if
                        necessary.
    """

    # Prepare the rows
    rows = _prep_rows(prefixes, backplane, blocker, column_descs,
                      planet, moon, moon_length,
                      tiles, tiling_min, ignore_shadows,
                      start_index, allow_zero_rows)

    # Write the complete rows to the output file
    for row in rows:
        outfile.write(row[0])
        for column in row[1:]:
            outfile.write(",")
            outfile.write(column)

        # Always use PDS-style line termination
        outfile.write("\r\n")

#===============================================================================
def _prep_rows(prefixes, backplane, blocker, column_descs,
               planet, moon=None, moon_length=0,
               tiles=[], tiling_min=100, ignore_shadows=False,
               start_index=1, allow_zero_rows=False):
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

    In a summmary listing, this routine writes one record per call, even if all
    values are null. In a detailed listing, only records associated with
    non-empty regions of the meshgrid are written.

    Input:
        prefixes        a list of the strings to appear at the beginning of the
                        line, up to and including the ring observation ID. Each
                        individual string should already be enclosed in quotes.
        backplane       backplane for the observation.
        blocker         the name of one moon that may be able to block or shadow
                        other bodies.
        column_descs    a list of column descriptions.
        planet          name of planet, uppercase, e.g., "SATURN".
        moon            optionally, the moon name to write into the record.
        moon_length     the character width of a column to contain moon names.
                        If zero (which is the default), then no moon name is
                        written into the record.
        tiles           an optional list of boolean backplane keys, used to
                        support the generation of detailed tabulations instead
                        of summary tabulations. See details above.
        tiling_min      the lower limit on the number of meshgrid points in a
                        region before that region is subdivided into tiles.
        ignore_shadows  True to ignore any mask constraints applicable to
                        shadowing or to the sunlit faces of surfaces.
        start_index     index to use for first subregion. Default 1.
        allow_zero_rows True to allow the function to return no rows. If False,
                        a row filled with null values will be returned if
                        necessary.
    """

    # Handle option for multiple tile sets
    if type(tiles) == tuple:
        rows = []
        local_index = start_index
        for tile in tiles:
            new_rows = _prep_rows(prefixes, backplane, blocker, column_descs,
                                  planet, moon, moon_length,
                                  tile, tiling_min, ignore_shadows,
                                  local_index, allow_zero_rows=True)
            rows += new_rows
            local_index += len(tile) - 1

        if rows or allow_zero_rows:
            return rows

        return _prep_rows(prefixes, backplane, blocker, column_descs,
                          planet, moon, moon_length,
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
    for column_desc in column_descs:
        event_key = column_desc[0]
        mask_desc = column_desc[1]
        target = event_key[1]

        key = (target,) + mask_desc
        if key in excluded_mask_dict: continue

        excluded_mask_dict[key] = \
            _construct_excluded_mask(backplane, target, planet, mask_desc,
                                     blocker, ignore_shadows)

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

        # Append the moon name if necessary
        if moon_length > 0:
            lmoon = len(moon)
            if lmoon > moon_length:
                entry = '"' + moon[:moon_length] + '"'
            else:
                entry = '"' + moon + (moon_length - lmoon) * ' ' + '"'

            prefix_columns.append(entry)

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
                      planet, moon, moon_length,
                      [], 0, ignore_shadows, start_index,
                      allow_zero_rows=False)

#===============================================================================
def _construct_excluded_mask(backplane, target, planet, mask_desc,
                             blocker=None, ignore_shadows=True):
    """Return a mask using the specified target, maskers and shadowers to
    indicate excluded pixels.

    Input:
        backplane       the backplane defining the target surface.
        target          the name of the target surface.
        planet          name of planet, e.g., "SATURN".
        mask_desc       (masker, shadower, face), where
            masker      a string identifying what surfaces can obscure the
                        target. It is a concatenation of:
                            "P" to let the planet obscure the target;
                            "R" to let the rings obscure the target;
                            "M" to let the blocker moon obscure the target.
            shadower    a string identifying what surfaces can shadow the
                        target. It is a string containing:
                            "P" to let the planet shadow the target;
                            "R" to let the rings shadow the target;
                            "M" to let the blocker moon shadow the target.
            face        a string identifying which face(s) of the surface to
                        include:
                            "D" to include only the day side of the target;
                            "N" to include only the night side of the target;
                            ""  to include both faces of the target.
        blocker         optionally, the name of the moon to use for any "M"
                        codes that appear in the mask_desc.
        ignore_shadows  True to ignore any shadower or face constraints; default
                        is False.
        planet          name of planet, e.g., "SATURN".
    """

    # Do not let a body block itself
    if target == blocker:
        blocker = None

    # Generate the new mask, with True means included
    if type(target) == str:
        body_name = target.split(':')[0]
        if not oops.Body.exists(body_name):
            return True

    (masker, shadower, face) = mask_desc

    excluded = np.zeros(backplane.shape, dtype='bool')

    # Handle maskers
    if "R" in masker and planet == "SATURN":
        excluded |= backplane.where_in_back(target, "SATURN_MAIN_RINGS").vals

    if "P" in masker:
        excluded |= backplane.where_in_back(target, planet).vals
        if planet == "PLUTO":
            excluded |= backplane.where_in_back(target, "CHARON").vals

    if "M" in masker and blocker is not None:
        excluded |= backplane.where_in_back(target, blocker).vals

    if not ignore_shadows:

      # Handle shadowers
      if "R" in shadower and planet == "SATURN":
        excluded |= backplane.where_inside_shadow(target, "SATURN_MAIN_RINGS").vals

      if "P" in shadower:
        excluded |= backplane.where_inside_shadow(target, planet).vals
        if planet == "PLUTO":
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

    Input:
        values          a Scalar of values with its applied mask.
        format          a tuple (flag, number_of_values, column_width,
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
        results = _get_range_mod360(values)

    elif flag == "-180":
        results = _get_range_mod360(values, alt_format=flag)

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
def _range_of_n_angles(n, prob=0.1, tests=100000):
    """Used to study the statistics of n randomly chosen angles.

    For a set of n randomly chosen angles 0-360, return the range such that the
    likelihood of all n angles falling within this range of one another has the
    given probability. Base this on the specified number of tests.
    """
    #### This function is not used.  It should be removed and placed in a 
    #### utility library.

    max_diffs = []
    for k in range(tests):
        values = np.random.rand(n) * 360.
        values = np.sort(values % 360)
        diffs = np.empty(values.size)
        diffs[:-1] = values[1:] - values[:-1]
        diffs[-1]  = values[0] + 360. - values[-1]
        max_diffs.append(diffs.max())

    max_diffs = np.sort(max_diffs)
    cutoff = int((1.-prob) * tests + 0.5)
    return 360. - max_diffs[cutoff]

# This is a tabulation of range_of_n_angles(N) for N in the range 0-1000
# We have 90% confidence that, if the N angles fall within this range, then the
# points do not sample a full 360 degrees of longitude.
NINETY_PERCENT_RANGE_DEGREES = np.array([
    0.000,   0.000,  18.000,  65.682, 105.260, 135.335, 158.717, 177.366, 192.527, 205.134,
  215.648, 225.089, 232.935, 239.913, 246.178, 251.693, 256.834, 261.349, 265.279, 269.092,
  272.471, 275.603, 278.550, 281.247, 283.765, 286.168, 288.339, 290.340, 292.325, 294.165,
  295.864, 297.473, 298.976, 300.490, 301.843, 303.207, 304.438, 305.556, 306.733, 307.824,
  308.847, 309.884, 310.841, 311.734, 312.588, 313.447, 314.264, 315.094, 315.822, 316.550,
  317.261, 317.970, 318.580, 319.220, 319.836, 320.457, 321.044, 321.560, 322.104, 322.608,
  323.119, 323.788, 324.007, 324.891, 325.153, 325.444, 325.846, 326.399, 326.476, 327.109,
  327.315, 327.836, 328.114, 328.482, 328.806, 329.285, 329.764, 329.890, 330.145, 330.617,
  330.905, 331.254, 331.386, 331.701, 332.006, 332.473, 332.484, 332.936, 333.199, 333.220,
  333.744, 333.740, 334.021, 334.347, 334.438, 334.794, 335.075, 335.232, 335.284, 335.611,
  335.909, 335.903, 336.214, 336.544, 336.682, 336.804, 336.868, 337.071, 337.370, 337.528,
  337.688, 337.753, 337.782, 338.255, 338.482, 338.519, 338.627, 338.681, 339.024, 339.043,
  339.346, 339.397, 339.602, 339.700, 339.894, 340.027, 340.092, 340.214, 340.468, 340.584,
  340.538, 340.687, 340.808, 341.034, 340.884, 341.211, 341.394, 341.394, 341.682, 341.751,
  341.812, 341.898, 342.161, 342.244, 342.359, 342.342, 342.426, 342.572, 342.702, 342.626,
  342.873, 343.100, 342.874, 343.032, 343.311, 343.285, 343.471, 343.518, 343.663, 343.694,
  343.727, 343.811, 344.054, 344.033, 344.099, 344.076, 344.212, 344.280, 344.473, 344.431,
  344.579, 344.582, 344.826, 344.849, 344.979, 344.987, 344.990, 345.085, 345.126, 345.149,
  345.264, 345.381, 345.464, 345.579, 345.546, 345.668, 345.718, 345.778, 345.800, 345.889,
  346.031, 345.977, 346.119, 346.129, 346.240, 346.259, 346.308, 346.400, 346.372, 346.454,
  346.527, 346.679, 346.624, 346.738, 346.772, 346.873, 346.938, 346.972, 347.079, 347.084,
  347.144, 347.174, 347.195, 347.298, 347.348, 347.385, 347.464, 347.477, 347.494, 347.526,
  347.618, 347.618, 347.743, 347.709, 347.852, 347.849, 347.970, 347.891, 348.000, 348.009,
  348.070, 348.135, 348.163, 348.210, 348.183, 348.348, 348.448, 348.324, 348.471, 348.483,
  348.515, 348.584, 348.621, 348.644, 348.651, 348.800, 348.774, 348.882, 348.885, 348.911,
  348.823, 348.969, 348.892, 348.970, 349.010, 349.121, 349.142, 349.193, 349.185, 349.329,
  349.318, 349.306, 349.408, 349.338, 349.416, 349.480, 349.479, 349.514, 349.616, 349.652,
  349.652, 349.621, 349.718, 349.735, 349.698, 349.778, 349.743, 349.888, 349.903, 349.864,
  349.951, 349.985, 349.937, 350.090, 350.021, 350.043, 350.226, 350.148, 350.174, 350.273,
  350.259, 350.245, 350.319, 350.264, 350.412, 350.421, 350.456, 350.414, 350.506, 350.563,
  350.593, 350.557, 350.614, 350.621, 350.620, 350.701, 350.669, 350.734, 350.754, 350.773,
  350.878, 350.850, 350.896, 350.863, 350.884, 350.942, 350.934, 351.004, 350.975, 351.065,
  351.036, 351.082, 351.087, 351.130, 351.167, 351.172, 351.161, 351.213, 351.284, 351.262,
  351.201, 351.353, 351.349, 351.336, 351.372, 351.395, 351.425, 351.426, 351.492, 351.507,
  351.555, 351.588, 351.578, 351.581, 351.631, 351.598, 351.621, 351.619, 351.692, 351.672,
  351.766, 351.699, 351.733, 351.759, 351.733, 351.830, 351.862, 351.907, 351.885, 351.869,
  351.982, 351.935, 351.999, 351.965, 352.035, 351.998, 352.025, 352.090, 352.072, 352.087,
  352.087, 352.122, 352.164, 352.123, 352.163, 352.143, 352.175, 352.218, 352.223, 352.352,
  352.307, 352.345, 352.352, 352.355, 352.346, 352.399, 352.362, 352.364, 352.445, 352.496,
  352.473, 352.485, 352.467, 352.530, 352.562, 352.551, 352.609, 352.619, 352.548, 352.652,
  352.612, 352.653, 352.671, 352.702, 352.767, 352.699, 352.759, 352.734, 352.752, 352.769,
  352.798, 352.759, 352.800, 352.862, 352.890, 352.900, 352.864, 352.949, 352.938, 352.921,
  352.975, 352.972, 352.977, 353.005, 352.975, 353.040, 352.997, 353.078, 353.059, 353.064,
  353.019, 353.110, 353.101, 353.141, 353.196, 353.161, 353.200, 353.176, 353.199, 353.178,
  353.252, 353.253, 353.271, 353.284, 353.272, 353.286, 353.321, 353.322, 353.331, 353.322,
  353.396, 353.328, 353.389, 353.370, 353.368, 353.411, 353.410, 353.460, 353.409, 353.483,
  353.475, 353.515, 353.497, 353.492, 353.573, 353.586, 353.509, 353.601, 353.585, 353.590,
  353.578, 353.574, 353.618, 353.645, 353.608, 353.674, 353.692, 353.696, 353.684, 353.697,
  353.701, 353.728, 353.733, 353.765, 353.785, 353.782, 353.777, 353.810, 353.779, 353.788,
  353.782, 353.835, 353.859, 353.864, 353.868, 353.875, 353.883, 353.922, 353.929, 353.952,
  353.937, 353.948, 353.981, 353.971, 353.933, 353.988, 354.019, 354.054, 354.000, 354.025,
  354.053, 354.067, 354.051, 354.050, 354.071, 354.076, 354.163, 354.124, 354.113, 354.122,
  354.145, 354.173, 354.168, 354.187, 354.199, 354.210, 354.252, 354.224, 354.232, 354.238,
  354.235, 354.219, 354.254, 354.283, 354.275, 354.265, 354.289, 354.317, 354.341, 354.318,
  354.366, 354.338, 354.330, 354.403, 354.339, 354.399, 354.377, 354.389, 354.405, 354.435,
  354.422, 354.420, 354.454, 354.463, 354.486, 354.481, 354.462, 354.485, 354.461, 354.508,
  354.520, 354.522, 354.513, 354.560, 354.523, 354.534, 354.585, 354.553, 354.572, 354.562,
  354.600, 354.564, 354.596, 354.642, 354.603, 354.625, 354.621, 354.640, 354.670, 354.661,
  354.686, 354.655, 354.701, 354.674, 354.680, 354.699, 354.731, 354.732, 354.742, 354.741,
  354.778, 354.776, 354.768, 354.767, 354.792, 354.820, 354.778, 354.798, 354.828, 354.844,
  354.826, 354.854, 354.850, 354.835, 354.868, 354.870, 354.888, 354.905, 354.871, 354.911,
  354.898, 354.902, 354.901, 354.974, 354.943, 354.951, 354.938, 354.973, 354.968, 354.979,
  354.997, 354.989, 355.002, 355.006, 355.038, 355.027, 355.043, 355.051, 354.994, 355.045,
  355.048, 355.048, 355.048, 355.059, 355.043, 355.104, 355.091, 355.122, 355.120, 355.099,
  355.099, 355.123, 355.155, 355.150, 355.118, 355.152, 355.176, 355.190, 355.124, 355.175,
  355.197, 355.170, 355.184, 355.256, 355.212, 355.236, 355.227, 355.221, 355.213, 355.260,
  355.277, 355.257, 355.278, 355.261, 355.280, 355.256, 355.309, 355.314, 355.290, 355.308,
  355.307, 355.331, 355.315, 355.336, 355.323, 355.335, 355.349, 355.376, 355.341, 355.400,
  355.357, 355.350, 355.366, 355.379, 355.398, 355.374, 355.409, 355.422, 355.406, 355.433,
  355.447, 355.447, 355.426, 355.459, 355.452, 355.475, 355.456, 355.471, 355.494, 355.496,
  355.483, 355.505, 355.495, 355.478, 355.517, 355.518, 355.530, 355.538, 355.551, 355.530,
  355.535, 355.572, 355.569, 355.543, 355.589, 355.555, 355.607, 355.586, 355.634, 355.578,
  355.604, 355.624, 355.616, 355.610, 355.629, 355.643, 355.629, 355.630, 355.634, 355.649,
  355.677, 355.650, 355.679, 355.658, 355.657, 355.690, 355.703, 355.686, 355.703, 355.694,
  355.714, 355.742, 355.729, 355.705, 355.721, 355.712, 355.741, 355.736, 355.768, 355.781,
  355.727, 355.758, 355.771, 355.794, 355.774, 355.794, 355.789, 355.772, 355.783, 355.807,
  355.804, 355.807, 355.828, 355.822, 355.838, 355.836, 355.820, 355.841, 355.840, 355.851,
  355.840, 355.857, 355.859, 355.889, 355.873, 355.887, 355.896, 355.876, 355.896, 355.936,
  355.896, 355.891, 355.934, 355.940, 355.934, 355.918, 355.927, 355.935, 355.921, 355.950,
  355.976, 355.998, 355.955, 355.937, 355.963, 355.984, 355.979, 355.969, 355.991, 355.980,
  355.994, 355.972, 355.999, 355.995, 355.989, 356.010, 356.025, 355.989, 356.038, 356.045,
  356.026, 356.042, 356.054, 356.038, 356.073, 356.058, 356.067, 356.074, 356.063, 356.077,
  356.091, 356.087, 356.116, 356.089, 356.103, 356.096, 356.124, 356.106, 356.126, 356.109,
  356.127, 356.101, 356.120, 356.132, 356.133, 356.141, 356.153, 356.162, 356.143, 356.142,
  356.167, 356.192, 356.168, 356.176, 356.170, 356.189, 356.167, 356.194, 356.188, 356.190,
  356.201, 356.189, 356.219, 356.216, 356.235, 356.233, 356.224, 356.218, 356.225, 356.257,
  356.248, 356.240, 356.244, 356.237, 356.261, 356.267, 356.293, 356.262, 356.275, 356.286,
  356.292, 356.293, 356.287, 356.306, 356.307, 356.297, 356.306, 356.300, 356.333, 356.310,
  356.329, 356.338, 356.302, 356.337, 356.314, 356.330, 356.336, 356.348, 356.335, 356.361,
  356.355, 356.377, 356.350, 356.389, 356.352, 356.380, 356.366, 356.378, 356.396, 356.382,
  356.402, 356.374, 356.381, 356.402, 356.406, 356.414, 356.390, 356.430, 356.424, 356.428,
  356.429, 356.440, 356.445, 356.441, 356.450, 356.463, 356.461, 356.439, 356.448, 356.462,
  356.451, 356.479, 356.471, 356.449, 356.495, 356.476, 356.486, 356.473, 356.479, 356.518,
  356.494, 356.492, 356.507, 356.494, 356.509, 356.513, 356.544, 356.509, 356.511, 356.504,
  356.517, 356.541, 356.526, 356.527, 356.542, 356.536, 356.553, 356.548, 356.553, 356.537,
  356.534, 356.557, 356.587, 356.563, 356.583, 356.588, 356.593, 356.582, 356.611, 356.583,
  356.589, 356.604, 356.585, 356.569, 356.598, 356.615, 356.598, 356.620, 356.624, 356.624,
  356.620, 356.625, 356.644, 356.627, 356.630, 356.651, 356.637, 356.640, 356.666, 356.651,
  356.661, 356.664, 356.679, 356.655, 356.638, 356.659, 356.674, 356.681, 356.672, 356.675,
  356.677, 356.687, 356.691, 356.685, 356.701, 356.712, 356.701, 356.696, 356.703, 356.717,
])

#===============================================================================
def _ninety_percent_gap_degrees(n):
    """For n samples, return the approximate number of degrees for the largest
    gap in coverage providing 90% confidence that the angular coverage is not
    actually complete."""

    # Below 1000, use the tabulation
    if n < 1000:
        return 360. - NINETY_PERCENT_RANGE_DEGREES[n]

    # Otherwise, this empirical fit does a good job
    return 1808. * n**(-0.912)

#===============================================================================
def _get_range_mod360(values, alt_format=None):
    """Returns the minimum and maximum values in the array, allowing for the
    possibility that the numeric range wraps around from 360 to 0.

    Input:
        values          the set of values for which to determine the range.
        alt_format      "-180" to return values in the range (-180,180) rather
                        than (0,360).
    """

    # Check for use of negative values
    use_minus_180 = (alt_format == "-180")

    complete_coverage = [-180.,180.] if use_minus_180 else [0.,360.]

    # Flatten the set of values
    values = np.asarray(values.flatten().vals)

    # With only one value, we know nothing
    if values.size <= 1:
#        return complete_coverage
        return [values, values]

    # Locate the largest gap in coverage
    values = np.sort(values % 360)
    diffs = np.empty(values.size)
    diffs[:-1] = values[1:] - values[:-1]
    diffs[-1]  = values[0] + 360. - values[-1]

    # Locate the largest gap and use it to define the range
    gap_index = np.argmax(diffs)
    diff_max  = diffs[gap_index]
    range_mod360 = [values[(gap_index + 1) % values.size], values[gap_index]]

    # Convert to range -180 to 180 if necessary
    if use_minus_180:
        (lower, upper) = range_mod360
        lower = (lower + 180.) % 360. - 180.
        upper = (upper + 180.) % 360. - 180.
        range_mod360 = [lower, upper]

    # We want 90% confidence that the coverage is not complete. Otherwise,
    # return the complete range
    if diff_max >= _ninety_percent_gap_degrees(values.size):
        return range_mod360
    else:
        return complete_coverage

#===============================================================================
def _make_label(filepath, creation_time=None, preserve_time=False):
    """Creates a label for a given geometry table.

    Input:
        filepath        Path to the geometry table.
        creation_time   Creation time to use instead of the current time.
        preserve_time   If True, the creation time is copied from any existing
                        label before it is overwrittten.
    """

    filename = filepath.name
    dir = filepath.parent
    body = filepath.stem
    lblfile = dir / (body + '.lbl')

    # Load the data file if it exists
    if not filepath.is_file():
        return

    f = open(filepath)
    lines = f.readlines()
    f.close()
    
    if lines == []:
        return
    
    recs = len(lines)
    linelen = len(lines[0])

    is_inventory = ('inventory' in body)
    for line in lines:
        if not is_inventory:
            assert len(line) == linelen     # all lines have the same length

    # Get the instrument and volume_id
    underscore = filename.index('_')
    inst_id = filename[:underscore]
    volume_id = filename[:underscore + 5]

    # Determine the creation time
    if preserve_time:
        if lblfile.is_file():
            f = open(lblfile)
            lines = f.readlines()
            f.close()

            creation_time = 'missing'
            for line in lines:
                if line.startswith('PRODUCT_CREATION_TIME'):
                    creation_time = line[-21:-2]
                    assert creation_time[:2] == '20'
                    break

            assert creation_time != 'missing'

    elif creation_time is None:
        creation_time = '%04d-%02d-%02dT%02d:00:00' % time.gmtime()[:4]

    # Read the template
    template = meta.TEMPLATES_DIR.as_posix() + '/%s.lbl' % body[underscore+6:]

    try:
        f = open(template)
        lines = f.readlines()
        f.close()
    except:
        return

    # Preprocess the template
    lines = meta.process_diectives(lines)

    # Replace the tags in the template
    if is_inventory:
        subs = ('"' + filename + '"',
                '"' + volume_id + '"',
                creation_time,
                creation_time[:10])
    else:
        subs = (str(recs),
                '"' + filename + '"',
                '"' + volume_id + '"',
                creation_time,
                str(recs))

    l = 0
    for i in range(len(subs)):
        while not lines[l].endswith('$\n'):
            l += 1

        lines[l] = lines[l][:-3] + ' ' + subs[i] + '\n'

    # Write the new label
    f = open(lblfile, 'w')
    for line in lines:
        f.write(line)

    f.close()

#===============================================================================
def _process_one_index(indir, outdir, 
                       selection='', append=False, exclude=None, glob=None, 
                       no_table=False, no_log=True):
    """Process the index file for a single volume and write a selection of 
    geometry files.

    Input:
        indir           directory containing the volume.
        outdir          directory in whioch to werite the geometry files.
        selection       a string containing...
                            "S" to generate summary files;
                            "D" to generate detailed files;
                            "T" to generate a test file (which matches the
                                set of columns in the old geometry files).
        append          if True, geometry files that already exist are not
                        ignored.
        exclude         list of volumes to exclude.
        glob            glob pattern for index files.
        no_table        if True, do not produce a table, just a label.
        no_log          if True, do not produce a log file.
    """

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
    supplemental_index_name = idx._get_index_name(indir, 'supplemental')
    supplemental_index_filename = indir.joinpath(supplemental_index_name+ext)
    if not supplemental_index_filename.exists():
        supplemental_index_filename = None

    # Get observations
    observations = config.from_index(index_filename, supplemental_index_filename)
    volume_id = observations[0].dict["VOLUME_ID"]
    records = len(observations)

    # Open the output files
    prefix = outdir.joinpath(volume_id).as_posix()

##    log_filename = Path(prefix + "_log.txt")
    inventory_filename = Path(prefix + "_inventory.tab")
    
    ring_summary_filename = Path(prefix + "_ring_summary.tab")
    planet_summary_filename = Path(prefix + "_%s_summary.tab" % config.PLANET.lower())
    moon_summary_filename = Path(prefix + "_moon_summary.tab")
    
    ring_detailed_filename = Path(prefix + "_ring_detailed.tab")
    planet_detailed_filename = Path(prefix + "_%s_detailed.tab" % config.PLANET.lower())
    moon_detailed_filename = Path(prefix + "_moon_detailed.tab")

    test_summary_filename = Path(prefix + "_test_summary.tab")

##    log_file = open(log_filename, "w")
    inventory_file = open(inventory_filename, "w")
    
    if not no_table:
##        print("Log file: " + log_file.name)
        print("Inventory file: " + inventory_file.name)

        if "S" in selection:
            ring_summary   = open(ring_summary_filename, "w")
            planet_summary = open(planet_summary_filename, "w")
            moon_summary   = open(moon_summary_filename, "w")

            print("Ring summary file:", ring_summary_filename)
            print("Planet summary file:", planet_summary_filename)
            print("Moon summary file:", moon_summary_filename)

        if "D" in selection:
            ring_detailed   = open(ring_detailed_filename, "w")
            planet_detailed = open(planet_detailed_filename,"w")
            moon_detailed   = open(moon_detailed_filename, "w")

            print("Ring detail file:", ring_detailed_filename)
            print("Planet detail file:", planet_detailed_filename)
            print("Moon detail file:", moon_detailed_filename)

        if "T" in selection:
            test_summary = open(test_summary_filename, "w")

            print("Test summary file:", test_summary_filename)

        # Loop through the observations...
        for i in range(records):
            observation = observations[i]
        
            if append:
                if ring_summary_filename.exists() or \
                    moon_summary_filename.exists() or \
                    planet_summary_filename.exists() :
                        continue

            target = config.target_name(observation.dict)

            if target in config.TRANSLATIONS.keys():
                target = config.TRANSLATIONS[target]

            # Don't abort if cspice throws a runtime error
            try:

                # Create the record prefix
                volume_id = observation.dict["VOLUME_ID"]
                filespec = observation.dict["FILE_SPECIFICATION_NAME"]
                roid = config.ring_observation_id(observation.dict)
                prefixes = ['"' + volume_id + '"',
                            '"%-45s"' % filespec.replace(".IMG", ".LBL"),
                            '"' + roid + '"']

                # Create the backplane
                meshgrid = config.meshgrid(observation)
                backplane = oops.backplane.Backplane(observation, meshgrid)

                # Print a log of progress. This records where errors occurred
                logstr = "%s  %4d/%4d  %s  %s" % (volume_id, i+1, records, roid,
                                                target)
                print(logstr)

                # Inventory the bodies in the FOV (including targeted irregulars)
                if target not in config.SYSTEM_NAMES and oops.Body.exists(target):
                    body_names = config.SYSTEM_NAMES + [target]
                else:
                    body_names = config.SYSTEM_NAMES

                inventory_names = observation.inventory(body_names, expand=config.EXPAND, cache=False)

                # Write a record into the inventory file
                inventory_file.write(",".join(prefixes))
                for name in inventory_names:
                    inventory_file.write(',"' + name + '"')

                inventory_file.write("\r\n")    # Use <CR><LF> line termination

                # Convert the inventory into a list of moon names
                if len(inventory_names) > 0 and inventory_names[0] == config.PLANET:
                    moon_names = inventory_names[1:]
                else:
                    moon_names = inventory_names

                # Define a blocker moon, if any
                if target in moon_names:
                    blocker = target
                else:
                    blocker = None

                # Add an irregular moon to the dictionaries if necessary
                if target in moon_names and target not in config.MOON_SUMMARY_DICT.keys():
                    config.MOON_SUMMARY_DICT[target] = meta.replace(config.MOON_SUMMARY_COLUMNS,
                                                                      config.MOONX, target)
                    config.MOON_DETAILED_DICT[target] = meta.replace(config.MOON_DETAILED_COLUMNS,
                                                                config.MOONX, target)
                    config.MOON_TILE_DICT[target] = meta.replace(config.MOON_TILES, config.MOONX, target)

                # Write the summary files
                if "S" in selection:
                    _write_record(prefixes, backplane, blocker,
                                  ring_summary, config.RING_SUMMARY_COLUMNS,
                                  config.PLANET)

                    _write_record(prefixes, backplane, blocker,
                                  planet_summary, config.PLANET_SUMMARY_COLUMNS,
                                  config.PLANET, moon=config.PLANET,
                                  moon_length=config.NAME_LENGTH)

                    for name in moon_names:
                        _write_record(prefixes, backplane, blocker,
                                      moon_summary, config.MOON_SUMMARY_DICT[name],
                                      config.PLANET, moon=name,
                                      moon_length=config.NAME_LENGTH)

                # Write the detailed files
                if "D" in selection:
                    _write_record(prefixes, backplane, blocker,
                                  ring_detailed, config.RING_DETAILED_COLUMNS,
                                  config.PLANET, tiles=(config.RING_TILES, config.OUTER_RING_TILES))

                    _write_record(prefixes, backplane, blocker,
                                  planet_detailed, config.PLANET_DETAILED_COLUMNS,
                                  config.PLANET, moon=config.PLANET,
                                  moon_length=config.NAME_LENGTH,
                                  tiles=PLANET_TILES)

                    for name in moon_names:
                        _write_record(prefixes, backplane, blocker,
                                      moon_detailed, config.MOON_DETAILED_DICT[name],
                                      config.PLANET, moon=name,
                                      moon_length=config.NAME_LENGTH,
                                      tiles=config.MOON_TILE_DICT[name])

                # Write the test geometry file
                if "T" in selection:
                    _write_record(prefixes, backplane, blocker,
                                  test_summary, config.TEST_SUMMARY_COLUMNS, config.PLANET)

            # A RuntimeError is probably caused by missing spice data. There is
            # probably nothing we can do.
            except RuntimeError as e:

                print(e)
##                log_file.write(40*"*" + "\n" + logstr + "\n")
##                log_file.write(str(e))
##                log_file.write("\n\n")

            # Other kinds of errors are genuine bugs. For now, we just log the
            # problem, and jump over the image; we can deal with it later.
            except (AssertionError, AttributeError, IndexError, KeyError,
                    LookupError, TypeError, ValueError):

                traceback.print_exc()
#                log_file.write(40*"*" + "\n" + logstr + "\n")
##                log_file.write(traceback.format_exc())
##                log_file.write("\n\n")

    # Close all files
##    log_file.close()
    inventory_file.close()

    try:
        ring_summary.close()
        planet_summary.close()
        moon_summary.close()
        ring_detailed.close()
        planet_detailed.close()
        moon_detailed.close()
        test_summary.close()
    except:
        pass

    # Make labels
    _make_label(inventory_filename)

    if "S" in selection:
        _make_label(ring_summary_filename)
        _make_label(planet_summary_filename)
        _make_label(moon_summary_filename)
    if "D" in selection:
        _make_label(ring_detailed_filename)
        _make_label(planet_detailed_filename)
        _make_label(moon_detailed_filename)
    if "T" in selection:
        _make_label(test_summary_filename)

################################################################################
# external functions
################################################################################

#===============================================================================
def process_index(input_tree, output_tree,
                  selection='', append=False, exclude=None, glob=None, 
                  volume=None, no_table=False):
    """Creates geometry files for a collection of volumes.

    Input:
        input tree      root of the tree containing the volumes.
        output tree     root of the tree in which the output files are
                        written in the same directory structure as in the 
                        input tree.
        selection       a string containing...
                            "S" to generate summary files;
                            "D" to generate detailed files;
                            "T" to generate a test file (which matches the
                                set of columns in the old geometry files).
        append          if True, geometry files that already exist are not
                        ignored.
        exclude         list of volumes to exclude.
        glob            glob pattern for index files.
        volume          if given, only this volume is processed.
        no_table        if True, do not produce a table, just a label.
    """

    input_tree = Path(input_tree) 
    output_tree = Path(output_tree) 

    # Build volume glob
    vol_glob = meta.get_volume_glob(input_tree.name)

    # Walk the input tree, making indexes for each found volume
#    for root, dirs, files in input_tree.walk():    #### Path.walk() doens't exist in python 3.8
    for root, dirs, files in os.walk(input_tree.as_posix()):
        root = Path(root)

        # Determine notional set and volume
        parts = root.parts
        set = parts[-2]
        vol = parts[-1]

        # Test whether this root is a volume
        if fnmatch.filter([vol], vol_glob):
            if not volume or vol == volume:
                indir = root
                if output_tree.parts[-1] != set: 
                    outdir = output_tree.joinpath(set)
                outdir = output_tree.joinpath(vol)
                _process_one_index(indir, outdir, 
                                   selection=selection, 
                                   append=append, 
                                   exclude=exclude, 
                                   glob=glob,
                                   no_table=no_table)

################################################################################
