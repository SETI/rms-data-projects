import os, sys

ROOT = '/Volumes/Migration2/pds4/COVIMS_0xxx/'
DEST = '/Volumes/Migration2/pds4/VIMS/'

execfile('VERSIONS.py')
for (pds4_basename, pds3_path) in VERSIONS_PDS4_VS_PDS3:
    outdir = pds4_basename[:5] + 'xxxxx'
    if not os.path.exists(DEST + outdir):
        os.mkdir(DEST + outdir)

    os.rename(ROOT + pds3_path, DEST + outdir + '/' + pds4_basename)

for root, dirs, files in os.walk(ROOT):
    print root
    for file in files:
        if not file.endswith('.qub'): continue
        if not file[0] == 'v':
            print 'skipped:', os.path.join(root, file)
            continue

        outdir = file[1:6] + 'xxxxx'
        if not os.path.exists(DEST + outdir):
            os.mkdir(DEST + outdir)

        parts = file.split('_')
        if len(parts) == 2:
            outfile = parts[0][1:] + '.qub'
        else:
            outfile = parts[0][1:] + '_' + parts[2]

        srcfile = os.path.join(root, file)
        destfile = DEST + outdir + '/' + outfile
        if os.path.exists(destfile):
            print 'dest exists:' + srcfile, destfile

        os.rename(srcfile, destfile)




