from typing import TYPE_CHECKING

from ImageArea import ImageArea
from MigrationInfo import MigrationInfo, add_migration_task
from Tail import Tail
from VicarFile import VicarFile

if TYPE_CHECKING:
    from typing import List, Optional
    from LabelItem import LabelItem
    from Labels import Labels
    from MigrationInfo import DICT


def migrate_labels(dat_tim, migration_info, pds3_labels):
    # type: (str, MigrationInfo, Labels) -> Labels
    old_recsize = pds3_labels.get_int_value('RECSIZE')
    old_nbb = pds3_labels.get_int_value('NBB')
    new_recsize = old_recsize - old_nbb
    pds4_system_labels = pds3_labels.system_labels.replace_label_items([
        LabelItem.create_int_item('NBB', 0),
        LabelItem.create_int_item('NLB', 0),
        LabelItem.create_int_item('RECSIZE', new_recsize)
    ])

    return Labels.create_labels_with_adjusted_lblsize(
        pds4_system_labels,
        pds3_labels.property_labels,
        add_migration_task(dat_tim,
                           migration_info,
                           pds3_labels.history_labels),
        pds3_labels.padding)


def migrate_image_area(pds3_image_area):
    # type: (ImageArea) -> ImageArea
    return ImageArea(None, None, pds3_image_area.binary_image_lines)


def migrate_eol_labels(new_recsize, pds3_eol_labels):
    # type: (int, Labels) -> Labels
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

    def pad_bytes_at_tail():
        # type: () -> str
        assert False, 'unimplemented'

    padded_bytes_at_tail = pad_bytes_at_tail()

    return Tail(pds3_image_area.binary_header,
                pds3_image_area.binary_prefixes,
                padded_bytes_at_tail)


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
    migration_info = build_migration_info(original_filepath,
                                          pds3_vicar_file)

    pds4_labels = migrate_labels(dat_tim,
                                 migration_info,
                                 pds3_vicar_file.labels)
    new_recsize = pds4_labels.get_int_value('RECSIZE')

    pds4_image_area = migrate_image_area(pds3_vicar_file.image_area)

    pds4_eol_labels = migrate_eol_labels(new_recsize,
                                         pds3_vicar_file.eol_labels)

    pds4_tail = migrate_tail(new_recsize,
                             pds3_vicar_file.image_area,
                             pds3_vicar_file.tail)

    return VicarFile(pds4_labels, pds4_image_area, pds4_eol_labels, pds4_tail)
