from typing import TYPE_CHECKING

from HistoryLabels import HistoryLabels, Task
from LabelItem import LabelItem
from Value import IntegerValue, StringValue

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Union
    from Value import Value

    DICT_VALUE = Union[str, int]
    DICT = Dict[str, DICT_VALUE]

MAIN_PREFIX = 'MAIN_'  # type: str

EOL_PREFIX = 'EOL_'  # type: str

PDS3_PREFIX = 'PDS3_'  # type: str


def dict_value_to_value(v):
    # type: (DICT_VALUE) -> Value
    """
    Convert a string or an integer into a Value.
    """
    if isinstance(v, int):
        return IntegerValue.from_raw_integer(v)
    elif isinstance(v, str):
        return StringValue.from_raw_string(v)
    else:
        assert False, 'dict_value_to_value: must be integer or string'


def value_to_dict_value(v):
    # type: (Value) -> DICT_VALUE
    """
    Convert a Value into a string or an integer.
    """
    if isinstance(v, IntegerValue):
        return v.to_raw_integer()
    elif isinstance(v, StringValue):
        return v.to_raw_string()
    else:
        assert False, 'value_to_dict_value: must be integer or string Value'


def dict_to_label_items(prefix, d):
    # type: (str, DICT) -> List[LabelItem]
    """
    Convert a dictionary containing strings and integers into a list
    of label items.  Prefix the given string to each dictionary key to
    make the LabelItem's keyword.
    """
    return [LabelItem.create(prefix + k, dict_value_to_value(d[k]))
            for k in sorted(d.keys())]


def label_items_to_dict(prefix, label_items):
    # type: (str, List[LabelItem]) -> (DICT)
    """
    Convert some LabelItems into a dictionary containing strings and
    integers.  Use the keyword prefix to determine which items to
    extract, and remove the prefix to make the dictionary's keys.
    """
    prefix_len = len(prefix)

    def strip_prefix(kw):
        # type: (str) -> str
        assert kw.startswith(prefix)
        return kw[prefix_len:]

    return {strip_prefix(label_item.keyword):
                value_to_dict_value(label_item.value)
            for label_item in label_items}


class MigrationInfo(object):
    """
    A temporary object containing information needed for migration,
    consisting of selected LabelItem from both the main label section
    and the EOL label section, plus a dictionary of extra
    miscellaneous integer and string values.
    """

    def __init__(self, label_items, eol_label_items, pds3_dict):
        # type: (List[LabelItem], List[LabelItem], DICT) -> None
        self.label_items = label_items
        self.eol_label_items = eol_label_items
        self.pds3_dict = pds3_dict

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, MigrationInfo) and \
               (self.label_items, self.eol_label_items, self.pds3_dict) == \
               (other.label_items, other.eol_label_items, other.pds3_dict)

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in self.label_items])
        eol_label_items_str = ', '.join([repr(label_item)
                                         for label_item in
                                         self.eol_label_items])
        return 'MigrationInfo([%r], [%r], %r)' % (label_items_str,
                                                  eol_label_items_str,
                                                  self.pds3_dict)

    def to_label_items(self):
        # type: () -> List[LabelItem]
        """Encode the migration info into a list of LabelItems."""
        return [label_item.to_saved_label_item(MAIN_PREFIX)
                for label_item in self.label_items] + \
               [label_item.to_saved_label_item(EOL_PREFIX)
                for label_item in self.eol_label_items] + \
               dict_to_label_items(PDS3_PREFIX, self.pds3_dict)

    @staticmethod
    def from_label_items(label_items):
        """Decode a list of LabelItems into the original migration info."""

        # type: (List[LabelItem]) -> MigrationInfo
        def filter_by_prefix(prefix, label_items):
            # type: (str, List[LabelItem]) -> List[LabelItem]
            return [label_item
                    for label_item in label_items
                    if label_item.keyword.startswith(prefix)]

        main_label_items = map(LabelItem.from_saved_label_item,
                               filter_by_prefix(MAIN_PREFIX, label_items))
        eol_label_items = map(LabelItem.from_saved_label_item,
                              filter_by_prefix(EOL_PREFIX, label_items))
        d = label_items_to_dict(PDS3_PREFIX,
                                filter_by_prefix(PDS3_PREFIX, label_items))

        return MigrationInfo(main_label_items,
                             eol_label_items,
                             d)

    def to_migration_task(self, dat_tim):
        # type: (str) -> Task
        """
        Create a migration task from the migration info.  The DAT_TIM
        is used as a timestamp.
        """
        return Task.create_migration_task(dat_tim, *self.to_label_items())

    @staticmethod
    def from_migration_task(task):
        # type: (Task) -> MigrationInfo
        """
        Reconstruct the migration info from a migration task.
        """
        assert task.is_migration_task()
        return MigrationInfo.from_label_items(
            task.get_migration_task_label_items())


def add_migration_task(dat_tim, migration_info, history_labels):
    # type: (str, MigrationInfo, HistoryLabels) -> HistoryLabels
    """
    Use the migration info to build a task and insert it into the
    HistoryLabels.
    """
    migration_task = migration_info.to_migration_task(dat_tim)
    return HistoryLabels(history_labels.tasks + [migration_task])


def remove_migration_task(history_labels):
    # type: (HistoryLabels) -> Tuple[MigrationInfo, HistoryLabels]
    """
    Remove the migration task from the HistoryLabels, extract the info
    from it, and return a 2-tuple of the migration info and the
    HistoryLabels without the task.
    """
    assert history_labels.has_migration_task()
    tasks = history_labels.tasks
    return (MigrationInfo.from_migration_task(tasks[-1]),
            HistoryLabels(tasks[:-1]))
