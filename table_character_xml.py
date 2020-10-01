################################################################################
# table_character_xml.py
#
# Print out a rough draft of the XML Table_Character object based on the PDS3
# label for an ASCII table.
#
# Syntax:
#   python table_character_xml.py pds3_label_path.lbl indent [col_offset char_offset]
#
# The program will print the object to standard output.
################################################################################

import sys, os
import pdsparser
from xml.sax.saxutils import escape

SPECIAL_CONSTANTS_KEYS = [
    'saturated_constant',
    'missing_constant',
    'error_constant',
    'invalid_constant',
    'unknown_constant',
    'not_applicable_constant',
    'valid_maximum',
    'high_instrument_saturation',
    'high_representation_saturation',
    'valid_minimum',
    'low_instrument_saturation',
    'low_representation_saturation',
]

def pds4_type(pds3_type):
    if 'INT'  in pds3_type: return 'ASCII_Integer'
    if 'REAL' in pds3_type: return 'ASCII_Real'
    if 'CHAR' in pds3_type: return 'ASCII_String'
    return 'ASCII_String ****REVIEW****'

def pds4_unit(pds3_unit):
    if 'KM/S'            in pds3_unit.upper():     return 'km/s'
    if 'KM'              in pds3_unit.upper():     return 'km'
    if 'CELSIUS'         in pds3_unit.upper():     return 'degC'
    if 'DEG'             in pds3_unit.upper():     return 'deg'
    if 'KILOBITS/SEC'    in pds3_unit.upper():     return 'kb/s'
    if 'BITS/PIX'        in pds3_unit.upper():     return 'bits/pixel'
    if 'MILLISEC'        in pds3_unit.upper():     return 'ms'
    if 'SEC'             == pds3_unit.upper()[:3]: return 's'
    if 'S'               == pds3_unit.upper():     return 's'

    return pds3_unit + ' ****REVIEW****'

def table_character(labelfile, indent=0, tab=4, shift=(0,0)):

    (dcols, dchars) = shift
    label = pdsparser.PdsLabel.from_file(labelfile)
    asdict = label.as_dict()

    caret_key = [k for k in asdict.keys() if k[0] == '^'][0]
    table = asdict[caret_key[1:]]

    column_info = []
    for (k,v) in table.iteritems():
        if not isinstance(v, dict): continue
        column_info.append((v['START_BYTE'], v['NAME']))

    column_info.sort()
    column_names = [i[1] for i in column_info]

    tabstr = tab * ' '
    indent1 = indent * ' '
    indent2 = indent1 + tabstr
    indent3 = indent2 + tabstr
    indent4 = indent3 + tabstr
    indent5 = indent4 + tabstr

    print indent1 + '<Table_Character>'
    print indent2 + '<offset unit="byte">0</offset>'
    print indent2 + '<records>' + str(table['ROWS']) + '</records>'
    print indent2 + '<description>'

    desc = str(label[caret_key[1:]].dict['DESCRIPTION'].pdsvalue)
    lines = desc.split('\n')
    for line in lines:
        if line.strip():
            print indent3 + escape(line.strip())
        else:
            print
    print indent2 + '</description>'

    print indent2 + '<record_delimiter>' + 'Carriage-Return Line-Feed' + \
                    '</record_delimiter>'

    print indent2 + '<Record_Character>'
    print indent3 + '<fields>' + str(table['COLUMNS'] + dcols) + '</fields>'
    print indent3 + '<groups>0</groups>'
    print indent3 + '<record_length unit="byte">' + str(table['ROW_BYTES'] + dchars) + '</record_length>'

    for k,name in enumerate(column_names):
        col = table[name]
        print indent3 + '<Field_Character>'
        print indent4 + '<name>' + name + '</name>'
        print indent4 + '<field_number>' + str(k+1+dcols) + '</field_number>'
        print indent4 + '<field_location unit="byte">' + str(col['START_BYTE'] + dchars) + \
                        '</field_location>'
        print indent4 + '<data_type>' + pds4_type(col['DATA_TYPE']) + \
                        '</data_type>'
        print indent4 + '<field_length unit="byte">' + str(col['BYTES']) + '</field_length>'
#         if 'FORMAT' in col:
#             print indent4 + '<field_format>' + col['FORMAT'] + '</field_format>'
        if 'UNIT' in col:
            print indent4 + '<unit>' + pds4_unit(col['UNIT']) + '</unit>'

        print indent4 + '<description>'

        lines = col['DESCRIPTION'].split('\n')
        for line in lines:
            if line.strip():
                print indent5 + escape(line.strip())
            else:
                print

        print indent4 + '</description>'

        constants = []
        for key in col:
            if key.endswith('_CONSTANT'):
                constants.append(key)
            if key.startswith('VALID_'):
                constants.append(key)

        if constants:
            if 'NULL_CONSTANT' in constants:
                if 'UNKNOWN_CONSTANT' not in constants:
                    constants.append('UNKNOWN_CONSTANT')
                    col['UNKNOWN_CONSTANT'] = col['NULL_CONSTANT']
                else:
                    constants.append('ERROR_CONSTANT')
                    col['ERROR_CONSTANT'] = col['NULL_CONSTANT']

                constants.remove('NULL_CONSTANT')

            print indent4 + '<Special_Constants>'

            for key in SPECIAL_CONSTANTS_KEYS:
                if key.upper() not in col: continue
                const = str(col[key.upper()])
                if const.endswith('.0'):
                    const = const[:-1]

                print indent5 + '<%s>%s</%s>' % (key, const, key)

            print indent4 + '</Special_Constants>'

        print indent3 + '</Field_Character>'
    print indent2 + '</Record_Character>'
    print indent1 + '</Table_Character>'

################################################################################
# Command line interface
################################################################################

def main():

    # Get the command line args
    labelfile = sys.argv[1]
    indent = int(sys.argv[2])
    if len(sys.argv) == 3:
        dcols = 0
        dchars = 0
    elif len(sys.argv) == 5:
        dcols = int(sys.argv[3])
        dchars = int(sys.argv[4])
    else:
        print 'Error: illegal number of arguments'
        sys.exit(1)

    table_character(labelfile, indent, shift=(dcols,dchars))

if __name__ == '__main__': main()
