################################################################################
# couvis_supplement.py: Generates all supplemental indices for Cassini UVIS
#
# Usage:
#   python COUVIS_supplement.py .../holdings/volumes/COUVIS/COUVIS_00xx ...
#
# 9/12/12 MRS
################################################################################

import oops
import oops.inst.cassini.uvis as uvis
import numpy as np
import os, sys
import julian

import tol

tol_list = tol.read_tol_file("TOL-as-flown.txt")

############################################
# Method to define prefix text for table
############################################

def volume_and_filespec(root, name):
    """Returns the volume_id and file_specification_name for a UVIS label file.
    """

    ivol = root.rindex("COUVIS_0")
    volume_id = root[ivol:ivol+11]
    dir_path = root[ivol+12:ivol+26]

    if len(dir_path) > ivol + 26:
        raise ValueError("Illegal directory path: ", dir_path)

    file_spec = "%s/%-25s" % (dir_path, name)
    return (volume_id, file_spec)

############################################

def index_one_file(root, name):

    COLUMNS = [
        ("RIGHT_ASCENSION",               1, 10, "%10.6f", None,     -99.),
        ("DECLINATION",                   1, 10, "%10.6f", None,     -99.),
        ("SUB_SOLAR_LATITUDE",            1,  8, "%8.3f",  None,     -99.),
        ("SUB_SOLAR_LONGITUDE",           1,  8, "%8.3f",  None,     -99.),
        ("SUB_SPACECRAFT_LATITUDE",       1,  8, "%8.3f",  None,     -99.),
        ("SUB_SPACECRAFT_LONGITUDE",      1,  8, "%8.3f",  None,     -99.),
        ("PHASE_ANGLE",                   1,  8, "%8.3f",  None,     -99.),
        ("INCIDENCE_ANGLE",               1,  8, "%8.3f",  None,     -99.),
        ("EMISSION_ANGLE",                1,  8, "%8.3f",  None,     -99.),
        ("CENTRAL_BODY_DISTANCE",         1, 12, "%12.3f", "%12.5e", -9.9e99),
        ("SC_PLANET_POSITION_VECTOR",     3, 12, "%12.3f", "%12.5e", -9.9e99),
        ("SC_PLANET_VELOCITY_VECTOR",     3, 12, "%8.3f",  "%8.1e",  -9.9e99),
        ("SC_SUN_POSITION_VECTOR",        3, 12, "%12.3f", "%12.5e", -9.9e99),
        ("SC_SUN_VELOCITY_VECTOR",        3, 12, "%8.3f",  "%8.1e",  -9.9e99),
        ("SC_TARGET_POSITION_VECTOR",     3, 12, "%12.3f", "%12.5e", -9.9e99),
        ("SC_TARGET_VELOCITY_VECTOR",     3, 12, "%8.3f",  "%8.1e",  -9.9e99),
        ("PLANET_CENTER_POSITION_VECTOR", 3, 12, "%12.3f", "%12.5e", -9.9e99),
        ("PLANET_CENTER_VELOCITY_VECTOR", 3, 12, "%8.3f",  "%8.1e",  -9.9e99)]

    (volume_id, file_spec) = volume_and_filespec(root, name)
    prefix = '"%s","%s"' % (volume_id, file_spec)

    # Create the observation object
    obs = uvis.from_file(os.path.join(root,name), enclose=True, data=False)

    supplement.write(prefix)
    supplement.write(',"%-21s"' % obs.dict["PRODUCT_ID"])

    tai = tol.utc_to_tai(obs.dict["START_TIME"])
    activity = tol.find_event(tai, tol_list)
    supplement.write(',"%-30s"' % activity)

    supplement.write(',"%-11s"' % obs.product_type)

    for info in COLUMNS:
        supplement.write("," + format_col(obs.dict[info[0]], *info[1:]))

    if obs.band_window is None: obs.band_window = (-1,0)
    if obs.line_window is None: obs.line_window = (-1,0)

    supplement.write("," + format_col(obs.band_window[0],   1, 4, "%4d", None, -1))
    supplement.write("," + format_col(obs.band_window[1]-1, 1, 4, "%4d", None, -1))
    supplement.write("," + format_col(obs.band_bin,         1, 4, "%4d", None, -1))
    supplement.write("," + format_col(obs.line_window[0],   1, 2, "%2d", None, -1))
    supplement.write("," + format_col(obs.line_window[1]-1, 1, 2, "%2d", None, -1))
    supplement.write("," + format_col(obs.line_bin,         1, 2, "%2d", None, -1))
    supplement.write("," + format_col(obs.samples,          1, 8, "%8d", None, -1))

    yyyy_doy = obs.dict["PRODUCT_CREATION_TIME"]
    year = int(yyyy_doy[:4])
    doy = int(yyyy_doy[-3:])
    day = julian.day_from_yd(year, doy)
    (yyyy, mm, dd) = julian.ymd_from_day(day)
    supplement.write(',"%04d-%02d-%02dT00:00:00"' % (yyyy, mm, dd))

    desc = obs.dict[obs.product_type]["DESCRIPTION"]
    istart = desc.find("The purpose of this observation")
    if istart < 0:
        desc = ""
    else:
        desc = desc[istart:]
        desc = desc.replace("\n        ", " ")
        desc = desc.replace("\n       ", " ")
        desc = desc.replace("\n      ", " ")
        desc = desc.replace("\n     ", " ")
        desc = desc.replace("\n    ", " ")
        desc = desc.replace("\n   ", " ")
        desc = desc.replace("\n  ", " ")
        desc = desc.replace("\n ", " ")
        desc = desc.replace("\n", " ")
        desc = desc.replace("  ", " ")

    if len(desc) > 500:
        print "**** WARNING: DESCRIPTION truncated in " + name
        desc = desc[:500]

    supplement.write(',"%-500s"\r\n' % desc)

def format_col(value, count, width, fmt0, fmt1, nullval):

    if count > 1:
        if type(value) != type([]) and type(value) != type(()):
            assert value in ("N/A", "UNK")
            value = count * ["N/A"]
        else:
            assert len(value) == count

        fmt_list = []
        for item in value:
            result = format_col(item, 1, width, fmt0, fmt1, nullval)
            fmt_list.append(result)

        return ",".join(fmt_list)

    if type(value) == type("") or value is None:
        value = nullval

    result = fmt0 % value
    if len(result) > width:
        if fmt1 is None:
            print "**** WARNING: No second format: ", value, fmt0, result

        result = fmt1 % value
        if len(result) > width:
            print "**** WARNING: Value too wide: ", value, fmt1

    return result

############################################
# Finally, generate the indices...
############################################

input_dir = sys.argv[1]
output_dir = sys.argv[2]

ivol = input_dir.rfind('COUVIS_')
volname = input_dir[ivol:ivol+11]

prefix = os.path.join(output_dir, volname)
data_dir = os.path.join(input_dir, 'DATA')

print prefix + "_supplemental_index.tab"
supplement = open(prefix + "_supplemental_index.tab", "w")

# Walk the directory tree...
for (root, dirs, files) in os.walk(data_dir):
  for name in files:

    # Ignore any file that is not a UVIS label
    if not name.lower().endswith(".lbl"): continue
    if len(name) > 6 and "20" not in name[3:6] and "19" not in name[3:6]:
        continue

    print '    ', root, name
    index_one_file(root, name)

# Close all files
supplement.close()

################################################################################

