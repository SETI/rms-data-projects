#!/bin/bash
################################################################################
# Create preview images for JNOSRU_xxxx images
#
# Sample usage:
#   JNOSRU_xxxx_previews.sh <volumes path>/JNOSRU_xxxx/JNOSRU_0001
################################################################################

versionpath=${0/.sh/.txt}               # change ".sh" to ".txt" in script path

for volpath in "$@"
do
    outpath=${volpath/volumes/previews} # change "volumes" to "previews"
    mkdir -p $outpath

    python /Users/Shared/bin/picmaker $volpath \
        --directory=$outpath  --pattern=\*.FIT \
        --recursive --verbose=2 --proceed --extension=jpg --down \
        --percentiles 0.3 99.7 --gamma 1 \
        --footprint=4 --valid 1 9999999 \
        --versions=$versionpath
done

