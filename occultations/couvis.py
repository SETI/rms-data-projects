# Scrape the necessary fields from the COUVIS_8xxx data label files and
# put them into a new supplemental index.
#
# Usage: python couvis.py <profile_index.lbl> <data_dir> <supp_index.lbl>
#

import csv
import json
import os
import requests
import sys
from datetime import datetime

import julian
import pdsparser
import pdstable

if len(sys.argv) != 4:
    print('Usage: python couvis.py <profile_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

profile_index_filename = sys.argv[1]
vol_root = sys.argv[2]
supp_index_label_filename = sys.argv[3]
supp_index_tab_filename = supp_index_label_filename.replace('.lbl', '.tab')

profile_index_table = pdstable.PdsTable(profile_index_filename)
profile_rows = profile_index_table.dicts_by_row()
profile_label = profile_index_table.info.label.as_dict()

output_fp = open(supp_index_tab_filename, 'w')

session = requests.Session()

for row in profile_rows:
    filespec = row['FILE_SPECIFICATION_NAME']
    clean_filespec = filespec.replace('DATA/', '').replace('.LBL', '')
    good_filespec = filespec.replace('DATA', 'data')
    data_label_filename = vol_root + '/' + good_filespec

    lines = pdsparser.PdsLabel.load_file(data_label_filename)
    lines = [x.replace('00A', '"00A"') for x in lines]

    data_label_info = pdstable.PdsTableInfo(data_label_filename, label_list=lines)
    data_label = data_label_info.label.as_dict()

    direction = row['RING_OCCULTATION_DIRECTION']
    start_time = row['START_TIME']
    stop_time = row['STOP_TIME']

    data_quality_score = data_label['DATA_QUALITY_SCORE'].strip()
    lowest_detectable_opacity = data_label['LOWEST_DETECTABLE_OPACITY']
    highest_detectable_opacity = data_label['HIGHEST_DETECTABLE_OPACITY']
    spacecraft_clock_start_count = data_label['SPACECRAFT_CLOCK_START_COUNT']
    spacecraft_clock_stop_count = data_label['SPACECRAFT_CLOCK_STOP_COUNT']

    if lowest_detectable_opacity > highest_detectable_opacity:
        print(f'{filespec} Opacities are in wrong order {lowest_detectable_opacity} {highest_detectable_opacity}')
        (lowest_detectable_opacity, highest_detectable_opacity) = (highest_detectable_opacity, lowest_detectable_opacity)

    if spacecraft_clock_stop_count < spacecraft_clock_start_count:
        # print(f'{clean_filespec} *** Spacecraft clock count in wrong order {spacecraft_clock_start_count} {spacecraft_clock_stop_count} - swapping')
        spacecraft_clock_start_count, spacecraft_clock_stop_count = (
            spacecraft_clock_stop_count, spacecraft_clock_start_count
        )

    start_time_sec = julian.tai_from_iso(start_time)
    stop_time_sec = julian.tai_from_iso(stop_time)

    if stop_time_sec - start_time_sec > 86400 * 10:
        print(f'{clean_filespec} *** Bad start/stop time {start_time} {stop_time} - looking at data file')
        # start_time_sec = None
        # stop_time_sec = None
        with open(data_label_info.table_file_path, 'r') as tab_fp:
            csv_reader = csv.reader(tab_fp, delimiter=',')
            tab_rows = [[y.strip('"').strip() for y in x] for x in csv_reader]
        tab_start_time_sec = julian.tai_from_tdb(float(tab_rows[0][6]))
        tab_ring_start_time_sec = julian.tai_from_tdb(float(tab_rows[0][7]))
        tab_stop_time_sec = julian.tai_from_tdb(float(tab_rows[-1][6]))
        tab_ring_stop_time_sec = julian.tai_from_tdb(float(tab_rows[-1][7]))
        if tab_start_time_sec > tab_stop_time_sec:
            (tab_start_time_sec, tab_stop_time_sec) = (tab_stop_time_sec, tab_start_time_sec)
        if tab_ring_start_time_sec > tab_ring_stop_time_sec:
            (tab_ring_start_time_sec, tab_ring_stop_time_sec) = (tab_ring_stop_time_sec, tab_ring_start_time_sec)
        # if abs(start_time_sec - tab_start_time_sec) > 1:
        #     print(f'{clean_filespec} START_TIME and data start time differ too much {start_time_sec} {tab_start_time_sec}')
        # else:
        start_time_sec = tab_start_time_sec
        stop_time_sec = tab_stop_time_sec
        start_time = julian.iso_from_tai(start_time_sec, ymd=False, digits=3)
        stop_time = julian.iso_from_tai(stop_time_sec, ymd=False, digits=3)
        print(f'{clean_filespec} *** Substituting START_TIME {start_time} STOP_TIME {stop_time} from data file')

    # Because some start/time stops are incorrect in the index, we use SCLK
    # to search on instead in those cases. Because the HSP stop times are wrong
    # in OPUS, we pad them by 2 days. But we first try without padding, because
    # if the ingress and egress occultations are separate observations, we'll
    # find them this way.
    for padding in (0, 2*86400):
        url = 'https://opus.pds-rings.seti.org/__api/dataimages.json'
        params = {'COUVISchannel': 'HSP',
                  'instrument': 'Cassini UVIS',
                  'qtype-time': 'any',
                  'cols': 'opusid,time1,time2,CASSINIobsname,COUVIScompressiontype,COUVISintegrationduration,CASSINIsequenceid,COUVISsamples',
                  'order': 'time1,opusid',
                  'limit': '100000',
                  'reqno': 1
                 }

        if start_time_sec is None:
            new_scc1 = float(spacecraft_clock_start_count.replace('1/', '')) - padding
            new_scc2 = float(spacecraft_clock_stop_count.replace('1/', ''))
            params['CASSINIspacecraftclockcount1'] = '%.3f'%new_scc1
            params['CASSINIspacecraftclockcount2'] = '%.3f'%new_scc2
        else:
            params['time1'] = julian.iso_from_tai(start_time_sec-padding, digits=3)
            params['time2'] = julian.iso_from_tai(stop_time_sec, digits=3)

        r = session.get(url, params=params)
        try:
            j = json.loads(r.text)
        except:
            print(f'{clean_filespec} *** Bad search return:\n{r.text}')
            continue
        page = j['page']

        star = filespec.split('_')[4]
        if star == 'SAO205839':
            new_star = '205839'
        elif star == '3CEN':
            new_star = star
        else:
            new_star = ''
            for c in star:
                if not c.isdigit():
                    new_star += c

        opus_start_time_sec = None
        opus_stop_time_sec = None
        opusid_list = []
        CASSINIobsname_set = set()
        COUVIScompressiontype_set = set()
        COUVISintegrationduration_set = set()
        CASSINIsequenceid_set = set()

        for row in page:
            cols = row['metadata']
            obsid = cols[3]
            if new_star == '205839' or new_star == '3CEN':
                new_obsid = obsid
            else:
                new_obsid = ''
                for c in obsid:
                    if not c.isdigit():
                        new_obsid += c
            if new_star not in new_obsid and new_obsid != 'UNK':
                continue

            if opus_start_time_sec is None:
                opus_start_time_sec = julian.tai_from_iso(cols[1])
            # Adjust for bad stop time field in OPUS
            opus_stop_time_sec = opus_start_time_sec + float(cols[5])*float(cols[7])/1000

            opusid_list.append(cols[0])
            CASSINIobsname_set.add(cols[3])
            COUVIScompressiontype_set.add(cols[4])
            COUVISintegrationduration_set.add(float(cols[5]))
            CASSINIsequenceid_set.add(cols[6])

        if len(opusid_list) == 0:
            continue # Try with padding, or exit

        # print(f'{filespec} {opusid_list}')
        # We found at least one good observation
        CASSINIobsname_list = sorted(CASSINIobsname_set)
        if len(CASSINIobsname_list) == 0:
            CASSINIobsname = 'UNK'
        elif len(CASSINIobsname_list) == 1:
            CASSINIobsname = CASSINIobsname_list[0]
        elif len(CASSINIobsname_list) > 1:
            if len(CASSINIobsname_list) == 2:
                if direction == 'I':
                    CASSINIobsname = CASSINIobsname_list[0]
                else:
                    CASSINIobsname = CASSINIobsname_list[1]
            else:
                CASSINIobsname = CASSINIobsname_list[0]
            print(f'{clean_filespec} *** Multiple observation ids {CASSINIobsname_list} - choosing {CASSINIobsname}')

        COUVIScompressiontype_list = sorted(COUVIScompressiontype_set)
        if len(COUVIScompressiontype_list) == 0:
            COUVIScompressiontype = 'NONE'
        elif len(COUVIScompressiontype_list) == 1:
            COUVIScompressiontype = COUVIScompressiontype_list[0].upper()
        elif len(COUVIScompressiontype_list) > 1:
            old_COUVIScompressiontype_list = COUVIScompressiontype_list[:]
            if 'None' in COUVIScompressiontype_list:
                del COUVIScompressiontype_list[COUVIScompressiontype_list.index('None')]
            COUVIScompressiontype = COUVIScompressiontype_list[0].upper()
            print(f'{clean_filespec} *** Multiple compression types {old_COUVIScompressiontype_list} - choosing {COUVIScompressiontype}')

        COUVISintegrationduration_list = sorted(COUVISintegrationduration_set)
        if len(COUVISintegrationduration_list) == 0:
            COUVISintegrationduration = 0.
        elif len(COUVISintegrationduration_list) == 1:
            COUVISintegrationduration = COUVISintegrationduration_list[0]
        elif len(COUVISintegrationduration_list) > 1:
            COUVISintegrationduration = COUVISintegrationduration_list[0]
            print(f'{clean_filespec} *** Multiple integration durations {COUVISintegrationduration_list} - choosing {COUVISintegrationduration}')

        CASSINIsequenceid_list = sorted(CASSINIsequenceid_set)
        if len(CASSINIsequenceid_list) == 0:
            CASSINIsequenceid = 'N/A'
        elif len(CASSINIsequenceid_list) == 1:
            CASSINIsequenceid = CASSINIsequenceid_list[0]
        elif len(CASSINIsequenceid_list) > 1:
            CASSINIsequenceid = CASSINIsequenceid_list[0]
            print(f'{clean_filespec} *** Multiple sequence ids {CASSINIsequenceid_list} - choosing {CASSINIsequenceid}')

        break

    if len(opusid_list) == 0:
        print(f'{clean_filespec} *** Never found a valid observation {start_time} {stop_time}')
    else:
        print(f'{clean_filespec:34} {start_time} {stop_time} {CASSINIobsname:32} {padding==0}')

    out_str = ''

    out_str += '"COUVIS_8001",'
    out_str += ('"%-50s",' % filespec)
    out_str += ('"%-21s",' % start_time)
    out_str += ('"%-21s",' % stop_time)
    out_str += ('"%-16s",' % spacecraft_clock_start_count)
    out_str += ('"%-16s",' % spacecraft_clock_stop_count)
    out_str += ('%10.6f,' % lowest_detectable_opacity)
    out_str += ('%10.6f,' % highest_detectable_opacity)
    out_str += ('"%-8s",' % data_quality_score)
    out_str += ('"%-32s",' % CASSINIobsname)
    out_str += ('"%-8s",' % CASSINIsequenceid)
    out_str += ('"%-6s",' % COUVIScompressiontype)
    out_str += ('%10.4f' % COUVISintegrationduration)

    out_str += '\r\n'

    output_fp.write(out_str)

# Note from here on we still use data_label, which is just the label of the
# last label file we read, to get things like the instrument name.

output_fp.close()

instrument_host_name = 'CASSINI ORBITER'
instrument_host_id = 'CO'
instrument_name = 'ULTRAVIOLET IMAGING SPECTROGRAPH'
instrument_id = 'UVIS'

label_template_fp = open('COUVIS_label_template.txt', 'r')
label_template = label_template_fp.read()

label_template = label_template.replace('$RECORDS$', str(len(profile_rows)))
label_template = label_template.replace(
                        '$TABLE$', os.path.split(supp_index_tab_filename)[1])
now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
label_template = label_template.replace('$TIME$', now)
label_template = label_template.replace('$INSTHOSTNAME$', instrument_host_name)
label_template = label_template.replace('$INSTHOSTID$', instrument_host_id)
label_template = label_template.replace('$INSTNAME$', instrument_name)
label_template = label_template.replace('$INSTID$', instrument_id)

output_fp = open(supp_index_label_filename, 'w')
output_fp.write(label_template)
output_fp.close()
