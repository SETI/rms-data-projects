################################################################################
# COLUMNS.py: Column definitions for geometry tables
#
# 1/6/16 MRS: Adapted for Jupiter.
################################################################################

################################################################################
# Create a list of body IDs
################################################################################

PLANET = "JUPITER"

planet_body = oops.Body.lookup(PLANET)
moon_bodies = planet_body.select_children("REGULAR")

MOON_NAMES   = [moon.name for moon in moon_bodies]
SYSTEM_NAMES = [PLANET] + MOON_NAMES
# NAME_LENGTH  = max([len(name) for name in MOON_NAMES])
NAME_LENGTH  = 12           # Big enough for names of irregulars

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
JMR = "JUPITER_MAIN_RINGS"

SKY_COLUMNS = [
    (("right_ascension",        ()),                         ("",  "",  "")),
    (("declination",            ()),                         ("",  "",  ""))]

RING_COLUMNS = [
    (("ring_radius",            "JUPITER:RING"),             ("PM", "P", "")),
    (("resolution",             "JUPITER:RING", "v"),        ("PM", "P", "")),
    (("ring_radial_resolution", "JUPITER:RING"),             ("PM", "P", "")),
    (("distance",               "JUPITER:RING"),             ("PM", "P", "")),
    (("ring_longitude",         "JUPITER:RING", "aries"),    ("PM", "P", "")),
    (("ring_longitude",         "JUPITER:RING", "sha"),      ("PM", "",  "")),
    (("ring_longitude",         "JUPITER:RING", "obs", -180),("PM", "P", ""), "-180"),
    (("ring_azimuth",           "JUPITER:RING", "obs"),      ("PM", "P", "")),
    (("phase_angle",            "JUPITER:RING"),             ("PM", "P", "")),
    (("ring_incidence_angle",   "JUPITER:RING"),             ("PM", "P", "")),
    (("ring_incidence_angle",   "JUPITER:RING", "prograde"), ("PM", "P", "")),
    (("ring_emission_angle",    "JUPITER:RING"),             ("PM", "P", "")),
    (("ring_emission_angle",    "JUPITER:RING", "prograde"), ("PM", "P", "")),
    (("ring_elevation",         "JUPITER:RING", "sun"),      ("PM", "P", "")),
    (("ring_elevation",         "JUPITER:RING", "obs"),      ("PM", "P", ""))]

RING_GRIDLESS_COLUMNS = [
    (("center_distance",        "JUPITER:RING", "obs"),      ("",   "",  "" )),
    (("ring_sub_solar_longitude",    "JUPITER:RING", "aries"),
                                                             ("",   "",  "" )),
    (("ring_sub_observer_longitude", "JUPITER:RING", "aries"),
                                                             ("",   "",  "" )),
    (("center_phase_angle",     "JUPITER:RING"),             ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                "JUPITER:RING"),             ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                "JUPITER:RING", "prograde"), ("",   "",  "" )),
    (("ring_center_emission_angle",
                                "JUPITER:RING"),             ("",   "",  "" )),
    (("ring_center_emission_angle",
                                "JUPITER:RING", "prograde"), ("",   "",  "" )),
    (("sub_solar_latitude",     "JUPITER:RING"),             ("",   "",  "" )),
    (("sub_observer_latitude",  "JUPITER:RING"),             ("",   "",  "" ))]

ANSA_COLUMNS = [
    (("ansa_radius",            "JUPITER:ANSA"),             ("PM", "P", "")),
    (("ansa_altitude",          "JUPITER:ANSA"),             ("PM", "P", "")),
    (("ansa_radial_resolution", "JUPITER:ANSA"),             ("PM", "P", "")),
    (("distance",               "JUPITER:ANSA"),             ("PM", "P", "")),
    (("ansa_longitude",         "JUPITER:ANSA", "aries"),    ("PM", "P", "")),
    (("ansa_longitude",         "JUPITER:ANSA", "sha"),      ("PM", "P", ""))]

PLANET_COLUMNS = [
    (("latitude",               "JUPITER", "centric"),       ("M", "",  "D")),
    (("latitude",               "JUPITER", "graphic"),       ("M", "",  "D")),
    (("longitude",              "JUPITER", "iau", "west"),   ("M", "",  "D")),
    (("longitude",              "JUPITER", "sha", "east"),   ("M", "",  "" )),
    (("longitude",              "JUPITER", "obs", "west", -180),
                                                             ("M", "",  "D"), "-180"),
    (("finest_resolution",      "JUPITER"),                  ("M", "",  "D")),
    (("coarsest_resolution",    "JUPITER"),                  ("M", "",  "D")),
    (("distance",               "JUPITER"),                  ("M", "",  "" )),
    (("phase_angle",            "JUPITER"),                  ("M", "",  "" )),
    (("incidence_angle",        "JUPITER"),                  ("M", "",  "" )),
    (("emission_angle",         "JUPITER"),                  ("M", "",  "" ))]

