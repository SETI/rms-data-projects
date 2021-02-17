import os
import sys
import shelve
import pickle

for arg in sys.argv[1:]:
  for (root, dirs, files) in os.walk(arg):
    for file in files:
        if not file.endswith('.py'): continue

        abspath = os.path.join(root, file)
        execfile(abspath)

        if '_info' in file:
            key = '_'.join(file.split('_')[:2]) + '_info'
        else:
            key = '_'.join(file.split('_')[:2]) + '_links'

        print abspath, key

        d = globals()[key]
        with open(abspath[:-3] + '.pickle', 'wb') as f:
            pickle.dump(d,f)

