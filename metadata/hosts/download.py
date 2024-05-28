#!/usr/bin/env python
################################################################################
# download.py: Download index files and labels for an entire collection.
#
# Usage:
#   python ../download.py <metadata_dir> <volume_dir>
#
#  Run from host directory, e.g., rms-data-projects/metadata/hosts/COISS_xxxx.
#  Collection directories are created in the specified directories, and 
#  subdirectories are created and populated under them.
#
#  e.g.:   python ../download.py $RMS_METADATA $RMS_VOLUMES
#
################################################################################
import sys
import metadata as meta


# Get output dirs
metadir = sys.argv[1]
voldir = sys.argv[2]

# Download data
print('Downloading index files...')
meta.download(metadir, 
    'https://pds-rings.seti.org/holdings/metadata/', [r'.*index\.lbl', r'.*index\.tab'])

print('Downloading volume labels...')
meta.download(voldir, 'https://pds-rings.seti.org/holdings/volumes/', [r'.*\.LBL'])


exit()
################################################################################

