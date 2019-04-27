"""
Syntax for VICAR files.
"""

from typing import TYPE_CHECKING

from LabelItem import LabelItem
from MigrationConstants import MIGRATION_TASK_NAME, MIGRATION_USER_NAME
from Value import *
from VicarSyntax import maybe_bs

if TYPE_CHECKING:
    from typing import List


##############################

class SystemLabels(VicarSyntax):
    def __init__(self, label_items):
        # type: (List[LabelItem]) -> None
        VicarSyntax.__init__(self)
        assert label_items is not None
        for label_item in label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)
        self.label_items = label_items

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in self.label_items])
        return 'SystemLabels([%s])' % label_items_str

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, SystemLabels) and \
               self.label_items == other.label_items

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings.
        return sum([label_item.to_byte_length()
                    for label_item in self.label_items])

    def to_byte_string(self):
        return ''.join([label_item.to_byte_string()
                        for label_item in self.label_items])

    def lookup_label_items(self, keyword):
        # type: (str) -> List[LabelItem]
        """
        Return a list of LabelItems with the given keyword.
        """
        assert keyword is not None
        return [label_item
                for label_item in self.label_items
                if label_item.keyword == keyword]

    def get_int_value(self, keyword, default=0):
        # type: (str, int) -> int
        """
        Look up a keyword in the LabelItems and return the
        corresponding integer value as an int.  If there are no matching
        LabelItems, return the default value.  If there are more than
        one, or if the value is not an IntegerValue, raise an exception.
        """
        labels = self.select_labels([keyword])
        len_labels = len(labels)
        assert len_labels <= 1
        if len_labels == 0:
            return default
        elif len_labels == 1:
            value = labels[0].value
            assert isinstance(value, IntegerValue)
            return int(value.value_byte_string)

    def select_labels(self, keywords):
        # type: (List[str]) -> List[LabelItem]
        """
        Given a list of sought keywords, return all the LabelItems with those
        keywords.
        """
        assert keywords is not None

        return [label_item
                for label_item in self.label_items
                if label_item.keyword in keywords]

    def replace_label_items(self, replacements):
        # type: (List[LabelItem]) -> SystemLabels
        """
        Create a new SystemLabels from this one, but substitute replacement
        LabelItems for any current LabelItem with a matching keyword.
        """
        assert replacements is not None

        def maybe_replace(current_label_item):
            # type: (LabelItem) -> LabelItem
            """
            If there is a replacement LabelItem with the same keyword,
            return it.  Else return the current LabelItem.
            """
            for replacement_label_item in replacements:
                if current_label_item.keyword == \
                        replacement_label_item.keyword:
                    return replacement_label_item
            return current_label_item

        return SystemLabels([maybe_replace(label_item)
                             for label_item in self.label_items])


##############################

class PropertyLabels(VicarSyntax):
    """Represents the list of properties of an image."""

    def __init__(self, properties):
        # type: (List[Property]) -> None
        VicarSyntax.__init__(self)
        assert properties is not None
        for property in properties:
            assert property is not None
            assert isinstance(property, Property)
        self.properties = properties

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, PropertyLabels) and \
               self.properties == other.properties

    def __repr__(self):
        properties_str = ', '.join([repr(property)
                                    for property in self.properties])
        return 'PropertyLabels([%s])' % properties_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([property.to_byte_length()
                    for property in self.properties])

    def to_byte_string(self):
        return ''.join([property.to_byte_string()
                        for property in self.properties])


class Property(VicarSyntax):
    """Represents a property of the image in the image domain."""

    def __init__(self, property_label_items):
        # type: (List[LabelItem]) -> None
        VicarSyntax.__init__(self)
        assert property_label_items is not None
        for label_item in property_label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)
        self.property_label_items = property_label_items

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, Property) and \
               self.property_label_items == other.property_label_items

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in
                                     self.property_label_items])
        return 'Property([%s])' % label_items_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([label_item.to_byte_length()
                    for label_item in self.property_label_items])

    def to_byte_string(self):
        return ''.join([label_item.to_byte_string()
                        for label_item in self.property_label_items])


##############################

class HistoryLabels(VicarSyntax):
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
        return self.tasks and self.tasks[-1].is_migration_task()


class Task(VicarSyntax):
    """Represents a step in the processing history of the image."""

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
        # type: (str, str, str, List[LabelItem]) -> Task
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
        # type: (str, List[LabelItem]) -> Task
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


##############################
class Labels(VicarSyntax):
    """A series of keyword-value pairs divided into three sections."""

    def __init__(self, system_labels, property_labels, history_labels,
                 padding):
        assert system_labels is not None
        assert property_labels is not None
        assert history_labels is not None
        self.system_labels = system_labels
        self.property_labels = property_labels
        self.history_labels = history_labels
        self.padding = padding

    def __eq__(self, other):
        return [self.system_labels,
                self.property_labels,
                self.history_labels,
                maybe_bs(self.padding)] == [other.system_labels,
                                            other.property_labels,
                                            other.history_labels,
                                            maybe_bs(other.padding)]

    def __repr__(self):
        items_str = ', '.join([repr(item)
                               for item in [self.system_labels,
                                            self.property_labels,
                                            self.history_labels,
                                            self.padding]])
        return 'Labels(%s)' % items_str

    def to_byte_length(self):
        return sum([self.system_labels.to_byte_length(),
                    self.property_labels.to_byte_length(),
                    self.history_labels.to_byte_length(),
                    len(maybe_bs(self.padding))])

    def to_byte_string(self):
        return ''.join([self.system_labels.to_byte_string(),
                        self.property_labels.to_byte_string(),
                        self.history_labels.to_byte_string(),
                        maybe_bs(self.padding)])

    def get_int_value(self, keyword, default=0):
        # type: (str, int) -> int
        """
        Look up a keyword in the system LabelItems and return the
        corresponding integer value as an int.  If there are no
        matching LabelItems, return the default value.  If there are
        more than one, or if the value is not an IntegerValue, raise
        an exception.
        """
        return self.system_labels.get_int_value(keyword, default)

    def has_migration_task(self):
        # type: () -> bool
        """
        Return True if the last task in the HistoryLabels is s a
        migration task.  It has to be the last task because we don't
        guarantee we can backmigrate the file if it's been further
        processed.
        """
        return self.history_labels.has_migration_task()
