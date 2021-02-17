# Scrape the necessary fields from the CORSS data label files and
# put them into a new supplemental index.
#
# Usage: python corss.py <profile_index.lbl> <data_dir> <supp_index.lbl>
#

import os
import sys
from datetime import datetime

import julian
import pdstable

if len(sys.argv) != 4:
    print('Usage: python corss.py <profile_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

profile_index_filename = sys.argv[1]
vol_root = sys.argv[2]
print(vol_root)
supp_index_label_filename = sys.argv[3]
supp_index_tab_filename = supp_index_label_filename.replace('.lbl', '.tab')

profile_index_table = pdstable.PdsTable(profile_index_filename)
profile_rows = profile_index_table.dicts_by_row()
profile_label = profile_index_table.info.label.as_dict()

tol_fp = open('Final-Cassini-TOL.txt', 'r')
tol_fp.readline() # Header

tol_list = []
while True:
    line = tol_fp.readline().strip()
    if line == '':
        break
    fields = line.split('\t')
    obs_id = fields[0]
    if (not obs_id.startswith('RSS') or
        not obs_id.endswith('PRIME') or
        not 'OCC' in obs_id):
        continue
    start_time = julian.tai_from_iso(fields[3])
    end_time = julian.tai_from_iso(fields[6])
    tol_list.append((obs_id, start_time, end_time))

tol_fp.close()

print('TOL entries:', len(tol_list))

output_fp = open(supp_index_tab_filename, 'w')

for row in profile_rows:
    filespec = row['FILE_SPECIFICATION_NAME']
    data_label_filename = vol_root + '/' + filespec
    data_label = pdstable.PdsTableInfo(data_label_filename).label.as_dict()

    lowest_detectable_opacity = data_label['LOWEST_DETECTABLE_OPACITY']
    highest_detectable_opacity = data_label['HIGHEST_DETECTABLE_OPACITY']
    dsn_station_number = data_label['DSN_STATION_NUMBER']
    mission_phase_name = data_label['MISSION_PHASE_NAME'].strip()
    spacecraft_clock_start_count = data_label['SPACECRAFT_CLOCK_START_COUNT'].strip()
    spacecraft_clock_stop_count = data_label['SPACECRAFT_CLOCK_STOP_COUNT'].strip()
    spacecraft_event_start_time = data_label['SPACECRAFT_EVENT_START_TIME'].strip()
    spacecraft_event_stop_time = data_label['SPACECRAFT_EVENT_STOP_TIME'].strip()
    earth_received_start_time = data_label['EARTH_RECEIVED_START_TIME'].strip()
    earth_received_stop_time = data_label['EARTH_RECEIVED_STOP_TIME'].strip()

    instrument_host_name = data_label['INSTRUMENT_HOST_NAME'].strip()
    instrument_name = data_label['INSTRUMENT_NAME'].strip()

    start_time = julian.tai_from_iso(spacecraft_event_start_time)
    stop_time = julian.tai_from_iso(spacecraft_event_stop_time)

    # print(filespec)
    # print(julian.iso_from_tai(start_time), julian.iso_from_tai(stop_time))

    obs_list = []
    for obs_id, time1, time2 in tol_list:
        if time1 <= stop_time and time2 >= start_time:
            obs_list.append(obs_id)
            # print(julian.iso_from_tai(time1), julian.iso_from_tai(time2), obs_id)

    if len(obs_list) != 1:
        obs_list = [x for x in obs_list if 'SA' not in x]

    if len(obs_list) != 1:
        print('Bad observation_ids for', filespec, obs_list)
        observation_id = ''
    else:
        observation_id = obs_list[0]

    out_str = ''

    out_str += '"CORSS_8001",'
    out_str += ('"%-90s",' % filespec)
    out_str += ('%10.8f,' % lowest_detectable_opacity)
    out_str += ('%10.8f,' % highest_detectable_opacity)
    out_str += ('%2d,' % dsn_station_number)
    out_str += ('"%-32s",' % mission_phase_name)
    out_str += ('"%-16s",' % spacecraft_clock_start_count)
    out_str += ('"%-16s",' % spacecraft_clock_stop_count)
    out_str += ('"%-21s",' % spacecraft_event_start_time)
    out_str += ('"%-21s",' % spacecraft_event_stop_time)
    out_str += ('"%-21s",' % earth_received_start_time)
    out_str += ('"%-21s",' % earth_received_stop_time)
    out_str += ('"%-32s"' % observation_id)
    out_str += '\r\n'

    output_fp.write(out_str)

# Note from here on we still use data_label, which is just the label of the
# last label file we read, to get things like the instrument name.

output_fp.close()

label_template_fp = open('CORSS_label_template.txt', 'r')
label_template = label_template_fp.read()

label_template = label_template.replace('$RECORDS$', str(len(profile_rows)))
label_template = label_template.replace(
                        '$TABLE$', os.path.split(supp_index_tab_filename)[1])
now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
label_template = label_template.replace('$TIME$', now)
label_template = label_template.replace('$INSTHOSTNAME$', instrument_host_name)
label_template = label_template.replace('$INSTHOSTID$',
                                        data_label['INSTRUMENT_HOST_ID'])
label_template = label_template.replace('$INSTNAME$', instrument_name)
label_template = label_template.replace('$INSTID$',
                                        data_label['INSTRUMENT_ID'])

output_fp = open(supp_index_label_filename, 'w')
output_fp.write(label_template)
output_fp.close()
