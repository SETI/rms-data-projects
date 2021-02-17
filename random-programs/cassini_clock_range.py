#!/usr/bin/env python
#
# python clock_range.py path_to_volume, ...
#
# Example:
#   python clock_range.py /Volumes/pdsdata/holdings/volumes/COCIRS_0xxx/COCIRS*/DATA/TSDR/

import sys
import os
import re
import datetime

VOLUME_ID_REGEX  = re.compile(r'(?:|.*/)([A-Z]{2}[A-Z0-9]{0,4}_[0-9]{4})(?:|_.*|/.*)\Z')
START_TIME_REGEX = re.compile(r'^START_TIME *= *(?:|")(....-.*T..:..:..[\.0-9]*)(|Z)(|")\s*\Z')
STOP_TIME_REGEX  = re.compile(r'^STOP_TIME *= *(?:|")(....-.*T..:..:..[\.0-9]*)(|Z)(|")\s*\Z')
ALT_TIME_REGEX   = re.compile(r'^IMAGE_TIME *= *(?:|")(....-.*T..:..:..[\.0-9]*)(|Z)(|")\s*\Z')

START_SCLK_REGEX = re.compile(r'^SPACECRAFT_CLOCK_START_COUNT *= *"(?:|[1-9]/)(.*)"\s*\Z')
STOP_SCLK_REGEX  = re.compile(r'^SPACECRAFT_CLOCK_STOP_COUNT *= *"(?:|[1-9]/)(.*)"\s*\Z')
ALT_SCLK_REGEX   = re.compile(r'^SPACECRAFT_CLOCK_COUNT *= *"(?:|[1-9]/)(.*)"\s*\Z')

START_REGEXES = (START_TIME_REGEX, START_SCLK_REGEX)
STOP_REGEXES  = (STOP_TIME_REGEX,  STOP_SCLK_REGEX)
ALT_REGEXES   = (ALT_TIME_REGEX,   ALT_SCLK_REGEX)

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

        if values[-1] == 'UNK':
            values[-1] = None

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

    # Search this directory and all subdirectories
    first = True
    for (root, dirs, files) in os.walk(arg):
        for dir in dirs:
            this_dir = os.path.join(root, dir)
            filenames = os.listdir(this_dir)
            filenames.sort()

            (start_time,
             start_sclk) = get_first_values(this_dir, filenames,
                                    START_REGEXES, STOP_REGEXES, ALT_REGEXES)
            filenames.reverse()
            (stop_time,
             stop_sclk) = get_first_values(this_dir, filenames,
                                    STOP_REGEXES, START_REGEXES, ALT_REGEXES)

            if stop_time is None and start_time is not None:
                stop_time = start_time
            if stop_sclk is None and start_sclk is not None:
                stop_sclk = start_sclk
            if start_time is None and stop_time is not None:
                start_time = stop_time
            if start_sclk is None and stop_sclk is not None:
                start_sclk = stop_sclk

            if first:
                start_time_min = start_time
                start_sclk_min = start_sclk

                stop_time_max = stop_time
                stop_sclk_max = stop_sclk

                first = False

            else:
                if start_time is not None and start_time < start_time_min:
                    start_time_min = start_time

                if stop_time is not None and stop_time > stop_time_max:
                    stop_time_max = stop_time

                if start_sclk is not None and start_sclk < start_sclk_min:
                    start_sclk_min = start_sclk

                if stop_sclk is not None and stop_sclk > stop_sclk_max:
                    stop_sclk_max = stop_sclk

    # Present dates in two formats
    (start_time_ymd_min, start_time_yd_min) = two_datetimes(start_time_min)
    (stop_time_ymd_max,  stop_time_yd_max)  = two_datetimes(stop_time_max)

    inst = volume_id[2:6]
    if inst[-1] == '_': inst = inst[:-1]

    if inst == 'ISS':
        typestr = 'Saturn images'
    elif inst == 'VIMS':
        typestr = 'near IR image cubes'
    else:
        typestr = 'Saturn data'

    start_sclk_min = start_sclk_min.split('/')[-1]
    stop_sclk_max  = stop_sclk_max.split('/')[-1]

    print "    '%sxxx/%s':" % (volume_id[:-3], volume_id),
    print "('Cassini %s %s" % (inst, typestr),
    print start_time_ymd_min[:10] + ' to ' + stop_time_ymd_max[:10],
    print "(SC clock %s-%s)'," % (start_sclk_min[:10], stop_sclk_max[:10]),
    print "'VOLUME'),"

