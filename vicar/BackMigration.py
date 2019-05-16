from typing import TYPE_CHECKING, cast

from ImageArea import ImageArea
from Labels import Labels
from MigrationInfo import remove_migration_task
from Tail import Tail
from VicarFile import VicarFile
from VicarSyntax import maybe_bs

if TYPE_CHECKING:
    from typing import Optional, Tuple
    from LabelItem import LabelItem
    from Labels import HL, PL, SL
    from MigrationInfo import MigrationInfo


def back_migrate_labels(pds4_labels):
    # type: (Labels) -> Tuple[MigrationInfo, Labels]
    """
    Extract saved information from the migration task.  Use it to
    replace the old label items in the labels, and we trim any added
    padding back off.
    """
    migration_info, pds3_history_labels = remove_migration_task(
        pds4_labels.history_labels)

    pds3_system_labels = pds4_labels.system_labels.replace_label_items(
        migration_info.label_items)

    pds3_labels = make_trimmed_labels(pds3_system_labels,
                                      pds4_labels.property_labels,
                                      pds3_history_labels,
                                      pds4_labels.padding)
    return migration_info, pds3_labels


def back_migrate_image_area(pds4_tail, pds4_image_area):
    # type: (Tail, ImageArea) -> ImageArea
    """
    Move any binary labels from the tail back into the image area.
    """
    return ImageArea(pds4_tail.binary_header_at_tail,
                     pds4_tail.binary_prefixes_at_tail,
                     pds4_image_area.binary_image_lines)


def make_trimmed_labels(system_labels,
                        property_labels,
                        history_labels,
                        padding):
    # type: (SL, PL, HL, Optional[str]) -> Labels
    """
    Figure the original length of the labels and trim any added
    padding.
    """
    orig_lblsize = system_labels.get_int_value('LBLSIZE')

    # First, we figure out how long it would be with the PDS4 padding.
    dummy_length = sum([system_labels.to_byte_length(),
                        property_labels.to_byte_length(),
                        history_labels.to_byte_length(),
                        len(maybe_bs(padding))])
    # then we figure how much to trim.
    excess = dummy_length - orig_lblsize

    return Labels(system_labels,
                  property_labels,
                  history_labels,
                  padding[:-excess])


def back_migrate_eol_labels(orig_label_items, pds4_eol_labels):
    # type: (List[LabelItem], Labels) -> Labels
    """
    Replace old label items using information saved in the migration
    task.  Trim any added padding.
    """
    pds3_system_labels = pds4_eol_labels.system_labels.replace_label_items(
        orig_label_items)

    orig_lblsize = pds3_system_labels.get_int_value('LBLSIZE')

    return make_trimmed_labels(pds3_system_labels,
                               pds4_eol_labels.property_labels,
                               pds4_eol_labels.history_labels,
                               pds4_eol_labels.padding)


def back_migrate_tail(tail_length, pds4_tail):
    # type: (int, Tail) -> Tail
    """
    Remove any binary labels stored in the tail and trim any added
    padding.
    """
    trimmed_tail_bytes = pds4_tail.tail_bytes[:tail_length]
    if len(trimmed_tail_bytes) == 0:
        trimmed_tail_bytes = None
    return Tail(None, None, trimmed_tail_bytes)


def back_migrate_vicar_file(pds4_vicar_file):
    # type: (VicarFile) -> Tuple[Optional[str], VicarFile]
    """
    Extract the information stored in the migration task and use it to
    back-migrate the parts of the VICAR file.  Return the optionally
    saved original filepath and the VicarFile object.
    """
    migration_info, pds3_labels = back_migrate_labels(
        pds4_vicar_file.labels)

    pds3_image_area = back_migrate_image_area(
        pds4_vicar_file.tail,
        pds4_vicar_file.image_area)

    if pds4_vicar_file.eol_labels is None:
        pds3_eol_labels = None
    else:
        pds3_eol_labels = back_migrate_eol_labels(
            migration_info.eol_label_items,
            pds4_vicar_file.eol_labels)

    # Here we assure mypy that this is an int, not a string.
    tail_length = cast(int, migration_info.pds3_dict['TAIL_LENGTH'])
    pds3_tail = back_migrate_tail(tail_length, pds4_vicar_file.tail)

    try:
        # Here we assure mypy that this is a string, not an int.
        original_filepath = cast(str, migration_info.pds3_dict['FILEPATH'])
    except KeyError:
        original_filepath = None

    pds3_vicar_file = VicarFile(pds3_labels,
                                pds3_image_area,
                                pds3_eol_labels,
                                pds3_tail)
    return (original_filepath, pds3_vicar_file)
