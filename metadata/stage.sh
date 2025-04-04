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

cur=$RMS_METADATA_STAGE/$col/current
prev=$RMS_METADATA_STAGE/$col/previous
fut=$RMS_METADATA_STAGE/$col/future

# Move current files to previous
rmdir -f $prev
if [ -d $cur ]; then
  mv -f $cur $prev
fi

# Move future files to current
rmdir -f cur
if [ -d $fut ]; then
  mv -f $fut $cur
fi

# Copy new files to future
mkdir -p $fut
for dir in $pfx*
do
    mkdir $fut/"$dir"
    cp $dir/GO* $fut/"$dir"
done




