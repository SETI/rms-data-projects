import os, sys
import numpy as np

def get_lblsize_from_file(filename):
    with open(filename, 'rb') as f:
        rec = f.read(40)

    if rec[:8] != 'LBLSIZE=':
        raise IOError('not a VICAR file: ' + filename)

    lblsize = rec[8:]
    while lblsize[0] == ' ':
        lblsize = lblsize[1:]

    lblsize = lblsize[:lblsize.index(' ')]
    return int(lblsize)

def get_header_from_file(filename):
    lblsize = get_lblsize_from_file(filename)

    with open(filename, 'rb') as f:
        header = f.read(lblsize)

    return header

def get_value_from_header(header, name):
    if name == 'LBLSIZE':
        loc = 0
    else:
        loc = header.index(' ' + name + '=') + 1

    value = header[loc + len(name) + 1:]
    value = value[:value.index(' ')]
    return value

def get_int_from_header(header, name):
    return int(get_value_from_header(header, name))

def get_byte_count(filename):
    return os.path.getsize(filename)

def check_byte_count(filename):
    header = get_header_from_file(filename)
    recsize = get_int_from_header(header, 'RECSIZE')
    bytes = os.path.getsize(filename)

    if bytes % recsize != 0:
        print '***', recsize, bytes % recsize, filename

for arg in sys.argv[1:]:

    if os.path.isfile(arg):
        if arg.endswith('.IMG') or arg.endswith('.img'):
            check_byte_count(arg)

    elif os.path.isdir(arg):
        datapath = os.path.join(arg, 'data')
        if os.path.exists(datapath):
            arg = datapath

        for root, dirs, files in os.walk(arg):
            prev_root = ''
            for name in files:
                if name.endswith('.IMG') or name.endswith('.img'):

                    if root != prev_root:
                        print root
                        prev_root = root

                    filename = os.path.join(root, name)
                    check_byte_count(filename)

