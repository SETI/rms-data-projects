from typing import TYPE_CHECKING

from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import List, Optional, Tuple


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
