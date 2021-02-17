#!/bin/bash
################################################################################
# Creates JPEG diagrams for missing COCIRS_0xxx and COCIRS_1xxx cubes
#
# Sample usage:
#   COCIRS_1xxx_new.sh <path>/COCIRS_1507/EXTRAS/CUBE_OVERVIEW/EQUIRECTANGULAR/219SA_COMPSIT001___CI____699_F4_401E.JPG
################################################################################

for jpgpath in "$@"
do
    outpath=${jpgpath/volumes/previews}
    outpath=${outpath/EXTRAS/DATA}
    outpath=${outpath/CUBE_OVERVIEW/CUBE}
    prefix=$(dirname "${outpath}")

    picmaker $jpgpath --directory $prefix \
        --verbose --noclobber --proceed --versions COCIRS_1xxx_previews.txt

    if [ "$?" = "2" ]; then
        exit 2
    fi

done

