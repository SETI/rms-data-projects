################################################################################
# COLUMNS_RING.py: Column definitions for test geometry tables
################################################################################
planet_ring = BODYX + ":RING"
planet_ansa = BODYX + ":ANSA"

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
TEST_COLUMNS = [
    (("right_ascension",        ()),                        ("",   "",  "")),
    (("declination",            ()),                        ("",   "",  "")),
    (("ring_radius",            planet_ring),               ("P",  "P", "")),
    (("ring_radial_resolution", planet_ring),               ("P",  "P", "")),
    (("ring_longitude",         planet_ring, "node"),       ("P",  "P", "")),
    (("ring_longitude",         planet_ring, "obs"),        ("P",  "P", "")),
    (("ring_longitude",         planet_ring, "sha"),        ("P",  "P", "")),
    (("phase_angle",            planet_ring),               ("P",  "P", "")),
    (("incidence_angle",        planet_ring),               ("P",  "P", "")),
    (("emission_angle",         planet_ring),               ("P",  "P", "")),
    (("distance",               planet_ring),               ("P",  "",  "")),
    (("where_inside_shadow",    planet_ring, BODYX),       ("P",  "",  "")),
    (("where_in_front",         planet_ring, BODYX),       ("P",  "",  "")),
    (("where_antisunward",      planet_ring),               ("P",  "",  "")),
    (("ansa_radius",            planet_ansa),               ("P",  "",  "")),
    (("ansa_altitude",          planet_ansa),               ("P",  "",  "")),
    (("ansa_longitude",         planet_ansa, "node"),       ("P",  "",  "")),
    (("ansa_longitude",         planet_ansa, "sha"),        ("P",  "",  "")),
    (("distance",               planet_ansa),               ("P",  "",  "")),
    (("ansa_radial_resolution", planet_ansa),               ("P",  "",  ""))]

# Create a dictionary for the columns of each planet
TEST_DICT = {}
for planet in PLANET_NAMES:
    TEST_DICT[planet]  = replacement_dict(TEST_COLUMNS, BODYX, [planet])
                                                         
################################################################################
