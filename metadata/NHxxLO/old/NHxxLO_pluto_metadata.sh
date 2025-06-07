#!/bin/bash
################################################################################
# Create geometric metadata files for NHxxLO images, Pluto only.
# It also creates their label files.
#
# Sample usage:
#   NHxxLO_pluto_metadata.sh .../holdings/volumes/COUVIS_xxxx/NHxxLO_2001 ...
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

    inpath=${volpath/volumes/metadata}/$(basename $volpath)_supplemental_index.lbl
    echo $inpath

    python NHxxLO_pluto_metadata.py $inpath

    dirpath=$(dirname $inpath)
    python make_label.py $dirpath/*moon_summary.tab
    python make_label.py $dirpath/*ring_summary.tab
    python make_label.py $dirpath/*pluto_summary.tab
    python make_label.py $dirpath/*charon_summary.tab
done
