import unittest

from ImageArea import *
from StringUtils import generate_block, generate_line
from VicarSyntaxTests import VicarSyntaxTests

if TYPE_CHECKING:
    from typing import List


class TestImageArea(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            ImageArea(None, None, None)
        with self.assertRaises(Exception):
            ImageArea(None, None, generate_block(0, 25))
        with self.assertRaises(Exception):
            ImageArea(None, None, generate_block(25, 0))
        with self.assertRaises(Exception):
            ImageArea(None, generate_block(2, 2), generate_block(2, 3))
        with self.assertRaises(Exception):
            ImageArea(generate_line(23), None, generate_block(2, 3))
        with self.assertRaises(Exception):
            ImageArea(generate_line(24), generate_block(3, 3),
                      generate_block(2, 3))

    def args_for_test(self):
        return [ImageArea(None, None, generate_block(1, 1)),
                ImageArea(generate_line(10), None, generate_block(5, 23)),
                ImageArea(generate_line(20), generate_block(3, 14),
                          generate_block(7, 14))]

    def syntax_parser_for_arg(self, arg):
        if arg.binary_header is None:
            header_len = 0
        else:
            header_len = len(arg.binary_header)
        image_height = len(arg.binary_image_lines)
        if arg.binary_prefixes:
            prefix_width = len(arg.binary_prefixes[0])
        else:
            prefix_width = 0
        image_width = len(arg.binary_image_lines[0])
        return lambda (byte_str): parse_image_area(header_len,
                                                   image_height,
                                                   prefix_width,
                                                   image_width,
                                                   byte_str)

    def test_has_binary_prefixes(self):
        header = generate_line(2)
        prefixes = generate_block(1, 1)
        image_lines = generate_block(1, 1)

        image_area = ImageArea(None, None, image_lines)
        self.assertFalse(image_area.has_binary_prefixes())

        image_area = ImageArea(None, prefixes, image_lines)
        self.assertTrue(image_area.has_binary_prefixes())

        image_area = ImageArea(header, None, image_lines)
        self.assertFalse(image_area.has_binary_prefixes())

        image_area = ImageArea(header, prefixes, image_lines)
        self.assertTrue(image_area.has_binary_prefixes())
