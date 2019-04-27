'''
Syntax for VICAR files.
'''
from abc import ABCMeta, abstractmethod

from StringUtils import escape_byte_string


class _VicarBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_byte_string(self):
        # type: () -> str
        '''Convert the syntax to a byte-string.'''
        pass

    def to_byte_length(self):
        # type: () -> int
        '''Return the length of the byte-string for this syntax.'''
        return len(self.to_byte_string())


##############################

class Value(_VicarBase):
    '''The value in a key-value pair in a label item.'''
    __metaclass__ = ABCMeta

    def __init__(self, str):
        # type: (str) -> None
        _VicarBase.__init__(self)
        assert str is not None
        self.value_byte_string = str

    def to_byte_string(self):
        return self.value_byte_string

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
               self.value_byte_string == other.value_byte_string

    def __str__(self):
        return '%s(%r)' % (type(self).__name__, self.value_byte_string)


###############

class IntegerValue(Value):
    '''An integer value.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)


class RealValue(Value):
    '''A real floating-point value.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)


class StringValue(Value):
    '''A string value.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)

    @staticmethod
    def from_raw_string(str):
        # type: (str) -> StringValue
        '''Programmatically create a StringValue from a raw Python string.'''
        return StringValue(escape_byte_string(str))


class IntegersValue(Value):
    '''An array of integer values.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)


class RealsValue(Value):
    '''An array of real, floating-point values.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)


class StringsValue(Value):
    '''An array of string values.'''

    def __init__(self, str):
        # type: (str) -> None
        Value.__init__(self, str)
