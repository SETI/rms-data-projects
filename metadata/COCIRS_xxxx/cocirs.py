# Scrape the necessary fields from the COCIRS data label files and
# put them into a new supplemental index.
#
# Usage: python cocirs.py <profile_index.lbl> <data_dir> <supp_index.lbl>
#

import os
import sys
from datetime import datetime

import julian
import pdstable
import pdsparser
import re

if len(sys.argv) != 4:
    print('Usage: python cocirs.py <profile_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

profile_index_filename = sys.argv[1]
vol_root = sys.argv[2]
print(vol_root)
supp_index_label_filename = sys.argv[3]
supp_index_tab_filename = supp_index_label_filename.replace('.lbl', '.tab')

# Modify CUBE_EQUI/POINT/RING_INDEX.LBL before passing into PdsTable
lines = pdsparser.PdsLabel.load_file(profile_index_filename)
for i in range(len(lines)):
    if 'CSS:' in lines[i]:
        lines[i] = lines[i].replace('CSS:', '')
profile_index_table = pdstable.PdsTable(profile_index_filename, label_contents=lines)

# profile_index_table = pdstable.PdsTable(profile_index_filename)
profile_rows = profile_index_table.dicts_by_row()
profile_label = profile_index_table.info.label.as_dict()

# tol_fp = open('Final-Cassini-TOL.txt', 'r')
# tol_fp.readline() # Header
#
# tol_list = []
# while True:
#     line = tol_fp.readline().strip()
#     if line == '':
#         break
#     fields = line.split('\t')
#     obs_id = fields[0]
#     if (not obs_id.startswith('RSS') or
#         not obs_id.endswith('PRIME') or
#         not 'OCC' in obs_id):
#         continue
#     start_time = julian.tai_from_iso(fields[3])
#     end_time = julian.tai_from_iso(fields[6])
#     tol_list.append((obs_id, start_time, end_time))
#
# tol_fp.close()
#
# print('TOL entries:', len(tol_list))

output_fp = open(supp_index_tab_filename, 'w')
print('###############')
print(f'profile_index_filename: {profile_index_filename}')
for row in profile_rows:
    filespec = row['FILE_SPECIFICATION_NAME']
    data_label_filename = vol_root + '/' + filespec

    print("$$$$$$$$$")
    print(data_label_filename)
    # Modify labels under DATA/CUBE before passing into PdsTable
    lines = pdsparser.PdsLabel.load_file(data_label_filename)
    obj_li = []
    obj_pattern = r'\s*OBJECT\s+=\s+(\w*)'
    unterminated_end_obj = r'\s*END_OBJECT\s*(^\=)'
    for i in range(len(lines)):
        if 'CSS:' in lines[i]:
            lines[i] = lines[i].replace('CSS:', '')

        # Fix the issue that END_OBJECT is not properly terminated
        if 'END_OBJECT' in lines[i]:
            try:
                current_obj = obj_li.pop()
            except IndexError:
                raise 'Unmatch OBJECT in ' + data_label_filename
            if lines[i].strip() == 'END_OBJECT':
                lines[i] = lines[i] + ' =' + current_obj
        elif 'OBJECT' in lines[i]:
            match = re.match(obj_pattern, lines[i])
            if match is not None:
                    obj_li.append(match[1])

    data_label = pdsparser.PdsLabel.from_string(lines).as_dict()

    # data_table = pdstable.PdsTable(data_label_filename, label_contents=lines)
    # data_label = data_table.info.label.as_dict()

    # data_label = pdstable.PdsTableInfo(data_label_filename).label.as_dict()
    # Use this to avoid checking for INTERCHANGE_FORMAT to be ASCII
    # data_label = pdsparser.PdsLabel.from_file(data_label_filename).as_dict()
    # print("###########")
    # print("row:")
    # print(row)
    # print("vol_root:")
    # print(vol_root)
    # print("filespec:")
    # print(filespec)
    # print("data_label_filename:")
    # print(data_label_filename)
    # print("data_label:")
    # print(data_label)

    # Getting data from *_INDEX.LBL or .LBL files under DATA/CUBE
    volume_id = row['VOLUME_ID'].strip()
    file_spec_name = row['FILE_SPECIFICATION_NAME'].strip()
    product_id = row['PRODUCT_ID'].strip()
    start_time = row['START_TIME'].strip()
    stop_time = row['STOP_TIME'].strip()
    space_clock_start_count = row['SPACECRAFT_CLOCK_START_COUNT'].strip()
    space_clock_stop_count = row['SPACECRAFT_CLOCK_STOP_COUNT'].strip()
    product_creation_time = row['PRODUCT_CREATION_TIME'].strip()

    if 'RING_INDEX' in profile_index_filename:
        # Not in *RING_INDEX.LBL
        right_ascension = 'N/A'
        declination = 'N/A'
        # PRIMARY_SUB_SOLAR_LONGITUDE* in *RING_INDEX.LBL
        min_sub_solar_longitude = row['PRIMARY_SUB_SOLAR_LONGITUDE_BEGINNING'].strip()
        max_sub_solar_longitude = row['PRIMARY_SUB_SOLAR_LONGITUDE_END'].strip()
        # PRIMARY_SUB_SPACECRAFT_LONGITUDE* in *RING_INDEX.LBL
        min_sub_ob_longitude = row['PRIMARY_SUB_SPACECRAFT_LONGITUDE_BEGINNING'].strip()
        max_sub_ob_longitude = row['PRIMARY_SUB_SPACECRAFT_LONGITUDE_END'].strip()
        # Not in *RING_INDEX.LBL
        phase_angle = 'N/A'
        # MEAN_RING_BORESIGHT_EMISSION_ANGLE in *RING_INDEX.LBL
        emission_angle = row['MEAN_RING_BORESIGHT_EMISSION_ANGLE'].strip()
    else:
        right_ascension = row['MEAN_BORESIGHT_RIGHT_ASCENSION'].strip()
        declination = row['MEAN_BORESIGHT_DECLINATION'].strip()
        # BODY_SUB_SOLAR_LONGITUDE* in *EQUI/POINT_INDEX.LBL
        # PRIMARY_SUB_SOLAR_LONGITUDE* in *RING_INDEX.LBL
        min_sub_solar_longitude = row['BODY_SUB_SOLAR_LONGITUDE_BEGINNING'].strip()
        max_sub_solar_longitude = row['BODY_SUB_SOLAR_LONGITUDE_END'].strip()
        # BODY_SUB_SPACECRAFT_LONGITUDE* in *EQUI/POINT_INDEX.LBL
        # PRIMARY_SUB_SPACECRAFT_LONGITUDE* in *RING_INDEX.LBL
        min_sub_ob_longitude = row['BODY_SUB_SPACECRAFT_LONGITUDE_BEGINNING'].strip()
        max_sub_ob_longitude = row['BODY_SUB_SPACECRAFT_LONGITUDE_END'].strip()
        # Not in *RING_INDEX.LBL
        phase_angle = row['MEAN_BODY_PHASE_ANGLE'].strip()
        # MEAN_EMISSION_ANGLE_FOV_AVERAGE in *EQUI/POINT_INDEX.LBL
        # MEAN_RING_BORESIGHT_EMISSION_ANGLE in *RING_INDEX.LBL
        emission_angle = row['MEAN_EMISSION_ANGLE_FOV_AVERAGE'].strip()

    target_name = data_label['TARGET_NAME'].strip()
    mission_phase = data_label['MISSION_PHASE_NAME'].strip()
    min_waveno = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][0]
    max_waveno = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][-1]
    spectrum_size = data_label['SPECTRAL_QUBE']['BAND_BIN']['BANDS']

    # if product_id == '000PH_FP13LTCRV005_CI003_609_F4_038E':
    #     print(row)
    #     print(f'volume_id: {volume_id}')
    #     print(f'file_spec_name: {file_spec_name}')
    #     print(f'product_id: {product_id}')
    #     print(f'start_time: {start_time}')
    #     print(f'stop_time: {stop_time}')
    #     print(f'space_clock_start_count: {space_clock_start_count}')
    #     print(f'space_clock_stop_count: {space_clock_stop_count}')
    #     print(f'product_creation_time: {product_creation_time}')
    #     print(f'right_ascension: {right_ascension}')
    #     print(f'declination: {declination}')
    #     print(f'min_sub_solar_longitude: {min_sub_solar_longitude}')
    #     print(f'max_sub_solar_longitude: {max_sub_solar_longitude}')
    #     print(f'min_sub_ob_longitude: {min_sub_ob_longitude}')
    #     print(row['BODY_SUB_SPACECRAFT_LONGITUDE_BEGINNING'])
    #     print(f'max_sub_ob_longitude: {max_sub_ob_longitude}')
    #     print(row['BODY_SUB_SPACECRAFT_LONGITUDE_END'])
    #     print(f'phase_angle: {phase_angle}')
    #     print(f'emission_angle: {emission_angle}')

    # highest_detectable_opacity = data_label['HIGHEST_DETECTABLE_OPACITY']
    # dsn_station_number = data_label['DSN_STATION_NUMBER']
    # mission_phase_name = data_label['MISSION_PHASE_NAME'].strip()
    # spacecraft_clock_start_count = data_label['SPACECRAFT_CLOCK_START_COUNT'].strip()
    # spacecraft_clock_stop_count = data_label['SPACECRAFT_CLOCK_STOP_COUNT'].strip()
    # spacecraft_event_start_time = data_label['SPACECRAFT_EVENT_START_TIME'].strip()
    # spacecraft_event_stop_time = data_label['SPACECRAFT_EVENT_STOP_TIME'].strip()
    # earth_received_start_time = data_label['EARTH_RECEIVED_START_TIME'].strip()
    # earth_received_stop_time = data_label['EARTH_RECEIVED_STOP_TIME'].strip()
    #
    # instrument_host_name = data_label['INSTRUMENT_HOST_NAME'].strip()
    # instrument_name = data_label['INSTRUMENT_NAME'].strip()
    #
    # start_time = julian.tai_from_iso(spacecraft_event_start_time)
    # stop_time = julian.tai_from_iso(spacecraft_event_stop_time)

    # print(filespec)
    # print(julian.iso_from_tai(start_time), julian.iso_from_tai(stop_time))

    # obs_list = []
    # for obs_id, time1, time2 in tol_list:
    #     if time1 <= stop_time and time2 >= start_time:
    #         obs_list.append(obs_id)
            # print(julian.iso_from_tai(time1), julian.iso_from_tai(time2), obs_id)

    # if len(obs_list) != 1:
    #     obs_list = [x for x in obs_list if 'SA' not in x]
    #
    # if len(obs_list) != 1:
    #     print('Bad observation_ids for', filespec, obs_list)
    #     observation_id = ''
    # else:
    #     observation_id = obs_list[0]

    out_str = ''
    # Get the label from index files
    out_str += ('"%-11s",' % volume_id)
    out_str += ('"%-73s",' % file_spec_name)
    out_str += ('"%-41s",' % product_id)
    out_str += ('"%-19s",' % start_time)
    out_str += ('"%-19s",' % stop_time)
    out_str += ('"%-16s",' % space_clock_start_count)
    out_str += ('"%-16s",' % space_clock_stop_count)
    out_str += ('"%-19s",' % product_creation_time)
    out_str += ('"%-16s",' % right_ascension)
    out_str += ('"%-16s",' % declination)
    out_str += ('"%-16s",' % min_sub_solar_longitude)
    out_str += ('"%-16s",' % max_sub_solar_longitude)
    out_str += ('"%-16s",' % min_sub_ob_longitude)
    out_str += ('"%-16s",' % max_sub_ob_longitude)
    out_str += ('"%-16s",' % phase_angle)
    out_str += ('"%-16s",' % emission_angle)
    # Need to create label for these:
    out_str += ('"%-13s",' % target_name)
    out_str += ('"%-32s",' % mission_phase)
    out_str += ('%6.7f,'   % min_waveno)
    out_str += ('%6.7f,'   % max_waveno)
    out_str += ('%5d'      % spectrum_size)
    out_str += '\r\n'

    output_fp.write(out_str)
