################################################################################
# metadata.py - Tools for generating geometric index files
################################################################################

import oops
import numpy as np
import warnings

NULL = "null"                   # Indicates a suppressed backplane calculation

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
################################################################################

FORMAT_DICT = {
    "right_ascension"           : ("360", 2, 10, "%10.6f", "%10.5f", -999.),
    "center_right_ascension"    : ("360", 1, 10, "%10.6f", "%10.5f", -999.),
    "declination"               : ("DEG", 2, 10, "%10.6f", "%10.5f", -999.),
    "center_declination"        : ("DEG", 1, 10, "%10.6f", "%10.5f", -999.),

    "distance"                  : ("",    2, 12, "%12.3f", "%12.5e", -999.),
    "center_distance"           : ("",    1, 12, "%12.3f", "%12.5e", -999.),

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
    "center_resolution"         : ("",    1, 10, "%10.5f", "%10.4e", -999.),

    "ring_angular_resolution"   : ("DEG", 2, 10, "%8.5f",  "%8.4f",  -999.),

    "longitude"                 : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_longitude"            : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ring_azimuth"              : ("360", 2,  8, "%8.3f",  None,     -999.),
    "ansa_longitude"            : ("360", 2,  8, "%8.3f",  None,     -999.),
    "sub_solar_longitude"       : ("360", 1,  8, "%8.3f",  None,     -999.),
    "sub_observer_longitude"    : ("360", 1,  8, "%8.3f",  None,     -999.),
    "ring_sub_solar_longitude"  : ("360", 1,  8, "%8.3f",  None,     -999.),
    "ring_sub_observer_longitude"
                                : ("360", 1,  8, "%8.3f",  None,     -999.),

    "latitude"                  : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "sub_solar_latitude"        : ("DEG", 1,  8, "%8.3f",  None,     -999.),
    "sub_observer_latitude"     : ("DEG", 1,  8, "%8.3f",  None,     -999.),

    "phase_angle"               : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_phase_angle"        : ("DEG", 1,  8, "%8.3f",  None,     -999.),
    "incidence_angle"           : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_incidence_angle"      : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_incidence_angle"    : ("DEG", 1,  8, "%8.3f",  None,     -999.),
    "ring_center_incidence_angle":("DEG", 1,  8, "%8.3f",  None,     -999.),
    "emission_angle"            : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "ring_emission_angle"       : ("DEG", 2,  8, "%8.3f",  None,     -999.),
    "center_emission_angle"     : ("DEG", 1,  8, "%8.3f",  None,     -999.),
    "ring_center_emission_angle": ("DEG", 1,  8, "%8.3f",  None,     -999.),
    "ring_elevation"            : ("DEG", 2,  8, "%8.3f",  None,     -999.),

    "where_inside_shadow"       : ("",    2,  1, "%1d",    None,        0 ),
    "where_in_front"            : ("",    2,  1, "%1d",    None,        0 ),
    "where_in_back"             : ("",    2,  1, "%1d",    None,        0 ),
    "where_antisunward"         : ("",    2,  1, "%1d",    None,        0 )}

ALT_FORMAT_DICT = {
    ("longitude", "-180")       : ("DEG", 2, 8, "%8.3f",   None,     -999.),
    ("sub_longitude", "-180")   : ("DEG", 1, 8, "%8.3f",   None,     -999.)}

################################################################################
# General functions for writing metadata files
################################################################################

def write_record(prefixes, backplane, blocker, outfile, column_descs, planet,
                 moon=None, moon_length=0, count_length=0,
                 tiles=[], tiling_min=100, ignore_shadows=False):
    """Generates the metadata and writes rows of a file, given a list of column
    descriptions.

    The tiles argument supports detailed listings where a geometric region is
    broken down into separate subregions. If the tiles argument is empty (which
    is the default), then this routine writes a summary file.

    If the tiles argument is not empty, then the routine writes a detailed file,
    which generally contains one record for each non-empty subregion. The tiles
    argument must be a list of boolean backplane keys, each equal to True for
    the pixels within the subregion. An additional column is added before the
    geometry columns, containing the index value of the associated tile.

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
        count_length    the character width of a column to contain the number
                        if samples obtained on the body or within a tile; zero
                        (which is the default) to suppress this column.
        tiles           an optional list of boolean backplane keys, used to
                        support the generation of detailed tabulations instead
                        of summary tabulations. See details above.
        tiling_min      the lower limit on the number of meshgrid points in a
                        region before that region is subdivided into tiles.
        ignore_shadows  True to ignore any mask constraints applicable to
                        shadowing or to the sunlit faces of surfaces.
    """

    # Prepare the rows
    rows = prep_rows(prefixes, backplane, blocker, column_descs,
                     planet, moon, moon_length, count_length,
                     tiles, tiling_min, ignore_shadows)

    # Write the complete rows to the output file
    for row in rows:
        outfile.write(row[0])
        for column in row[1:]:
            outfile.write(",")
            outfile.write(column)

        # Always use PDS-style line termination
        outfile.write("\r\n")

