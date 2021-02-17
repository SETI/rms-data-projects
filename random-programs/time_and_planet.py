#!/usr/bin/env python
################################################################################
# python time_and_planet.py path_to_volume ...
#
# Example:
#   python time_and_planet.py <path>HSTJ0_9725 ...
################################################################################

import sys
import os
import re
import datetime

VOLUME_ID_REGEX  = re.compile(r'(?:|.*/)([A-Z]{2}[A-Z0-9]{0,4}_[0-9]{4})(?:|_.*|/.*)\Z')
START_TIME_REGEX = re.compile(r'^START_TIME *= *(?:|")(....-.*T..:..:..[\.0-9]*)(|Z)(|")\s*\Z')
STOP_TIME_REGEX  = re.compile(r'^STOP_TIME *= *(?:|")(....-.*T..:..:..[\.0-9]*)(|Z)(|")\s*\Z')
PLANET_REGEX     = re.compile(r"^PLANET_NAME *= *'(.*)'\s*\Z")
PI_REGEX         = re.compile(r"^HST_PI_NAME *= *'(.*)'\s*\Z")

START_REGEXES = (START_TIME_REGEX, PLANET_REGEX, PI_REGEX)
STOP_REGEXES  = (STOP_TIME_REGEX, PLANET_REGEX, PI_REGEX)
ALT_REGEXES   = (STOP_TIME_REGEX, PLANET_REGEX, PI_REGEX)


# The arg should point to directory on a single volume containing (recursively)
# all the data files 

def get_first_values(dirpath, filenames, regexes, alt_regexes, alt2_regexes):
    """Return the values found in the first label file of a directory.
    Filenames must be provided in the order to be searched."""

    for filename in filenames:
        if not filename.upper().endswith('.LBL'): continue

        first_values = get_label_values(os.path.join(dirpath, filename),
                                        regexes, alt_regexes, alt2_regexes)
        if None not in first_values: return first_values

    return len(regexes) * (None,)

def get_label_values(filepath, regexes, alt_regexes, alt2_regexes):
    """Return a list of values found in a label file, based on a list of
    regular expressions.
    """

    f = open(filepath)
    recs = f.readlines()
    f.close()

    number_of_values = len(regexes)
    values = number_of_values * [None]

    for k in range(number_of_values):
        regex = regexes[k]
        for rec in recs:
            (value, count) = regex.subn(r'\1', rec)
            if count == 1:
                values[k] = value
                break

        regex = alt_regexes[k]
        for rec in recs:
            (value, count) = regex.subn(r'\1', rec)
            if count == 1:
                values[k] = value
                break

        regex = alt2_regexes[k]
        for rec in recs:
            (value, count) = regex.subn(r'\1', rec)
            if count == 1:
                values[k] = value
                break

    return values

def two_datetimes(date):
    """Returns times in both y-m-d and y-d formats."""

    try:
        year = int(date[:4])
        doy = int(date[5:8])
        dt = datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1)
        date_ymd = dt.strftime('%Y-%m-%d') + start_time_min[8:]
        date_yd = date
        return (date_ymd, date_yd)
    except ValueError:
        pass

    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:10])
    dt = datetime.datetime(year, month, day)
    date_yd = dt.strftime('%Y-%j') + date[10:]
    date_ymd = date
    return (date_ymd, date_yd)

for arg in sys.argv[1:]:

    if not os.path.exists(arg):
        print 'Error: Not found:' + arg
        continue

    # Extract the volume ID from the path. Skip if not found.
    (volume_id, count) = VOLUME_ID_REGEX.subn(r'\1', arg)
    if count == 0:
        print 'Error: Volume ID not found in ' + arg
        continue

    # Initialize
    start_time_min = '9999'
    stop_time_max  = '0000'
    planet_min = '~'
    planet_max = ' '
    pi_min = '~'
    pi_max = ' '

    # Search this directory and all subdirectories
    for (root, dirs, files) in os.walk(arg):
        for dir in dirs:
            this_dir = os.path.join(root, dir)
            filenames = os.listdir(this_dir)
            filenames.sort()
            (start_time,
             planet_name, pi_name) = get_first_values(this_dir, filenames,
                                    START_REGEXES, STOP_REGEXES, ALT_REGEXES)
            filenames.reverse()
            (stop_time,
             planet_name, pi_name) = get_first_values(this_dir, filenames,
                                    STOP_REGEXES, START_REGEXES, ALT_REGEXES)

            if start_time is not None and start_time < start_time_min:
                start_time_min = start_time

            if stop_time is not None and stop_time > stop_time_max:
                stop_time_max = stop_time

            if planet_name is not None and planet_name < planet_min:
                planet_min = planet_name

            if planet_name is not None and planet_name > planet_max:
                planet_max = planet_name

            if pi_name is not None and pi_name < pi_min:
                pi_min = pi_name

            if pi_name is not None and pi_name > pi_max:
                pi_max = pi_name

    # Present dates in two formats
    (start_time_ymd_min, start_time_yd_min) = two_datetimes(start_time_min)
    (stop_time_ymd_max,  stop_time_yd_max)  = two_datetimes(stop_time_max)

    print volume_id,
    print start_time_ymd_min, stop_time_ymd_max,
    print start_time_yd_min, stop_time_yd_max,
    if planet_min != planet_max:
        print planet_min, planet_max
    else:
        print planet_max
                                                 
