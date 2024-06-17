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
import numpy as np
import pdstable
import pdsparser
import re

# The list of COLUMN_NUMBER that has the data being modified by replacing " with
# space
MOD_COL_LI = []
VOLUME_ID = ''
INDEX_TAB = ''
OLD_DATA_TYPE = "CHARACTER"
NEW_DATA_TYPE = ("ASCII_REAL", "ASCII_INTEGER")
EMPTY_SUPPLEMENTAL_INDEX = False

CORRECT_EQUI_POINT_WIDTHS = {
    18: 14,     # CSS:BODY_SUB_SOLAR_LATITUDE_BEGINNING
    19: 14,     # CSS:BODY_SUB_SOLAR_LATITUDE_MIDDLE
    20: 14,     # CSS:BODY_SUB_SOLAR_LATITUDE_END
    21: 16,     # CSS:BODY_SUB_SOLAR_LATITUDE_PC_BEGINNING
    22: 16,     # CSS:BODY_SUB_SOLAR_LATITUDE_PC_MIDDLE
    23: 16,     # CSS:BODY_SUB_SOLAR_LATITUDE_PC_END
    27: 14,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_BEGINNING
    28: 14,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_MIDDLE
    29: 14,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_END
    30: 16,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_PC_BEGINNING
    31: 16,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_PC_MIDDLE
    32: 16,     # CSS:BODY_SUB_SPACECRAFT_LATITUDE_PC_END
    37: 14,     # CSS:MEAN_BORESIGHT_LATITUDE_ZPD
    38: 16,     # CSS:MEAN_BORESIGHT_LATITUDE_ZPD_PC
}

BODY_DIMENSIONS = {
    "MIMAS"     : ( 207.4,  196.8,  190.6),
    "ENCELADUS" : ( 256.6,  251.4,  248.3),
    "TETHYS"    : ( 540.4,  531.1,  527.5),
    "DIONE"     : ( 563.8,  561. ,  560.3),
    "RHEA"      : ( 767.2,  762.5,  763.1),
    "TITAN"     : (2575. , 2575. , 2575. ),
    "HYPERION"  : ( 164. ,  130. ,  107. ),
    "IAPETUS"   : ( 747.4,  747.4,  712.4),
    "PHOEBE"    : ( 115. ,  110. ,  105. ),
    "JANUS"     : (  96.6,   86.6,   68.6),
    "EPIMETHEUS": (  67.4,   54.2,   52.3),
    "HELENE"    : (  16. ,   16. ,   16. ),
    "TELESTO"   : (  14.6,   11.1,   10.2),
    "CALYPSO"   : (  15.1,   11.4,    7. ),
    "PANDORA"   : (  51.5,   39.8,   32. ),
    "PALLENE"   : (  10. ,   10. ,   10. ),
    "POLYDEUCES": (  10. ,   10. ,   10. ),
    "SATURN"    : (60268., 60268., 54364.),
}

GRAPHIC_COLUMNS = { # maps graphic latitude column to centric latitude column
    18: 22,
    19: 23,
    20: 24,
    27: 30,
    28: 31,
    29: 32,
    37: 38,
}

CENTRIC_COLUMNS = {v:k for k,v in GRAPHIC_COLUMNS.items()}

