import datetime
import os.path
import sys

from CassiniBug import fix_cassini_bug
from Migration import migrate_vicar_file
from Parsers import parse_all
from VicarFile import parse_vicar_file


def make_output_filepath(in_filepath):
    # type: (str) -> str
    """
    Given the path to the input file, generate a path to the output file.
    """
    dirname, basename = os.path.split(in_filepath)
    root, ext = os.path.splitext(basename)
    return os.path.join(dirname, root + "_pds4" + ext.lower())


def migrate_file(input_filepath, output_filepath=None, original_filepath=None):
    if not output_filepath:
        output_filepath = make_output_filepath(input_filepath)

    if not original_filepath:
        original_filepath = input_filepath

    # Read the file.
    with open(input_filepath, 'r') as f:
        pds3_bytes = f.read()

    # Parse it.
    pds3_vicar_file = parse_all(parse_vicar_file, pds3_bytes)

    # Fix the Cassini bug
    fixed_pds3_vicar_file = fix_cassini_bug(input_filepath, pds3_vicar_file)

    # Create the DAT_TIM string.
    now = datetime.datetime.utcnow()
    dat_tim = now.strftime('%a %b %d %H:%M:%S %Y')

    # Migrate it.
    pds4_vicar_file = migrate_vicar_file(original_filepath,
                                         dat_tim,
                                         fixed_pds3_vicar_file)

    # Write it out
    pds4_bytes = pds4_vicar_file.to_byte_string()
    with open(output_filepath, 'w') as f:
        f.write(pds4_bytes)


if __name__ == '__main__':
    input_filepath = sys.argv[1]
    print "**** Migrating %s." % input_filepath

    MIGRATE_IN_PLACE = False  # type: bool
    if MIGRATE_IN_PLACE:
        output_filepath = input_filepath
    else:
        output_filepath = make_output_filepath(input_filepath)

    migrate_file(input_filepath, output_filepath, input_filepath)

    # Print progress message.
    print "**** Migrated %s." % output_filepath
