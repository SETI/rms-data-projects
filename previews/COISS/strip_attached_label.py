#!/usr/bin/env python

import sys
import os

for arg in sys.argv[1:]:
    with open(arg, 'rb') as f:
        lines = f.readlines()

    content = ''.join(lines)
    k = content.index('LBLSIZE=')

    with open(arg, 'wb') as f:
        f.write(content[k:])

