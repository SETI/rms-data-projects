#!/usr/bin/env python
################################################################################
# GO_0xxx_index.py: Generate supplemental index files and labels for Galileo SSI.
#
# Usage:
#   python3 GO_0xxx_index.py input_tree output_tree [volume]
#
#   e.g., python3 GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ $RMS_METADATA/GO_0xxx/
#         python3 GO_0xxx_index.py $RMS_VOLUMES/GO_0xxx/ $RMS_METADATA/GO_0xxx/ GO_0017
#
# Procedure:
#  1) Point $RMS_METADATA and $RMS_VOLUMES to the top of the local metadata and
#     volume trees respectively., e.g.,
#
#         RMS_METADATA = ~/SETI/RMS/metadata_test
#         RMS_VOLUMES = ~/SETI/RMS/holdings/volumes
#
#  2) Create a template for the supplemental label, e.g.: rms-data-projects/
#     hosts/GO_0xxx/templates/GO_0xxx_index_supplemental.lbl
#
#  3) Create a host_defs.lbl file in the host templates directory, e.g.:
#     rms-data-projects/hosts/GO_0xxx/templates/host_defs.lbl
#
#  4) Run this script to generate the supplemental files in that tree.
#
################################################################################
import metadata.index_support as idx

idx.process_index(host='GOISS', 
                  type='supplemental', 
                  glob='C0*')
################################################################################
