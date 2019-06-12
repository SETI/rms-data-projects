import os, sys

prev_root = ''
for root, dirs, files in os.walk('/Volumes/Migration/holdings/previews/COISS_2xxx/'):
  for name in files:
    if not name.endswith('_full.png'):
        continue

    if root != prev_root:
        print root
        prev_root = root

    oldpath = os.path.join(root, name)
    newdir = '/Volumes/Migration/pds4/COISS_2xxx/browse/%sxxxxx/' % name[1:6]
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    newname = name[1:11] + '_full.png'
    os.rename(oldpath, newdir + '/' newname)
