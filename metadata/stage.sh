#! /bin/bash
################################################################################
# stage.sh
#
#  Copy metadata collection from test directories to staging directories.
#
#     Run from the top of the collection test tree, e.g.:
#
#         $RMS_METADATA_TEST/GO_0xxx/
#
#     Metadata tables and labels are copied to:
#
#         $RMS_METADATA_STAGE/<collection>/current/
#
#     Existing files are copied to:
#
#         $RMS_METADATA_STAGE/<collection>/previous/
#
################################################################################

# Collection is current dir name
pwd=`pwd`
parts=($(echo $pwd | tr "/" " "))
pfx=${parts[0]}
col=${parts[-1]}

parts=($(echo $col | tr "_" " "))
pfx=${parts[0]}

dest=$RMS_METADATA_STAGE/$col/current
prev=$RMS_METADATA_STAGE/$col/previous

# Move current files to previous
rmdir -f $prev
if [ -d $dest ]; then
  mv -f $dest $prev
fi

# Copy new files to current
mkdir -p $dest
for dir in $pfx*
do
    mkdir $dest/"$dir"
    cp $dir/GO* $dest/"$dir"
done