output_fp.close()

# Generate the label
label_template_fp = open('COCIRS_label_template.txt', 'r')
label_template = label_template_fp.read()

instrument_host_name = profile_label['SPACECRAFT_NAME'].strip()
instrument_host_id = profile_label['SPACECRAFT_ID'].strip()
instrument_name = profile_label['INSTRUMENT_NAME'].strip()
instrument_id = profile_label['INSTRUMENT_ID'].strip()
# instrument_host_name = data_label['INSTRUMENT_HOST_NAME'].strip()
# instrument_name = data_label['INSTRUMENT_NAME'].strip()

label_template = label_template.replace('$RECORDS$', str(len(profile_rows)))
label_template = label_template.replace(
                        '$TABLE$', os.path.split(supp_index_tab_filename)[1])
now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
label_template = label_template.replace('$VOLUME_ID$', volume_id)
label_template = label_template.replace('$TIME$', now)
label_template = label_template.replace('$INSTHOSTNAME$', instrument_host_name)
label_template = label_template.replace('$INSTHOSTID$', instrument_host_id)
label_template = label_template.replace('$INSTNAME$', instrument_name)
label_template = label_template.replace('$INSTID$', instrument_id)

output_fp = open(supp_index_label_filename, 'w')
output_fp.write(label_template)
output_fp.close()
