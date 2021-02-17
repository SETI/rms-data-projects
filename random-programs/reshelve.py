#!/usr/bin/env python
################################################################################
# reshelve.py
#
# Syntax:
#   reshelve.py directory [directory...]
#
# Searches recursively from the given root directory or directories for every
# python file ending in '.py'. Reads the dictonary defined in that file and
# then rewrites the associated shelf file.
#
# It prints the name of each shelf file as it is rewritten.
#
# This tool is needed because not all versions of the Python shelve module
# create compatible files.
#
################################################################################

import os
import sys
import shelve
import re

REGEX = re.compile('(\w+?_\w+?)_.*(info|link)(|_v[0-9][0-9][0-9]+)\.py')

for arg in sys.argv[1:]:
    for (root, dirs, files) in os.walk(arg):
        for file in files:
            if not file.endswith('.py'): continue

            python_abspath = os.path.join(root, file)
            shelf_abspath = python_abspath[:-3] + '.shelf'
            if not os.path.exists(shelf_abspath): continue

            execfile(python_abspath, globals(), locals())

            matchobj = REGEX.match(file)
            if matchobj:
                key = matchobj.expand(r'\1_\2')
            else:
                key = file[:-3]
            python_dict = globals()[key]

            shelf_abspath = python_abspath[:-3] + '.shelf'
            os.remove(shelf_abspath)
            shelf_dict = shelve.open(shelf_abspath, flag='c')

            for (key,value) in python_dict.iteritems():
                shelf_dict[key] = value

            shelf_dict.close()
            print shelf_abspath
