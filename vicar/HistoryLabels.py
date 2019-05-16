from typing import TYPE_CHECKING

from LabelItem import LabelItem
from MigrationConstants import MIGRATION_TASK_NAME, MIGRATION_USER_NAME
from StringUtils import escape_byte_string
from Value import StringValue
from VicarSyntax import VicarSyntax

if TYPE_CHECKING:
    from typing import List, Tuple


def parse_history_labels(byte_str):
    # type: (str) -> Tuple[str, HistoryLabels]
    """
    Parse the given bytes into HistoryLabels.  Return a 2-tuple of any
    remaining bytes (must be empty, by construction) and the
    HistoryLabels object.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular import
    return '', PlyParser.ply_parse_history_labels(byte_str)


class HistoryLabels(VicarSyntax):
    """
    An object representing the history labels of the VICAR file.  It
    is made up of a list of Tasks.
    """

    def __init__(self, tasks):
        # type: (List[Task]) -> None
        VicarSyntax.__init__(self)
        assert tasks is not None
        for task in tasks:
            assert task is not None
            assert isinstance(task, Task)
        self.tasks = tasks

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, HistoryLabels) and \
               self.tasks == other.tasks

    def __repr__(self):
        tasks_str = ', '.join([repr(task)
                               for task in
                               self.tasks])
        return 'HistoryLabels([%s])' % tasks_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([task.to_byte_length()
                    for task in self.tasks])

    def to_byte_string(self):
        return ''.join([task.to_byte_string()
                        for task in self.tasks])

    def has_migration_task(self):
        # type: () -> bool
        """
        Return True if the last task is a migration task.  It has to be the
        last task because we don't guarantee  we can backmigrate the file if
        it's been further processed.
        """
        return len(self.tasks) > 0 and self.tasks[-1].is_migration_task()


def parse_task(byte_str):
    # type: (str) -> Tuple[str, Task]
    import PlyParser  # to avoid circular import
    return '', PlyParser.ply_parse_task(byte_str)


class Task(VicarSyntax):
    """
    Represents a step in the processing history of the image.  It
    consists of a list of LabelItems.
    """

    def __init__(self, history_label_items):
        # type: (List[LabelItem]) -> None
        VicarSyntax.__init__(self)
        assert history_label_items is not None
        for label_item in history_label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)
        assert len(history_label_items) >= 3
        assert ['TASK', 'USER', 'DAT_TIM'] == [label_item.keyword for
                                               label_item in
                                               history_label_items[:3]]
        self.history_label_items = history_label_items

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, Task) and \
               self.history_label_items == other.history_label_items

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in
                                     self.history_label_items])
        return 'Task([%s])' % label_items_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([label_item.to_byte_length()
                    for label_item in self.history_label_items])

    def to_byte_string(self):
        return ''.join([label_item.to_byte_string()
                        for label_item in self.history_label_items])

    @staticmethod
    def create(task_name, user_name, dat_tim, *other_history_label_items):
        # type: (str, str, str, *LabelItem) -> Task
        """
        Create a task from its name, user name, datetime, and the
        other LabelItems it contains.
        """
        label_items = [
            LabelItem.create('TASK', StringValue.from_raw_string(task_name)),
            LabelItem.create('USER', StringValue.from_raw_string(user_name)),
            LabelItem.create('DAT_TIM',
                             StringValue.from_raw_string(dat_tim))]
        label_items.extend(other_history_label_items)
        return Task(label_items)

    @staticmethod
    def create_migration_task(dat_tim, *other_history_label_items):
        # type: (str, *LabelItem) -> Task
        """
        Create a migration task from its datetime and the other
        LabelItems it contains.
        """
        return Task.create(MIGRATION_TASK_NAME,
                           MIGRATION_USER_NAME,
                           dat_tim,
                           *other_history_label_items)

    def is_migration_task(self):
        # type: () -> bool
        """
        Returns True if this is a migration task created by this program.
        """
        label_items = self.history_label_items[:2]
        expected_tags = map(escape_byte_string,
                            [MIGRATION_TASK_NAME, MIGRATION_USER_NAME])
        return expected_tags == [label_item.value.value_byte_string
                                 for label_item in label_items]

    def get_migration_task_label_items(self):
        # type: () -> List[LabelItem]
        """
        Returns the label items with the content of the migration task.
        """
        assert self.is_migration_task()
        return self.history_label_items[3:]
