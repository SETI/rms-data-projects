################################################################################
# python compare.py <files>
#
#  python ~/SETI/RMS/holdings/volumes/compare.py *summary.lbl
#
#  TODO: subsample
################################################################################
import os, sys
import numbers
import numpy as np
import warnings

import pdstable
import pdsparser


# Get input files
files = sys.argv[1:]


refdir = './'
compdir = '../'

# Compare each file
for file in files:

    # Read the files
    reftab = pdstable.PdsTable(os.path.join(refdir, file))
    comptab = pdstable.PdsTable(os.path.join(compdir, file))

    # Compute differences 
    diffs = np.empty((reftab.rows, len(reftab.keys)), dtype=float)
    reldiffs = np.empty((reftab.rows, len(reftab.keys)), dtype=float)
    for col in range(len(reftab.keys)):
        key = reftab.keys[col]

        # Get column values
        refvals = reftab.get_column(key)
        compvals = comptab.get_column(key)
        
        # Create (hopefully) unique row IDs by combining filespec and target name 
        try:
            reftarg = np.char.add('-', reftab.get_column('TARGET_NAME'))
            comptarg = np.char.add('-', comptab.get_column('TARGET_NAME'))
        except KeyError:
            reftarg = comptarg = ''

        refids = np.char.add(reftab.get_column('FILE_SPECIFICATION_NAME'), reftarg)
        compids = np.char.add(comptab.get_column('FILE_SPECIFICATION_NAME'), comptarg)

        # Determine field type for this column
        numeric = isinstance(refvals[0], numbers.Number)
        if numeric:
            try:
                unit = reftab.info.column_info_dict[key].node_dict['UNIT']
            except KeyError:
                unit = ''

            if unit == 'DEGREES':
                max = 360.
                angle = True
            elif unit == 'RADIANS':
                max = 2*np.pi
                angle = True
            else:
                angle = False

        # Compute differences for each row
        for row in range(len(refvals)):
            refid = refids[row]
        
            # Determine which comparison row corresponds to this reference row
            w = np.where(compids==refid)[0]

            if len(w) == 0:
                warnings.warn('Missing comparison for ' + refid)
                continue
            if len(w) > 1:
                warnings.warn('Duplicate comparisons for ' + refid)
                continue

            # Non-numeric column
            print(refid)
            if not numeric:
                diff = int(refvals[row] != compvals[w][0])
                reldiff = diff

            # Numeric column
            else:
                diff = refvals[row] - compvals[w][0]
                if angle:
                    diff = (diff + max/2) % max - max/2
                else:
                    max = np.abs(refvals[row])
                reldiff = diff/max

            # Add to tables
            diffs[row,col] = diff
            reldiffs[row,col] = reldiff
    
    # Compute statistic for each column
    diffs_max = np.max(diffs, axis=0)
    reldiffs_max = np.max(reldiffs, axis=0)
    imax = np.argmax(reldiffs, axis=0)

    # Write diff file
    prefix = os.path.splitext(file)[0]
    diff_filename = prefix + '_diffs.txt'

    print("Difference file: " + diff_filename)
    diff_file = open(diff_filename, 'w')

    diff_file.write('%-38s %-21s %-21s %-4s \n' % \
                    ('Name', 'Abs. Diff.(Max)', 'Rel. Diff.(Max)', 'ID'))

    for col in range(len(reftab.keys)):
        key = reftab.keys[col]
        diff_file.write('%-38s %10.3f %20.6f  ' % (key, diffs_max[col], reldiffs_max[col]))

        if reldiffs_max[col] >= 0.01:
            diff_file.write('%-7s' % '***  ') 
        else:
            diff_file.write('%-7s' % '     ') 


        diff_file.write('%-60s' % refids[imax[col]])

        diff_file.write('\n')

    diff_file.close()



