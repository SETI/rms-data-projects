from abc import ABCMeta, abstractmethod


class VicarSyntax(object):
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


def maybe_bs(byte_str):
    # type: (str) -> str
    """Convert an optional byte-string into a byte-string."""
    if byte_str is None:
        return ''
    else:
        return byte_str
