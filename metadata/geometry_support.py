################################################################################
# geometry_support.py - Tools for generating geometry tables.
################################################################################
import oops
import numpy as np
import os, traceback
import warnings
import fnmatch

import metadata as meta
import metadata.label_support as lab
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

SYSTEMS_TABLE = meta.convert_systems_table(config.SYSTEMS_TABLE, config.SCLK_BASES)

########################
### Table should represent a single complete SKY RING or BODY table
### --> Table.Body, Ring, Sky classes
### Suite represents all tables for one obs
###  --> Suite.process would loop over observations, adding a rows to each table

################################################################################
# Record class
################################################################################
class Record(object):
    """Class describing a single geometry record, i.e., a single row in a table.
    """

    #===========================================================================
    def __init__(self, observation, volume_id):
        """Constructor for a geometry record.

        Args:
        """
        pass
#####backplane 
        self.observation = observation

        # Determine system, if any
        sclk = observation.dict["SPACECRAFT_CLOCK_START_COUNT"] + '' 
        self.system, self.secondaries = \
            meta.get_system(SYSTEMS_TABLE, sclk, config.SCLK_BASES)

        # Set up planet-based geometry
        self.bodies = []
        self.blocker = None

        if self.system:
            self.rings_present = meta.BODIES[self.system].ring_frame is not None    
            self.ring_tile_dict = meta.RING_TILE_DICT[self.system]
            self.body_tile_dict = meta.BODY_TILE_DICT[self.system]

        # Determine target
        self.target = config.target_name(observation.dict)
        if self.target in meta.TRANSLATIONS.keys():
            self.target = meta.TRANSLATIONS[self.target]

        # Create the record prefix
        filespec = observation.dict["FILE_SPECIFICATION_NAME"]
        self.prefixes = ['"' + volume_id + '"',
                         '"%-32s"' % filespec.replace(".IMG", ".LBL")]

    #===============================================================================
    def add(self, prefixes, backplane, column_descs, 
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
        rows = Record._prep_row(prefixes, backplane, blocker, column_descs,
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
            lines.append(line)

        return lines
    #===============================================================================
    @staticmethod
    def _prep_row(prefixes, backplane, blocker, column_descs,
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
                new_rows = Record._prep_row(prefixes, backplane, blocker, column_descs,
                                            system, target, name_length,
                                            tile, tiling_min, ignore_shadows,
                                            local_index, allow_zero_rows=True)
                rows += new_rows
                local_index += len(tile) - 1

            if rows or allow_zero_rows:
                return rows

            return Record._prep_row(prefixes, backplane, blocker, column_descs,
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
                    Suite._construct_excluded_mask(backplane, mask_target, system, mask_desc,
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
                Suite._append_body_prefix(prefix_columns, system, name_length)
                if target is not None:
                    Suite._append_body_prefix(prefix_columns, target, name_length)

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

                data_columns.append(Suite._formatted_column(values, format))

            # Save the row if it was completed
            if len(data_columns) < len(column_descs): continue # hopeless error
            if nothing_found and (indx > 0 or allow_zero_rows): continue
            rows.append(prefix_columns + data_columns)

        # Return something if we can
        if rows or allow_zero_rows:
            return rows

        return Record._prep_row(prefixes, backplane, blocker, column_descs,
                                system, target, name_length,
                                [], 0, ignore_shadows, start_index,
                                allow_zero_rows=False)

################################################################################
# Batch class
################################################################################
class Batch(object):
    """Class describing the set of geometry records associated with a single 
    observation.  The batch consists of records for each geometric type (SKY, RING,
    BODY).
    """

    #===========================================================================
    def __init__(self, observation, volume_id):
        """Constructor for a set of geometry records.

        Args:
            input_dir (Path): Directory containing the volume.
            output_dir (Path): Directory in which to write the geometry files.
            selection (str, optional):
                A string containing...
                "S" to generate summary files;
                "D" to generate detailed files.
            glob (str, optional): Glob pattern for index files.
            first (bool, optional): 
                If given, at most this many files are processed in each volume.
        """
        self.observation = observation

        # Determine system, if any
        sclk = observation.dict["SPACECRAFT_CLOCK_START_COUNT"] + '' 
        self.system, self.secondaries = \
            meta.get_system(SYSTEMS_TABLE, sclk, config.SCLK_BASES)

        # Record-specific column dictionaries
        self.dicts = {
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

        # Set up planet-based geometry
        self.bodies = []
        self.blocker = None

        if self.system:
            self.rings_present = meta.BODIES[self.system].ring_frame is not None    
            self.ring_tile_dict = meta.RING_TILE_DICT[self.system]
            self.body_tile_dict = meta.BODY_TILE_DICT[self.system]

        # Determine target
        self.target = config.target_name(observation.dict)
        if self.target in meta.TRANSLATIONS.keys():
            self.target = meta.TRANSLATIONS[self.target]

        # Create the record prefix
        filespec = observation.dict["FILE_SPECIFICATION_NAME"]
        self.prefixes = ['"' + volume_id + '"',
                         '"%-32s"' % filespec.replace(".IMG", ".LBL")]

    #===============================================================================
    def _add(self, table):
        """Add a batch of records.

        Args:
            selection (str):
                A string containing...
                "summary" to generate summary files;
                "detailed" to generate detailed files.
            record (dict): xxx.

        Returns:
            None.
        """

        # Add sky columns
        table.tables[table.selection]['sky'] += \
            Batch._add_record(self.prefixes, self.backplane, self.dicts[table.selection]['sky'],
                              blocker=self.blocker, system=self.system, 
                              name_length=meta.NAME_LENGTH, no_body=True)

        # Add rings and system primary body
        if self.system:
            if self.rings_present:
                table.tables[table.selection]['ring'] += \
                    Batch._add_record(self.prefixes, self.backplane,
                                      self.dicts[table.selection]['ring'][self.system], blocker=self.blocker, 
                                      system=self.system, name_length=meta.NAME_LENGTH)

            table.tables[table.selection]['body'] += \
                Batch._add_record(self.prefixes, self.backplane,
                                  self.dicts[table.selection]['body'][self.system], blocker=self.blocker, 
                                  system=self.system, target=self.system, name_length=meta.NAME_LENGTH)

        # Add other bodies
        for name in self.bodies:
            if name != self.system:
                table.tables[table.selection]['body'] += \
                    Batch._add_record(self.prefixes, self.backplane, 
                                      self.dicts[table.selection]['body'][name], 
                                      blocker=self.blocker, system=self.system, 
                                      target=name, name_length=meta.NAME_LENGTH)
    #        if self.rings_present:
    #            table.tables[table.selection]['ring'][name] += Batch._add_record(self.prefixes, self.backplane, 
    #                                                self.dicts[table.selection]['ring'][name], 
    #                                                    target=name+'-ring', name_length=meta.NAME_LENGTH,
    #                                                    no_mask=True)

    #===============================================================================
    @staticmethod
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

        # Prepare the rows   #### record.prep_rows()
        rows = Suite._prep_rows(prefixes, backplane, blocker, column_descs,
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
            lines.append(line)

        return lines


################################################################################
# Table class
################################################################################
class Table(object):
    """Class describing a single geometry table for a single volume.
    """

    #===========================================================================
    def __init__(self, volume_id):
        """Constructor for a geometry table object.

        Args:
            selection (str, optional):
                A string containing...
                "S" to generate summary files;
                "D" to generate detailed files.
            observation (oops.Observation): Observation object for this data file.
        """
        logger = meta.get_logger()

    #===========================================================================
    """Class describing a sky geometry table.
    """
    class Sky(object):
        #===========================================================================
        def __init__(self, table):
            """Constructor for a Sky Table object.

            Args:
            """
            self.table = table
            self.dict = meta.SKY_COLUMNS
            self.rows = []

        #===============================================================================
        def add(self, record):
            """Add a record.

            Args:
                record (dict): xxx.

            Returns:
                None.
            """
            self.rows += \
                self.table.record.add(record.prefixes, record.backplane, self.dict,
                                       blocker=record.blocker, system=record.system, 
                                       name_length=meta.NAME_LENGTH, no_body=True)

#            self.rows += \
#                self.table.record.add(self.dict,
#                                  name_length=meta.NAME_LENGTH, no_body=True)

    #===========================================================================
    """Class describing a ring geometry table.
    """
    class Ring(object):
        #===========================================================================
        def __init__(self, table, selection):
            """Constructor for a Ring Table object.

            Args:
            """
            self.table = table
            self.dict = meta.RING_SUMMARY_DICT if selection == 'S' else meta.RING_DETAILED_DICT
            self.rows = []

        #===============================================================================
        def add(self, record):
            """Add a record.

            Args:
                record (dict): xxx.

            Returns:
                None.
            """

            # Add record
            if record.system:
                if self.rings_present:
                    self.rows += \
                        self.table.record.add(record.prefixes, record.backplane,
                                               self.dict[record.system], blocker=record.blocker, 
                                               system=record.system, name_length=meta.NAME_LENGTH)
#            # Add other bodies
#            for name in [[self.bodies]]:
#               if self.rings_present:
#                   self.rows += \
#                       self.table.record.add(record.prefixes, record.backplane, 
#                                              self.dict[name], 
#                                              target=name+'-ring', name_length=meta.NAME_LENGTH,
#                                              no_mask=True)


    #===========================================================================
    """Class describing a body geometry table.
    """
    class Body(object):
        #===========================================================================
        def __init__(self, table, selection):
            """Constructor for a Body Table object.

            Args:
            """
            self.table = table
            self.dict = meta.BODY_SUMMARY_DICT if selection == 'S' else meta.BODY_DETAILED_DICT
            self.rows = []

        #===============================================================================
        def add(self, record):
            """Add a record.

            Args:
                record (dict): xxx.

            Returns:
                None.
            """

            # Add record
            if record.system:
                self.rows += \
                    self.table.record.add(record.prefixes, record.backplane,
                                           self.dict[record.system], blocker=record.blocker, 
                                           system=record.system, target=record.system, name_length=meta.NAME_LENGTH)

            # Add other bodies
            for name in self.bodies:
                if name != record.system:
                    self.rows += \
                        self.table.record.add(record.prefixes, record.backplane, 
                                          self.dict[name], 
                                          blocker=record.blocker, system=record.system, 
                                          target=name, name_length=meta.NAME_LENGTH)



#            if record.system:
#                self.rows += \
#                    self.table.record.add(self.dict[record.system], 
#                                           target=record.system, name_length=meta.NAME_LENGTH)
#
#            # Add other bodies
#            for name in self.bodies:
#                if name != recor, .system:
#                    self.rows += \
#                        self.table.record.add(self.dict[name], 
#                                          blocker=record.blocker, system=record.system, 
#                                          target=name, name_length=meta.NAME_LENGTH)

################################################################################
# Suite class
################################################################################
class Suite(object):
    """Class describing the suite of geometry tables for a single volume.
    """

    #===========================================================================
    def __init__(self, input_dir, output_dir,
                       selection='', glob=None, first=None, sampling=8):
        """Constructor for a geometry Suite object.

        Args:
            input_dir (Path): Directory containing the volume.
            output_dir (Path): Directory in which to write the geometry files.
            selection (str, optional):
                A string containing...
                "S" to generate summary files;
                "D" to generate detailed files.
            glob (str, optional): Glob pattern for index files.
            first (bool, optional): 
                If given, at most this many files are processed in each volume.
            sampling (int, optional): Pixel sampling density.
        """
        logger = meta.get_logger()

        # Save inputs
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.glob = glob
        self.first = first
 
        self.selection = 'summary' if 'S' in selection else 'detailed'

        # Check for supplemental index
        index_filenames = list(self.input_dir.glob(self.glob))
        if len(index_filenames) == 0:
            return
        if len(index_filenames) > 1:
            raise RuntimeError('Mulitple index files found in %s.' % self.input_dir)

        index_filename = index_filenames[0]
        ext = index_filename.suffix
        self.volume_id = config.get_volume_id(self.input_dir)
        supplemental_index_name = meta.get_index_name(self.input_dir, self.volume_id, 'supplemental')
        supplemental_index_filename = self.input_dir.joinpath(supplemental_index_name+ext)

        logger = meta.get_logger()
        logger.info('New geometry index for %s.' % self.volume_id)

        # Get observations
        try:
            self.observations = config.from_index(index_filename, supplemental_index_filename)
        except FileNotFoundError:
            pass

        # Set file prefix
        self.prefix = self.output_dir.joinpath(self.volume_id).as_posix()

        # Initialize inventory table
        self.inventory_filename = Path(self.prefix + "_inventory.csv")
        self.inventory = []
        logger.info("Inventory file: " + self.inventory_filename.as_posix())




        # Initialize data tables
        table = Table(self.volume_id)
        self.tables = [
            Table.Sky(table),
            Table.Ring(table, selection),
            Table.Body(table, selection)
            ]





        self.tables = {
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

        # Initialize meshgrids
        self.meshgrids = config.meshgrids(sampling)


#===============================================================================
    def _create(self):
        """Process the volume and write a selection of geometry files.

        Args: None
        Returns: None
        """
        logger = meta.get_logger()
        if not hasattr(self, 'observations'):
            return

        # Loop through the observations...
        nobs = len(self.observations)
        count = 0
        for i in range(nobs):
            if self.first and count >= self.first:
                continue

            batch = Batch(self.observations[i], self.volume_id)
 ####batch.process...


            # Create the backplane
            meshgrid = self._meshgrid(batch.observation)
            batch.backplane = oops.backplane.Backplane(batch.observation, meshgrid)

            # Print a log of progress
            logger.info("%s  %4d/%4d  %s" % (self.volume_id, i+1, nobs, batch.target))

            # Don't abort if cspice throws a runtime error
            try:
                body_names = meta.BODIES.keys()
                if batch.target not in meta.BODIES and oops.Body.exists(batch.target):
                    body_names += [batch.target]

                # Inventory the bodies in the FOV (including targeted irregulars)
                if body_names:
                    body_names = batch.observation.inventory(body_names, expand=config.EXPAND, cache=False)

                # Add any secondaries to body_names
                if batch.secondaries:
                    body_names += batch.secondaries

                batch.bodies = body_names

                # Write a record into the inventory file
                self.inventory += ",".join(batch.prefixes)
                for name in batch.bodies:
                    self.inventory += ',"' + name + '"'
                self.inventory += "\r\n"             # Use <CR><LF> line termination

                if batch.system:
                    # Define a blocker body, if any
                    if batch.target in batch.bodies:
                        batch.blocker = batch.target

                    # Add an irregular moon to the dictionaries if necessary
                    if batch.target in batch.bodies and batch.target not in batch.dicts['summary']['body'].keys():
                        batch.dicts['summary']['body'][batch.target] = meta.replace(meta.BODY_SUMMARY_COLUMNS,
                                                                 meta.BODYX, batch.target)
                        batch.dicts['detailed']['body'][batch.target] = meta.replace(meta.BODY_DETAILED_COLUMNS,
                                                                  meta.BODYX, batch.target)
                        body_tile_dict[batch.target] = meta.replace(meta.BODY_TILES, meta.BODYX, batch.target)

                # Update the tables
                batch._add(self)

                count += 1

            # A RuntimeError is probably caused by missing spice data. There is
            # probably nothing we can do.
            except RuntimeError as e:
                logger.warn(str(e))

            # Other kinds of errors are genuine bugs. For now, we just log the
            # problem, and jump over the image; we can deal with it later.
            except (AssertionError, AttributeError, IndexError, KeyError,
                    LookupError, TypeError, ValueError):
                logger.error(traceback.format_exc())

        # Write tables and make labels
        self._write()

        # Clean up
        config.cleanup() 

    #===============================================================================
    def _meshgrid(self, observation):
        """Looks up the meshgrid for an observation.

        Args: 
            observation (oops.observation): Observation object.

        Returns: 
            oops.Meshgrid: Meshgrid for the given observation.
        """
        return config.meshgrid(self.meshgrids, observation)

    #===============================================================================
    def _write(self):
        """Write all tables and their labels.

        Args: None
        Returns: None
        """
        meta.write_txt_file, self.inventory_filename, self.inventory
        lab.create(self.inventory_filename)

        for qualifier in self.tables[self.selection].keys():
            Suite._write_table(self.tables[self.selection][qualifier], self.prefix, 
                                selection=self.selection, qualifier=qualifier)

    #===============================================================================
    @staticmethod
    def _write_table(table, dir, selection, qualifier=None):
        """Write a single summary table and its label.

        Args:
            table (list): List of strings comprising the table to write.
            dir (str): Directory in which to write the table and its label.
            selection (str):
                A string containing...
                "summary" to generate summary files;
                "detailed" to generate detailed files.
            qualifier (str, optional): Type of table to write, e.g. 'sky'. 'body'. 'ring'.

        Returns:
            None.
        """
        if table == []:
            return

        logger = meta.get_logger()
        filename = Path(dir + "_%s_%s.tab" % (qualifier, selection))

        # Write table
        logger.info("Writing:", filename)
        meta.write_txt_file(filename, table)

        # Write label
        table_type = ''
        if qualifier:
            table_type = qualifier + '_' + selection
        lab.create(filename, table_type=table_type)

    #===============================================================================
    @staticmethod
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
    @staticmethod
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
                new_rows = Suite._prep_rows(prefixes, backplane, blocker, column_descs,
                                            system, target, name_length,
                                            tile, tiling_min, ignore_shadows,
                                            local_index, allow_zero_rows=True)
                rows += new_rows
                local_index += len(tile) - 1

            if rows or allow_zero_rows:
                return rows

            return Suite._prep_rows(prefixes, backplane, blocker, column_descs,
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
                    Suite._construct_excluded_mask(backplane, mask_target, system, mask_desc,
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
                Suite._append_body_prefix(prefix_columns, system, name_length)
                if target is not None:
                    Suite._append_body_prefix(prefix_columns, target, name_length)

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

                data_columns.append(Suite._formatted_column(values, format))

            # Save the row if it was completed
            if len(data_columns) < len(column_descs): continue # hopeless error
            if nothing_found and (indx > 0 or allow_zero_rows): continue
            rows.append(prefix_columns + data_columns)

        # Return something if we can
        if rows or allow_zero_rows:
            return rows

        return Suite._prep_rows(prefixes, backplane, blocker, column_descs,
                                system, target, name_length,
                                [], 0, ignore_shadows, start_index,
                                allow_zero_rows=False)

    #===============================================================================
    @staticmethod
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
    @staticmethod
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



################################################################################
# external functions
################################################################################

#===============================================================================
def get_args(host=None, selection=None, exclude=None, sampling=8):
    """Argument parser for geometric metadata.

    Args:
        host (str): Host name, e.g. 'GOISS'.
        selection (str, optional):
            A string containing...
            "S" to generate summary files;
            "D" to generate detailed files.
        exclude (list, optional): List of volumes to exclude.
        sampling (int, optional): Pixel sampling density.

     Returns:
        argparser.ArgumentParser : 
            Parser containing the argument specifications.
    """

    # Get parser with common args
    parser = meta.get_common_args(host=host)

    # Add parser for index args
    gr = parser.add_argument_group('Geometry Arguments')
    gr.add_argument('--selection', type=str, metavar='selection',
                    default=selection, 
                    help='''A string containing:
                             "S" to generate summary files;
                             "D" to generate detailed files.''')
    gr.add_argument('--exclude', '-e', nargs='*', type=str, metavar='exclude',
                    default=exclude, 
                    help='''List of volumes to exclude.''')
    gr.add_argument('--new_only', '-n', nargs='*', type=str, metavar='new_only',
                    default=False, 
                    help='''Only volumes that contain no output files are processed.''')
    gr.add_argument('--first', '-f',type=int, metavar='first',
                    help='''If given, at most this many input files are processed
                            in each volume.''')
    gr.add_argument('--sampling', '-s', type=int, metavar='sampling',
                    default=sampling, 
                    help='''Pixel sampling density.''')

    # Return parser
    return parser

#===============================================================================
def process_index(host=None, selection=None, exclude=None, sampling=8, glob=None):
    """Creates geometry files for a collection of volumes.

    Args:
        host (str): Host name e.g. 'GOISS'.
        selection (str, optional):
            A string containing...
            "S" to generate summary files;
            "D" to generate detailed files.
        exclude (list, optional): List of volumes to exclude.
        sampling (int, optional): Pixel sampling density.
        glob (str, optional): Glob pattern for index files.
  """

    # Parse arguments
    parser = get_args(host=host, selection=selection, exclude=exclude, sampling=sampling)
    args = parser.parse_args()

    input_tree = Path(args.input_tree) 
    output_tree = Path(args.output_tree) 
    volume = args.volume
    new_only = args.new_only

    if volume:
        new_only = False

    # Build volume glob
    vol_glob = meta.get_volume_glob(input_tree.name)

    # Walk the input tree, making indexes for each found volume
    for root, dirs, files in input_tree.walk():
        # __skip directory will not be scanned, so it's safe for test results
        if '__skip' in root.as_posix():
            continue

        # Sort directories for progress monitoring
        dirs.sort()
        root = Path(root)

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

                # Do not continue if this volume is excluded
                skip = False
                if exclude is not None:
                    for item in exclude:
                        if item in indir.parts:
                            skip = True
                if skip:
                    continue

                # Check whether this volume has already been processed
                if new_only & (list(outdir.glob('*_inventory.csv')) != []):
                    continue

                # Process this volumne
                table = Suite(indir, outdir, 
                              selection=args.selection, glob=glob, first=args.first, 
                              sampling=args.sampling)
                table._create()

################################################################################