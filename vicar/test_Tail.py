import unittest

from StringUtils import generate_block, generate_line
from Tail import *
from VicarSyntaxTests import VicarSyntaxTests


class TestTail(unittest.TestCase, VicarSyntaxTests):
    def args_for_test(self):
        header = generate_line(25)
        prefixes = generate_block(7, 8)
        tail = generate_line(124)
        # all combinations are legal
        return [Tail(None, None, None),
                Tail(None, None, tail),
                Tail(None, prefixes, None),
                Tail(None, prefixes, tail)]

    def syntax_parser_for_arg(self, arg):
        if arg.has_binary_prefixes():
            # It's PDS4.
            if arg.binary_header_at_tail:
                hdr_bytes = len(arg.binary_header_at_tail)
            else:
                hdr_bytes = 0

            if arg.binary_prefixes_at_tail:
                img_height = len(arg.binary_prefixes_at_tail)
                prefix_width = len(arg.binary_prefixes_at_tail[0])
            else:
                img_height = 0
                prefix_width = 0

            return lambda (byte_str): parse_pds4_tail(hdr_bytes, img_height,
                                                      prefix_width, byte_str)
        else:
            # It's PDS3.
            return parse_pds3_tail

    def test_has_binary_prefixes(self):
        header = generate_line(2)
        prefixes = generate_block(1, 1)

        tail = Tail(None, None, None)
        self.assertFalse(tail.has_binary_prefixes())

        tail = Tail(None, prefixes, None)
        self.assertTrue(tail.has_binary_prefixes())
