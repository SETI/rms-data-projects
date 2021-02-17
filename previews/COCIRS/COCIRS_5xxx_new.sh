#!/bin/bash
################################################################################
# Creates JPEG diagrams for missing COCIRS_5xxx and COCIRS_6xxx browse images
#
# Sample usage:
#   COCIRS_5xxx_new.sh <path>/COCIRS_5402/BROWSE/SATURN/POI0402140126_FP3.PNG
################################################################################

for pngpath in "$@"
do
    outpath=${pngpath/volumes/diagrams}
    prefix=$(dirname "${outpath}")

    picmaker $pngpath --directory $prefix \
        --verbose --noclobber --proceed --versions COCIRS_5xxx_diagrams.txt

    if [ "$?" = "2" ]; then
        exit 2
    fi

done

