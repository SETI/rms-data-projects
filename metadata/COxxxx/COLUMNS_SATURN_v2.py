################################################################################
# COLUMNS_SATURN.py: Column definitions for Saturn geometry tables
################################################################################

PLANET = "SATURN"
PLANET_RING = PLANET + ":RING"
PLANET_ANSA = PLANET + ":ANSA"
PLANET_LIMB = PLANET + ":LIMB"

################################################################################
# Create a list of body IDs
################################################################################

planet_body = oops.Body.lookup(PLANET)
moon_bodies = planet_body.select_children("REGULAR")

MOON_NAMES   = [moon.name for moon in moon_bodies] + ["PHOEBE"]
SYSTEM_NAMES = [PLANET] + MOON_NAMES
# NAME_LENGTH  = max([len(name) for name in MOON_NAMES])
NAME_LENGTH  = 10

CIMS_TARGET_ABBREVIATIONS = {
    "AG": "AEGAEON",
    "AN": "ANTHE",
    "AT": "ATLAS",
    "CP": "CALYPSO",
    "DA": "DAPHNIS",
    "DI": "DIONE",
    "EN": "ENCELADUS",
    "EP": "EPIMETHEUS",
    "HE": "HELENE",
    "HY": "HYPERION",
    "IA": "IAPETUS",
    "JA": "JANUS",
    "ME": "METHONE",
    "MI": "MIMAS",
    "PA": "PANDORA",
    "PH": "PHOEBE",
    "PL": "PALLENE",
    "PM": "PROMETHEUS",
    "PN": "PAN",
    "PO": "POLYDEUCES",
    "RH": "RHEA",
    "SA": "SATURN",
    "TE": "TETHYS",
    "TI": "TITAN",
    "TL": "TELESTO",
}

# Maintain a list of translations for target names

TRANSLATIONS = {"K07S4": "ANTHE",
                "HYROKKIN": "HYRROKKIN",
                "ERRIAPO": "ERRIAPUS",
                "SUTTUNG": "SUTTUNGR",
                "SKADI": "SKATHI",
                "THRYM": "THRYMR"}


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

SKY_COLUMNS = [
    (("right_ascension",        ()),                        ("",  "",  "")),
    (("declination",            ()),                        ("",  "",  ""))]

RING_COLUMNS = [
    (("ring_radius",            PLANET_RING),               ("PM", "P", "")),
    (("resolution",             PLANET_RING, "v"),          ("PM", "P", "")),
    (("ring_radial_resolution", PLANET_RING),               ("PM", "P", "")),
    (("distance",               PLANET_RING),               ("PM", "P", "")),
    (("ring_longitude",         PLANET_RING, "aries"),      ("PM", "P", "")),
    (("ring_longitude",         PLANET_RING, "node"),       ("PM", "P", "")),
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
    (("ring_sub_solar_longitude",
                                PLANET_RING, "node"),       ("",   "",  "" )),
    (("ring_sub_observer_longitude",
                                PLANET_RING, "node"),       ("",   "",  "" )),
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
    (("ansa_longitude",         PLANET_ANSA, "node"),       ("PM", "P", "")),
    (("ansa_longitude",         PLANET_ANSA, "sha"),        ("PM", "P", ""))]

