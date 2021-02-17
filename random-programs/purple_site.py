import os

import os
import subprocess

COLOR_VALUES = {
    'none'   : 0,
    'orange' : 1,
    'red'    : 2,
    'yellow' : 3,
    'blue'   : 4,
    'violet' : 5,
    'purple' : 5,
    'green'  : 6,
    'gray'   : 7,
    'grey'   : 7,
}

def set_color(filepath, color):
    filepath = os.path.abspath(filepath)
    color = color.lower()
    script = ('tell application "Finder" to set label index of ' +
              '(POSIX file "%s" as alias) to %d' % (filepath,
                                                    COLOR_VALUES[color]))
    cmd = ['osascript', '-e', script]

    _ = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE)

for (root, dirs, files) in os.walk('/Library/Server/Web/Data/Sites/Default/'):
    for file in files:
        abspath = os.path.join(root, file)
        set_color(abspath, 'purple')
    for dir in dirs:
        abspath = os.path.join(root, dir)
        set_color(abspath, 'purple')
