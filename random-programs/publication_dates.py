#!/usr/bin/env python
################################################################################
# publication_dates.py
################################################################################

import os
import glob
import pdsparser

pub_dates = {}

for root in ['/Volumes/pdsdata/holdings/',
             '/Volumes/pdsdata2/holdings/',
             '/Volumes/pdsdata3/holdings/']:

    lskip = len(root)

    pattern = os.path.join(root, 'volumes/*/*/voldesc.cat')
    voldescs = glob.glob(pattern)

    voldescs.sort()

    for voldesc in voldescs:
        pdsdict = pdsparser.PdsLabel.from_file(voldesc).as_dict()

        volpath = os.path.split(voldesc)[0]
        pub_date = pdsdict['VOLUME']['PUBLICATION_DATE']

        key = volpath[lskip:]
        pub_dates[volpath[lskip:]] = pub_date

        print volpath[lskip:], pdsdict['VOLUME']['PUBLICATION_DATE']

keys = pub_dates.keys()
keys.sort()
len_key = max([len(k) for k in keys])

f = open('PUBLICATION_DATES_FOR_VOLUMES.py', 'w')
f.write('PUBLICATION_DATES_FOR_VOLUMES = {\n')

for key in keys:
    date = pub_dates[key]
    f.write('  "' + key + '"' + (len_key-len(key))*' ' + ': "' + date + '",\n')

f.write('}\n')
f.close()

