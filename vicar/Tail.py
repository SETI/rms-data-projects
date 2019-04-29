from typing import TYPE_CHECKING

from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import List, Optional


class Tail(VicarSyntax):
    def __init__(self,
                 binary_header_at_tail,
                 binary_prefixes_at_tail,
                 tail_bytes):
        # type: (Optional[str], Optional[List[str]], Optional[str]) -> None
        VicarSyntax.__init__(self)
        if binary_prefixes_at_tail:
            for binary_prefix in binary_prefixes_at_tail:
                assert binary_prefix is not None
        self.binary_header_at_tail = binary_header_at_tail
        self.binary_prefixes_at_tail = binary_prefixes_at_tail
        self.tail_bytes = tail_bytes

    def __eq__(self, other):
        return [self.binary_header_at_tail,
                self.binary_prefixes_at_tail,
                self.tail_bytes] == [other.binary_header_at_tail,
                                     other.binary_prefixes_at_tail,
                                     other.tail_bytes]

    def __repr__(self):
        return 'Tail(%r, %r, %r)' % (self.binary_header_at_tail,
                                     self.binary_prefixes_at_tail,
                                     self.tail_bytes)

    def to_byte_string(self):
        if self.binary_prefixes_at_tail:
            binary_prefixes = ''.join(self.binary_prefixes_at_tail)
        else:
            binary_prefixes = ''
        return ''.join([maybe_bs(self.binary_header_at_tail),
                        binary_prefixes,
                        maybe_bs(self.tail_bytes)])

    def has_binary_labels(self):
        # type: () -> bool
        """
        Return True if a binary header or binary prefixes are stored
        in the tail.
        """
        return self.binary_header_at_tail is not None or \
               self.binary_prefixes_at_tail is not None
