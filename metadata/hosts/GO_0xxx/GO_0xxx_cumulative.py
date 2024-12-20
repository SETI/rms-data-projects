#!/usr/bin/env python
################################################################################
# GO_0xxx_cumulative.py: Generate cumulative files and labels for Galileo SSI.
#
# Usage:
#   python GO_0xxx_cumulative.py input_tree output_dir [volume]
#
#   e.g., python GO_0xxx_cumulative.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/GO_0999/
#         python GO_0xxx_cumulative.py $RMS_METADATA/GO_0xxx/ $RMS_METADATA/GO_0xxx/GO_0999/ GO_0017
#
################################################################################
import metadata as meta
import metadata.cumulative_support as cml

parser = cml.get_args(host='GOISS', exclude=['GO_0999'])
args = parser.parse_args()

cml.create_cumulative_indexes(args.input_tree, args.output_tree, 
                              volume=args.volume,
                              exclude=args.exclude)
################################################################################
