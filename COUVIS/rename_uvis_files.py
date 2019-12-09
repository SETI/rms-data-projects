import os, sys

DAT_DEST = '/Volumes/Migration2/UVIS/cassini_uvis_saturn/'
LBL_DEST = '/Volumes/Migration2/UVIS/pds3-labels/'

for v in range(1,61):
  ROOT = '/Volumes/Migration2/UVIS/holdings/volumes/COUVIS_00%02d/DATA' % v
  for root, dirs, files in os.walk(ROOT):
    print root
    for file in files:
        if not file[-4:] in ('.LBL', '.DAT'): continue

        parts = file.split('_')
        inst = parts[0][:-4].lower()
        ext = parts[-1][-4:].lower()

        parts[0] = parts[0][-4:]
        parts[-1] = parts[-1][:-4]

        newname = '_'.join(parts) + '_' + inst + ext
        newdir = 'data_raw_' + inst + '/' + newname[:7] + 'x'

        if ext == '.dat':
            fulldir = DAT_DEST + newdir
        else:
            fulldir = LBL_DEST + newdir

        if not os.path.exists(fulldir):
            os.mkdir(fulldir)

#         print os.path.join(root,file), fulldir + '/' + newname
        os.rename(os.path.join(root,file), fulldir + '/' + newname)

DAT_DEST = '/Volumes/Migration2/UVIS/cassini_uvis_saturn/'
LBL_DEST = '/Volumes/Migration2/UVIS/pds3-calibration-labels/'

# Calibration files
for v in range(1,61):
  ROOT = '/Volumes/Migration2/UVIS/holdings/volumes/COUVIS_00%02d/CALIB/' % v
  files = os.listdir(ROOT)
  files.sort()
  versions = [f for f in files if f.startswith('VERSION_')]
  for version in versions:
    for root, dirs, files in os.walk(ROOT + version):
      print root
      for file in files:
        if not file[-4:] in ('.LBL', '.DAT'): continue

        parts = file.split('_')
        inst = parts[0][:-4].lower()
        ext = parts[-1][-4:].lower()

        parts[0] = parts[0][-4:]
        parts[-1] = parts[-1][:-4]

        newname = '_'.join(parts) + '_' + inst + ext
        newname = newname.lower()
        newdir = 'calibration_data_' + inst + '/' + newname[:7] + 'x'

        if ext == '.dat':
            fulldir = DAT_DEST + newdir
        else:
            fulldir = LBL_DEST + newdir

        if not os.path.exists(fulldir):
            os.mkdir(fulldir)

#         print os.path.join(root,file), fulldir + '/' + newname
        os.rename(os.path.join(root,file), fulldir + '/' + newname)

PNG_DEST = '/Volumes/Migration2/UVIS/cassini_uvis_saturn/'

for v in range(1,61):
  ROOT = '/Volumes/Migration2/UVIS/holdings/previews/COUVIS_00%02d/DATA' % v
  for root, dirs, files in os.walk(ROOT):
    print root
    for file in files:
        if not file.endswith('full.png'): continue

        parts = file.split('_')
        inst = parts[0][:-4].lower()

        parts[0] = parts[0][-4:]
        parts[-1:] = [inst, parts[-1]]

        newname = '_'.join(parts)
        newdir = 'browse_raw_' + inst + '/' + newname[:7] + 'x'

        fulldir = PNG_DEST + newdir

        if not os.path.exists(fulldir):
            os.mkdir(fulldir)

#         print os.path.join(root,file), fulldir + '/' + newname
        os.rename(os.path.join(root,file), fulldir + '/' + newname)