def prep_rows(prefixes, backplane, blocker, column_descs,
                 planet, moon=None, moon_length=0, count_length=0,
                 tiles=[], tiling_min=100, ignore_shadows=False):
    """Generates the metadata and returns a list of lists of strings. The inner
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
        count_length    the character width of a column to contain the number
                        if samples obtained on the body or within a tile; zero
                        (which is the default) to suppress this column.
        tiles           an optional list of boolean backplane keys, used to
                        support the generation of detailed tabulations instead
                        of summary tabulations. See details above.
        tiling_min      the lower limit on the number of meshgrid points in a
                        region before that region is subdivided into tiles.
        ignore_shadows  True to ignore any mask constraints applicable to
                        shadowing or to the sunlit faces of surfaces.
    """

    # Handle option for tiles
    if tiles:
        subregion_masks = [None]    # let zone indexing start at 1

        # Handle a 1-D set of regions
        if len(tiles) == 1:
            indices = range(1, len(tiles[0]) + 1)
            for tile in tiles[0]:
                mask = backplane.evaluate(tile).vals
                subregion_masks.append(np.logical_not(mask))

        # Handle a 2-D set of regions
        else:
            indices = range(1, len(tiles[0]) * len(tiles[1]) + 1)
            for tile1 in tiles[0]:
                mask1 = backplane.evaluate(tile1).vals
                for tile2 in tiles[1]:
                    mask2 = backplane.evaluate(tile2).vals & mask1
                    subregion_masks.append(np.logical_not(mask2))

        # Check size of tile
        pixels = 0
        for mask in subregion_masks[1:]:
            pixels += mask.size - np.count_nonzero(mask)

        if pixels < tiling_min:
            return []

    # Without tiling, the subregion index is zero
    else:
        indices = [0]
        subregion_masks = []

    # Create all the needed pixel masks
    excluded_mask_dict = {}
    for column_desc in column_descs:
        event_key = column_desc[0]
        mask_desc = column_desc[1]
        target = event_key[1]

        key = (target,) + mask_desc
        if key in excluded_mask_dict: continue

        excluded_mask = construct_excluded_mask(backplane, target, planet,
                                                mask_desc,
                                                blocker, ignore_shadows)
        excluded_mask_dict[key] = excluded_mask

    # Initialize the list of rows
    rows = []

    # For each subregion...
    for indx in indices:

        # Skip a tile if it contains no pixels
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

        # Insert the subregion zone if necessary
        if tiles:
            prefix_columns.append('%2d' % indx)

        # Prepare the backplane columns
        data_columns = []

        # For each column...
        pixel_count = 0
        for column_desc in column_descs:
            event_key = column_desc[0]
            mask_desc = column_desc[1]

            # Fill in the backplane array
            if event_key[1] == NULL:
                values = oops.Scalar(0., True)
            else:
                values = backplane.evaluate(event_key)

            # Make a shallow copy and apply the new masks
            target = event_key[1]
            excluded = excluded_mask_dict[(target,) + mask_desc]
            values = values.mask_where(excluded)
            if tiles:
                values = values.mask_where(subregion_masks[indx])

            if values.size > 1:
                pixel_count = max(pixel_count, values.unmasked())

            # Write the column using the specified format
            if len(column_desc) > 2:
                format = ALT_FORMAT_DICT[(event_key[0], column_desc[2])]
            else:
                format = FORMAT_DICT[event_key[0]]

            data_columns.append(formatted_column(values, format))

        # Save the row if it was completed
        if len(data_columns) < len(column_descs): continue # hopeless error
        if indx > 0 and pixel_count == 0: continue

        # Generate the sample count column if necessary
        if count_length:
            count_str = str(pixel_count)
            lcount = len(count_str)
            if count_length > lcount:
                count_str = (count_length - lcount) * ' ' + count_str
            elif count_length < lcount:
                count_str = count_length * '9'  # truncate so it fits

            count_columns = [count_str]
        else:
            count_columns = []

        rows.append(prefix_columns + count_columns + data_columns)

    return rows

def construct_excluded_mask(backplane, target, planet, mask_desc,
                            blocker=None, ignore_shadows=False):
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
        excluded |= backplane.where_in_back(target, "SATURN_AB_RINGS").vals

    if "P" in masker:
        excluded |= backplane.where_in_back(target, planet).vals
        if planet == "PLUTO":
            excluded |= backplane.where_in_back(target, "CHARON").vals

    if "M" in masker and blocker is not None:
        excluded |= backplane.where_in_back(target, blocker).vals

    if not ignore_shadows:

      # Handle shadowers
      if "R" in shadower and planet == "SATURN":
        excluded |= backplane.where_inside_shadow(target, "SATURN_B_RING").vals

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

    return excluded

