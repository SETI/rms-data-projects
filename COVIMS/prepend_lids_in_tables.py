import sys, os, re

execfile('VERSIONS.py')

lookup = {rec[1].split('/')[-1]: rec[0] for rec in VERSIONS_PDS4_VS_PDS3}

pattern = re.compile('v(1[0-9]{9})_[0-9]+(|_[0-9]{3})\.(qub|lbl)')

infile = '/Volumes/Marks-Migration-HD/holdings/metadata/COVIMS_0999/COVIMS_0999_saturn_summary.tab'
outfile = '/Volumes/Marks-Migration-HD/pds4/COVIMS_0xxx/metadata/body2-geometry.tab'

with open(infile) as f:
    recs = f.readlines()

newrecs = []
for k,rec in enumerate(recs):
    match = pattern.search(rec)
    if match is None:
        print 'ERROR', k, rec
        continue

    sclk = match.group(1)
    line = match.group(2)
    basename = match.group(0)

    if sclk < '1452':
        phase = 'cruise'
    else:
        phase = 'saturn'

    pds4name = lookup.get(basename.replace('lbl','qub'), sclk + line + '.qub')
    col1 = 'urn:nasa:pds:cassini_vims_' + phase + ':data_raw:' + sclk + line + '    '
    col2 = '%sxxxxx/%s' % (pds4name[:5], pds4name) + '       '
    col1 = col1[:56]
    col2 = col2[:32]
    newrecs.append(col1 + ',' + col2 + ',' + rec)

with open(outfile, 'w') as f:
    f.writelines(newrecs)