PLANET_COLUMNS = [
    (("latitude",               PLANET, "centric"),         ("RM", "",  "D")),
    (("latitude",               PLANET, "graphic"),         ("RM", "",  "D")),
    (("longitude",              PLANET, "iau", "west"),     ("RM", "",  "D")),
    (("longitude",              PLANET, "iau", "east"),     ("RM", "",  "D")),
    (("longitude",              PLANET, "sha", "east"),     ("RM", "",  "" )),
    (("longitude",              PLANET, "obs", "west", -180),
                                                            ("RM", "",  "D"), "-180"),
    (("longitude",              PLANET, "obs", "east", -180),
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
    (("sub_solar_longitude",    PLANET, "iau", "east"),     ("",   "",  "" )),
    (("sub_observer_longitude", PLANET, "iau", "west"),     ("",   "",  "" )),
    (("sub_observer_longitude", PLANET, "iau", "east"),     ("",   "",  "" )),
    (("center_resolution",      PLANET, "u"),               ("",   "",  "" )),
    (("center_distance",        PLANET, "obs"),             ("",   "",  "" )),
    (("center_phase_angle",     PLANET),                    ("",   "",  "" ))]

MOON_COLUMNS = [
    (("latitude",               MOONX, "centric"),          ("P",  "",  "D")),
    (("latitude",               MOONX, "graphic"),          ("P",  "",  "D")),
    (("longitude",              MOONX, "iau", "west"),      ("P",  "",  "D")),
    (("longitude",              MOONX, "iau", "east"),      ("P",  "",  "D")),
    (("longitude",              MOONX, "sha", "east"),      ("P",  "",  "" )),
    (("longitude",              MOONX, "obs", "west", -180),("P",  "",  "D"), "-180"),
    (("longitude",              MOONX, "obs", "east", -180),("P",  "",  "D"), "-180"),
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
    (("sub_solar_longitude",    MOONX, "iau", "east"),      ("",   "",  "" )),
    (("sub_observer_longitude", MOONX, "iau", "west"),      ("",   "",  "" )),
    (("sub_observer_longitude", MOONX, "iau", "east"),      ("",   "",  "" )),
    (("center_resolution",      MOONX, "u"),                ("",   "",  "" )),
    (("center_distance",        MOONX, "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     MOONX),                     ("",   "",  "" ))]

SUN_COLUMNS = [
    (("latitude",               "SUN", "centric"),          ("",  "",  "" )),
    (("latitude",               "SUN", "graphic"),          ("",  "",  "" )),
    (("longitude",              "SUN", "iau", "west"),      ("",  "",  "" )),
    (("longitude",              "SUN", "iau", "east"),      ("",  "",  "" )),
    (("longitude",              meta.NULL, "sha", "east"),  ("",  "",  "" )),
    (("longitude",              "SUN", "obs", "west", -180),("",  "",  "" ), "-180"),
    (("longitude",              "SUN", "obs", "east", -180),("",  "",  "" ), "-180"),
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
    (("sub_solar_longitude",    meta.NULL, "iau", "east"),  ("",   "",  "" )),
    (("sub_observer_longitude", "SUN", "west"),             ("",   "",  "" )),
    (("sub_observer_longitude", "SUN", "east"),             ("",   "",  "" )),
    (("center_resolution",      "SUN", "u"),                ("",   "",  "" )),
    (("center_distance",        "SUN", "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     meta.NULL),                 ("",   "",  "" ))]

TEST_COLUMNS = [
    (("right_ascension",        ()),                        ("",   "",  "")),
    (("declination",            ()),                        ("",   "",  "")),
    (("ring_radius",            PLANET_RING),               ("P",  "P", "")),
    (("ring_radial_resolution", PLANET_RING),               ("P",  "P", "")),
    (("ring_longitude",         PLANET_RING, "node"),       ("P",  "P", "")),
    (("ring_longitude",         PLANET_RING, "obs"),        ("P",  "P", "")),
    (("ring_longitude",         PLANET_RING, "sha"),        ("P",  "P", "")),
    (("phase_angle",            PLANET_RING),               ("P",  "P", "")),
    (("incidence_angle",        PLANET_RING),               ("P",  "P", "")),
    (("emission_angle",         PLANET_RING),               ("P",  "P", "")),
    (("distance",               PLANET_RING),               ("P",  "",  "")),
    (("where_inside_shadow",    PLANET_RING, PLANET),       ("P",  "",  "")),
    (("where_in_front",         PLANET_RING, PLANET),       ("P",  "",  "")),
    (("where_antisunward",      PLANET_RING),               ("P",  "",  "")),
    (("ansa_radius",            PLANET_ANSA),               ("P",  "",  "")),
    (("ansa_altitude",          PLANET_ANSA),               ("P",  "",  "")),
    (("ansa_longitude",         PLANET_ANSA, "node"),       ("P",  "",  "")),
    (("ansa_longitude",         PLANET_ANSA, "sha"),        ("P",  "",  "")),
    (("distance",               PLANET_ANSA),               ("P",  "",  "")),
    (("ansa_radial_resolution", PLANET_ANSA),               ("P",  "",  ""))]

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

RING_TILES = [
    ("where_all", ("where_in_front", PLANET_RING, PLANET),
                  ("where_below", ("ring_radius", PLANET_RING), 200000.)),
    ("where_below",   ("ring_radius", PLANET_RING),  75000.),
    ("where_between", ("ring_radius", PLANET_RING),  75000.,  85000.),
    ("where_between", ("ring_radius", PLANET_RING),  85000.,  95000.),
    ("where_between", ("ring_radius", PLANET_RING),  95000., 105000.),
    ("where_between", ("ring_radius", PLANET_RING), 105000., 115000.),
    ("where_between", ("ring_radius", PLANET_RING), 115000., 125000.),
    ("where_between", ("ring_radius", PLANET_RING), 125000., 135000.),
    ("where_between", ("ring_radius", PLANET_RING), 135000., 145000.),
    ("where_between", ("ring_radius", PLANET_RING), 145000., 160000.), # F/G
    ("where_between", ("ring_radius", PLANET_RING), 160000., 175000.), # G
    ("where_between", ("ring_radius", PLANET_RING), 175000., 200000.), # Mimas
    ("where_between", ("ring_radius", PLANET_RING), 200000., 300000.), # E
    ("where_above",   ("ring_radius", PLANET_RING), 300000.)]

PLANET_TILES = [
    ("where_sunward", PLANET),                        # union of regions[1:]
    ("where_below",   ("latitude", PLANET), -70. * oops.RPD),
    ("where_between", ("latitude", PLANET), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", PLANET), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", PLANET), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", PLANET), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", PLANET),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", PLANET),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", PLANET),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", PLANET),  70. * oops.RPD)]

MOON_TILES = [
    ("where_all", ("where_in_front", MOONX, PLANET),
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
for name in (MOON_NAMES + ["SUN"]):
    MOON_TILE_DICT[name] = meta.replace(MOON_TILES, MOONX, name)

################################################################################