####################################################
# help methods
####################################################
def create_index_tab(original_index_tab, metadata_dir, new_index_tab_path):
    """Create new tab by changing all int/float string into int/float
    """
    global MOD_COL_LI, CORRECT_EQUI_POINT_WIDTHS
    # Get the list of rows in the original tab file
    index_tab_li = original_index_tab.readlines()
    # Modify the list of rows by replacing " with space
    for i1 in range(len(index_tab_li)):
        col_li = []
        new_row = ''
        row = index_tab_li[i1]
        row_li = row.split(",")
        target = row_li[10].strip('"').rstrip(' ')

        if 'ring_index' not in new_index_tab_path:
            # Remove the surrounding quotes, fixes the column width, and then puts
            # the quotes back, this only applies to EQUI/POINT
            for w in CORRECT_EQUI_POINT_WIDTHS:
                width = CORRECT_EQUI_POINT_WIDTHS[w]
                data = row_li[w].strip('"').rstrip(' ')
                if len(data) < width:
                    data = '"' + data + (width - len(data)) * ' ' + '"'
                assert len(data) == width + 2, f'Value is too wide: {data}, {i1}, {w}'
                row_li[w] = data

            # If planetographic is N/A, we convert it from planetocentric
            for idx in GRAPHIC_COLUMNS:
                if 'N/A' in row_li[idx]:
                    width = len(row_li[idx].strip('"'))
                    centric_value = float(row_li[GRAPHIC_COLUMNS[idx]].strip('"'))
                    graphic_value = graphic_from_centric(centric_value, target)
                    row_li[idx] = '"' + ('%8.4f' % graphic_value).ljust(width) + '"'
            # If planetocentric is N/A, we convert it from planetographic
            for idx in CENTRIC_COLUMNS:
                if 'N/A' in row_li[idx]:
                    width = len(row_li[idx].strip('"'))
                    graphic_value = float(row_li[CENTRIC_COLUMNS[idx]].strip('"'))
                    centric_value = centric_from_graphic(graphic_value, target)
                    row_li[idx] = '"' + ('%8.4f' % centric_value).ljust(width) + '"'

        for i2 in range(len(row_li)):
            # In RING_INDEX, change target name "SATURN_RINGS" to "S_RINGS     "
            if i2 == 10 and 'ring_index' in new_index_tab_path:
                row_li[i2] = row_li[i2].replace("SATURN_RINGS", "S_RINGS     ")
                continue

            # Handling N/A in CSS:* columns
            if 'N/A' in row_li[i2]:
                new_val = row_li[i2].replace('"', ' ')
                row_li[i2] = new_val.replace('N/A  ', '-200.')
                continue

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
    output_fp = open(new_index_tab_path, 'w')
    for row in index_tab_li:
        row = row.replace('\n', '\r\n')
        output_fp.write(row)
    output_fp.close()

def create_index_label(
    original_index_lbl, metadata_dir, new_index_label_path, new_index_tab_name
):
    """Create new lbl for new tab with int/float data type changed to ASCII_REAL
    """
    global MOD_COL_LI, OLD_DATA_TYPE, NEW_DATA_TYPE, INDEX_TAB
    # Get the label files
    original_lbl_list = original_index_lbl.readlines()
    # 1. Change data type to "ASCII_REAL" if COLUMN_NUMBER is in the mod_col_li
    # 2. Change data type to "ASCII_INTERGER" for SCET_START/SCET_END/FOCAL_PLANE
    # 3. If it's CSS: columns, change data type to "ASCII_REAL" & add a new line
    # "NOT_APPLICABLE_CONSTANT= -200." Also put quotes around the NAME value.
    new_lbl = open(new_index_label_path, 'w')
    i = 0
    while i < len(original_lbl_list):
        line = original_lbl_list[i]
        if INDEX_TAB in line:
            original_lbl_list[i] = original_lbl_list[i].replace(INDEX_TAB, new_index_tab_name)
        elif ('SCET_START' in line or
              'SCET_END' in line or
              'FOCAL_PLANE' in line):
            original_lbl_list[i+1] = original_lbl_list[i+1].replace(OLD_DATA_TYPE, NEW_DATA_TYPE[1])
        elif 'CSS:' in line:
            line = line.replace('CSS:','"CSS:').rstrip() + '"\n'    # put quotes around NAME
            original_lbl_list[i] = line
            original_lbl_list[i+1] = (original_lbl_list[i+1].replace(OLD_DATA_TYPE, NEW_DATA_TYPE[0])
                        + '    NOT_APPLICABLE_CONSTANT= -200.\n')   # \n converted to \r\n below!
        i += 1

    # create new index label file
    for line in original_lbl_list:
        # Make sure each line in the label is separated by \r\n
        line = line.replace('\n', '\r\n')
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
        if not obs_id.startswith('CIRS') or obs_id.endswith('_SI'):
            continue
        start_time = julian.tai_from_iso(fields[3])
        end_time = julian.tai_from_iso(fields[6])
        tol_list.append((obs_id, start_time, end_time))

    tol_fp.close()
    return tol_list

