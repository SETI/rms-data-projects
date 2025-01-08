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
import metadata.cumulative_support as cml

cml.create_cumulative_indexes(host='GOISS', 
                              exclude=['GO_0999'])
################################################################################
