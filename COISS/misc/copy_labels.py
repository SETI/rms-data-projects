import os, sys
from shutil import copyfile

def migrate1(pds3_file):
    pds3_file = os.path.abspath(pds3_file)

    (in_dir, basename) = os.path.split(pds3_file)
    out_dir = in_dir.replace('holdings/volumes', 'pds4')
    out_dir.replace('COISS_2xxx', 'COISS_xxxx')
    out_dir.replace('COISS_1xxx', 'COISS_xxxx')

    sclk = basename[1:11]
    camera = basename[0].lower()
    out_dir = out_dir[:out_dir.index('xxx/')+4] + 'pds3-labels/%sxxxxx' % sclk[:5]

    pds4_file = os.path.join(out_dir, sclk + camera + '.lbl')
    print os.path.exists(pds4_file), pds4_file
    if os.path.exists(pds4_file): return

    if in_dir == out_dir:
        print 'Invalid input directory:', in_dir
        return

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    copyfile(pds3_file, pds4_file)

for arg in sys.argv[1:]:
    if not os.path.isdir(arg): continue

    datapath = os.path.join(arg, 'data')
    if os.path.exists(datapath):
        arg = datapath

    for root, dirs, files in os.walk(arg):
        prev_root = ''
        for name in files:
            if name.endswith('.LBL') or name.endswith('.lbl'):

                if root != prev_root:
                    print root
                    prev_root = root

                filename = os.path.join(root, name)
                migrate1(filename)

