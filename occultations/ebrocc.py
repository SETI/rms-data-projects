# Scrape the necessary fields from the EBROCC data label files and
# put them into a new supplemental index.
#
# Usage: python ebrocc.py <profile_index.lbl> <data_dir> <supp_index.lbl>
#

import os
import sys
from datetime import datetime

import julian
import pdstable

if len(sys.argv) != 4:
    print('Usage: python ebrocc.py <profile_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

profile_index_filename = sys.argv[1]
vol_root = sys.argv[2]
print(vol_root)
supp_index_label_filename = sys.argv[3]
supp_index_tab_filename = supp_index_label_filename.replace('.lbl', '.tab')

profile_index_table = pdstable.PdsTable(profile_index_filename)
profile_rows = profile_index_table.dicts_by_row()
profile_label = profile_index_table.info.label.as_dict()

output_fp = open(supp_index_tab_filename, 'w')

inst_host_mapping = {
    'EUROPEAN SOUTHERN OBSERVATORY 1-M TELESCOPE':
        'European Southern Observatory La Sille 1-m Telescope',
    'EUROPEAN SOUTHERN OBSERVATORY 2.2-M TELESCOPE':
        'European Southern Observatory La Sille 2.2-m Telescope',
    'NASA INFRARED TELESCOPE FACILITY':
        'NASA Infrared Telescope Facility',
    'LICK OBSERVATORY ANNA L. NICKEL 1-METER TELESCOPE':
        'Lick Observatory Anna L. Nickel 1-m Telescope',
    'MCDONALD OBSERVATORY 2.7-M HARLAN J. SMITH TELESCOPE':
        'McDonald Observatory 2.7-m Harlan J. Smith Telescope',
    'PALOMAR OBSERVATORY 200-IN HALE TELESCOPE':
        'Palomar Observatory 200-in Hale Telescope'
}

for row in profile_rows:
    filespec = row['FILE_SPECIFICATION_NAME']
    data_label_filename = vol_root + filespec
    data_label = pdstable.PdsTableInfo(data_label_filename).label.as_dict()

    body_occultation_flag = data_label['PLANETARY_OCCULTATION_FLAG'].strip()
    instrument_host_name = data_label['INSTRUMENT_HOST_NAME'].strip()
    instrument_host_name = inst_host_mapping[instrument_host_name]
    instrument_name = data_label['INSTRUMENT_NAME'].strip()
    minimum_ring_radius = data_label['MINIMUM_RING_RADIUS']
    maximum_ring_radius = data_label['MAXIMUM_RING_RADIUS']
    radial_resolution = data_label['RADIAL_RESOLUTION']
    incidence_angle = data_label['INCIDENCE_ANGLE']
    if incidence_angle == 'UNK':
        incidence_angle = 64.627

    out_str = ''

    out_str += '"EBROCC_0001",'
    out_str += ('"%-45s",' % filespec)
    out_str += ('"%1s",' % body_occultation_flag)
    out_str += ("%12.3f," % minimum_ring_radius)
    out_str += ("%12.3f," % maximum_ring_radius)
    out_str += ("%10.5f," % radial_resolution)
    out_str += ("%8.3f," % incidence_angle)
    out_str += ('"%-60s"' % instrument_host_name)
    out_str += '\r\n'

    output_fp.write(out_str)

# Note from here on we still use data_label, which is just the label of the
# last label file we read, to get things like the instrument name.

output_fp.close()

label_template_fp = open('EBROCC_label_template.txt', 'r')
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
