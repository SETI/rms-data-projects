#!/usr/bin/env python
################################################################################
# volume_info.py
#
# Syntax:
#   python volume_info.py path/to/holdings
#
# Create Python dictionary of volume info.
#   Keys are [volset] and [volset/volname]
#   Tuple returned for volumes is (version number, release date, dataset IDs)
#   Tuple returned for volume sets is (maximum version, latest release, [])
#   Files are written to the current default directory.
################################################################################

import os, sys
import glob
import shutil
import pdsparser

volume_info = {}
data_set_info = {}

volset_max_date = {}
volset_max_version = {}

USE_DSID_VERSIONS = ['COISS_2xxx']

for root in sys.argv[1:]:

    # Handle special case--undefined preliminary volume
    path = os.path.join(root, 'volumes/RES_xxxx_prelim/RES_0001')
    if os.path.exists(path):
        volume_info['RES_xxxx_prelim/RES_0001'] = (0.9, '2008-03-30',
                                                   ['SR-5-DDR-RESONANCES-V0.9'])
        volume_info['RES_xxxx_prelim'] = (0.9, '2008-03-30', [])
        data_set_info['SR-5-DDR-RESONANCES-V0.9'] = ['RES_xxxx_prelim/RES_0001']

    pattern = os.path.join(root, 'volumes/*/*/voldesc.*')
    voldescs = glob.glob(pattern)

    pattern = os.path.join(root, 'volumes/*/*/VOLDESC.*')
    voldescs += glob.glob(pattern)

    lskip = len(os.path.join(root,'volumes')) + 1
    rskip = len('/voldesc.cat')

    for voldesc in voldescs:
        volume_key = voldesc[lskip:-rskip]
        volset_key = volume_key.split('/')[0]

        if volset_key not in volset_max_date:
            volset_max_date[volset_key] = ''
            volset_max_version[volset_key] = 0.

        if voldesc.endswith('.SFD'):
            recs = pdsparser.PdsLabel.load_file(voldesc)

            for k in range(len(recs)):
                if recs[k].startswith('OBJECT '):
                    obj = recs[k].split(' = ')[1]
                elif recs[k].startswith('END_OBJECT'):
                    recs[k] = 'END_OBJECT = ' + obj
                elif recs[k].strip() == 'END':
                    recs = recs[1:k+1]
                    break

            pdsdict = pdsparser.PdsLabel.from_string(recs).as_dict()

            planet_id = pdsdict['MISSION_PHASE_NAME'][0]
            scid = pdsdict['SPACECRAFT_ID']
            if type(scid) == str:
                dsids = [scid + '-' + planet_id + '-ISS-2-EDR-V1.0']
            else:
                dsids = ['VG1-' + planet_id + '-ISS-2-EDR-V1.0',
                         'VG2-' + planet_id + '-ISS-2-EDR-V1.0']

            version = 1.0
            pub_date = pdsdict['DATASETINFO_GROUP']['RELEASE_DATE']

        else:
            pdsdict = pdsparser.PdsLabel.from_file(voldesc).as_dict()

            dsids = pdsdict['VOLUME']['DATA_SET_ID']
            if type(dsids) == str:
                dsids = [dsids]

            pub_date = pdsdict['VOLUME']['PUBLICATION_DATE']

            version = pdsdict['VOLUME']['VOLUME_VERSION_ID']
            version = float(version.split(' ')[-1])

            dsid_version = float(dsids[0][-3:])

        # Known repairs
        if 'COISS_0xxx/COISS_0011' in voldesc:
            dsids[0] = dsids[0][:-3] + '3.0'
            dsid_version = 3.0

        if volset_key in ['COISS_0xxx', 'COISS_0xxx_v2', 'COISS_2xxx']:
            version = dsid_version

        if pub_date == '2016-090':      # COUVIS_0051
            pub_date = '2016-03-31'

        volume_info[volume_key] = (version, pub_date, dsids)
        print volume_key, volset_key, version, pub_date

        volset_max_date[volset_key] = max(volset_max_date[volset_key],
                                          pub_date)

        volset_max_version[volset_key] = max(volset_max_version[volset_key],
                                             version)

        for dsid in dsids:
            if dsid not in data_set_info:
                data_set_info[dsid] = []

            data_set_info[dsid].append(volume_key)

# Fold volume set info into the volume info dictionary
for volset_key in volset_max_date:
    volume_info[volset_key] = (volset_max_version[volset_key],
                               volset_max_date[volset_key], [])


# Write the volume info dictionary file after backing up the previous version
# dest = voldescs[0].split('holdings/')[0] + 'shelves/VOLUME_INFO.py'
dest = './VOLUME_INFO.py'
if os.path.exists(dest):
    k = 0
    while True:
        k += 1
        backup = dest[:-3] + ('_v%03d.py' % k)
        if not os.path.exists(backup):
            break

    shutil.move(dest, backup)

f = open(dest, 'w')
f.write('VOLUME_INFO = {\n')

keys = volume_info.keys()
keys.sort()
len_key = max([len(k) for k in keys])

for key in keys:
    f.write('  "' + key + '"' + (len_key - len(key)) * ' ' + ': (')

    (version, pub_date, dsids) = volume_info[key]
    f.write('%3.1f, "%-10s", [' % (version, pub_date))
    if len(dsids) == 0:
        f.write(']),\n')
    else:
        dsids.sort()
        for dsid in dsids[:-1]:
            f.write('"' + dsid + '",\n')
            f.write((len_key + 27) * ' ')
        f.write('"' + dsids[-1] + '"]),\n')

f.write('}\n')
f.close()

# Write the dataset info dictionary file after backing up the previous version
# dest = voldescs[0].split('holdings/')[0] + 'shelves/DATA_SET_INFO.py'
dest = './DATA_SET_INFO.py'
if os.path.exists(dest):
    k = 0
    while True:
        k += 1
        backup = dest[:-3] + ('_v%03d.py' % k)
        if not os.path.exists(backup):
            break

    shutil.move(dest, backup)

f = open(dest, 'w')
f.write('DATA_SET_INFO = {\n')

keys = data_set_info.keys()
keys.sort()
len_key = max([len(k) for k in keys])

for key in keys:
    f.write('  "' + key + '"' + (len_key - len(key)) * ' ' + ': [')

    volnames = data_set_info[key]
    volnames.sort()
    for volname in volnames[:-1]:
        f.write('"' + volname + '",\n')
        f.write((len_key + 7) * ' ')
    f.write('"' + volnames[-1] + '"],\n')

f.write('}\n')
f.close()

