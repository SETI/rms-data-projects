# Scrape the necessary fields from the COVIMS_8xxx data label files and
# put them into a new supplemental index.
#
# Usage: python covims.py <profile_index.lbl> <data_dir> <supp_index.lbl>
#

import json
import os
import requests
import sys
from datetime import datetime

import julian
import pdsparser
import pdstable

if len(sys.argv) != 4:
    print('Usage: python covims.py <profile_index.lbl> <vol_root> <supp_index.lbl>')
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
    good_filespec = filespec.replace('DATA', 'data')
    data_label_filename = vol_root + '/' + good_filespec

    data_label = pdstable.PdsTableInfo(data_label_filename).label.as_dict()

    source_products = data_label['SOURCE_PRODUCT_NAME']

    data_quality_score = data_label['DATA_QUALITY_SCORE'].strip()
    lowest_detectable_opacity = data_label['LOWEST_DETECTABLE_OPACITY']
    highest_detectable_opacity = data_label['HIGHEST_DETECTABLE_OPACITY']
    spacecraft_clock_start_count = row['SPACECRAFT_CLOCK_START_COUNT']
    spacecraft_clock_stop_count = row['SPACECRAFT_CLOCK_STOP_COUNT']
    start_time = row['START_TIME']
    stop_time = row['STOP_TIME']

    if spacecraft_clock_stop_count < spacecraft_clock_start_count:
        print(f'{filespec} Spacecraft clock count in wrong order {spacecraft_clock_start_count} {spacecraft_clock_stop_count}')
        spacecraft_clock_start_count, spacecraft_clock_stop_count = (
            spacecraft_clock_stop_count, spacecraft_clock_start_count
        )

    page = []

    our_product_list = []

    for offset in range(0, len(source_products), 50):
        url = 'https://opus.pds-rings.seti.org/__api/dataimages.json'
        params = {'COVIMSchannel': 'IR',
                  'instrument': 'Cassini VIMS',
                  'cols': 'opusid,time1,time2,CASSINIobsname,CASSINIsequenceid,COVIMSirsamplingmode,COVIMSirexposure,COVIMSswathwidth,COVIMSswathlength,COVIMSspectralsumming,COVIMSspectralediting,COVIMSinstrumentmode,COVIMSstartracking',
                  'order': 'time1,opusid',
                  'limit': '100000',
                  'reqno': 1
                 }

        for product_num, product in enumerate(source_products[offset:offset+50]):
            if product.startswith('VYCMAOCC'):
                # XXX See DATA/VIMS_2017_007_VYCMA_E_TAU_01KM.LBL
                continue
            product = product.split('_')[0]
            our_product_list.append(product)
            params['opusid_'+str(product_num+1)] = product

        if len(our_product_list) == 0:
            params['time1'] = start_time
            params['time2'] = stop_time
            print(f'{filespec} Bad SOURCE_PRODUCT_NAME, using time range instead')
            page = [] # Reset and start over

        r = session.get(url, params=params)
        try:
            j = json.loads(r.text)
        except:
            print(f'{filespec} Failed OPUS query:')
            print(r.text)
            continue
        sub_page = j['page']
        page.extend(sub_page)

        if len(our_product_list) == 0:
            break

    if len(page) != len(our_product_list) and len(our_product_list) != 0:
        print(f'{filespec} Not all OPUS IDs found in product source list - expected {len(our_product_list)} got {len(page)}')

    opusid_list = []
    CASSINIobsname_set = set()
    CASSINIsequenceid_set = set()
    COVIMSirsamplingmode_set = set()
    COVIMSirexposure_set = set()
    COVIMSswathwidth_set = set()
    COVIMSswathlength_set = set()
    COVIMSspectralsumming_set = set()
    COVIMSspectralediting_set = set()
    COVIMSinstrumentmode_set = set()
    COVIMSstartracking_set = set()

    for row in page:
        cols = row['metadata']
        opusid = cols[0]
        for i, product in enumerate(our_product_list):
            if product.lower() in opusid:
                del our_product_list[i]
                break
        obsid = cols[3]
        opusid_list.append(cols[0])
        CASSINIobsname_set.add(cols[3])
        if cols[11] != 'OCCULTATION':
            continue
        CASSINIsequenceid_set.add(cols[4])
        COVIMSirsamplingmode_set.add(cols[5])
        COVIMSirexposure_set.add(float(cols[6]))
        COVIMSswathwidth_set.add(int(cols[7]))
        COVIMSswathlength_set.add(int(cols[8]))
        COVIMSspectralsumming_set.add(cols[9])
        COVIMSspectralediting_set.add(cols[10])
        COVIMSinstrumentmode_set.add(cols[11])
        COVIMSstartracking_set.add(cols[12])

    if len(our_product_list):
        print(our_product_list)

    CASSINIobsname_list = sorted(CASSINIobsname_set)
    if len(CASSINIobsname_list) == 1:
        CASSINIobsname = CASSINIobsname_list[0]
    else:
        CASSINIobsname = CASSINIobsname_list[0]
        print(f'{filespec} Multiple observation ids {CASSINIobsname_list} - choosing {CASSINIobsname}')

    CASSINIsequenceid_list = sorted(CASSINIsequenceid_set)
    if len(CASSINIsequenceid_list) == 1:
        CASSINIsequenceid = CASSINIsequenceid_list[0]
    else:
        CASSINIsequenceid = CASSINIsequenceid_list[0]
        print(f'{filespec} Multiple sequence ids {CASSINIsequenceid_list} - choosing {CASSINIsequenceid}')

    COVIMSirsamplingmode_list = sorted(COVIMSirsamplingmode_set)
    if len(COVIMSirsamplingmode_list) == 1:
        COVIMSirsamplingmode = COVIMSirsamplingmode_list[0]
    else:
        COVIMSirsamplingmode = COVIMSirsamplingmode_list[0]
        print(f'{filespec} Multiple sampling modes {COVIMSirsamplingmode_list} - choosing {COVIMSirsamplingmode}')

    COVIMSirexposure_list = sorted(COVIMSirexposure_set)
    if len(COVIMSirexposure_list) == 1:
        COVIMSirexposure = COVIMSirexposure_list[0]
    else:
        COVIMSirexposure = COVIMSirexposure_list[0]
        print(f'{filespec} Multiple exposures {COVIMSirexposure_list} - choosing {COVIMSirexposure}')

    COVIMSswathwidth_list = sorted(COVIMSswathwidth_set)
    if len(COVIMSswathwidth_list) == 1:
        COVIMSswathwidth = COVIMSswathwidth_list[0]
    else:
        COVIMSswathwidth = COVIMSswathwidth_list[0]
        print(f'{filespec} Multiple swath widths {COVIMSswathwidth_list} - choosing {COVIMSswathwidth}')

    COVIMSswathlength_list = sorted(COVIMSswathlength_set)
    if len(COVIMSswathlength_list) == 1:
        COVIMSswathlength = COVIMSswathlength_list[0]
    else:
        COVIMSswathlength = COVIMSswathlength_list[0]
        print(f'{filespec} Multiple swath lengths {COVIMSswathlength_list} - choosing {COVIMSswathlength}')

    COVIMSspectralsumming_list = sorted(COVIMSspectralsumming_set)
    if len(COVIMSspectralsumming_list) == 1:
        COVIMSspectralsumming = COVIMSspectralsumming_list[0]
    else:
        COVIMSspectralsumming = 'Yes'
        print(f'{filespec} Multiple spectral summing {COVIMSspectralsumming_list} - choosing {COVIMSspectralsumming}')
    if COVIMSspectralsumming == 'No':
        COVIMSspectralsumming = 'OFF'
    else:
        COVIMSspectralsumming = 'ON'

    COVIMSspectralediting_list = sorted(COVIMSspectralediting_set)
    if len(COVIMSspectralediting_list) == 1:
        COVIMSspectralediting = COVIMSspectralediting_list[0]
    else:
        COVIMSspectralediting = COVIMSspectralediting_list[0]
        print(f'{filespec} Multiple spectral editing {COVIMSspectralediting_list} - choosing {COVIMSspectralediting}')
    if COVIMSspectralediting == 'No':
        COVIMSspectralediting = 'OFF'
    else:
        COVIMSspectralediting = 'ON'

    COVIMSinstrumentmode_list = sorted(COVIMSinstrumentmode_set)
    if len(COVIMSinstrumentmode_list) == 1:
        COVIMSinstrumentmode = COVIMSinstrumentmode_list[0]
    else:
        COVIMSinstrumentmode = COVIMSinstrumentmode_list[0]
        print(f'{filespec} Multiple instrument modes {COVIMSinstrumentmode_list} - choosing {COVIMSinstrumentmode}')

    COVIMSstartracking_list = sorted(COVIMSstartracking_set)
    if len(COVIMSstartracking_list) == 1:
        COVIMSstartracking = COVIMSstartracking_list[0]
    else:
        COVIMSstartracking = COVIMSstartracking_list[0]
        print(f'{filespec} Multiple star tracking {COVIMSstartracking_list} - choosing {COVIMSstartracking}')

    out_str = ''

    out_str += '"COVIMS_8001",'
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
    out_str += ('"%-6s",' % COVIMSirsamplingmode.upper())
    out_str += ('%10.4f,' % COVIMSirexposure)
    out_str += ('%2d,' % COVIMSswathwidth)
    out_str += ('%2d,' % COVIMSswathlength)
    out_str += ('"%-3s",' % COVIMSspectralsumming)
    out_str += ('"%-3s",' % COVIMSspectralediting)
    out_str += ('"%-20s",' % COVIMSinstrumentmode.upper())
    out_str += ('"%-3s"' % COVIMSstartracking.upper())

    out_str += '\r\n'

    output_fp.write(out_str)

# Note from here on we still use data_label, which is just the label of the
# last label file we read, to get things like the instrument name.

output_fp.close()

instrument_host_name = 'CASSINI ORBITER'
instrument_host_id = 'CO'
instrument_name = 'VISUAL AND INFRARED MAPPING SPECTROMETER'
instrument_id = 'VIMS'

label_template_fp = open('COVIMS_label_template.txt', 'r')
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
