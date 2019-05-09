from typing import TYPE_CHECKING

from Parsers import bytes, repeat
from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


def parse_image_area(header_len,
                     image_height,
                     prefix_width,
                     image_width,
                     byte_str):
    # type: (int, int, int, int, str) -> Tuple[str, ImageArea]
    print '**** header_len=%d, image_height=%d, ' \
          'prefix_width=%d, image_width=%d' % (header_len,
                                               image_height,
                                               prefix_width,
                                               image_width)

    # Parse the header as necessary;
    if header_len > 0:
        byte_str, header = bytes(header_len)(byte_str)
    else:
        header = None

    if prefix_width > 0:
        # If there are binary prefixes, parse the prefixes and the image.

        def parse_prefixed_image_line(byte_str):
            # type: (str) -> Tuple[str, Tuple[str,str]]
            """
            Parse a prefixed image line as a tuple of the prefix and
            image_line.
            """
            byte_str, prefix = bytes(prefix_width)(byte_str)
            byte_str, image_line = bytes(image_width)(byte_str)
            return byte_str, (prefix, image_line)

        byte_str, prefixed_image_lines = \
            repeat(image_height, parse_prefixed_image_line)(byte_str)

        # prefixed_image_lines is a list of tuples of prefix and
        # image_line.  But we want a list the prefixes and a list of
        # the image_lines, so we have to zip the result.
        prefixes, image_lines = zip(*prefixed_image_lines)

        # Furthermore, zip() produces tuples; we want lists.
        prefixes = list(prefixes)
        image_lines = list(image_lines)
        # All good now.
    else:
        # Just parse the image.
        prefixes = None
        byte_str, image_lines = repeat(image_height,
                                       bytes(image_width))(byte_str)

    return byte_str, ImageArea(header, prefixes, image_lines)


class ImageArea(VicarSyntax):
    def __init__(self,
                 binary_header,
                 binary_prefixes,
                 binary_image_lines):
        # type: (Optional[str], Optional[List[str]], List[str]) -> None
        VicarSyntax.__init__(self)

        def assert_widths_are_consistent(str_list):
            # type: (List[str]) -> None
            """
            Assert that the lengths of the strings in the list are all
            the same.
            """
            if str_list:
                for str_ in str_list:
                    assert str_ is not None
                    assert len(str_) == len(str_list[0])

        def get_dimensions(str_list):
            # type: (List[str]) -> Tuple[int, int]
            """Returns the width and the height of the image."""
            assert_widths_are_consistent(str_list)
            if str_list:
                height = len(str_list)
                assert height > 0
                width = len(str_list[0])
                assert width > 0
                return width, height
            else:
                return 0, 0

        assert binary_image_lines
        image_width, image_height = get_dimensions(binary_image_lines)
        prefixes_width, prefixes_height = get_dimensions(binary_prefixes)

        if binary_header is None:
            header_len = 0
        else:
            header_len = len(binary_header)
        assert header_len % (prefixes_width + image_width) == 0
        if binary_prefixes is not None:
            assert prefixes_height == image_height

        self.binary_header = binary_header
        self.binary_prefixes = binary_prefixes
        self.binary_image_lines = binary_image_lines

    def __eq__(self, other):
        return [self.binary_header,
                self.binary_prefixes,
                self.binary_image_lines] == [other.binary_header,
                                             other.binary_prefixes,
                                             other.binary_image_lines]

    def __repr__(self):
        return 'ImageArea(%r, %r, %r)' % (self.binary_header,
                                          self.binary_prefixes,
                                          self.binary_image_lines
                                          )

    def to_byte_length(self):
        if self.binary_prefixes:
            prefix_width = len(self.binary_prefixes[0])
        else:
            prefix_width = 0

        image_width = len(self.binary_image_lines[0])
        width = prefix_width + image_width

        image_height = len(self.binary_image_lines)
        if self.binary_header is None:
            header_height = 0
        else:
            header_height = len(self.binary_header) / width
        height = image_height + header_height

        return width * height

    def to_byte_string(self):
        if self.binary_prefixes:
            prefixed_lines = [prefix + line
                              for (prefix, line)
                              in zip(self.binary_prefixes,
                                     self.binary_image_lines)]
        else:
            prefixed_lines = self.binary_image_lines

        prefixed_image = ''.join(prefixed_lines)
        header = maybe_bs(self.binary_header)

        return header + prefixed_image

    def has_binary_labels(self):
        # type: () -> bool
        """
        Return True if there are a binary header or binary prefixes.
        """
        return self.binary_header is not None or \
               self.binary_prefixes is not None

    def implicit_nbb_value(self):
        # type: () ->  int
        """Return what the NBB value should be for this ImageArea."""
        if self.binary_prefixes:
            return len(self.binary_prefixes[0])
        else:
            return 0

    def implicit_nlb_value(self):
        # type: () ->  int
        """Return what the NLB value should be for this ImageArea."""
        if self.binary_header:
            return len(self.binary_header) / self.implicit_recsize_value()
        else:
            return 0

    def implicit_recsize_value(self):
        # type: () ->  int
        """Return what the RECSIZE value should be for this ImageArea."""
        return self.implicit_nbb_value() + len(self.binary_image_lines[0])
