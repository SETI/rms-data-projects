#!/bin/bash
################################################################################
# Create smaller JPEG diagrams for COCIRS_5xxx and COCIRS_6xxx browse images
#
# Sample usage:
#   COCIRS_5xxx_diagrams.sh <volumes path>/COCIRS_5501 ...
################################################################################

cd /Tools/pds-tools-dev-git/website/previews/COCIRS

for volpath in "$@"
do
    outpath=${volpath/volumes/diagrams}
    mkdir -p $outpath/BROWSE

    picmaker $volpath/BROWSE \
        --directory $outpath/BROWSE --pattern \*.PNG \
        --recursive --verbose=2 --proceed --versions COCIRS_5xxx_diagrams.txt

    if [ "$?" = "2" ]; then
        exit 2
    fi

done

