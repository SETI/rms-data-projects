################################################################################
# COLUMNS.py: Column definitions for geometry tables
#
# 8/20/12 MRS
#
# 1/4/13 MRS: Added new north-based incidence and emission angles for rings;
#   added new gridless quantities for rings; changed ring longitude origin to
#   "aries".
################################################################################

################################################################################
# Create a list of body IDs
################################################################################

saturn_body = oops.Body.lookup("SATURN")
moon_bodies = saturn_body.select_children("REGULAR")

MOON_NAMES   = [moon.name for moon in moon_bodies]
SYSTEM_NAMES = ["SATURN"] + MOON_NAMES
NAME_LENGTH  = max([len(name) for name in MOON_NAMES])

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

TRANSLATIONS = {"K07S4":"ANTHE"}

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
SMR = "SATURN_MAIN_RINGS"

SKY_COLUMNS = [
    (("right_ascension",        ()),                        ("",  "",  "")),
    (("declination",            ()),                        ("",  "",  ""))]

RING_COLUMNS = [
    (("ring_radius",            "SATURN:RING"),             ("PM", "P", "")),
    (("resolution",             "SATURN:RING", "v"),        ("PM", "P", "")),
    (("ring_radial_resolution", "SATURN:RING"),             ("PM", "P", "")),
    (("distance",               "SATURN:RING"),             ("PM", "P", "")),
    (("ring_longitude",         "SATURN:RING", "aries"),    ("PM", "P", "")),
    (("ring_longitude",         "SATURN:RING", "sha"),      ("PM", "",  "")),
    (("ring_longitude",         "SATURN:RING", "obs", -180),("PM", "P", ""), "-180"),
    (("ring_azimuth",           "SATURN:RING", "obs"),      ("PM", "P", "")),
    (("phase_angle",            "SATURN:RING"),             ("PM", "P", "")),
    (("ring_incidence_angle",   "SATURN:RING"),             ("PM", "P", "")),
    (("ring_incidence_angle",   "SATURN:RING", "prograde"), ("PM", "P", "")),
    (("ring_emission_angle",    "SATURN:RING"),             ("PM", "P", "")),
    (("ring_emission_angle",    "SATURN:RING", "prograde"), ("PM", "P", "")),
    (("ring_elevation",         "SATURN:RING", "sun"),      ("PM", "P", "")),
    (("ring_elevation",         "SATURN:RING", "obs"),      ("PM", "P", ""))]

RING_GRIDLESS_COLUMNS = [
    (("center_distance",        "SATURN:RING", "obs"),      ("",   "",  "" )),
    (("sub_ring_longitude",     "SATURN:RING", "sun", "aries"),
                                                            ("",   "",  "" )),
    (("sub_ring_longitude",     "SATURN:RING", "obs", "aries"),
                                                            ("",   "",  "" )),
    (("center_phase_angle",     "SATURN:RING"),             ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                "SATURN:RING"),             ("",   "",  "" )),
    (("ring_center_incidence_angle",
                                "SATURN:RING", "prograde"), ("",   "",  "" )),
    (("ring_center_emission_angle",
                                "SATURN:RING"),             ("",   "",  "" )),
    (("ring_center_emission_angle",
                                "SATURN:RING", "prograde"), ("",   "",  "" )),
    (("sub_latitude",           "SATURN:RING", "sun"),      ("",   "",  "" )),
    (("sub_latitude",           "SATURN:RING", "obs"),      ("",   "",  "" ))]

ANSA_COLUMNS = [
    (("ansa_radius",            "SATURN:ANSA"),             ("PM", "P", "")),
    (("ansa_altitude",          "SATURN:ANSA"),             ("PM", "P", "")),
    (("ansa_radial_resolution", "SATURN:ANSA"),             ("PM", "P", "")),
    (("distance",               "SATURN:ANSA"),             ("PM", "P", "")),
    (("ansa_longitude",         "SATURN:ANSA", "aries"),    ("PM", "P", "")),
    (("ansa_longitude",         "SATURN:ANSA", "sha"),      ("PM", "P", ""))]

