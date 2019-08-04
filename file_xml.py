################################################################################
# file_xml.py
#
# Print out a rough draft of the XML File object based on a data file.
#
# Syntax:
#   python file_xml.py data_file.dat
#
# The program will print the object to standard output.
################################################################################

import sys, os
import string
import hashlib
import time, datetime, pytz
from xml.sax.saxutils import escape

TIMEZONE = 'America/Los_Angeles'

def basename(filename):
    """Return the basename of a file path."""

    return os.path.basename(filename)

def file_zulu(filename):
    """Return the modification time of a file as a formatted string."""

    timestamp = os.path.getmtime(filename)
    creation_dt = datetime.datetime.fromtimestamp(timestamp)
    local = pytz.timezone(TIMEZONE)
    local_dt = local.localize(creation_dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt.strftime('%Y-%m-%dT%H:%M:%S')

def file_bytes(filename):
    """Return the number of bytes in a file."""

    return os.path.getsize(filename)

def file_records(filename):
    """Return the number of records in a file; 0 if the file is not ASCII."""

    with open(filename) as f:
        count = 0
        asciis = 0
        non_asciis = 0
        for line in f:
            for c in line:
                if c in string.printable:
                    asciis += 1
                else:
                    non_asciis += 1

            count += 1

    if non_asciis > 0.05 * asciis:
        return 0

    return count

def file_md5(filename, blocksize=65536):
    """Return the MD5 checksum of the file at the specified path."""

    f = open(filename, 'rb')
    hasher = hashlib.md5()
    buf = f.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(blocksize)

    return hasher.hexdigest()

def file_xml(datafile, indent, tab=4, comment='**** REVIEW ****'):

    tabstr = tab * ' '
    indent1 = indent * ' '
    indent2 = indent1 + tabstr
    indent3 = indent2 + tabstr
    indent4 = indent3 + tabstr
    indent5 = indent4 + tabstr

    print indent1 + '<File>'
    print indent2 + '<file_name>' + basename(datafile) + '</file_name>'
    print indent2 + '<creation_date_time>' + file_zulu(datafile) +  '</creation_date_time>'
    print indent2 + '<file_size unit="byte">' + str(file_bytes(datafile)) + '</file_size>'

    recs = file_records(datafile)
    if recs:
        print indent2 + '<records>' + str(recs) + '</records>'

    print indent2 + '<md5_checksum>' + file_md5(datafile) + '</md5_checksum>'

    if comment:
        print indent2 + '<comment>'
        lines = comment.split('\n')
        for line in lines:
            if line.strip():
                print indent3 + escape(line.strip())
            else:
                print
        print indent2 + '</comment>'

    print indent1 + '</File>'

################################################################################
# Command line interface
################################################################################

def main():

    # Get the command line args
    datafile = sys.argv[1]
    indent = int(sys.argv[2])
    if len(sys.argv) == 3:
        comment = "**** REVIEW ****"
    elif len(sys.argv) == 4:
        comment = sys.argv[3]
    else:
        print 'Error: illegal number of arguments'
        sys.exit(1)

    file_xml(datafile, indent, comment=comment)

if __name__ == '__main__': main()
