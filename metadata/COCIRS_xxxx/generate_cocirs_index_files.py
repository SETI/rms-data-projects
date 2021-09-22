# Generate new COCIRS index files from orginal index files by changing all
# string integer and float fields into integer and float, and update the
# corresponding data type in the label.
#
# Usage: python generate_cocirs_index_files.py <original_index.lbl> <vol_root> <supp_index.lbl>
#
# EX: python generate_cocirs_index_files.py /Volumes/pdsdata/COCIRS/Volumes/pdsdata-raid45/holdings/volumes/COCIRS_0xxx/COCIRS_0406/INDEX/CUBE_EQUI_INDEX.LBL /Volumes/pdsdata/COCIRS/Volumes/pdsdata-raid45/holdings/volumes/COCIRS_0xxx/COCIRS_0406 COCIRS_0406_equi_supplemental_index.lbl

import os
import sys
from datetime import datetime

import julian
import pdstable
import pdsparser
import re

# The list of COLUMN_NUMBER that has the data being modified by replacing " with
# space
MOD_COL_LI = []
VOLUME_ID = ''
OLD_DATA_TYPE = "CHARACTER"
NEW_DATA_TYPE = "ASCII_REAL"
EMPTY_SUPPLEMENTAL_INDEX = False

####################################################
# help methods
####################################################
def create_index_tab(original_index_tab, metadata_dir, new_index_tab_filename):
    """Create new tab by changing all int/float string into int/float
    """
    global MOD_COL_LI
    # Get the list of rows in the original tab file
    index_tab_li = original_index_tab.readlines()
    # Modify the list of rows by replacing " with space
    for i1 in range(len(index_tab_li)):
        col_li = []
        new_row = ''
        row = index_tab_li[i1]
        row_li = row.split(",")
        for i2 in range(len(row_li)):
            isInt = True
            isFloat = True
            data = row_li[i2].replace('"', ' ')
            try:
                int(data)
            except ValueError:
                isInt = False

            if isInt:
                row_li[i2] = row_li[i2].replace('"', ' ')
                col_li.append(i2+1)
                continue
            try:
                float(data)
            except ValueError:
                isFloat = False
            if isFloat:
                row_li[i2] = row_li[i2].replace('"', ' ')
                col_li.append(i2+1)
                continue
        index_tab_li[i1] = ",".join(row_li)

        if not MOD_COL_LI:
            MOD_COL_LI = col_li
    # create new index tab file
    output_fp = open(new_index_tab_filename, 'w')
    for row in index_tab_li:
        output_fp.write(row)
    output_fp.close()

def create_index_label(original_index_lbl, metadata_dir, new_index_label_filename):
    """Create new lbl for new tab with int/float data type changed to ASCII_REAL
    """
    global MOD_COL_LI, OLD_DATA_TYPE, NEW_DATA_TYPE
    # Get the label files
    original_lbl_list = original_index_lbl.readlines()
    # Replace "CHARACTER" with "ASCII_REAL" if COLUMN_NUMBER is in the mod_col_li
    new_lbl = open(new_index_label_filename, 'w')
    for i in range(len(original_lbl_list)):
        line = original_lbl_list[i]
        if 'COLUMN_NUMBER' in line and int(line[line.find('=')+1::]) in MOD_COL_LI:
            original_lbl_list[i-1] = original_lbl_list[i-1].replace(OLD_DATA_TYPE, NEW_DATA_TYPE)
    # create new index label file
    for line in original_lbl_list:
        new_lbl.write(line)
    new_lbl.close()

def get_cassini_tol_list():
    tol_fp = open('Final-Cassini-TOL.txt', 'r')
    tol_fp.readline() # Header
    tol_list = []
    while True:
        line = tol_fp.readline().strip()
        if line == '':
            break
        fields = line.split('\t')
        obs_id = fields[0]
        if (not obs_id.startswith('CIRS') or
            not obs_id.endswith('PRIME') or
            'OCC' in obs_id):
            continue
        start_time = julian.tai_from_iso(fields[3])
        end_time = julian.tai_from_iso(fields[6])
        tol_list.append((obs_id, start_time, end_time))

    tol_fp.close()
    return tol_list

