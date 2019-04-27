"""
Syntax for VICAR files.
"""
from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

from StringUtils import escape_byte_string

if TYPE_CHECKING:
    from typing import List


class _VicarBase(object):
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


##############################

class SystemLabels(_VicarBase):
    def __init__(self, label_items):
        # type: (List[LabelItem]) -> None
        _VicarBase.__init__(self)
        assert label_items is not None
        for label_item in label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)
        self.label_items = label_items

    def __str__(self):
        assert False, 'unimplemented'

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

    def lookup_label_items(self, keyword):
        # type: (str) -> List[LabelItem]
        """
        Return a list of LabelItems with the given keyword.
        """
        assert keyword is not None
        return [label_item
                for label_item in self.label_items
                if label_item.keyword == keyword]


##############################

class LabelItem(_VicarBase):
    """A key-value pair used for a VICAR label."""

    def __init__(self, initial_space, keyword, equals, value, trailing_space):
        # type: (str, str, str, Value, str) -> None
        _VicarBase.__init__(self)
        assert keyword is not None
        assert equals is not None
        assert value is not None
        assert isinstance(value, Value)

        self.initial_space = initial_space
        self.keyword = keyword
        self.equals = equals
        self.value = value
        self.trailing_space = trailing_space

    def __str__(self):
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

class Value(_VicarBase):
    """The value in a key-value pair in a label item."""
    __metaclass__ = ABCMeta

    def __init__(self, byte_str):
        # type: (str) -> None
        _VicarBase.__init__(self)
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