def formatted_column(values, format):
    """Returns one formatted column (or a pair of columns) as a string.

    Input:
        columns         a list of the columns so far.
        values          a Scalar of values with its applied mask.
        format          a tuple (flag, number_of_values, column_width,
                        standard_format, overflow_format, null_value),
                        describing the format to use. Here...
            flag        "DEG" implies that the values should be converted from
                        radians to degrees; "360" implies that the values should
                        be converted to a range of degrees, allowing for ranges
                        that cross from 360 to 0.
    """

    # Interpret the format
    (flag, number_of_values, column_width,
     standard_format, overflow_format, null_value) = format

    # Convert from radians to degrees if necessary
    if flag in ("DEG","360","-180"):
        values = values * oops.DPR

    # Create a list of the numeric values for this column
    if number_of_values == 1:
        meanval = values.mean()
        if type(meanval) == oops.Scalar and meanval.mask:
            results = [null_value]
        else:
            results = [meanval]

    elif np.all(values.mask):
        results = [null_value, null_value]

    elif flag == "360":
        results = get_range_mod360(values)

    elif flag == "-180":
        results = get_range_mod360(values, alt_format=flag)

    else:
        results = [values.min(), values.max()]

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

def get_range_mod360(values, sigma_cutoff=100., alt_format=None):
    """Returns the minimum and maximum values in the array, allowing for the
    possibility that the numeric range wraps around from 360 to 0.

    Input:
        values          the set of values for which to determine the range.
        sigma_cutoff    the number of standard deviations by which the largest
                        gap in longitude differs from the others before it is
                        recognized as a true gap. Default is 100, which appears
                        to eliminate most statistical flukes that arise when a
                        continuous range is sampled poorly.
        alt_format      "-180" to return values in the range (-180,180) rather
                        than (0,360).
    """

    # Flatten the set of values
    if values.mask is False:
        flattened = values.vals.flatten()
    else:
        flattened = values.vals[~values.mask]

    # Deal with only one value
    if flattened.size == 1:
        return [flattened[0], flattened[0]]

    # Check for use of negative values
    use_minus_180 = (alt_format == "-180")

    # Sort mod 360
    sorted = np.sort(flattened % 360)

    # Calculate consecutive differences
    diffs = np.empty(sorted.size)
    diffs[:-1] = sorted[1:] - sorted[:-1]
    diffs[-1]  = sorted[0] + 360. - sorted[-1]

    # Locate the largest gap and use it to define the range
    gap_index = np.argmax(diffs)
    diff_max  = diffs[gap_index]
    range_mod360 = [sorted[(gap_index + 1) % sorted.size], sorted[gap_index]]

    # Convert to range -180 to 180 if necessary
    if use_minus_180:
        (lower, upper) = range_mod360
        lower = (lower + 180.) % 360. - 180.
        upper = (upper + 180.) % 360. - 180.
        range_mod360 = [lower, upper]

    # Deal with only two values
    if flattened.size == 2:
        return range_mod360

    # How many sigmas is the largest from the mean of the rest?
    sum0 = diffs.size - 1
    sum1 = 360. - diff_max
    sum2 = np.sum(diffs**2) - diff_max**2
    diff_mean = sum1 / sum0
    diff_var = (sum0 * sum2 - sum1**2) / (sum0 * (sum0 - 1))
    diff_std = np.sqrt(max(diff_var, 0.))       # var can be < 0 due to roundoff
    sigmas = (diff_max - diff_mean) / max(diff_std, 1.e-99) # diff_std can be 0

    # If it is larger by more than the cutoff, return the range with this gap
    if sigmas > sigma_cutoff:
        return range_mod360

    # Deal with only three values
    if flattened.size == 3:
        return range_mod360

    # Allow for the possibility that a second gap biased our statistics...

    # Find the second largest gap
    diffs[gap_index] = 0.
    diff_2nd = np.max(diffs)

    # How many sigmas is this gap from the mean of the rest?
    sum0 -= 1
    sum1 -= diff_2nd
    sum2 -= diff_2nd**2
    diff_mean = sum1 / sum0
    diff_var = (sum0 * sum2 - sum1**2) / (sum0 * (sum0 - 1))
    diff_std = np.sqrt(max(diff_var, 0.))       # var can be < 0 due to roundoff
    sigmas = (diff_2nd - diff_mean) / max(diff_std, 1.e-99) # diff_std can be 0

    # If this one is larger by more than the cutoff, return the range
    if sigmas > sigma_cutoff:
        return range_mod360

    if use_minus_180:
        return [-180., 180.]
    else:
        return [0., 360.]

def replace(tree, placeholder, name):
    """Return a copy of the tree of objects, with each occurrence of the
    placeholder string replaced by the given name."""

    new_tree = []
    for leaf in tree:
        if type(leaf) in (tuple, list):
            new_tree.append(replace(leaf, placeholder, name))

        elif leaf == placeholder:
            new_tree.append(name)

        else:
            new_tree.append(leaf)

    if type(tree) == tuple:
        return tuple(new_tree)
    else:
        return new_tree

def replacement_dict(tree, placeholder, names):
    """Return a dictionary of copies of the tree of objects, where each
    dictionary entry is keyed by a name in the list and returns a copy of the 
    tree using that name as the replacement."""

    dict = {}
    for name in names:
        dict[name] = replace(tree, placeholder, name)

    return dict

################################################################################
