################################################################################
# COLUMNS_PLUTO.py: Column definitions for geometry tables
#
# 8/27/16 MRS: Adapted for Pluto.
################################################################################

PLANET = "PLUTO"
PLANET_RING = "PLUTO_RING_PLANE"
PLANET_ANSA = "PLUTO BARYCENTER:ANSA"
PLANET_LIMB = PLANET + ":LIMB"

################################################################################
# Create a list of body IDs
################################################################################

planet_body = oops.Body.lookup(PLANET)
moon_bodies = planet_body.select_children("REGULAR")

MOON_NAMES   = [moon.name for moon in moon_bodies]
SYSTEM_NAMES = [PLANET] + MOON_NAMES
# NAME_LENGTH  = max([len(name) for name in MOON_NAMES])
NAME_LENGTH  = 12           # Big enough for names of Jupiter irregulars

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
#                       "P" = let the planet mask the surface; (Pluto or Charon)
#                       "R" = let the rings mask the surface; (unused)
#                       "M" = let the moon mask the surface. (unused)
#
#   shadower        a string indicating which bodies shadow the surface. It is
#                   constructed by concatenating any of these characters:
#                       "P" = let the planet shadow the surface; (Pluto or Charon)
#                       "R" = let the rings shadow the surface; (unused)
#                       "M" = let the moon shadow the surface. (unused)
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

SKY_COLUMNS = [
    (("right_ascension",        ()),                        ("",  "",  "")),
    (("declination",            ()),                        ("",  "",  ""))]

RING_COLUMNS = [
    (("ring_radius",            PLANET_RING),               ("PM", "P", "")),
    (("resolution",             PLANET_RING, "v"),          ("PM", "P", "")),
    (("ring_radial_resolution", PLANET_RING),               ("PM", "P", "")),
    (("distance",               PLANET_RING),               ("PM", "P", "")),
    (("ring_longitude",         PLANET_RING, "aries"),      ("PM", "P", "")),
    (("ring_longitude",         PLANET_RING, "sha"),        ("PM", "",  "")),
    (("ring_longitude",         PLANET_RING, "obs", -180),  ("PM", "P", ""), "-180"),
    (("ring_azimuth",           PLANET_RING, "obs"),        ("PM", "P", "")),
    (("phase_angle",            PLANET_RING),               ("PM", "P", "")),
    (("ring_incidence_angle",   PLANET_RING),               ("PM", "P", "")),
    (("ring_incidence_angle",   PLANET_RING, "prograde"),   ("PM", "P", "")),
    (("ring_emission_angle",    PLANET_RING),               ("PM", "P", "")),
    (("ring_emission_angle",    PLANET_RING, "prograde"),   ("PM", "P", "")),
    (("ring_elevation",         PLANET_RING, "sun"),        ("PM", "P", "")),
    (("ring_elevation",         PLANET_RING, "obs"),        ("PM", "P", ""))]

RING_GRIDLESS_COLUMNS = [
    (("center_distance",        PLANET_RING, "obs"),        ("",   "",  "" )),
    (("ring_sub_solar_longitude",
                                PLANET_RING, "aries"),      ("",   "",  "" )),
    (("ring_sub_observer_longitude",
                                PLANET_RING, "aries"),      ("",   "",  "" )),
    (("center_phase_angle",     PLANET_RING),               ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                PLANET_RING),               ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                PLANET_RING, "prograde"),   ("",   "",  "" )),
    (("ring_center_emission_angle",
                                PLANET_RING),               ("",   "",  "" )),
    (("ring_center_emission_angle",
                                PLANET_RING, "prograde"),   ("",   "",  "" )),
    (("sub_solar_latitude",     PLANET_RING),               ("",   "",  "" )),
    (("sub_observer_latitude",  PLANET_RING),               ("",   "",  "" ))]

ANSA_COLUMNS = [
    (("ansa_radius",            PLANET_ANSA),               ("PM", "P", "")),
    (("ansa_altitude",          PLANET_ANSA),               ("PM", "P", "")),
    (("ansa_radial_resolution", PLANET_ANSA),               ("PM", "P", "")),
    (("distance",               PLANET_ANSA),               ("PM", "P", "")),
    (("ansa_longitude",         PLANET_ANSA, "aries"),      ("PM", "P", "")),
    (("ansa_longitude",         PLANET_ANSA, "sha"),        ("PM", "P", ""))]

