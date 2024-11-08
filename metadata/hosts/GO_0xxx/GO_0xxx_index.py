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
#  1) Point $RMS_METADATA and $RMS_VOLUMES to the top of the local metadata and
#     volume trees respectively., e.g.,
#
#         RMS_METADATA = ~/SETI/RMS/metadata_test
#         RMS_VOLUMES = ~/SETI/RMS/holdings/volumes
#
#  2) From the host directory (e.g., rms-data-projects/metadata/hosts/GO_0xxx),
#     run download.sh to create and populate the metadata and volume trees:
#
#         python ../download.py $RMS_METADATA $RMS_VOLUMES
#
#  3) Create a template for the supplemental label, e.g.: rms-data-projects/
#     hosts/GO_0xxx/templates/GO_0xxx_index_supplemental.lbl
#
#  4) Create a host_defs.lbl file in the host templates directory, e.g.:
#     rms-data-projects/hosts/GO_0xxx/templates/host_defs.lbl
#
#  5) Run this script to generate the supplemental files in that tree.
#
################################################################################
import metadata as meta
import metadata.index_support as idx

parser = meta.get_index_args(host='GOISS', type='supplemental')
args = parser.parse_args()

idx.make_index(args.input_tree, args.output_tree, volume=args.volume,
               type=args.type, glob='C0*')
################################################################################