def create_supplemental_index_tab(orig_rows, vol_root, supp_index_tab_filename):
    """Create supplemental index tab
    """
    global VOLUME_ID, EMPTY_SUPPLEMENTAL_INDEX

    tol_list = get_cassini_tol_list()
    output_fp = open(supp_index_tab_filename, 'w')

    for row in orig_rows:
        filespec = row['FILE_SPECIFICATION_NAME']
        data_label_filename = vol_root + '/' + filespec

        if not VOLUME_ID:
            VOLUME_ID = row['VOLUME_ID'].strip()

        # Modify labels under DATA/CUBE before passing into PdsTable
        try:
            lines = pdsparser.PdsLabel.load_file(data_label_filename)
        except FileNotFoundError:
            # Print a warning is data label is missing under DATA/
            print(f'****** Warning: missing data label {data_label_filename} ******')
            continue
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
        # Get the data in supplemental index files
        mission_phase = data_label['MISSION_PHASE_NAME'].strip()
        min_waveno = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][0]
        max_waveno = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][-1]
        min_fp_line = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MIN_FOOTPRINT_LINE']
        max_fp_line = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MAX_FOOTPRINT_LINE']
        min_fp_sample = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MIN_FOOTPRINT_SAMPLE']
        max_fp_sample = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MAX_FOOTPRINT_SAMPLE']
        spectrum_size = data_label['SPECTRAL_QUBE']['BAND_BIN']['BANDS']

        focal_plane = data_label['FOCAL_PLANE']
        detector_id = 'FP' + str(focal_plane)


        start_time = julian.tai_from_iso(data_label['START_TIME'])
        stop_time = julian.tai_from_iso(data_label['STOP_TIME'])

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
        # print('========================')
        # print(f'Running data_label_filename: {data_label_filename}')
        # print(f'mission_phase: {mission_phase}')
        # print(f'min_waveno: {min_waveno}')
        # print(f'max_waveno: {max_waveno}')
        # print(f'min_fp_line: {min_fp_line}')
        # print(f'max_fp_line: {max_fp_line}')
        # print(f'min_fp_sample: {min_fp_sample}')
        # print(f'max_fp_sample: {max_fp_sample}')
        # print(f'observation_id: {observation_id}')
        # print(f'detector_id: {detector_id}')
        # print(f'observation_name: {observation_name}')
        # print(f'spectrum_size: {spectrum_size}')

        out_str = ''
        # Need to create label for these:
        out_str += ('"%-32s",' % mission_phase)
        out_str += ('%4d,'   % min_waveno)
        out_str += ('%4d,'   % max_waveno)
        out_str += ('%10.8f,'   % min_fp_line)
        out_str += ('%10.8f,'   % max_fp_line)
        out_str += ('%10.8f,'   % min_fp_sample)
        out_str += ('%10.8f,'   % max_fp_sample)
        out_str += ('"%-3s",'   % detector_id)
        out_str += ('"%-32s",'   % observation_id)
        out_str += ('%5d'      % spectrum_size)
        out_str += '\r\n'

        output_fp.write(out_str)
    output_fp.close()

    if os.path.getsize(supp_index_tab_filename) == 0:
        EMPTY_SUPPLEMENTAL_INDEX = True
        os.remove(supp_index_tab_filename)

def create_supplemental_index_label(
    orig_rows, supp_index_tab_filename, supp_index_label_filename
    ):
    """Create supplemental index label
    """
    global VOLUME_ID, EMPTY_SUPPLEMENTAL_INDEX

    if EMPTY_SUPPLEMENTAL_INDEX:
        EMPTY_SUPPLEMENTAL_INDEX = False
        return
    # Generate the label
    label_template_fp = open('COCIRS_supplemental_label_template.txt', 'r')
    label_template = label_template_fp.read()

    instrument_host_name = orig_label['SPACECRAFT_NAME'].strip()
    instrument_host_id = orig_label['SPACECRAFT_ID'].strip()
    instrument_name = orig_label['INSTRUMENT_NAME'].strip()
    instrument_id = orig_label['INSTRUMENT_ID'].strip()

    label_template = label_template.replace('$RECORDS$', str(len(orig_rows)))
    label_template = label_template.replace(
                            '$TABLE$', os.path.split(supp_index_tab_filename)[1])
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    label_template = label_template.replace('$VOLUME_ID$', VOLUME_ID)
    label_template = label_template.replace('$TIME$', now)
    label_template = label_template.replace('$INSTHOSTNAME$', instrument_host_name)
    label_template = label_template.replace('$INSTHOSTID$', instrument_host_id)
    label_template = label_template.replace('$INSTNAME$', instrument_name)
    label_template = label_template.replace('$INSTID$', instrument_id)

    output_fp = open(supp_index_label_filename, 'w')
    output_fp.write(label_template)
    output_fp.close()

####################################################
# Steps to generate index lbl/tab under /metadata
####################################################
if len(sys.argv) != 4:
    print('Usage: python generate_cocirs_index_files.py <original_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

orig_index_filename = sys.argv[1]
orig_index_tab = orig_index_filename.replace('.LBL', '.TAB')
vol_root = sys.argv[2]
supp_index_label_filename = sys.argv[3]
metadata_dir = vol_root.replace('holdings/volumes', 'holdings/metadata')

# reset the modification list & volume id
MOD_COL_LI = []
VOLUME_ID = ''

try:
    original_index_lbl = open(orig_index_filename, 'r')
    original_index_tab = open(orig_index_tab, 'r')
except FileNotFoundError:
    exit()

if not os.path.exists(metadata_dir):
    os.makedirs(metadata_dir)

if metadata_dir[-1] != '/':
    metadata_dir += '/'
new_index_label_filename = metadata_dir + orig_index_filename[orig_index_filename.rindex('/')+1::]
new_index_tab_filename = new_index_label_filename.replace('.LBL', '.TAB')
supp_index_tab_filename = metadata_dir + supp_index_label_filename.replace('.LBL', '.TAB')
supp_index_label_filename = metadata_dir + supp_index_label_filename

create_index_tab(original_index_tab, metadata_dir, new_index_tab_filename)
create_index_label(original_index_lbl, metadata_dir, new_index_label_filename)

# Modify CUBE_EQUI/POINT/RING_INDEX.LBL before passing into PdsTable
lines = pdsparser.PdsLabel.load_file(orig_index_filename)
for i in range(len(lines)):
    if 'CSS:' in lines[i]:
        lines[i] = lines[i].replace('CSS:', '')
orig_index_table = pdstable.PdsTable(orig_index_filename, label_contents=lines)

# orig_index_table = pdstable.PdsTable(orig_index_filename)
orig_rows = orig_index_table.dicts_by_row()
orig_label = orig_index_table.info.label.as_dict()

create_supplemental_index_tab(orig_rows, vol_root, supp_index_tab_filename)
create_supplemental_index_label(orig_rows, supp_index_tab_filename, supp_index_label_filename)
