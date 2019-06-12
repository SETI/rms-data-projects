import os, sys

prev_root = ''
for root, dirs, files in os.walk('/Volumes/Migration/holdings/previews/COVIMS_0xxx/'):
  for name in files:
    if not name.startswith('v') or not name.endswith('_full.png') or '_1_' not in name:
        continue

    if root != prev_root:
        print root
        prev_root = root

    oldpath = os.path.join(root, name)

    newdir = '/Volumes/Migration/pds4/COVIMS_0xxx/raw-browse/%sxxxxx/' % name[1:6]
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    parts = name.split('_')
    if len(parts) == 2:
        newname = name[1:11] + '-v1-full.png'
    else:
        newname = name[1:11] + '_' + parts[2:5] + '-v1-full.png'

    newpath = os.path.join(newdir, newname)
    k = 1
    while os.path.exists(newpath):
        newpath = newpath.replace('-v%d' % k, '-v%d' % (k+1))
        k += 1

    print newpath
    os.rename(oldpath, newpath)