PLANET_COLUMNS = [
    (("latitude",               PLANET, "centric"),         ("RM", "",  "D")),
    (("latitude",               PLANET, "graphic"),         ("RM", "",  "D")),
    (("longitude",              PLANET, "iau", "west"),     ("RM", "",  "D")),
    (("longitude",              PLANET, "sha", "east"),     ("RM", "",  "" )),
    (("longitude",              PLANET, "obs", "west", -180),
                                                            ("RM", "",  "D"), "-180"),
    (("finest_resolution",      PLANET),                    ("RM", "",  "D")),
    (("coarsest_resolution",    PLANET),                    ("RM", "",  "D")),
    (("distance",               PLANET),                    ("RM", "",  "" )),
    (("phase_angle",            PLANET),                    ("RM", "",  "" )),
    (("incidence_angle",        PLANET),                    ("RM", "",  "" )),
    (("emission_angle",         PLANET),                    ("RM", "",  "" ))]

PLANET_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     PLANET, "centric"),         ("",   "",  "" )),
    (("sub_solar_latitude",     PLANET, "graphic"),         ("",   "",  "" )),
    (("sub_observer_latitude",  PLANET, "centric"),         ("",   "",  "" )),
    (("sub_observer_latitude",  PLANET, "graphic"),         ("",   "",  "" )),
    (("sub_solar_longitude",    PLANET, "iau", "west"),     ("",   "",  "" )),
    (("sub_observer_longitude", PLANET, "iau", "west"),     ("",   "",  "" )),
    (("center_resolution",      PLANET, "u"),               ("",   "",  "" )),
    (("center_distance",        PLANET, "obs"),             ("",   "",  "" )),
    (("center_phase_angle",     PLANET),                    ("",   "",  "" ))]

CHARON_COLUMNS = [
    (("latitude",               "CHARON", "centric"),         ("RM", "",  "D")),
    (("latitude",               "CHARON", "graphic"),         ("RM", "",  "D")),
    (("longitude",              "CHARON", "iau", "west"),     ("RM", "",  "D")),
    (("longitude",              "CHARON", "sha", "east"),     ("RM", "",  "" )),
    (("longitude",              "CHARON", "obs", "west", -180),
                                                            ("RM", "",  "D"), "-180"),
    (("finest_resolution",      "CHARON"),                    ("RM", "",  "D")),
    (("coarsest_resolution",    "CHARON"),                    ("RM", "",  "D")),
    (("distance",               "CHARON"),                    ("RM", "",  "" )),
    (("phase_angle",            "CHARON"),                    ("RM", "",  "" )),
    (("incidence_angle",        "CHARON"),                    ("RM", "",  "" )),
    (("emission_angle",         "CHARON"),                    ("RM", "",  "" ))]

CHARON_GRIDLESS_COLUMNS = [
    (("sub_solar_latitude",     "CHARON", "centric"),         ("",   "",  "" )),
    (("sub_solar_latitude",     "CHARON", "graphic"),         ("",   "",  "" )),
    (("sub_observer_latitude",  "CHARON", "centric"),         ("",   "",  "" )),
    (("sub_observer_latitude",  "CHARON", "graphic"),         ("",   "",  "" )),
    (("sub_solar_longitude",    "CHARON", "iau", "west"),     ("",   "",  "" )),
    (("sub_observer_longitude", "CHARON", "iau", "west"),     ("",   "",  "" )),
    (("center_resolution",      "CHARON", "u"),               ("",   "",  "" )),
    (("center_distance",        "CHARON", "obs"),             ("",   "",  "" )),
    (("center_phase_angle",     "CHARON"),                    ("",   "",  "" ))]

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

CHARON_SUMMARY_COLUMNS  = CHARON_COLUMNS + CHARON_GRIDLESS_COLUMNS
CHARON_DETAILED_COLUMNS = CHARON_COLUMNS

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
    ("where_sunward", "PLUTO"),                        # union of regions[1:]
    ("where_below",   ("latitude", "PLUTO"), -70. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", "PLUTO"),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", "PLUTO"),  70. * oops.RPD)]

CHARON_TILES = [
    ("where_sunward", "CHARON"),                        # union of regions[1:]
    ("where_below",   ("latitude", "CHARON"), -70. * oops.RPD),
    ("where_between", ("latitude", "CHARON"), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", "CHARON"), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", "CHARON"), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", "CHARON"), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", "CHARON"),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", "CHARON"),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", "CHARON"),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", "CHARON"),  70. * oops.RPD)]

MOON_TILES = [
    ("where_all", ("where_in_front", MOONX, "PLUTO"),
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
