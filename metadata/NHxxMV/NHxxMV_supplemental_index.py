#!/usr/bin/env python
################################################################################
# NHxxMV_supplemental_index.py: Generates supplemental indices for the MVIC
#                               data sets.
#
# Syntax:
#  python NHxxMV_supplemental_index.py path/to/volumes/NHxxMV_xxxx/NHccMV_n00n
################################################################################

import os, sys
import pdsparser

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

    label = pdsparser.PdsLabel.from_file(label_filename).as_dict()

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
    binning_mode = 'N/A'

    target_name = label['TARGET_NAME']
    if target_name[:3] == 'J17':
        target_name = target_name[4:]
    elif target_name[:2] in ('J1', 'J2', 'J6', 'J7'): # Fix Jupiter errors
        target_name = target_name[3:]

    # Strip parenthetical names
    target_name = target_name.partition('(')[0].strip()

    f.write('"%-11s",' % volume_id)
    f.write('"%-52s",' % file_specification_name)
    f.write('"%-30s",' % label['DATA_SET_ID'])
    f.write('"%-27s",' % label['PRODUCT_ID'])
    f.write('"%-3s",'  % label['PRODUCT_TYPE'])
    f.write('"%-48s",' % sequence_id)
    f.write('"%-22s",' % target_name)
    f.write('"%-22s",' % label['MISSION_PHASE_NAME'])
    f.write('"%-19s",' % label['PRODUCT_CREATION_TIME'])
    f.write('"%-23s",' % label['START_TIME'])
    f.write('"%-23s",' % label['STOP_TIME'])
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

    write_value_or_na(f, '%19.7f,', 'SC_TARGET_POSITION_VECTOR' , 0., 0)
    write_value_or_na(f, '%19.7f,', 'SC_TARGET_POSITION_VECTOR' , 0., 1)
    write_value_or_na(f, '%19.7f,', 'SC_TARGET_POSITION_VECTOR' , 0., 2)
    write_value_or_na(f, '%10.6f,', 'SC_TARGET_VELOCITY_VECTOR' , 0., 0)
    write_value_or_na(f, '%10.6f,', 'SC_TARGET_VELOCITY_VECTOR' , 0., 1)
    write_value_or_na(f, '%10.6f,', 'SC_TARGET_VELOCITY_VECTOR' , 0., 2)
    write_value_or_na(f, '%19.7f,', 'TARGET_CENTER_DISTANCE'    , 0.)

    write_value_or_na(f, '%19.7f,', 'TARGET_SUN_POSITION_VECTOR', 0., 0)
    write_value_or_na(f, '%19.7f,', 'TARGET_SUN_POSITION_VECTOR', 0., 1)
    write_value_or_na(f, '%19.7f,', 'TARGET_SUN_POSITION_VECTOR', 0., 2)
    write_value_or_na(f, '%10.6f,', 'TARGET_SUN_VELOCITY_VECTOR', 0., 0)
    write_value_or_na(f, '%10.6f,', 'TARGET_SUN_VELOCITY_VECTOR', 0., 1)
    write_value_or_na(f, '%10.6f,', 'TARGET_SUN_VELOCITY_VECTOR', 0., 2)
    write_value_or_na(f, '%19.7f,', 'SOLAR_DISTANCE'            , 0.)

    write_value_or_na(f, '%19.7f,', 'SC_SUN_POSITION_VECTOR'    , 0., 0)
    write_value_or_na(f, '%19.7f,', 'SC_SUN_POSITION_VECTOR'    , 0., 1)
    write_value_or_na(f, '%19.7f,', 'SC_SUN_POSITION_VECTOR'    , 0., 2)
    write_value_or_na(f, '%10.6f,', 'SC_SUN_VELOCITY_VECTOR'    , 0., 0)
    write_value_or_na(f, '%10.6f,', 'SC_SUN_VELOCITY_VECTOR'    , 0., 1)
    write_value_or_na(f, '%10.6f,', 'SC_SUN_VELOCITY_VECTOR'    , 0., 2)
    write_value_or_na(f, '%19.7f,', 'SPACECRAFT_SOLAR_DISTANCE' , 0.)

    write_value_or_na(f, '%19.7f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 0)
    write_value_or_na(f, '%19.7f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 1)
    write_value_or_na(f, '%19.7f,', 'SC_EARTH_POSITION_VECTOR'  , 0., 2)
    write_value_or_na(f, '%10.6f,', 'SC_EARTH_VELOCITY_VECTOR'  , 0., 0)
    write_value_or_na(f, '%10.6f,', 'SC_EARTH_VELOCITY_VECTOR'  , 0., 1)
    write_value_or_na(f, '%10.6f,', 'SC_EARTH_VELOCITY_VECTOR'  , 0., 2)
    write_value_or_na(f, '%19.7f,', 'SC_GEOCENTRIC_DISTANCE'    , 0.)

    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 0)
    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 1)
    write_value_or_na(f, '%13.10f,', 'QUATERNION', 0., 2)
    write_value_or_na(f, '%13.10f',  'QUATERNION', 0., 3)

    f.write('\r\n')
    return

#### Begin executable code

for arg in sys.argv[1:]:
    arg = os.path.abspath(arg)
    ivolume = arg.rindex('/volumes/NHxxMV_xxxx/NH') + \
                     len('/volumes/NHxxMV_xxxx/')
    volume_id = arg[ivolume:][:11]

    outdir = arg.replace('/volumes/', '/metadata/')
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    outpath = outdir.rstrip('/') + '/' + volume_id + '_supplemental_index.tab'
    f = open(outpath, 'w')

    prev_root = ''
    for (root, dirs, files) in os.walk(os.path.join(arg, 'data')):
        for name in files:
            if not name.upper().endswith('.LBL'): continue

            if prev_root != root:
                print(root)
                prev_root = root

            write_rec(f, os.path.join(root, name), volume_id)

    f.close()