PLANET_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     "JUPITER", "centric"),       ("",   "",  "" )),
    (("sub_solar_latitude",     "JUPITER", "graphic"),       ("",   "",  "" )),
    (("sub_observer_latitude",  "JUPITER", "centric"),       ("",   "",  "" )),
    (("sub_observer_latitude",  "JUPITER", "graphic"),       ("",   "",  "" )),
    (("sub_solar_longitude",    "JUPITER", "iau", "west"),   ("",   "",  "" )),
    (("sub_observer_longitude", "JUPITER", "iau", "west"),   ("",   "",  "" )),
    (("center_resolution",      "JUPITER", "u"),             ("",   "",  "" )),
    (("center_distance",        "JUPITER", "obs"),           ("",   "",  "" )),
    (("center_phase_angle",     "JUPITER"),                  ("",   "",  "" ))]

MOON_COLUMNS = [
    (("latitude",               MOONX, "centric"),          ("P",  "",  "D")),
    (("latitude",               MOONX, "graphic"),          ("P",  "",  "D")),
    (("longitude",              MOONX, "iau", "west"),      ("P",  "",  "D")),
    (("longitude",              MOONX, "sha", "east"),      ("P",  "",  "" )),
    (("longitude",              MOONX, "obs", "west", -180),("P",  "",  "D"), "-180"),
    (("finest_resolution",      MOONX),                     ("P",  "",  "D")),
    (("coarsest_resolution",    MOONX),                     ("P",  "",  "D")),
    (("distance",               MOONX),                     ("P",  "",  "" )),
    (("phase_angle",            MOONX),                     ("P",  "",  "" )),
    (("incidence_angle",        MOONX),                     ("P",  "",  "" )),
    (("emission_angle",         MOONX),                     ("P",  "",  "" ))]

MOON_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     MOONX, "centric"),          ("",   "",  "" )),
    (("sub_solar_latitude",     MOONX, "graphic"),          ("",   "",  "" )),
    (("sub_observer_latitude",  MOONX, "centric"),          ("",   "",  "" )),
    (("sub_observer_latitude",  MOONX, "graphic"),          ("",   "",  "" )),
    (("sub_solar_longitude",    MOONX, "iau", "west"),      ("",   "",  "" )),
    (("sub_observer_longitude", MOONX, "iau", "west"),      ("",   "",  "" )),
    (("center_resolution",      MOONX, "u"),                ("",   "",  "" )),
    (("center_distance",        MOONX, "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     MOONX),                     ("",   "",  "" ))]

# Assemble the column lists for each type of file for the rings and for Saturn

RING_SUMMARY_COLUMNS  = (SKY_COLUMNS + RING_COLUMNS + ANSA_COLUMNS +
                         RING_GRIDLESS_COLUMNS)
RING_DETAILED_COLUMNS = RING_COLUMNS

PLANET_SUMMARY_COLUMNS  = PLANET_COLUMNS + PLANET_GRIDLESS_COLUMNS
PLANET_DETAILED_COLUMNS = PLANET_COLUMNS

# Create a dictionary for the columns of each moon

MOON_SUMMARY_COLUMNS  = MOON_COLUMNS + MOON_GRIDLESS_COLUMNS
MOON_DETAILED_COLUMNS = MOON_COLUMNS

MOON_SUMMARY_DICT  = meta.replacement_dict(MOON_SUMMARY_COLUMNS,
                                           MOONX, MOON_NAMES)
MOON_DETAILED_DICT = meta.replacement_dict(MOON_DETAILED_COLUMNS,
                                           MOONX, MOON_NAMES)

################################################################################
# Define the tiling for detailed listings
#
# The first item in the list defines a region to test for a suitable pixel
# count. The remaining items define a sequence of tiles to use in a
# detailed tabulation.
################################################################################

RING_TILES = []

PLANET_TILES = [
    ("where_sunward", "JUPITER"),                        # union of regions[1:]
    ("where_below",   ("latitude", "JUPITER"), -70. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", "JUPITER"),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", "JUPITER"),  70. * oops.RPD)]

MOON_TILES = [
    ("where_all", ("where_in_front", MOONX, "JUPITER"),
                  ("where_sunward",  MOONX)),           # union of regions[1:]
    ("where_below",   ("latitude", MOONX), -70. * oops.RPD),
    ("where_between", ("latitude", MOONX), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", MOONX), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", MOONX), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", MOONX), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", MOONX),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", MOONX),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", MOONX),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", MOONX),  70. * oops.RPD)]

MOON_TILE_DICT = {}
for name in MOON_NAMES:
    MOON_TILE_DICT[name] = meta.replace(MOON_TILES, MOONX, name)

################################################################################
