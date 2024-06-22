#!/usr/bin/env python
################################################################################
# download.py: Download index files and labels for an entire collection.
#
# Usage:
#   python ../download.py <metadata_dir> <volume_dir> [-archive]
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

try:
    archive = sys.argv[3] == '-archive'
except:
    imgaes = False


#===============================================================================
def _download(voldir, url, patterns, first=False):
    i = meta.download(voldir, url, patterns, first=first)
    if i==0:
        pass  #... untar


# Download data
if archive:
    print('Downloading volume images...')
    from IPython import embed; print('+++++++++++++'); embed()
    _download(voldir, 'https://pds-rings.seti.org/holdings/archives-volumes/GO_0xxx/', 
                      [r'.*\.tar.gz', r'.*\.img'], first=True)
    exit()


# Download indexes and labels
print('Downloading index files...')
#meta.download(metadir, 
#    'https://pds-rings.seti.org/holdings/metadata/', [r'.*index\.lbl', r'.*index\.tab'])
_download(metadir, 'https://pds-rings.seti.org/holdings/metadata/',
                   [r'.*index\.lbl', r'.*index\.tab'])
from IPython import embed; print('+++++++++++++'); embed()

#meta.download(voldir, 'https://pds-rings.seti.org/holdings/volumes/', [r'.*\.LBL'])
print('Downloading volume labels...')
_download(voldir, 'https://pds-rings.seti.org/holdings/volumes/', 
                  [r'.*\.-lbl.tar.gz', r'.*\.LBL'], first=True)

exit()
################################################################################

