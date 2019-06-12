from __future__ import print_function
import os,sys
import hashlib
import pdsparser
import vicar
import time, pytz, datetime
import traceback

TEMPLATE = 'cassini-iss-preview-template-20190602.xml'

# Read the template
with open(TEMPLATE) as f:
    recs = f.readlines()

# Remove Mitch's comments; strip trailing whitespace
for k,rec in enumerate(recs):
    parts = rec.split('<!-- [mkg]')
    assert len(parts) <= 2
    recs[k] = parts[0].rstrip() + '\r\n'

# Break up into SECTIONS
SECTIONS = [[]]
TESTS = ['$ALWAYS']
for rec in recs:
    if rec[0] == '$':
        SECTIONS.append([])
        TESTS.append(rec.rstrip())
    else:
        SECTIONS[-1].append(rec)

# Break up SECTIONS into expressions to be evaluated
EVALUATIONS = []
for k,section in enumerate(SECTIONS):
    EVALUATIONS.append([])
    new_recs = []
    for rec in section:
        parts = rec.split('$')
        assert len(parts) % 2 == 1
        for j in range(1,len(parts),2):
            EVALUATIONS[-1].append(len(new_recs) + j)
        new_recs += parts
    SECTIONS[k] = new_recs

# EVALUATIONS[k] is a list of the indices of all the expressions that need to be
# evaluated inside SECTIONS[k].

################################################################################

# From http://stackoverflow.com/questions/3431825/-
#       generating-an-md5-checksum-of-a-file

def hashfile(fname, blocksize=65536):
    f = open(fname, 'rb')
    hasher = hashlib.md5()
    buf = f.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(blocksize)
    return hasher.hexdigest()

################################################################################

def write_pds4_label(png_filename):

    # Function to fill out one section of the template
    # Defined internally here because it needs access to all the derived
    # quantities inside this function.
    def fill_out_one_section(recs, evaluations, null_value=None):
        recs = list(recs)       # Make a copy so we can update in-place
        for j in evaluations:
            if recs[j] == '':
                recs[j] = str(null_value)
            else:
                recs[j] = str(eval(recs[j], globals(), locals()))

        return recs

    # Define all the derived quantities
    basename = os.path.basename(png_filename)
    cruise_or_saturn = 'cruise' if basename <= '1452000000' else 'saturn'
    modification_date = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())

    timestamp = os.path.getmtime(png_filename)
    creation_dt = datetime.datetime.fromtimestamp(timestamp)
    local = pytz.timezone('America/Los_Angeles')
    local_dt = local.localize(creation_dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    creation_date = utc_dt.strftime('%Y-%m-%dT%H:%M:%S')

    md5_checksum = hashfile(png_filename, blocksize=65536)

    # Shift these locals to the global namespace
    globals()['basename'         ] = basename
    globals()['cruise_or_saturn' ] = cruise_or_saturn
    globals()['modification_date'] = modification_date
    globals()['creation_date'    ] = creation_date
    globals()['md5_checksum'     ] = md5_checksum

    # Fill in the template
    filled_out = []
    for k in range(len(SECTIONS)):
        test = TESTS[k]

        # For a $ALWAYS section, just perform evaluations
        if test == '$ALWAYS':
            filled_out += fill_out_one_section(SECTIONS[k], EVALUATIONS[k])

        # For an $IF section, first decide whether to include it
        elif test.startswith('$IF'):
            result = eval(test[4:-1])
            if result:
                filled_out += fill_out_one_section(SECTIONS[k], EVALUATIONS[k])

        # For a $FOR_EACH, make a list of the values that will be inserted and
        # repeat for each one. The evaluated value replaces '$$' in the
        # template.
        elif test.startswith('$FOR_EACH'):
            results = list(eval(test[10:-1]))
            for result in results:
                filled_out += fill_out_one_section(SECTIONS[k], EVALUATIONS[k],
                                                   null_value=result)

    # Write the label
    outfile = pds4_datafile[:-4] + '.xml'
    with open(outfile, 'w') as f:
        f.write(''.join(filled_out))

################################################################################

def label1(png_filename, replace=False):
    """Generate one label file, replacing a pre-existing one only if necessary.
    """

    try:
        png_filename = os.path.abspath(png_filename)
        if not replace and os.path.exists(png_filename[:-4] + '.xml'):
            return

        write_pds4_label(png_filename)

    # A KeyboardInterrupt must stop the program
    except KeyboardInterrupt:
        sys.exit(1)

    # For any other exception, print an error message and keep going
    except Exception as e:
        print('*** error for: ', png_filename)
        print(e)
        (etype, value, tb) = sys.exc_info()
        print(''.join(traceback.format_tb(tb)))

### MAIN PROGRAM

def main():

    # Get the command line args
    args = sys.argv[1:]

    # Set the replace flag if it's in the argument list
    if '--replace' in args:
        replace = True
        args.remove('--replace')
    else:
        replace = False

    # Step through the args
    for arg in args:

        # Case 1: Label a single image
        if os.path.isfile(arg):
          if arg.endswith('_full.png'):
            label1(arg, replace)

        # Case 2: Label all the images in a directory tree, recursively
        elif os.path.isdir(arg):
          prev_root = ''
          for root, dirs, files in os.walk(os.path.join(arg)):
            for name in files:
              if name.endswith('_full.png'):

                if root != prev_root:
                    print(root)
                    prev_root = root

                filename = os.path.join(root, name)
                label1(filename, replace)

if __name__ == '__main__': main()

