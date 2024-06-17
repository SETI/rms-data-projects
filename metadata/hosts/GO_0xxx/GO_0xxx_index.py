#!/usr/bin/env python
################################################################################
# GO_0xxx_index.py: Generate sypplemental index files and labels for Galileo SSI.
#
# Usage:
#   python GO_0xxx_index.py input_tree output_tree [volume]
#
#   e.g., python GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ $RMS_METADATA/GO_0xxx/
#         python GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ $RMS_METADATA/GO_0xxx/ GO_0017
#
# Procedure:
#  1) Create the volume tree under $RMS_METADATA.
#  2) Point $RMS_VOLUMES to the top of the volume tree contining the data
#     files.
#  2) Populate the volume tree with the RMS updated index files from viewmaster: 
#     <volume>_index.lbl/tab.  
#  3) Run this script to generate the supplemental files in that tree.
#
################################################################################
import sys
import metadata.index_support as idx

try:
    volume = sys.argv[3]
except IndexError:
    volume = None

idx.make_index(sys.argv[1], sys.argv[2], 
               type='supplemental', glob='C0*', volume=volume)
################################################################################