def get_cirs_obs_id(filespec, start_time, stop_time, tol_list):
    """Return the observation id
    """
    basename = os.path.basename(filespec)
    parts = basename.split('_')
    parts = [p for p in parts if p]     # omit empty entries due to repeated "_"
    pattern = ('CIRS_' + parts[0] + '_' + parts[1] + '_' +
               ('PRIME' if parts[2][:2] == 'CI' else parts[2][:2]))
    # python 3.8
    # pattern = ('CIRS_' + parts[0] + '_' + parts[1] + '_' +
    #            ('PRIME' if (p := parts[2][:2]) == 'CI' else p))

    # TOL does not include events before mid-May 2004. They all have a simple
    # form, "CIRS_C4xSA_something_ISS". This is consistent with the pattern,
    # except that the pattern ends with "_IS" instead of "_ISS".
    if basename.startswith('C4'):
        obs_id = pattern + 'S'
        print('Early activity name', obs_id)
        return obs_id

    obs_by_time = []
    obs_by_name = []
    for obs_id, time1, time2 in tol_list:
        if time1 <= stop_time and time2 >= start_time:
            obs_by_time.append(obs_id)
        if obs_id.startswith(pattern):
            obs_by_name.append(obs_id)

    best_match = list(set(obs_by_time).intersection(set(obs_by_name)))
    if len(best_match) == 1:
        return best_match[0]

    if len(best_match) > 1:
        best_match.sort()
        print('Ambiguous observation_id', filespec,
              'ID used:', best_match[0], 'ignored:', best_match[1:])
        return best_match[0]

    if len(obs_by_time) == 1:
        if len(obs_by_name) == 1:
            print('Time falls within observation with a different ID:',
                  filespec, 'ID used:', obs_by_name[0], 'ignored:', obs_by_time[0])
            return obs_by_name[0]

        if len(obs_by_name) == 0:
            print('Name does not match a known ID; timing used for match:',
                  filespec, 'ID used:', obs_by_time[0])
            return obs_by_time[0]

        print('Name is ambiguous; timing used for match:',
              filespec, 'ID used:', obs_by_time[0], 'ignored:', obs_by_name)
        return obs_by_time[0]

    if len(obs_by_time) == 0:
        if len(obs_by_name) == 1:
            print('No timing match; name used for ID:',
                  filespec, 'ID used:', obs_by_name[0])
            return obs_by_name[0]

        if len(obs_by_name) == 0:
            print('No timing or name match:', filespec)
            return ''

        print('No timing match; multiple IDs match name',
              filespec, 'ID used:', obs_by_name[0], 'ignored:', obs_by_name[1:])
        return obs_by_name[0]

    # ... at this point, multiple IDs match the observation time ...

    if len(obs_by_name) == 1:
        print('Timing is ambiguous; name used to match ID:',
              filespec, 'ID used:', obs_by_name[0], 'ignored:', obs_by_time)
        return obs_by_name[0]

    if len(obs_by_name) == 0:
        print('Timing is ambiguous; no name matches ID:',
              filespec, 'ID used:', obs_by_time[0], 'ignored:', obs_by_time[1:])
        return obs_by_time[0]

    print('Name and timing are both ambigous and disjoint',
          filespec, 'ID used:', obs_by_time[0], 'ignored:', obs_by_time[1:],
          obs_by_name)
    return obs_by_time[0]

