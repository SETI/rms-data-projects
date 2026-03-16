def merge_duplicate_rows(filepath):
    """Write a new version of the given index file where multiple entries for the same
    filespec are merged into a single record.

    Columns are assumed to be strings followed by floats. Floats must be ordered with
    alternating minimum and maximum values. FILE_SPECIFICATION_NAME must be the second
    column.

    The output file is matches the input file put with a "-merged" suffix.
    """

    with open(filepath, 'r') as f:
        recs = f.readlines()

    # Strings must be in quotes
    values = [eval(rec) for rec in recs]

    # Organize by filespec
    values_by_key = {}
    for vlist in values:
        key = vlist[1]
        values_by_key.setdefault(key, []).append(vlist)

    # Find the first float in the record
    kstart = [k for k,v in enumerate(values[0]) if isinstance(v, float)][0]

    # Create a list of new values, one for each filespec
    new_values = []
    for key, vlists in values_by_key.items():
        if len(vlists) == 1:
            new_vlist = vlists[0]
        else:
            # Float values alternate minimum and maximum
            new_vlist = list(vlists[0])
            for k in range(kstart, len(vlists[0]), 2):
                new_vlist[k]   = min(vlist[k] for vlist in vlists)
                new_vlist[k+1] = max(vlist[k+1] for vlist in vlists)

        new_values.append(new_vlist)

    # Infer the formats from the file
    fmts = ['' for k in range(len(values[0]))]
    for rec in recs:
        example = rec.split(',')
        for k, vstring in enumerate(example):
            vstring = vstring.rstrip()
            if vstring.startswith('"'):
                fmts[k] = '"%s"'
            elif 'E' in vstring.upper():        # e-format takes precedence over f
                echar = 'e' if 'e' in vstring else 'E'
                iexp = vstring.index(echar)
                ipt = vstring.index('.')
                fmts[k] = f'%{len(vstring)}.{iexp - ipt - 1}{echar}'
            else:                               # longest f-format (< 10 digits) wins
                ipt = vstring.index('.')
                fmts[k] = max(fmts[k], f'%{len(vstring)}.{len(vstring) - ipt - 1}f')

    # Write the output file
    outfile = filepath[:-4] + '-merged.tab'
    with open(outfile, 'wb') as f:
        for vlist in new_values:
            rec = ','.join(fmts[k] % v for k, v in enumerate(vlist)) + '\r\n'
            f.write(rec.encode('latin-1'))

