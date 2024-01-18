# To create labels:
#   python make_label.py path/.../*.tab

import os, sys, time

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
    template = 'templates/%sxxx%s.lbl' % (volume_id[:-3],
                                          body[underscore+5:])

    f = open(template)
    lines = f.readlines()
    f.close()

    # Replace the tags in the template
    if is_inventory:
        subs = ('"' + filename + '"',
                '"' + volume_id + '"',
                creation_time,
                creation_time[:10])
    else:
        subs = (str(recs),
                '"' + filename + '"',
                '"' + volume_id + '"',
                creation_time,
                str(recs))

    l = 0
    for i in range(len(subs)):
        while not lines[l].endswith('$\r\n'):
            l += 1

        lines[l] = lines[l][:-3] + subs[i] + '\r\n'
        #print lines[l]

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
    print filepath
    #make_label(filepath, preserve_time=True)    # Uses date from previous .lbl
    make_label(filepath)                        # Uses the current date