def create_supplemental_index_tab(orig_rows, vol_root, supp_index_tab_path):
    """Create supplemental index tab
    """
    global EMPTY_SUPPLEMENTAL_INDEX, VOLUME_ID

    tol_list = get_cassini_tol_list()
    output_fp = open(supp_index_tab_path, 'w')

    for row in orig_rows:
        filespec = row['FILE_SPECIFICATION_NAME']
        data_label_filename = vol_root + '/' + filespec

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
        focal_plane = data_label['FOCAL_PLANE']
        core_items = data_label['SPECTRAL_QUBE']['CORE']['CORE_ITEMS']
        band_bin_width = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_WIDTH']
        min_band_bin_center = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][0]
        max_band_bin_center = data_label['SPECTRAL_QUBE']['BAND_BIN']['BAND_BIN_CENTER'][-1]
        min_waveno = (min_band_bin_center) - band_bin_width/2
        max_waveno = (min_band_bin_center) + band_bin_width/2
        data_count = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['DATA_COUNT']
        min_fp_line = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MIN_FOOTPRINT_LINE']
        max_fp_line = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MAX_FOOTPRINT_LINE']
        min_fp_sample = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MIN_FOOTPRINT_SAMPLE']
        max_fp_sample = data_label['SPECTRAL_QUBE']['IMAGE_MAP_PROJECTION']['MAX_FOOTPRINT_SAMPLE']
        spectrum_size = data_label['SPECTRAL_QUBE']['BAND_BIN']['BANDS']
        backplanes = data_label['SPECTRAL_QUBE']['SUFFIX']['SUFFIX_ITEMS'][-1]

        start_time = julian.tai_from_iso(data_label['START_TIME'])
        stop_time = julian.tai_from_iso(data_label['STOP_TIME'])
        observation_id = get_cirs_obs_id(filespec, start_time, stop_time, tol_list)

        # For debugging purpose:
        # print('========================')
        # print(f'Running data_label_filename: {data_label_filename}')
        # print(f'VOLUME_ID: {VOLUME_ID}')
        # print(f'filespec.ljust(73): {filespec.ljust(73)}')
        # print(f'mission_phase.ljust(25): {mission_phase.ljust(25)}')
        # print(f'focal_plane: {focal_plane}')
        # print(f'core_items[1]: {core_items[1]}')
        # print(f'core_items[0]: {core_items[0]}')
        # print(f'min_waveno: {min_waveno}')
        # print(f'max_waveno: {max_waveno}')
        # print(f'band_bin_width: {band_bin_width}')
        # print(f'spectrum_size: {spectrum_size}')
        # print(f'data_count: {data_count}')
        # print(f'min_fp_line: {min_fp_line}')
        # print(f'max_fp_line: {max_fp_line}')
        # print(f'min_fp_sample: {min_fp_sample}')
        # print(f'max_fp_sample: {max_fp_sample}')

        out_str = ''
        # Need to create label for these:
        # Use formats suggested by Mark:
        out_str += ('"' + VOLUME_ID + '",')
        out_str += ('"' + filespec.ljust(73) + '",')
        out_str += ('"' + observation_id.ljust(29) + '",')
        out_str += ('"' + mission_phase.ljust(25) + '",')
        out_str += ('"FP%d",' % focal_plane) # DETECTOR_ID
        out_str += ('%5d,'     % core_items[1]) # LINES
        out_str += ('%5d,'     % core_items[0]) # LINE_SAMPLES
        out_str += ('%5d,'     % spectrum_size)
        out_str += ('%2d,'     % backplanes)
        out_str += ('%8.3f,'   % min_waveno)
        out_str += ('%8.3f,'   % max_waveno)
        out_str += ('%6.3f,'   % band_bin_width)
        out_str += ('%6d,'     % data_count)
        out_str += ('%12.5f,'  % min_fp_line)
        out_str += ('%12.5f,'  % max_fp_line)
        out_str += ('%12.5f,'  % min_fp_sample)
        out_str += ('%12.5f'   % max_fp_sample)
        out_str += '\r\n'

        output_fp.write(out_str)
    output_fp.close()

    if os.path.getsize(supp_index_tab_path) == 0:
        EMPTY_SUPPLEMENTAL_INDEX = True
        os.remove(supp_index_tab_path)

