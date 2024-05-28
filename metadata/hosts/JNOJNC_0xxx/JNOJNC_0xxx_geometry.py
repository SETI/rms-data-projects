#!/usr/bin/env python
################################################################################
# GO_0xxx_geometry.py: Generates all geometry indices for Galileo SSI
#
# Usage:
#   python GO_0xxx_geometry.py input_tree output_tree [volume]
#
#   e.g., python GO_0xxx_geometry.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/
#         python GO_0xxx_geometry.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/ GO_0017
#
# Procedure:
#  1) Create the supplemental index files in the input tree using 
#     GO_0xxx_index.py.
#  2) Run this script to generate the geometry tables in the output tree.
#
################################################################################
import sys
import metadata.geometry_support as geom

try:
    volume = sys.argv[3]
except IndexError:
    volume = None

geom.process_index(sys.argv[1], sys.argv[2], volume=volume, append=False, #no_table=True,
                   selection="S", 
                   exclude=['GO_0016', 'GO_0999'],
                   glob='GO_????_index.lbl')
################################################################################
