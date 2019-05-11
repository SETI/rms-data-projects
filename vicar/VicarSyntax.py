from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from Parsers import Parser


class VicarSyntax(object):
    """Elements of VICAR syntax."""
    __metaclass__ = ABCMeta

    def syntax_parser(self):
        # type: () -> Optional[Parser]
        """
        Return a parser appropriate for this value's byte-string.
        Used for testing only.
        """
        return None

    @abstractmethod
    def to_byte_string(self):
        # type: () -> str
        """Convert the syntax to a byte-string."""
        pass

    def to_byte_length(self):
        # type: () -> int
        """Return the length of the byte-string for this syntax."""
        return len(self.to_byte_string())


def maybe_bs(byte_str):
    # type: (str) -> str
    """Convert an optional byte-string into a byte-string."""
    if byte_str is None:
        return ''
    else:
        return byte_str
