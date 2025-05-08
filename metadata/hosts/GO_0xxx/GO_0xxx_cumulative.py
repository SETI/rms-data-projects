#!/usr/bin/env python
################################################################################
# GO_0xxx_cumulative.py: Generate cumulative files and labels for Galileo SSI.
#
# Usage:
#   python3 GO_0xxx_cumulative.py input_tree output_dir [volume]
#
#   e.g., python3 GO_0xxx_cumulative.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/GO_0999/
#         python3 GO_0xxx_cumulative.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/GO_0999/ GO_0017
#
# Procedure:
#  1) Create the supplemental index files in the input tree using
#     GO_0xxx_index.py.
#  2) Create the geometry tables in the input tree using GO_0xxx_geometry.py.
#  3) Run this script to generate the cumulative tables in the output tree.
#
################################################################################
import host_init
import metadata.cumulative_support as cml

cml.create_cumulative_indexes(host='GOISS', 
                              exclude=['GO_0999'])
################################################################################
