import os, sys

ROOT = '/Volumes/Migration/pds4/COVIMS_0xxx/raw-before-rename'

prev_root = ''
for root, dirs, files in os.walk(ROOT):
  for name in files:
    if not name.endswith('.qub'):
        continue

    if name.endswith('_test.qub'):
        continue

    if root != prev_root:
        print root
        prev_root = root

    oldpath = os.path.join(root, name)
    if name[0] != 'v':
        print 'Missing V:', oldpath
        continue

    oldlabel = os.path.join('/Volumes/Migration/holdings/volumes/COVIMS_0xxx-labels/' +
                            root[len(ROOT)+1:], name.replace('.qub','.lbl'))
    if not os.path.exists(oldlabel):
        print 'Missing label file!:', oldlabel
        continue

    newdir = '/Volumes/Migration/pds4/COVIMS_0xxx/raw/%sxxxxx/' % name[1:6]
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    # Get version if any
    if '-v' in name:
        parts = name.split('-v')
        version = '-v' + parts[1][0]
        name = parts[0] + parts[1][1:]
    else:
        version = ''

    parts = name.split('_')
    if len(parts) == 2:
        newname = name[1:11] + version + '.qub'
    else:
        newname = name[1:11] + '_' + parts[2][:-4] + version + '.qub'

    newpath = os.path.join(newdir, newname)
    if os.path.exists(newpath):
        print 'File aleady exists!:', newpath
        continue

    newlabel = newpath.replace('.qub', '.lbl')
    if os.path.exists(newlabel):
        print 'Label already exists!:', newlabel
        continue

    os.rename(oldpath, newpath)
    os.rename(oldlabel, newlabel)
