# Python 2 only!!!
#
# This rewrites all pickle files as protocol=2 and also rewrites all shelves.
# It also makes sure no files contain unicode.

import pickle
import shelve
import os
GDBM_MODULE = __import__("gdbm")

def update_shelves(filename):

    execfile(filename)

    name = os.path.basename(filename)
    name = name.replace('.py','')
    parts = name.split('_')
    if len(parts) == 4:
        del parts[2]
    elif len(parts) == 5:
        del parts[2]
        del parts[2]
    name = '_'.join(parts)
    mydict = locals()[name]

    outfile = filename.replace('.py', '.pickle')
    f = open(outfile, 'wb')
    pickle.dump(mydict, f, protocol=2)
    f.close()

    outfile = filename.replace('.py', '.shelf')
    shelf = shelve.Shelf(GDBM_MODULE.open(outfile, 'n'))

    for (key, value) in mydict.iteritems():
        shelf[key] = value

    shelf.close()

for (root, dirs, files) in os.walk('/Volumes/Untitled/shelves'):
  for file in files:
    if not file.endswith('py'): continue
    filepath = os.path.join(root, file)
    print filepath
    update_shelves(filepath)