def create_supplemental_index_label(
    orig_rows, supp_index_tab_path, supp_index_label_path
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
                            '$TABLE$', os.path.split(supp_index_tab_path)[1])
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    label_template = label_template.replace('$VOLUME_ID$', VOLUME_ID)
    label_template = label_template.replace('$TIME$', now)
    label_template = label_template.replace('$INSTHOSTNAME$', instrument_host_name)
    label_template = label_template.replace('$INSTHOSTID$', instrument_host_id)
    label_template = label_template.replace('$INSTNAME$', instrument_name)
    label_template = label_template.replace('$INSTID$', instrument_id)

    output_fp = open(supp_index_label_path, 'w')
    output_fp.write(label_template.replace('\n', '\r\n'))
    output_fp.close()

def graphic_from_centric(value, target):
    # Convert from planetocentric to planetographic
    (a,b,c) = BODY_DIMENSIONS[target]
    flattening = 2.*c / (a + b)
    tangent = np.tan(value * np.pi/180.)
    return 180./np.pi * np.arctan(tangent / flattening**2)

def centric_from_graphic(value, target):
    # Convert from planetographic to planetocentric
    (a,b,c) = BODY_DIMENSIONS[target]
    flattening = 2.*c / (a + b)
    tangent = np.tan(value * np.pi/180.)
    return 180./np.pi * np.arctan(tangent * flattening**2)

####################################################
# Steps to generate index lbl/tab under /metadata
####################################################

SKIP_SUPPLEMENTAL = False

if len(sys.argv) != 4:
    print('Usage: python generate_cocirs_index_files.py <original_index.lbl> <vol_root> <supp_index.lbl>')
    sys.exit(-1)

orig_index_label_path = sys.argv[1]
orig_index_tab_path = orig_index_label_path.replace('.LBL', '.TAB')
vol_root = sys.argv[2]
supp_index_label_name = sys.argv[3].replace('.LBL', '.lbl')
metadata_dir = vol_root.replace('holdings/volumes', 'holdings/metadata')

# reset the modification list & volume id
MOD_COL_LI = []
VOLUME_ID = vol_root[vol_root.rindex('/')+1::]

try:
    original_index_lbl = open(orig_index_label_path, 'r')
    original_index_tab = open(orig_index_tab_path, 'r')
except FileNotFoundError:
    exit()

if not os.path.exists(metadata_dir):
    os.makedirs(metadata_dir)

if metadata_dir[-1] != '/':
    metadata_dir += '/'

orig_index_label_name = orig_index_label_path[orig_index_label_path.rindex('/')+1::]
INDEX_TAB = orig_index_label_name.replace('.LBL', '.TAB')
new_index_label_name = VOLUME_ID + '_' +  orig_index_label_name.lower()
new_index_tab_name = new_index_label_name.replace('lbl', 'tab')
new_index_label_path = metadata_dir + new_index_label_name
new_index_tab_path = metadata_dir + new_index_tab_name
supp_index_tab_path = metadata_dir + supp_index_label_name.replace('.lbl', '.tab')
supp_index_label_path = metadata_dir + supp_index_label_name

create_index_tab(original_index_tab, metadata_dir, new_index_tab_path)
create_index_label(original_index_lbl, metadata_dir,
                   new_index_label_path, new_index_tab_name)

if not SKIP_SUPPLEMENTAL:
    # Modify CUBE_EQUI/POINT/RING_INDEX.LBL before passing into PdsTable
    lines = pdsparser.PdsLabel.load_file(orig_index_label_path)
    for i in range(len(lines)):
        if 'CSS:' in lines[i]:
            lines[i] = lines[i].replace('CSS:', '')
    orig_index_tab_pathle = pdstable.PdsTable(orig_index_label_path, label_contents=lines)

    # orig_index_tab_pathle = pdstable.PdsTable(orig_index_label_path)
    orig_rows = orig_index_tab_pathle.dicts_by_row()
    orig_label = orig_index_tab_pathle.info.label.as_dict()

    create_supplemental_index_tab(orig_rows, vol_root, supp_index_tab_path)
    create_supplemental_index_label(orig_rows, supp_index_tab_path, supp_index_label_path)
