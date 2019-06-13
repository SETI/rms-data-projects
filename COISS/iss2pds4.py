import os, sys
from Migrate import migrate_file

def migrate1(pds3_file):
    pds3_file = os.path.abspath(pds3_file)
    original_filepath = pds3_file[pds3_file.index('xxx/')+4:]

    (in_dir, basename) = os.path.split(pds3_file)
    out_dir = in_dir.replace('holdings/volumes', 'pds4')
    out_dir = in_dir.replace('COISS_2xxx', 'COISS_xxxx')
    out_dir = in_dir.replace('COISS_1xxx', 'COISS_xxxx')

    sclk = basename[1:11]
    camera = basename[0].lower()
    out_dir = out_dir[:out_dir.index('xxx/')+4] + 'data_raw/%sxxxxx' % sclk[:5]

    if in_dir == out_dir:
        print 'Invalid input directory:', in_dir

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    pds4_file = os.path.join(out_dir, sclk + camera + '.img')
    migrate_file(pds3_file, output_filepath=pds4_file,
                            original_filepath=original_filepath)

for arg in sys.argv[1:]:

    if os.path.isfile(arg):
        if arg.endswith('.IMG') or arg.endswith('.img'):
            migrate1(arg)

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
                    migrate1(filename)

