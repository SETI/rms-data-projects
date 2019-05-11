from typing import TYPE_CHECKING

from ImageArea import ImageArea
from MigrationInfo import MigrationInfo
from Tail import Tail
from VicarFile import VicarFile

if TYPE_CHECKING:
    from typing import List, Optional
    from LabelItem import LabelItem
    from Labels import Labels
    from MigrationInfo import DICT


def migrate_labels(pds3_label):
    # type: (Labels) -> Labels
    assert False, 'unimplemented'


def migrate_image_area(pds3_image_area):
    # type: (ImageArea) -> ImageArea
    return ImageArea(None, None, pds3_image_area.binary_image_lines)


def migrate_eol_labels(pds3_eol_labels):
    # type: (Labels) -> Labels
    if pds3_eol_labels is None:
        return None

    assert False, 'unimplemented'


def migrate_tail(pds3_image_area, pds3_tail):
    # type: (ImageArea, Tail) -> Tail
    def pad_bytes_at_tail():
        # type: () -> str
        assert False, 'unimplemented'

    padded_bytes_at_tail = pad_bytes_at_tail()

    return Tail(pds3_image_area.binary_header,
                pds3_image_area.binary_prefixes,
                padded_bytes_at_tail)


def select_label_items(keywords, labels):
    # type: (List[str], Labels) -> List[LabelItem]
    if labels is None:
        return []
    else:
        return [label_item
                for label_item in labels.system_labels.label_items
                if label_item.keyword in keywords]


def build_migration_info(original_filepath, pds3_vicar_file):
    # type: (str, VicarFile) -> MigrationInfo
    def select_main_label_items():
        # type: () -> List[LabelItem]
        keywords = ['RECSIZE', 'LBLSIZE', 'NBB', 'NLB']
        return select_label_items(keywords, pds3_vicar_file.labels)

    def select_eol_label_items():
        # type: () -> List[LabelItem]
        keywords = ['LBLSIZE']
        return select_label_items(keywords, pds3_vicar_file.eol_labels)

    def build_dictionary():
        # type: () -> DICT
        tail_bytes = pds3_vicar_file.tail.tail_bytes
        if tail_bytes is None:
            tail_length = 0
        else:
            tail_length = len(tail_bytes)

        dictionary = {'TAIL_LENGTH': tail_length}  # type: DICT
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

    pds4_labels = migrate_labels(pds3_vicar_file.labels)
    pds4_image_area = migrate_image_area(pds3_vicar_file.image_area)
    pds4_eol_labels = migrate_eol_labels(pds3_vicar_file.eol_labels)
    pds4_tail = migrate_tail(pds3_vicar_file.image_area,
                             pds3_vicar_file.tail)
    return VicarFile(pds4_labels, pds4_image_area, pds4_eol_labels, pds4_tail)
