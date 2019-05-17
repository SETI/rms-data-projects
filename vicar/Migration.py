from typing import TYPE_CHECKING

from ImageArea import ImageArea
from LabelItem import LabelItem
from Labels import Labels
from MigrationInfo import MigrationInfo, add_migration_task
from Tail import Tail
from VicarFile import VicarFile
from VicarSyntax import round_to_multiple_of

if TYPE_CHECKING:
    from typing import List, Optional
    from MigrationInfo import DICT


def migrate_labels(dat_tim, migration_info, pds3_labels):
    # type: (str, MigrationInfo, Labels) -> Labels
    """
    Migrate the labels by adjusting the values of selected label
    items; store the old label items into the migration task.  Add the
    migration task to the history labels.  Adjust LBLSIZE and re-pad
    the labels according to the new RECSIZE.
    """
    old_recsize = pds3_labels.get_int_value('RECSIZE')
    old_nbb = pds3_labels.get_int_value('NBB')
    new_recsize = old_recsize - old_nbb

    old_nlb = pds3_labels.get_int_value('NLB')
    old_header_len = old_nlb * old_recsize
    new_header_len = round_to_multiple_of(old_header_len, new_recsize)
    new_nlb = new_header_len / new_recsize

    pds4_system_labels = pds3_labels.system_labels.replace_label_items([
        LabelItem.create_int_item('NBB', 0),
        LabelItem.create_int_item('NLB', new_nlb),
        LabelItem.create_int_item('RECSIZE', new_recsize)
    ])

    return Labels.create_labels_with_adjusted_lblsize(
        pds4_system_labels,
        pds3_labels.property_labels,
        add_migration_task(dat_tim,
                           migration_info,
                           pds3_labels.history_labels),
        pds3_labels.padding)


def migrate_image_area(new_recsize, pds3_image_area):
    # type: (int, ImageArea) -> ImageArea
    """
    Drop the binary labels.
    """
    if pds3_image_area.binary_header is None:
        pds4_binary_header = None
    else:
        pds3_len = len(pds3_image_area.binary_header)
        pds4_len = round_to_multiple_of(pds3_len, new_recsize)
        excess = pds4_len - pds3_len
        padding = excess * '\0'
        pds4_binary_header = pds3_image_area.binary_header + padding
    return ImageArea(pds4_binary_header,
                     None,
                     pds3_image_area.binary_image_lines)


def migrate_eol_labels(new_recsize, pds3_eol_labels):
    # type: (int, Labels) -> Labels
    """
    Adjust LBLSIZE and re-pad the labels according to the new RECSIZE.
    """
    if pds3_eol_labels is None:
        return None

    return Labels.create_eol_labels_with_adjusted_lblsize(
        new_recsize,
        pds3_eol_labels.system_labels,
        pds3_eol_labels.property_labels,
        pds3_eol_labels.history_labels,
        pds3_eol_labels.padding)


def migrate_tail(new_recsize, pds3_image_area, pds3_tail):
    # type: (int, ImageArea, Tail) -> Tail
    """
    Pull the binary labels from the PDS3 image area, put them into the
    PDS4 tail, and pad appropriately.
    """
    return Tail.create_with_padding(new_recsize,
                                    pds3_image_area.binary_prefixes,
                                    pds3_tail.tail_bytes)


def build_migration_info(original_filepath, pds3_vicar_file):
    # type: (str, VicarFile) -> MigrationInfo
    """Collect PDS3 information to be saved within the PDS4 file."""

    def select_main_label_items():
        # type: () -> List[LabelItem]
        """Select and extract certain LabelItems from the Labels."""
        keywords_to_select = ['RECSIZE', 'LBLSIZE', 'NBB', 'NLB']
        return pds3_vicar_file.labels.system_labels.select_labels(
            keywords_to_select)

    def select_eol_label_items():
        # type: () -> List[LabelItem]
        """Select and extract certain LabelItems from the EolLabels."""
        eol_labels = pds3_vicar_file.eol_labels
        if eol_labels is None:
            return []
        else:
            keywords_to_select = ['LBLSIZE']
            return eol_labels.system_labels.select_labels(keywords_to_select)

    def build_dictionary():
        # type: () -> DICT
        """Build a dictionary with selected data."""
        tail_bytes = pds3_vicar_file.tail.tail_bytes
        if tail_bytes is None:
            tail_length = 0
        else:
            tail_length = len(tail_bytes)

        # We'll need the original tail length to peel off any added
        # padding when back-migrating.
        dictionary = {'TAIL_LENGTH': tail_length}  # type: DICT

        # If the user gave an original_filepath, archive it too.
        if original_filepath is not None:
            dictionary['FILEPATH'] = original_filepath

        return dictionary

    return MigrationInfo(select_main_label_items(),
                         select_eol_label_items(),
                         build_dictionary())


def migrate_vicar_file(original_filepath, dat_tim, pds3_vicar_file):
    # type: (Optional[str], str, VicarFile) -> VicarFile
    """
    Extract the information needed for migration, then migrate each
    part of the VICAR file.
    """
    migration_info = build_migration_info(original_filepath,
                                          pds3_vicar_file)

    pds4_labels = migrate_labels(dat_tim,
                                 migration_info,
                                 pds3_vicar_file.labels)
    new_recsize = pds4_labels.get_int_value('RECSIZE')

    pds4_image_area = migrate_image_area(new_recsize,
                                         pds3_vicar_file.image_area)

    pds4_eol_labels = migrate_eol_labels(new_recsize,
                                         pds3_vicar_file.eol_labels)

    pds4_tail = migrate_tail(new_recsize,
                             pds3_vicar_file.image_area,
                             pds3_vicar_file.tail)

    return VicarFile(pds4_labels, pds4_image_area, pds4_eol_labels, pds4_tail)


if __name__ == '__main__':
    import sys

    in_filepath = sys.argv[1]
    out_filepath = sys.argv[2]
    with open(in_filepath, 'r') as f:
        pds3_bytes = f.read()

    from Parsers import parse_all
    from VicarFile import parse_vicar_file

    pds3_vicar_file = parse_all(parse_vicar_file, pds3_bytes)

    import datetime

    now = datetime.datetime.utcnow()
    dat_tim = now.strftime('%a %b %d %H:%M:%S %Y')

    # Try migrating.
    from Migration import migrate_vicar_file

    pds4_vicar_file = migrate_vicar_file(in_filepath, dat_tim, pds3_vicar_file)

    # Write it out
    pds4_bytes = pds4_vicar_file.to_byte_string()
    with open(out_filepath, 'w') as f:
        f.write(pds4_bytes)

    # Sanity check: can I parse a PDS4 file?  Yep.
    pds4_rt_vicar_file = parse_all(parse_vicar_file, pds4_bytes)
    assert pds4_bytes == pds4_rt_vicar_file.to_byte_string()

    # Now try back-migrating.
    from BackMigration import back_migrate_vicar_file

    orig_filepath, pds3_rt_vicar_file = back_migrate_vicar_file(
        pds4_vicar_file)

    # check that we got the original stuff back
    assert orig_filepath == in_filepath
    assert pds3_vicar_file == pds3_rt_vicar_file

    print '**** All good!'
