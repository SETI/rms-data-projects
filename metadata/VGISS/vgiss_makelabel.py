#!/usr/bin/env python
#
# To create labels:
#   python VGISS_makelabel.py path/.../*.tab

import os, sys, time

PLANETS = ['', '', '', '', '', 'JUPITER', 'SATURN', 'URANUS', 'NEPTUNE']

def make_label(filepath, creation_time=None, preserve_time=False):

    (dir, filename) = os.path.split(filepath)
    (body, ext) = os.path.splitext(filename)
    lblfile = os.path.join(dir, body) + '.lbl'

    # Check the data file
    f = open(filepath)
    lines = f.readlines()
    f.close()

    recs = len(lines)
    linelen = len(lines[0])

    is_inventory = ('inventory' in body)
    for line in lines:
        if not is_inventory:
            assert len(line) == linelen     # all lines have the same length
        assert line[-2:] == '\r\n'          # all lines have proper <cr><lf>

    # Get the instrument and volume_id
    underscore = filename.index('_')
    inst_id = filename[:underscore]
    volume_id = filename[:underscore + 5]
    iplanet = int(volume_id[6])
    ivgr = int(volume_id[7])

    vgs = "VG2" if iplanet >= 7 else "VG1/VG2"
    dataset_id = '%s-%s-ISS-2/3/4/6-PROCESSED-V1.0' % (vgs, PLANETS[iplanet][0])

    # Determine the creation time
    if preserve_time:
        f = open(lblfile)
        lines = f.readlines()
        f.close()

        creation_time = 'missing'
        for line in lines:
            if line.startswith('PRODUCT_CREATION_TIME'):
                creation_time = line[-21:-2]
                assert creation_time[:2] == '20'
                break

        assert creation_time != 'missing'

    elif creation_time is None:
        creation_time = '%04d-%02d-%02dT%02d:00:00' % time.gmtime()[:4]

    # Read the template
    template = 'templates/%sxxxx%s.lbl' % (volume_id[:-4],
                                          body[underscore+5:])
    template = template.replace('jupiter', 'planet')
    template = template.replace('saturn' , 'planet')
    template = template.replace('uranus' , 'planet')
    template = template.replace('neptune', 'planet')

    f = open(template)
    lines = f.readlines()
    f.close()

    # Replace the tags in the template
    if is_inventory:
        subs = ['"' + filename + '"',
                '"' + volume_id + '"',
                '"' + dataset_id + '"',
                creation_time,
                '"VOYAGER %d"' % ivgr,
                'VG%d' % ivgr,
                '"%s ENCOUNTER"' % PLANETS[iplanet],
                creation_time[:10]
               ]
    else:
        subs = [str(recs),
                '"' + filename + '"',
                '"' + volume_id + '"',
                '"' + dataset_id + '"',
                creation_time,
                '"VOYAGER %d"' % ivgr,
                'VG%d' % ivgr,
                '"%s ENCOUNTER"' % PLANETS[iplanet],
                str(recs)
               ]

    l = 0
    for i in range(len(subs)):
        while not lines[l].endswith('$\r\n'):
            l += 1

        lines[l] = lines[l][:-3] + subs[i] + '\r\n'
#         print lines[l]

    for line in lines:
        assert line[-2:] == '\r\n'
        assert not line.endswith('$\r\n')

    # Write the new label
    f = open(lblfile, 'w')
    for line in lines:
        f.write(line)

    f.close()

################################################################################

for filepath in sys.argv[1:]:
    if filepath.endswith('index.tab'): continue
    print filepath
    #make_label(filepath, preserve_time=True)    # Uses date from previous .lbl
    make_label(filepath)                        # Uses the curent date




