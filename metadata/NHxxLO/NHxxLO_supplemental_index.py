#!/usr/bin/env python
################################################################################
# NHxxLO_supplemental_index.py: Generates supplemental indices for the LORRI
#                               data sets.
#
# Syntax:
#  python NHxxLO_supplemental_index.py path/to/volumes/NHxxLO_xxxx/NHccLO_n00n
################################################################################

import os
import pdsparser
import re
import sys

# Matches the mis-valued TARGET_NAME fields
JUPITER_MOON_TARGET = re.compile(r'J\d+ (.*)')

def fix_target(target):

    # Fix Jupiter moon targets
    match = JUPITER_MOON_TARGET.fullmatch(target)
    if match:
        return match.group(1)

    # "M 7" -> "M7"
    if target == 'M 7':
        return 'M7'

    # Missing right paren
    if '(' in target and ')' not in target:
        return target.rstrip() + ')'

    return target


def write_rec(f, label_filename, volume_id):

    def write_value_or_na(f, fmt1, value, na_value, k=None, limits=None):

        try:
            if type(value) == str:
                value = label[value]

                if k is not None:
                    value = value[k]

            if limits is not None:
                if value < limits[0] or value > limits[1]:
                    f.write(fmt1 % na_value)
                    return

            f.write(fmt1 % value)

        except Exception:
            f.write(fmt1 % na_value)

        return

    label = pdsparser.Pds3Label(label_filename)

    cap_filename = label_filename.upper()
    idata = cap_filename.rindex('DATA')
    file_specification_name = label_filename[idata:]

    try:
        sequence_id = label['NEWHORIZONS:SEQUENCE_ID'].strip()  # for Pluto

        icolon = sequence_id.find(':')
        sequence_id = sequence_id[icolon+1:].strip()
    except KeyError:
        sequence_id = label['SEQUENCE_ID'].strip()              # for Jupiter

    telemetry_application_id = label['TELEMETRY_APPLICATION_ID']
    if telemetry_application_id in ['0x633', '0x634', '0x635',
                                    '0x639', '0x63A', '0x63B']:
        binning_mode = '4x4'
    else:
        binning_mode = '1x1'

    f.write('"%-11s",' % volume_id)
    f.write('"%-52s",' % file_specification_name)
    f.write('"%-30s",' % label['DATA_SET_ID'])
    f.write('"%-27s",' % label['PRODUCT_ID'])
    f.write('"%-3s",'  % label['PRODUCT_TYPE'])
    f.write('"%-48s",' % sequence_id)
    f.write('"%-28s",' % fix_target(label['TARGET_NAME']))
    f.write('"%-29s",' % label['MISSION_PHASE_NAME'])
    f.write('"%-19s",' % label['PRODUCT_CREATION_TIME_fmt'])
    f.write('"%-23s",' % label['START_TIME_fmt'])
    f.write('"%-23s",' % label['STOP_TIME_fmt'])
    f.write('"%-16s",' % label['SPACECRAFT_CLOCK_START_COUNT'])
    f.write('"%-16s",' % label['SPACECRAFT_CLOCK_STOP_COUNT'])
    f.write('%1d,'     % label['SPACECRAFT_CLOCK_CNT_PARTITION'])
    f.write('"%-5s",'  % telemetry_application_id)
    f.write('"%-3s",'  % binning_mode)
    f.write('%7.3f,'   % label['EXPOSURE_DURATION'])
    f.write('"%-10s",' % label['INST_CMPRS_TYPE'])

    try:        # Pluto only
      f.write('"%-80s",'  % label['NEWHORIZONS:OBSERVATION_DESC'].strip()[:80])
      if len(label['NEWHORIZONS:OBSERVATION_DESC'].strip()) > 80:
        print('OBSERVATION_DESC overflow in', label['PRODUCT_ID'])
    except KeyError:
      f.write('"%-80s",'  % 'NULL')

    write_value_or_na(f, '%7d,',    'NEWHORIZONS:APPROX_TARGET_LINE'  , -999999,
                                    limits=(-999998,999998))
    write_value_or_na(f, '%7d,',    'NEWHORIZONS:APPROX_TARGET_SAMPLE', -999999,
                                    limits=(-999998,999998))
    write_value_or_na(f, '%10.5f,', 'PHASE_ANGLE'                     , -999.)
    write_value_or_na(f, '%10.5f,', 'SOLAR_ELONGATION'                , -999.)
    write_value_or_na(f, '%10.5f,', 'SUB_SOLAR_LATITUDE'              , -999.)
    write_value_or_na(f, '%10.5f,', 'SUB_SOLAR_LONGITUDE'             , -999.)
    write_value_or_na(f, '%10.5f,', 'SUB_SPACECRAFT_LATITUDE'         , -999.)
    write_value_or_na(f, '%10.5f,', 'SUB_SPACECRAFT_LONGITUDE'        , -999.)
    write_value_or_na(f, '%10.5f,', 'RIGHT_ASCENSION'                 , -999.)
    write_value_or_na(f, '%10.5f,', 'DECLINATION'                     , -999.)
    write_value_or_na(f, '%10.5f,', 'CELESTIAL_NORTH_CLOCK_ANGLE'     , -999.)
    write_value_or_na(f, '%10.5f,', 'BODY_POLE_CLOCK_ANGLE'           , -999.)

    write_value_or_na(f, '%14.2f,', 'SC_TARGET_POSITION_VECTOR' , 0., 0)
    write_value_or_na(f, '%14.2f,', 'SC_TARGET_POSITION_VECTOR' , 0., 1)
    write_value_or_na(f, '%14.2f,', 'SC_TARGET_POSITION_VECTOR' , 0., 2)
    write_value_or_na(f, '%8.4f,' , 'SC_TARGET_VELOCITY_VECTOR' , 0., 0)
    write_value_or_na(f, '%8.4f,' , 'SC_TARGET_VELOCITY_VECTOR' , 0., 1)
    write_value_or_na(f, '%8.4f,' , 'SC_TARGET_VELOCITY_VECTOR' , 0., 2)
    write_value_or_na(f, '%14.2f,', 'TARGET_CENTER_DISTANCE'    , 0.)

    write_value_or_na(f, '%14.2f,', 'TARGET_SUN_POSITION_VECTOR', 0., 0)
    write_value_or_na(f, '%14.2f,', 'TARGET_SUN_POSITION_VECTOR', 0., 1)
    write_value_or_na(f, '%14.2f,', 'TARGET_SUN_POSITION_VECTOR', 0., 2)
    write_value_or_na(f, '%8.4f,' , 'TARGET_SUN_VELOCITY_VECTOR', 0., 0)
    write_value_or_na(f, '%8.4f,' , 'TARGET_SUN_VELOCITY_VECTOR', 0., 1)
    write_value_or_na(f, '%8.4f,' , 'TARGET_SUN_VELOCITY_VECTOR', 0., 2)
    write_value_or_na(f, '%14.2f,', 'SOLAR_DISTANCE'            , 0.)

    write_value_or_na(f, '%14.2f,', 'SC_SUN_POSITION_VECTOR'    , 0., 0)
    write_value_or_na(f, '%14.2f,', 'SC_SUN_POSITION_VECTOR'    , 0., 1)
    write_value_or_na(f, '%14.2f,', 'SC_SUN_POSITION_VECTOR'    , 0., 2)
    write_value_or_na(f, '%8.4f,' , 'SC_SUN_VELOCITY_VECTOR'    , 0., 0)
    write_value_or_na(f, '%8.4f,' , 'SC_SUN_VELOCITY_VECTOR'    , 0., 1)
    write_value_or_na(f, '%8.4f,' , 'SC_SUN_VELOCITY_VECTOR'    , 0., 2)
    write_value_or_na(f, '%14.2f,', 'SPACECRAFT_SOLAR_DISTANCE' , 0.)

    write_value_or_na(f, '%14.2f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 0)
    write_value_or_na(f, '%14.2f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 1)
    write_value_or_na(f, '%14.2f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 2)
    write_value_or_na(f, '%8.4f,' , 'SC_EARTH_VELOCITY_VECTOR'  , 0., 0)
    write_value_or_na(f, '%8.4f,' , 'SC_EARTH_VELOCITY_VECTOR'  , 0., 1)
    write_value_or_na(f, '%8.4f,' , 'SC_EARTH_VELOCITY_VECTOR'  , 0., 2)
    write_value_or_na(f, '%14.2f,', 'SC_GEOCENTRIC_DISTANCE'    , 0.)

    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 0)
    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 1)
    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 2)
    write_value_or_na(f, '%13.10f',  'QUATERNION', 0., 3)

    f.write('\r\n')
    return

#### Begin executable code

for arg in sys.argv[1:]:
    arg = os.path.abspath(arg)
    ivolume = arg.rindex('/volumes/NHxxLO_xxxx/NH') + \
                     len('/volumes/NHxxLO_xxxx/')
    volume_id = arg[ivolume:][:11]

    outdir = arg.replace('/volumes/', '/metadata/')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    outpath = outdir.rstrip('/') + '/' + volume_id + '_supplemental_index.tab'
    f = open(outpath, 'w', encoding='latin-1')

    prev_root = ''
    for (root, dirs, files) in os.walk(os.path.join(arg, 'data')):
        for name in files:
            if not name.upper().endswith('.LBL'):
                continue

            if prev_root != root:
                print(root)
                prev_root = root

            write_rec(f, os.path.join(root, name), volume_id)

    f.close()
