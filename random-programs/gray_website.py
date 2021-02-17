f = open('/Users/mark/Desktop/linked.txt')
PATHS = f.readlines()
f.close()


import os
import finder_colors

ROOT = "/Library/Server/Web/Data/Sites/Default"

for path in PATHS:
    abspath = ROOT + path.rstrip()
    if os.path.exists(abspath):
        finder_colors.set_color(abspath, 'gray')
    else:
        print 'Missing:', abspath

