import sys, os, re

execfile('VERSIONS.py')

LOOKUP = {rec[3].split('/')[-1]: rec[:3] for rec in VERSIONS}

PATTERN = re.compile('v(1[0-9]{9})_[0-9]+(|_[0-9]{3})\.(qub|lbl)')
ROID = re.compile('^(.*),"[SJ]/CUBE/CO/VIMS/.*?/(IR |VIS) *"')

# INFILE = '/Volumes/Marks-Migration-HD/holdings/metadata/COVIMS_0999/COVIMS_0999_saturn_summary.tab'
# OUTFILE = '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/metadata_raw/body-geometry2.tab'

# INFILE = '/Volumes/Marks-Migration-HD/holdings/metadata/COVIMS_0999/COVIMS_0999_ring_summary.tab'
# OUTFILE = '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/metadata_raw/ring-geometry2.tab'

# INFILE = '/Volumes/Marks-Migration-HD/holdings/metadata/COVIMS_0999/COVIMS_0999_index.tab'
# OUTFILE = '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/metadata_raw/index2.tab'

INFILE = '/Volumes/Marks-Migration-HD/holdings/metadata/COVIMS_0999/COVIMS_0999_inventory.tab'
OUTFILE = '/Volumes/Migration2/pds4/VIMS/cassini_vims_saturn/metadata_raw/body-inventory2.csv'

with open(INFILE) as f:
    recs = f.readlines()

newrecs1 = []   # cruise
newrecs2 = []   # saturn
for k,rec in enumerate(recs):
    match = PATTERN.search(rec)
    if match is None:
        print 'ERROR', k, rec
        continue

    sclk = match.group(1)
    line = match.group(2)
    basename = match.group(0)

    if sclk < '1452':
        phase = 'cruise'
        newrecs = newrecs1
    else:
        phase = 'saturn'
        newrecs =  newrecs2

    (pds4_root, version, _) = LOOKUP.get(basename.replace('lbl','qub'),
                                         (sclk + line, '1.0', ''))
    if version != '1.0': continue

    pds4name = pds4_root + '.qub'
    col1 = 'urn:nasa:pds:cassini_vims_' + phase + ':data_raw:' + sclk + line + '    '
    col2 = '%sxxxxx/%s' % (pds4name[:5], pds4name) + '       '
    col1 = col1[:56]
    col2 = col2[:32]

    # Replace a RING_OBSERVATION_ID if necessary and move 'IR' or 'VIS' to front
    rec = ROID.sub(r'\2,\1,', rec)
    newrec = col1 + ',' + col2 + ',' + rec

    newrecs.append(newrec)

if 'inventory' not in INFILE:
  lencheck = len(newrecs2[0])
  for (k,newrec) in enumerate(newrecs1 + newrecs2):
    if len(newrec) != lencheck:
        print ('record length discrepancy in row %d' % k)
        sys.exit(1)

if newrecs1:
    with open(OUTFILE.replace('/cassini_vims_saturn/',
                              '/cassini_vims_cruise/'), 'w') as f:
        f.writelines(newrecs1)

with open(OUTFILE, 'w') as f:
    f.writelines(newrecs2)



# Note: Files after 1530409854 on COVIMS_0012 are duplicated on COVIMS_0013. Delete from COVIMS_0012.
