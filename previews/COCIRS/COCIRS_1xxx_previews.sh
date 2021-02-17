#!/bin/bash
################################################################################
# Create smaller preview images for COCIRS cube overviews
#
# Sample usage:
#   COCIRS_1xxx_previews.sh <volumes path>/COCIRS_1007 ...
################################################################################

HOME=`pwd`

# get the absolute path of the executable
SELF_PATH=$(cd -P -- "$(dirname -- "$0")" && pwd -P) && SELF_PATH=$SELF_PATH/$(basename -- "$0")

# resolve symlinks
while [[ -h $SELF_PATH ]]; do
    # 1) cd to directory of the symlink
    # 2) cd to the directory of where the symlink points
    # 3) get the pwd
    # 4) append the basename
    DIR=$(dirname -- "$SELF_PATH")
    SYM=$(readlink "$SELF_PATH")
    SELF_PATH=$(cd "$DIR" && cd "$(dirname -- "$SYM")" && pwd)/$(basename -- "$SYM")
done

DIR=$(dirname "$SELF_PATH")
cd $DIR

for volpath in "$@"
do
    # If path does not exist, maybe it was relative to the original working dir
    if [ -d $volpath ]; then
        volpath=$volpath
    else
        volpath=$HOME/$volpath
    fi

    outpath=${volpath/volumes/previews}
    mkdir -p $outpath/DATA/CUBE

    picmaker $volpath/EXTRAS/CUBE_OVERVIEW \
        --directory $outpath/DATA/CUBE --pattern \*.JPG \
        --recursive --verbose --proceed --versions COCIRS_1xxx_previews.txt

    if [ "$?" = "2" ]; then
        exit 2
    fi

done

