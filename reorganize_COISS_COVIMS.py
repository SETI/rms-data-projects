import os
import sys
import re
import time

ROOT = '/Volumes/pdsdata-admin/pds4-holdings/bundles/'

PATTERN1 = re.compile('1[0-9]{9}')
PATTERN2 = re.compile('1[0-9]{9}_0[0-9]{2}')

RENAME = True

for inst in ('_iss', '_vims'):
  for phase in ('_cruise', '_saturn'):
    for subdir in ('/browse_raw/', '/data_raw/'):
      combo = 'cassini' + inst + phase + subdir
      for root, dirs, files in os.walk(ROOT + combo):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in ('.xml', '.img', '.qub', '.png', '.jpg'):
                continue

            if not PATTERN1.match(file): continue

            part1 = file[:3] + 'xxxxxxx/'
            part2 = file[:5] + 'xxxxx/'

            if PATTERN2.match(file):
                part3 = file[:10] + '_xxx/'
            else:
                part3 = ''

            oldpath = root + '/' + file
            newpath = combo + part1 + part2 + part3 + file
            if oldpath == ROOT + newpath: continue

            if RENAME:
                for dirpath in (combo + part1,
                                combo + part1 + part2,
                                combo + part1 + part2 + part3):
                    if not os.path.exists(ROOT + dirpath):
                        print(dirpath)
                        os.mkdir(ROOT + dirpath)

            print(newpath)
            if RENAME:
                os.rename(oldpath, ROOT + newpath)
#                 time.sleep(0.05)

# Remove empty directories

for inst in ('_iss', '_vims'):
  for phase in ('_cruise', '_saturn'):
    for subdir in ('/browse_raw/', '/data_raw/'):
      combo = 'cassini' + inst + phase + subdir
      for root, dirs, files in os.walk(ROOT + combo):
        for dir in dirs:
            absdir = os.path.join(root, dir)
            contents = os.listdir(absdir)
            if not contents:
                print('Removing', absdir)
                if RENAME: os.rmdir(absdir)

