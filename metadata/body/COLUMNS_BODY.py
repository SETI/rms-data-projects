################################################################################
# COLUMNS_BODY.py: Column definitions for body geometry tables
################################################################################
import oops
import metadata as meta

planet_limb = PLANET + ":LIMB"

################################################################################
# Create a list of body IDs
################################################################################
planet_body = oops.Body.lookup(PLANET)
moon_bodies = planet_body.select_children("REGULAR")

MOON_NAMES   = [moon.name for moon in moon_bodies]
BODY_NAMES = [PLANET] + MOON_NAMES
NAME_LENGTH = 12

# Maintain a list of translations for target names
TRANSLATIONS = {}

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

MOONX = "moonx"                 # Indicates a placeholder for an arbitrary moon

#SKY_COLUMNS = [
#    (("right_ascension",        ()),                        ("",  "",  "")),
#    (("declination",            ()),                        ("",  "",  ""))]

PLANET_COLUMNS = [
    (("latitude",               PLANET, "centric"),         ("RM", "R",  "D")),
    (("latitude",               PLANET, "graphic"),         ("RM", "R",  "D")),
    (("longitude",              PLANET, "iau", "west"),     ("RM", "R",  "D")),
#    (("longitude",              PLANET, "iau", "east"),     ("RM", "R",  "D")),
    (("longitude",              PLANET, "sha", "east"),     ("RM", "R",  "" )),
    (("longitude",              PLANET, "obs", "west"),
                                                            ("RM", "R",  "D"), "-180"),
#    (("longitude",              PLANET, "obs", "east"),
#                                                            ("RM", "R",  "D"), "-180"),
    (("finest_resolution",      PLANET),                    ("RM", "R",  "D")),
    (("coarsest_resolution",    PLANET),                    ("RM", "R",  "D")),
    (("distance",               PLANET),                    ("RM", "",   "" )),
#    (("phase_angle",            PLANET),                    ("RM", "",   "D")),
    (("phase_angle",            PLANET),                    ("RM", "",   "")),
    (("incidence_angle",        PLANET),                    ("RM", "",   "" )),
    (("emission_angle",         PLANET),                    ("RM", "",   "" ))]

PLANET_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     PLANET, "centric"),         ("",   "",  "" )),
    (("sub_solar_latitude",     PLANET, "graphic"),         ("",   "",  "" )),
    (("sub_observer_latitude",  PLANET, "centric"),         ("",   "",  "" )),
    (("sub_observer_latitude",  PLANET, "graphic"),         ("",   "",  "" )),
    (("sub_solar_longitude",    PLANET, "iau", "west"),     ("",   "",  "" )),
#    (("sub_solar_longitude",    PLANET, "iau", "east"),     ("",   "",  "" )),
    (("sub_observer_longitude", PLANET, "iau", "west"),     ("",   "",  "" )),
#    (("sub_observer_longitude", PLANET, "iau", "east"),     ("",   "",  "" )),
    (("center_resolution",      PLANET, "u"),               ("",   "",  "" )),
    (("center_distance",        PLANET, "obs"),             ("",   "",  "" )),
    (("center_phase_angle",     PLANET),                    ("",   "",  "" ))]

MOON_COLUMNS = [
    (("latitude",               MOONX, "centric"),          ("P",  "",  "D")),
    (("latitude",               MOONX, "graphic"),          ("P",  "",  "D")),
    (("longitude",              MOONX, "iau", "west"),      ("P",  "",  "D")),
#    (("longitude",              MOONX, "iau", "east"),      ("P",  "",  "D")),
    (("longitude",              MOONX, "sha", "east"),      ("P",  "",  "" )),
    (("longitude",              MOONX, "obs", "west"),("P",  "",  "D"), "-180"),
#    (("longitude",              MOONX, "obs", "east"),("P",  "",  "D"), "-180"),
    (("finest_resolution",      MOONX),                     ("P",  "",  "D")),
    (("coarsest_resolution",    MOONX),                     ("P",  "",  "D")),
    (("distance",               MOONX),                     ("P",  "",  "" )),
#    (("phase_angle",            MOONX),                     ("P",  "",  "D")),
    (("phase_angle",            MOONX),                     ("P",  "",  "")),
    (("incidence_angle",        MOONX),                     ("P",  "",  "" )),
    (("emission_angle",         MOONX),                     ("P",  "",  "" ))]

MOON_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     MOONX, "centric"),          ("",   "",  "" )),
    (("sub_solar_latitude",     MOONX, "graphic"),          ("",   "",  "" )),
    (("sub_observer_latitude",  MOONX, "centric"),          ("",   "",  "" )),
    (("sub_observer_latitude",  MOONX, "graphic"),          ("",   "",  "" )),
    (("sub_solar_longitude",    MOONX, "iau", "west"),      ("",   "",  "" )),
