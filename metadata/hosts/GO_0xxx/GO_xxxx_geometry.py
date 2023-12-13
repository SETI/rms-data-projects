#!/usr/bin/env python
################################################################################
# GO_xxxx_geometry.py: Generates all geometry indices for Galileo SSI
#
# Usage:
#   python GO_xxxx_geometry.py input_tree output_tree [volume] 
#
#   e.g., python GO_xxxx_geometry.py $RMS_METADATA/GO_0xxx/ ./ 
#         python GO_xxxx_geometry.py $RMS_METADATA/GO_0xxx/ ./ GO_0017
#
################################################################################
import sys
import metadata.geometry_support as geom

try:
    volume = sys.argv[3]
except IndexError:
    volume = None

geom.process_index(sys.argv[1], sys.argv[2], 
                   selection="S", exclude=['GO_0016', 'GO_0999'], append=False, 
                   glob='GO_????_index.lbl', volume=volume)

################################################################################
