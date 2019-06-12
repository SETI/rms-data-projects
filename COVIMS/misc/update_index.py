import os, sys

execfile('VERSIONS.py')
PDS4_TO_PDS3 = {key:value for (key,value) in VERSIONS_PDS4_VS_PDS3}
PDS3_TO_PDS4 = {key:value for (value,key) in VERSIONS_PDS4_VS_PDS3}

f = open('PDS3_FILES.txt')
for rec in f:
    pds3_fullpath = rec.rstrip()
    if pds3_fullpath in PDS3_TO_PDS4:
        continue

    pds3_basename = os.path.basename(pds3_fullpath)
    if pds3_basename[0] == 'v':
        sclk = pds3_basename[1:11]
    else:
        sclk = pds3_basename[:10]

    parts = pds3_basename.split('_')
    if len(parts) == 3:
        pds4_basename = sclk + '_' + parts[2]
    else:
        pds4_basename = sclk + '.qub'

    if pds4_basename in PDS4_TO_PDS3:
        print 'ERROR: PDS4 basename already in index for ', pds3_fullpath

    PDS4_TO_PDS3[pds4_basename] = pds3_fullpath
    PDS3_TO_PDS4[pds3_fullpath] = pds4_basename

f.close()

CUMINDEX = {}
CUMINDEX_BY_BASENAME = {}
f = open('COVIMS_0999_index.tab')
for rec in f:
    filename = rec[1:25].rstrip()
    directory = rec[29:64]
    volume = rec[350:361]

    pds3_fullpath = volume + directory + '/' + filename
    CUMINDEX[pds3_fullpath] = rec

    parts = filename.split('_')
    if len(parts) == 3:
        basename = parts[0] + '_' + parts[2]
    else:
        basename = parts[0] + '.qub'
    if basename[0] != 'v':
        basename = 'v' + basename

    CUMINDEX_BY_BASENAME[basename] = rec

f.close()

f = open('PDS4_FILES.txt')
g = open('cum-index.tab', 'w')
for rec in f:
    pds4_basename = rec.split('/')[1].rstrip()
    pds3_fullpath = PDS4_TO_PDS3[pds4_basename]

    try:
        rec = CUMINDEX[pds3_fullpath]
    except KeyError:
        basename = 'v' + pds4_basename
        if '-v' in basename:
            basename = basename[:-7] + '.qub'

        try:
            rec = CUMINDEX_BY_BASENAME[basename]
        except KeyError:
            print 'NOT FOUND!', pds3_fullpath

        (dir,filename) = os.path.split(pds3_fullpath)
        dir = '/' + dir.partition('/')[2]

        rec = rec[:1] + (filename + 24*' ')[:24] + rec[25:]
        rec = rec[:29] + dir + rec[64:]

    pds4_fullpath = pds4_basename[:4] + 'xxxxx/' + pds4_basename

    year = int(rec[73:77])
    if year < 2004:
        lidvid = 'urn:nasa:pds:cassini_vims_cruise:data_raw:'
    else:
        lidvid = 'urn:nasa:pds:cassini_vims_saturn:data_raw:'

    if '-v' in pds4_basename:
        version = pds4_basename[-5:-4]
        basename = pds4_basename[:-7]
    else:
        version = '1'
        basename = pds4_basename[:-4]

    lidvid = lidvid + basename + '::' + version + '.0'

    rec = '"' + (lidvid + 6*' ')[:61] + '","' + (pds4_fullpath + 7*' ')[:31] + '",' + rec
    g.write(rec)

f.close()
g.close()