#    (("sub_solar_longitude",    MOONX, "iau", "east"),      ("",   "",  "" )),
    (("sub_observer_longitude", MOONX, "iau", "west"),      ("",   "",  "" )),
#    (("sub_observer_longitude", MOONX, "iau", "east"),      ("",   "",  "" )),
    (("center_resolution",      MOONX, "u"),                ("",   "",  "" )),
    (("center_distance",        MOONX, "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     MOONX),                     ("",   "",  "" ))]

SUN_COLUMNS = [
    (("latitude",               "SUN", "centric"),          ("",  "",  "" )),
    (("latitude",               "SUN", "graphic"),          ("",  "",  "" )),
    (("longitude",              "SUN", "iau", "west"),      ("",  "",  "" )),
#    (("longitude",              "SUN", "iau", "east"),      ("",  "",  "" )),
    (("longitude",              meta.NULL, "sha", "east"),  ("",  "",  "" )),
    (("longitude",              "SUN", "obs", "west"),("",  "",  "" ), "-180"),
#    (("longitude",              "SUN", "obs", "east"),("",  "",  "" ), "-180"),
    (("finest_resolution",      "SUN"),                     ("",  "",  "" )),
    (("coarsest_resolution",    "SUN"),                     ("",  "",  "" )),
    (("distance",               "SUN"),                     ("",  "",  "" )),
    (("phase_angle",            meta.NULL),                 ("",  "",  "" )),
    (("incidence_angle",        meta.NULL),                 ("",  "",  "" )),
    (("emission_angle",         meta.NULL),                 ("",  "",  "" ))]

SUN_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     meta.NULL, "centric"),      ("",   "",  "" )),
    (("sub_solar_latitude",     meta.NULL, "graphic"),      ("",   "",  "" )),
    (("sub_observer_latitude",  "SUN", "centric"),          ("",   "",  "" )),
    (("sub_observer_latitude",  "SUN", "graphic"),          ("",   "",  "" )),
    (("sub_solar_longitude",    meta.NULL, "iau", "west"),  ("",   "",  "" )),
#    (("sub_solar_longitude",    meta.NULL, "iau", "east"),  ("",   "",  "" )),
    (("sub_observer_longitude", "SUN", "west"),             ("",   "",  "" )),
#    (("sub_observer_longitude", "SUN", "east"),             ("",   "",  "" )),
    (("center_resolution",      "SUN", "u"),                ("",   "",  "" )),
    (("center_distance",        "SUN", "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     meta.NULL),                 ("",   "",  "" ))]

# Assemble the column lists for each type of file for the rings and for Saturn

PLANET_SUMMARY_COLUMNS  = PLANET_COLUMNS + PLANET_GRIDLESS_COLUMNS
PLANET_DETAILED_COLUMNS = PLANET_COLUMNS

# Create a dictionary for the columns of each moon

MOON_SUMMARY_COLUMNS  = MOON_COLUMNS + MOON_GRIDLESS_COLUMNS
MOON_DETAILED_COLUMNS = MOON_COLUMNS

MOON_SUMMARY_DICT  = meta.replacement_dict(MOON_SUMMARY_COLUMNS,
                                           MOONX, MOON_NAMES)
MOON_DETAILED_DICT = meta.replacement_dict(MOON_DETAILED_COLUMNS,
                                           MOONX, MOON_NAMES)

# Treat the Sun as a moon for purposes of metadata

SUN_SUMMARY_COLUMNS  = SUN_COLUMNS + SUN_GRIDLESS_COLUMNS
SUN_DETAILED_COLUMNS = SUN_COLUMNS

MOON_SUMMARY_DICT["SUN"]  = SUN_SUMMARY_COLUMNS
MOON_DETAILED_DICT["SUN"] = SUN_DETAILED_COLUMNS

################################################################################
# Define the tiling for detailed listings
#
# The first item in the list defines a region to test for a suitable pixel
# count. The remaining items define a sequence of tiles to use in a
# detailed tabulation.
################################################################################
PLANET_TILES = [
    ("where_sunward", PLANET),                      # mask over remaining tiles
    ("where_below",   ("latitude", PLANET), -70. * oops.RPD),
    ("where_between", ("latitude", PLANET), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", PLANET), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", PLANET), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", PLANET), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", PLANET),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", PLANET),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", PLANET),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", PLANET),  70. * oops.RPD)
]

MOON_TILES = [
    ("where_all", ("where_in_front", MOONX, PLANET), # mask over remaining tiles
                  ("where_sunward",  MOONX)),
    ("where_below",   ("latitude", MOONX), -70. * oops.RPD),
    ("where_between", ("latitude", MOONX), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", MOONX), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", MOONX), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", MOONX), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", MOONX),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", MOONX),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", MOONX),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", MOONX),  70. * oops.RPD)
]

MOON_TILE_DICT = {}
for name in (MOON_NAMES + ["SUN"]):
    MOON_TILE_DICT[name] = meta.replace(MOON_TILES, MOONX, name)

################################################################################
