from abc import ABCMeta

from StringUtils import escape_byte_string, unescape_byte_string
from VicarSyntax import VicarSyntax


class Value(VicarSyntax):
    """The value in a key-value pair in a label item."""
    __metaclass__ = ABCMeta

    def __init__(self, byte_str):
        # type: (str) -> None
        VicarSyntax.__init__(self)
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

    def to_raw_integer(self):
        # type: () -> int
        """Extract the integer value."""
        return int(self.value_byte_string)

    @staticmethod
    def from_raw_integer(n):
        # type: (int) -> IntegerValue
        """Create an IntegerValue from a Python int."""
        return IntegerValue(str(n))


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

    def to_raw_string(self):
        # type: () -> str
        """Extract the string value."""
        return unescape_byte_string(self.value_byte_string)

    @staticmethod
    def from_raw_string(byte_str):
        # type: (str) -> StringValue
        """Create a StringValue from a raw Python string."""
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
