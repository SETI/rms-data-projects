"""
Syntax for VICAR files.
"""
from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

from MigrationConstants import MIGRATION_TASK_NAME, MIGRATION_USER_NAME
from StringUtils import escape_byte_string

if TYPE_CHECKING:
    from typing import List


class _VicarSyntax(object):
    """Elements of VICAR syntax."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_byte_string(self):
        # type: () -> str
        """Convert the syntax to a byte-string."""
        pass

    def to_byte_length(self):
        # type: () -> int
        """Return the length of the byte-string for this syntax."""
        return len(self.to_byte_string())

    def to_padded_byte_string(self, recsize):
        """
        Convert the syntax to a byte-string and pad it with NULs until
        its length is a multiple of the given record size.
        """
        assert recsize > 0
        excess = self.to_byte_length() % recsize
        if excess == 0:
            padding = ''
        else:
            padding = (recsize - excess) * '\0'
        return self.to_byte_string() + padding


##############################

class SystemLabels(_VicarSyntax):
    def __init__(self, label_items):
        # type: (List[LabelItem]) -> None
        _VicarSyntax.__init__(self)
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

class PropertyLabels(_VicarSyntax):
    """Represents the list of properties of an image."""

    def __init__(self, properties):
        # type: (List[Property]) -> None
        _VicarSyntax.__init__(self)
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


class Property(_VicarSyntax):
    """Represents a property of the image in the image domain."""

    def __init__(self, property_label_items):
        # type: (List[LabelItem]) -> None
        _VicarSyntax.__init__(self)
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

class Task(_VicarSyntax):
    """Represents a step in the processing history of the image."""

    def __init__(self, history_label_items):
        # type: (List[LabelItem]) -> None
        _VicarSyntax.__init__(self)
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

class LabelItem(_VicarSyntax):
    """A key-value pair used for a VICAR label."""

    def __init__(self, initial_space, keyword, equals, value, trailing_space):
        # type: (str, str, str, Value, str) -> None
        _VicarSyntax.__init__(self)
        assert keyword is not None
        assert equals is not None
        assert value is not None
        assert isinstance(value, Value)

        self.initial_space = initial_space
        self.keyword = keyword
        self.equals = equals
        self.value = value
        self.trailing_space = trailing_space

    def __repr__(self):
        return 'LabelItem(%r, %r, %r, %s, %r)' % \
               (self.initial_space, self.keyword, self.equals,
                self.value, self.trailing_space)

    def __eq__(self, other):
        return isinstance(other, LabelItem) and \
               self.to_byte_string() == other.to_byte_string()

    def to_byte_string(self):
        return ''.join([_maybe_bs(self.initial_space),
                        self.keyword,
                        self.equals,
                        self.value.to_byte_string(),
                        _maybe_bs(self.trailing_space)])

    def to_saved_string_value(self):
        # type: () -> StringValue
        """
        Convert the LabelItem to a byte-string, then convert that
        byte-string into a string value.  Useful for saving the
        original contents of a LabelItem, including its whitespace.
        """
        return StringValue.from_raw_string(self.to_byte_string())

    def to_saved_label_item(self, prefix):
        # type: (str) -> LabelItem
        """
        Convert the LabelItem to a byte-string, then convert that
        byte-string into a string value.  Prepend the prefix to the
        original item's keyword, and using that and the string value,
        create a new LabelItem.  Useful for saving the original
        contents of a LabelItem, including its whitespace.
        """
        return LabelItem.create(prefix + self.keyword,
                                self.to_saved_string_value())

    @staticmethod
    def create(keyword, value):
        # type: (str, Value) -> LabelItem
        """
        Synthesize a LabelItem with a single trailing space as
        whitespace.
        """
        return LabelItem(None, keyword, '=', value, ' ')


##############################

class Value(_VicarSyntax):
    """The value in a key-value pair in a label item."""
    __metaclass__ = ABCMeta

    def __init__(self, byte_str):
        # type: (str) -> None
        _VicarSyntax.__init__(self)
        assert byte_str is not None
        assert isinstance(byte_str, str)
        self.value_byte_string = byte_str

    def to_byte_string(self):
        return self.value_byte_string

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.value_byte_string == other.value_byte_string

    def __repr__(self):
        return '%s(%r)' % (type(self).__name__, self.value_byte_string)


###############

class IntegerValue(Value):
    """An integer value."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)


class RealValue(Value):
    """A real floating-point value."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)


class StringValue(Value):
    """A string value."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)

    @staticmethod
    def from_raw_string(byte_str):
        # type: (str) -> StringValue
        """
        Programmatically create a StringValue from a raw Python string.
        """
        return StringValue(escape_byte_string(byte_str))


class IntegersValue(Value):
    """An array of integer values."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)


class RealsValue(Value):
    """An array of real, floating-point values."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)


class StringsValue(Value):
    """An array of string values."""

    def __init__(self, byte_str):
        # type: (str) -> None
        Value.__init__(self, byte_str)


############################################################

def _maybe_bs(byte_str):
    # type: (str) -> str
    """Convert a possibly missing byte-string into a byte string."""
    if byte_str is None:
        return ''
    else:
        return byte_str
