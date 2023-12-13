#!/usr/bin/env python
################################################################################
# GO_0xxx_index.py: Generate index files and labels for Galileo SSI.
#
# Usage:
#   python GO_0xxx_index.py input_tree output_tree [volume]
#
#   e.g., python GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ ./
#         python GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ ./ GO_0017
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
