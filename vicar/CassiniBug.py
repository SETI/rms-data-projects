from typing import TYPE_CHECKING, cast

from HistoryLabels import HistoryLabels, Task
from LabelItem import LabelItem
from Labels import Labels
from SystemLabels import SystemLabels
from Value import StringValue
from VicarFile import VicarFile

if TYPE_CHECKING:
    from typing import Optional, Tuple


def _remove_lblsize_space(label_item):
    # type: (LabelItem) -> LabelItem
    trailing_space = label_item.trailing_space
    assert trailing_space and trailing_space[0] == ' ', \
        'No spaces to remove from LBLSIZE to fix Cassini bug'
    return LabelItem(label_item.initial_space,
                     label_item.keyword,
                     label_item.equals,
                     label_item.value,
                     trailing_space[1:])


def _remove_spaces(system_labels, space_count):
    # type: (SystemLabels, int) -> SystemLabels
    assert space_count == 1, \
        'Unexpected multiple (%d) errors in file' % (space_count,)
    # We assume the above is true and would like to know if we're
    # wrong.
    label_items = system_labels.label_items
    new_lblsize = _remove_lblsize_space(label_items[0])
    new_label_items = [new_lblsize] + label_items[1:]
    return SystemLabels(new_label_items)


def _is_bad_label_item(label_item):
    # type: (LabelItem) -> bool
    if isinstance(label_item.value, StringValue):
        # Does it have a single quote in the middle of its string?  We
        # already know the format of the error.
        return "FW'S " in label_item.value.value_byte_string
    else:
        return False


def fix_history_labels(history_labels):
    # type: (HistoryLabels) -> Tuple[HistoryLabels, int]
    space_count = [0]

    def fix_label_item(label_item):
        # type: (LabelItem) -> LabelItem
        if _is_bad_label_item(label_item):
            string_value = cast(StringValue, label_item.value)
            new_byte_str = string_value.value_byte_string.replace("FW'S",
                                                                  "FW''S")
            space_count[0] = space_count[0] + 1
            new_value = StringValue(new_byte_str)
            return LabelItem(label_item.initial_space,
                             label_item.keyword,
                             label_item.equals,
                             new_value,
                             label_item.trailing_space)
        else:
            return label_item

    def fix_task(tsk):
        # type: (Task) -> Task
        return Task([fix_label_item(label_item)
                     for label_item in tsk.history_label_items])

    fixed_history_labels = HistoryLabels([fix_task(task)
                                          for task in history_labels.tasks])
    if space_count[0]:
        return fixed_history_labels, space_count[0]
    else:
        return history_labels, 0


def fix_labels(labels):
    # type: (Optional[Labels]) -> Optional[Labels]
    if labels is None:
        return None
    (new_history_labels,
     spaces_to_remove) = fix_history_labels(labels.history_labels)
    if spaces_to_remove:
        new_system_labels = _remove_spaces(labels.system_labels,
                                           spaces_to_remove)

        # The size is checked by the constructor to be equal to
        # LBLSIZE.
        return Labels(new_system_labels,
                      labels.property_labels,
                      new_history_labels,
                      labels.padding)
    else:
        return None


def fix_cassini_bug(filepath, vicar_file):
    # type: (str, VicarFile) -> VicarFile
    fixed_labels = fix_labels(vicar_file.labels)
    fixed_eol_labels = fix_labels(vicar_file.eol_labels)
    if fixed_labels or fixed_eol_labels:
        print '**** Fixing Cassini bug in %s' % (filepath,)
        new_labels = fixed_labels or vicar_file.labels
        new_eol_labels = fixed_eol_labels or vicar_file.eol_labels
        return VicarFile(new_labels, vicar_file.image_area,
                         new_eol_labels, vicar_file.tail)
    else:
        return vicar_file
