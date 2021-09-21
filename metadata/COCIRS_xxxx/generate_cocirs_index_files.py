# Generate new COCIRS index files from orginal index files by changing all
# string integer and float fields into integer and float, and update the
# corresponding data type in the label.
#
# Usage: python generate_cocirs_index_files.py <profile_index.lbl> <metadata_dir>
#

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
OLD_DATA_TYPE = "CHARACTER"
NEW_DATA_TYPE = "ASCII_REAL"

def create_index_files(original_index_tab, metadata_dir):
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

def create_index_label(original_index_lbl, metadata_dir):
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

if len(sys.argv) != 3:
    print('Usage: python generate_cocirs_index_files.py <profile_index.lbl> <metadata_dir>')
    sys.exit(-1)

# python generate_cocirs_index_files.py /Volumes/pdsdata/COCIRS/Volumes/pdsdata-raid45/holdings/volumes/COCIRS_0xxx/COCIRS_0406/INDEX/CUBE_RING_INDEX.LBL /Volumes/pdsdata/COCIRS/Volumes/pdsdata-raid45/holdings/metadata/COCIRS_0xxx/COCIRS_0406/
profile_index_filename = sys.argv[1]
profile_index_tab = profile_index_filename.replace('.LBL', '.TAB')
metadata_dir = sys.argv[2]
# reset the modification list
MOD_COL_LI = []

try:
    original_index_lbl = open(profile_index_filename, 'r')
    original_index_tab = open(profile_index_tab, 'r')
except FileNotFoundError:
    exit()

if not os.path.exists(metadata_dir):
    os.makedirs(metadata_dir)

if metadata_dir[-1] != '/':
    metadata_dir += '/'
new_index_label_filename = metadata_dir + profile_index_filename[profile_index_filename.rindex('/')+1::]
new_index_tab_filename = new_index_label_filename.replace('.LBL', '.TAB')

create_index_files(original_index_tab, metadata_dir)
create_index_label(original_index_lbl, metadata_dir)
