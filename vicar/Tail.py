from typing import TYPE_CHECKING

from Parsers import bytes, rest_of_input
from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


def parse_pds3_tail(byte_str):
    # type: (str) -> Tuple[str, Tail]
    """Parse a PDS3 tail.  All the bytes go into the tail of the tail."""
    byte_str2, res = rest_of_input(byte_str)
    if len(res) == 0:
        res = None
    return (byte_str2, Tail(None, None, res))


def parse_pds4_tail(hdr_bytes, img_height, prefix_width, byte_str):
    # type: (int, int, int, str) -> Tuple[str, Tail]
    """
    Parse a PDS4 tail.  Some of the bytes may be parts of the binary
    header, some may be binary prefixes.  The rest goes into the
    tail_bytes.  We determine what goes where from the integer
    arguments: the length of the header and the dimensions of the
    binary prefixes.
    """
    if hdr_bytes > 0:
        byte_str, hdr = bytes(hdr_bytes)(byte_str)
    else:
        hdr = None

    if prefix_width > 0:
        prefs = list()  # type: List[str]
        for i in xrange(img_height):
            byte_str, line = bytes(prefix_width)(byte_str)
            prefs.append(line)
    else:
        prefs = None
    byte_str, rst = rest_of_input(byte_str)
    if len(rst) == 0:
        rst = None
    return byte_str, Tail(hdr, prefs, rst)


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

    def syntax_parser(self):
        if self.has_binary_labels():
            # It's PDS4.
            if self.binary_header_at_tail:
                hdr_bytes = len(self.binary_header_at_tail)
            else:
                hdr_bytes = 0
            if self.binary_prefixes_at_tail:
                img_height = len(self.binary_prefixes_at_tail)
                prefix_width = len(self.binary_prefixes_at_tail[0])
            else:
                img_height = 0
                prefix_width = 0
            return lambda (byte_str): parse_pds4_tail(hdr_bytes, img_height,
                                                      prefix_width, byte_str)
        else:
            # It's PDS3.
            return parse_pds3_tail

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
