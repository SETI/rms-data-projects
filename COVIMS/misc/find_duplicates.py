#!/usr/bin/env python

import sys, os
import numpy as np
import pdsparser

for arg in sys.argv[1:]:
    basenames = set()
    prev_root = ''
    for root, dirs, files in os.walk(os.path.join(arg, 'data')):
      for name in files:
        if name.endswith('.QUB') or name.endswith('.qub'):

            if root != prev_root:
#                 print root
                prev_root = root

            parts = name.split('_')
            parts.append('')
            rootname = parts[0] + '_' + parts[2]

            if rootname in basenames:
                print root + '/' + name

            basenames.add(rootname)