SATURN_COLUMNS = [
    (("latitude",               "SATURN", "centric"),       ("RM", "",  "D")),
    (("latitude",               "SATURN", "graphic"),       ("RM", "",  "D")),
    (("longitude",              "SATURN", "iau", "west"),   ("RM", "",  "D")),
    (("longitude",              "SATURN", "sha", "east"),   ("RM", "",  "" )),
    (("longitude",              "SATURN", "obs", "west", -180),
                                                            ("RM", "",  "D"), "-180"),
    (("finest_resolution",      "SATURN"),                  ("RM", "",  "D")),
    (("coarsest_resolution",    "SATURN"),                  ("RM", "",  "D")),
    (("distance",               "SATURN"),                  ("RM", "",  "" )),
    (("phase_angle",            "SATURN"),                  ("RM", "",  "" )),
    (("incidence_angle",        "SATURN"),                  ("RM", "",  "" )),
    (("emission_angle",         "SATURN"),                  ("RM", "",  "" ))]

SATURN_GRIDLESS_COLUMNS = [
    (("sub_latitude",           "SATURN", "sun", "centric"),("",   "",  "" )),
    (("sub_latitude",           "SATURN", "sun", "graphic"),("",   "",  "" )),
    (("sub_latitude",           "SATURN", "obs", "centric"),("",   "",  "" )),
    (("sub_latitude",           "SATURN", "obs", "graphic"),("",   "",  "" )),
    (("sub_longitude",          "SATURN", "sun", "west"),   ("",   "",  "" )),
    (("sub_longitude",          "SATURN", "obs", "west"),   ("",   "",  "" )),
    (("center_resolution",      "SATURN", "u"),             ("",   "",  "" )),
    (("center_distance",        "SATURN", "obs"),           ("",   "",  "" )),
    (("center_phase_angle",     "SATURN"),                  ("",   "",  "" ))]

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
    (("sub_latitude",           MOONX, "sun", "centric"),   ("",   "",  "" )),
    (("sub_latitude",           MOONX, "sun", "graphic"),   ("",   "",  "" )),
    (("sub_latitude",           MOONX, "obs", "centric"),   ("",   "",  "" )),
    (("sub_latitude",           MOONX, "obs", "graphic"),   ("",   "",  "" )),
    (("sub_longitude",          MOONX, "sun", "west"),      ("",   "",  "" )),
    (("sub_longitude",          MOONX, "obs", "west"),      ("",   "",  "" )),
    (("center_resolution",      MOONX, "u"),                ("",   "",  "" )),
    (("center_distance",        MOONX, "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     MOONX),                     ("",   "",  "" ))]

SUN_COLUMNS = [
    (("latitude",               "SUN", "centric"),          ("P",  "",  "" )),
    (("latitude",               "SUN", "graphic"),          ("P",  "",  "" )),
    (("longitude",              "SUN", "iau", "west"),      ("P",  "",  "" )),
    (("longitude",              meta.NULL, "sha", "east"),  ("P",  "",  "" )),
    (("longitude",              "SUN", "obs", "west", -180),("P",  "",  "" ), "-180"),
    (("finest_resolution",      "SUN"),                     ("P",  "",  "" )),
    (("coarsest_resolution",    "SUN"),                     ("P",  "",  "" )),
    (("distance",               "SUN"),                     ("P",  "",  "" )),
    (("phase_angle",            meta.NULL),                 ("P",  "",  "" )),
    (("incidence_angle",        meta.NULL),                 ("P",  "",  "" )),
    (("emission_angle",         meta.NULL),                 ("P",  "",  "" ))]

SUN_GRIDLESS_COLUMNS = [
    (("sub_latitude",           meta.NULL, "sun"),          ("",   "",  "" )),
    (("sub_latitude",           meta.NULL, "sun"),          ("",   "",  "" )),
    (("sub_latitude",           "SUN", "obs", "centric"),   ("",   "",  "" )),
    (("sub_latitude",           "SUN", "obs", "graphic"),   ("",   "",  "" )),
    (("sub_longitude",          meta.NULL, "sun", "west"),  ("",   "",  "" )),
    (("sub_longitude",          "SUN", "obs", "west"),      ("",   "",  "" )),
    (("center_resolution",      "SUN", "u"),                ("",   "",  "" )),
    (("center_distance",        "SUN", "obs"),              ("",   "",  "" )),
    (("center_phase_angle",     meta.NULL),                 ("",   "",  "" ))]

# In development; currently unused...

TEST_COLUMNS = [
    (("right_ascension",        ()),                        ("",   "",  "")),
    (("declination",            ()),                        ("",   "",  "")),
    (("ring_radius",            "SATURN:RING"),             ("P",  "P", "")),
    (("ring_radial_resolution", "SATURN:RING"),             ("P",  "P", "")),
    (("ring_longitude",         "SATURN:RING", "j2000"),    ("P",  "P", "")),
    (("ring_longitude",         "SATURN:RING", "obs"),      ("P",  "P", "")),
    (("ring_longitude",         "SATURN:RING", "sha"),      ("P",  "P", "")),
    (("phase_angle",            "SATURN:RING"),             ("P",  "P", "")),
    (("incidence_angle",        "SATURN:RING"),             ("P",  "P", "")),
    (("emission_angle",         "SATURN:RING"),             ("P",  "P", "")),
    (("distance",               "SATURN:RING"),             ("P",  "",  "")),
    (("where_inside_shadow",    "SATURN:RING", "SATURN"),   ("P",  "",  "")),
    (("where_in_front",         "SATURN:RING", "SATURN"),   ("P",  "",  "")),
    (("where_antisunward",      "SATURN:RING"),             ("P",  "",  "")),
    (("ansa_radius",            "SATURN:ANSA"),             ("P",  "",  "")),
    (("ansa_altitude",          "SATURN:ANSA"),             ("P",  "",  "")),
    (("ansa_longitude",         "SATURN:ANSA", "j2000"),    ("P",  "",  "")),
    (("ansa_longitude",         "SATURN:ANSA", "sha"),      ("P",  "",  "")),
    (("distance",               "SATURN:ANSA"),             ("P",  "",  "")),
    (("ansa_radial_resolution", "SATURN:ANSA"),             ("P",  "",  ""))]

RING_AND_SATURN_COLUMNS = [
    (("where_inside_shadow","SATURN:RING", "SATURN"),       ("PM", "",  "")),
    (("where_in_back",      "SATURN", "SATURN:RING"),       ("M",  "",  "")),
    (("where_inside_shadow","SATURN", "SATURN_MAIN_RINGS"), ("RM", "",  ""))]

SATURN_COLUMNS_WITH_RING_SHADOW = [
    (("latitude",               "SATURN", "centric"),       ("RM", "R", "D")),
    (("latitude",               "SATURN", "graphic"),       ("RM", "R", "D")),
    (("longitude",              "SATURN", "iau", "west"),   ("RM", "R", "D")),
    (("longitude",              "SATURN", "sha", "east"),   ("RM", "",  "" )),
    (("longitude",              "SATURN", "obs", "west", -180),
                                                            ("RM", "R", "D")),
    (("finest_resolution",      "SATURN"),                  ("RM", "R", "D")),
    (("coarsest_resolution",    "SATURN"),                  ("RM", "R", "D")),
    (("distance",               "SATURN"),                  ("RM", "R", "" )),
    (("phase_angle",            "SATURN"),                  ("RM", "R", "" )),
    (("incidence_angle",        "SATURN"),                  ("RM", "R", "" )),
    (("emission_angle",         "SATURN"),                  ("RM", "R", "" ))]

SATURN_LIMB_COLUMNS = [
    (("altitude",           "SATURN:LIMB"),                 ("RM", "P", "")),
    (("resolution",         "SATURN:LIMB"),                 ("RM", "P", "")),
    (("distance",           "SATURN:LIMB"),                 ("RM", "P", "")),
    (("latitude",           "SATURN:LIMB", "centric"),      ("RM", "P", "")),
    (("latitude",           "SATURN:LIMB", "graphic"),      ("RM", "P", "")),
    (("longitude",          "SATURN:LIMB", "iau", "west"),  ("RM", "P", "")),
    (("longitude",          "SATURN:LIMB", "sha", "east"),  ("RM", "P", "")),
    (("longitude",          "SATURN:LIMB", "obs", "west", -180),
                                                            ("RM", "P", ""))]

TITAN_LIMB_COLUMNS = [
    (("altitude",           "TITAN:LIMB"),                  ("P",  "M", "")),
    (("resolution",         "TITAN:LIMB"),                  ("P",  "M", "")),
    (("distance",           "TITAN:LIMB"),                  ("P",  "M", "")),
    (("latitude",           "TITAN:LIMB", "centric"),       ("P",  "M", "")),
    (("latitude",           "TITAN:LIMB", "graphic"),       ("P",  "M", "")),
    (("longitude",          "TITAN:LIMB", "iau", "west"),   ("P",  "M", "")),
    (("longitude",          "TITAN:LIMB", "sha", "east"),   ("P",  "M", "")),
    (("longitude",          "TITAN:LIMB", "obs", "east", -180),
                                                            ("P",  "M", ""))]

MOON_LIMB_COLUMNS = [
    (("altitude",           meta.NULL),                     ("P",  "M", "")),
    (("resolution",         meta.NULL),                     ("P",  "M", "")),
    (("distance",           meta.NULL),                     ("P",  "M", "")),
    (("latitude",           meta.NULL, "centric"),          ("P",  "M", "")),
    (("latitude",           meta.NULL, "graphic"),          ("P",  "M", "")),
    (("longitude",          meta.NULL, "iau", "west"),      ("P",  "M", "")),
    (("longitude",          meta.NULL, "sha", "east"),      ("P",  "M", "")),
    (("longitude",          meta.NULL, "obs", "east", -180),("P",  "M", ""))]

# Assemble the column lists for each type of file for the rings and for Saturn

RING_SUMMARY_COLUMNS  = (SKY_COLUMNS + RING_COLUMNS + ANSA_COLUMNS +
                         RING_GRIDLESS_COLUMNS)
RING_DETAILED_COLUMNS = RING_COLUMNS

SATURN_SUMMARY_COLUMNS  = SATURN_COLUMNS + SATURN_GRIDLESS_COLUMNS
SATURN_DETAILED_COLUMNS = SATURN_COLUMNS

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
    ("where_all", ("where_in_front", "SATURN:RING", "SATURN"),
                  ("where_below", ("ring_radius", "SATURN:RING"), 200000.)),
    ("where_below",   ("ring_radius", "SATURN:RING"),  75000.),
    ("where_between", ("ring_radius", "SATURN:RING"),  75000.,  85000.),
    ("where_between", ("ring_radius", "SATURN:RING"),  85000.,  95000.),
    ("where_between", ("ring_radius", "SATURN:RING"),  95000., 105000.),
    ("where_between", ("ring_radius", "SATURN:RING"), 105000., 115000.),
    ("where_between", ("ring_radius", "SATURN:RING"), 115000., 125000.),
    ("where_between", ("ring_radius", "SATURN:RING"), 125000., 135000.),
    ("where_between", ("ring_radius", "SATURN:RING"), 135000., 145000.),
    ("where_between", ("ring_radius", "SATURN:RING"), 145000., 160000.), # F/G
    ("where_between", ("ring_radius", "SATURN:RING"), 160000., 175000.), # G
    ("where_between", ("ring_radius", "SATURN:RING"), 175000., 200000.), # Mimas
    ("where_between", ("ring_radius", "SATURN:RING"), 200000., 300000.), # E
    ("where_above",   ("ring_radius", "SATURN:RING"), 300000.)]

SATURN_TILES = [
    ("where_sunward", "SATURN"),                        # union of regions[1:]
    ("where_below",   ("latitude", "SATURN"), -70. * oops.RPD),
    ("where_between", ("latitude", "SATURN"), -70. * oops.RPD, -50. * oops.RPD),
    ("where_between", ("latitude", "SATURN"), -50. * oops.RPD, -30. * oops.RPD),
    ("where_between", ("latitude", "SATURN"), -30. * oops.RPD, -10. * oops.RPD),
    ("where_between", ("latitude", "SATURN"), -10. * oops.RPD,  10. * oops.RPD),
    ("where_between", ("latitude", "SATURN"),  10. * oops.RPD,  30. * oops.RPD),
    ("where_between", ("latitude", "SATURN"),  30. * oops.RPD,  50. * oops.RPD),
    ("where_between", ("latitude", "SATURN"),  50. * oops.RPD,  70. * oops.RPD),
    ("where_above",   ("latitude", "SATURN"),  70. * oops.RPD)]

MOON_TILES = [
    ("where_all", ("where_in_front", MOONX, "SATURN"),
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
