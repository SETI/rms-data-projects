################################################################################
# COLUMNS_BODY.py: Column definitions for body geometry tables
################################################################################
import oops


################################################################################
# *COLUMN description tuples are
#
#   (backplane_key, (masker, shadower, face), alt_format)
#
# where...
#
#   backplane_key   tuple passed to Backplane.evaluate().
#
#   masker          a string indicating which bodies obscure the surface. It is
#                   constructed by concatenating any of these characters:
#                       "P" = let the planet mask the surface;
#                       "R" = let the rings mask the surface;
#                       "M" = let the moon mask the surface.
#
#   shadower        a string indicating which bodies shadow the surface. It is
#                   constructed by concatenating any of these characters:
#                       "P" = let the planet shadow the surface;
#                       "R" = let the rings shadow the surface;
#                       "M" = let the moon shadow the surface.
#
#   face            a string indicating which face of the surface to include:
#                       "D" = include only the day side of the body;
#                       "N" = include only the night side of the body;
#                       ""  = include both faces of the body.
#
#   alt_format      if present, this is an extra tag used to identify the output
#                   format of the column.
#                       "-180" = use the range (-180,180) instead of (0,360).
#
################################################################################
BODY_COLUMNS = [
    (("latitude",               BODYX, "centric"),         ("RM", "R",  "D")),
    (("latitude",               BODYX, "graphic"),         ("RM", "R",  "D")),
    (("longitude",              BODYX, "iau", "west"),     ("RM", "R",  "D")),
#    (("longitude",              BODYX, "iau", "east"),     ("RM", "R",  "D")),
    (("longitude",              BODYX, "sha", "east"),     ("RM", "R",  "" )),
    (("longitude",              BODYX, "obs", "west"),
                                                            ("RM", "R",  "D"), "-180"),
#    (("longitude",              BODYX, "obs", "east"),
#                                                            ("RM", "R",  "D"), "-180"),
    (("finest_resolution",      BODYX),                    ("RM", "R",  "D")),
    (("coarsest_resolution",    BODYX),                    ("RM", "R",  "D")),
    (("distance",               BODYX),                    ("RM", "",   "" )),
#    (("phase_angle",            BODYX),                    ("RM", "",   "D")),
    (("phase_angle",            BODYX),                    ("RM", "",   "")),
    (("incidence_angle",        BODYX),                    ("RM", "",   "" )),
    (("emission_angle",         BODYX),                    ("RM", "",   "" ))]

BODY_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     BODYX, "centric"),         ("",   "",  "" )),
    (("sub_solar_latitude",     BODYX, "graphic"),         ("",   "",  "" )),
    (("sub_observer_latitude",  BODYX, "centric"),         ("",   "",  "" )),
    (("sub_observer_latitude",  BODYX, "graphic"),         ("",   "",  "" )),
    (("sub_solar_longitude",    BODYX, "iau", "west"),     ("",   "",  "" )),
#    (("sub_solar_longitude",    BODYX, "iau", "east"),     ("",   "",  "" )),
    (("sub_observer_longitude", BODYX, "iau", "west"),     ("",   "",  "" )),
#    (("sub_observer_longitude", BODYX, "iau", "east"),     ("",   "",  "" )),
    (("center_resolution",      BODYX, "u"),               ("",   "",  "" )),
    (("center_distance",        BODYX, "obs"),             ("",   "",  "" )),
    (("center_phase_angle",     BODYX),                    ("",   "",  "" )),
    (("center_x_coordinate",    BODYX),                    ("",   "",  "" )),
    (("center_y_coordinate",    BODYX),                    ("",   "",  "" ))]

# Assemble the column lists for each type of file for the moons and planet

BODY_SUMMARY_COLUMNS  = BODY_COLUMNS + BODY_GRIDLESS_COLUMNS
BODY_DETAILED_COLUMNS = BODY_COLUMNS

BODY_SUMMARY_DICT = {}
BODY_DETAILED_DICT = {}
for body in BODIES:
    BODY_SUMMARY_DICT.update(replacement_dict(BODY_SUMMARY_COLUMNS,
                                                         BODYX, [body]))
    BODY_DETAILED_DICT.update(replacement_dict(BODY_DETAILED_COLUMNS,
                                                         BODYX, [body]))

################################################################################
# Define the tiling for detailed listings
#
# The first item in the list defines a region to test for a suitable pixel
# count. The remaining items define a sequence of tiles to use in a
# detailed tabulation.
################################################################################
PLANET_TILES = {}
for planet in PLANET_NAMES:
    PLANET_TILES[planet] = [
        ("where_sunward", planet),                      # mask over remaining tiles
        ("where_below",   ("latitude", planet), -70. * oops.RPD),
        ("where_between", ("latitude", planet), -70. * oops.RPD, -50. * oops.RPD),
        ("where_between", ("latitude", planet), -50. * oops.RPD, -30. * oops.RPD),
        ("where_between", ("latitude", planet), -30. * oops.RPD, -10. * oops.RPD),
        ("where_between", ("latitude", planet), -10. * oops.RPD,  10. * oops.RPD),
        ("where_between", ("latitude", planet),  10. * oops.RPD,  30. * oops.RPD),
        ("where_between", ("latitude", planet),  30. * oops.RPD,  50. * oops.RPD),
        ("where_between", ("latitude", planet),  50. * oops.RPD,  70. * oops.RPD),
        ("where_above",   ("latitude", planet),  70. * oops.RPD)
    ]

BODY_TILES = {}
for planet in PLANET_NAMES:
    BODY_TILES[planet] = [
        ("where_all", ("where_in_front", BODYX, planet), # mask over remaining tiles
                      ("where_sunward",  BODYX)),
        ("where_below",   ("latitude", BODYX), -70. * oops.RPD),
        ("where_between", ("latitude", BODYX), -70. * oops.RPD, -50. * oops.RPD),
        ("where_between", ("latitude", BODYX), -50. * oops.RPD, -30. * oops.RPD),
        ("where_between", ("latitude", BODYX), -30. * oops.RPD, -10. * oops.RPD),
        ("where_between", ("latitude", BODYX), -10. * oops.RPD,  10. * oops.RPD),
        ("where_between", ("latitude", BODYX),  10. * oops.RPD,  30. * oops.RPD),
        ("where_between", ("latitude", BODYX),  30. * oops.RPD,  50. * oops.RPD),
        ("where_between", ("latitude", BODYX),  50. * oops.RPD,  70. * oops.RPD),
        ("where_above",   ("latitude", BODYX),  70. * oops.RPD)
    ]

BODY_TILE_DICT = {}

for body in PLANET_NAMES:
    BODY_TILE_DICT[body] = {}
    BODY_TILE_DICT[body] = replace(BODY_TILES[body], BODYX, body)
################################################################################
