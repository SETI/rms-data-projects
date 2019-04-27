"""
Syntax for VICAR files.
"""
from abc import ABCMeta, abstractmethod

from StringUtils import escape_byte_string


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
