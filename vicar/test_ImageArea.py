import unittest

from ImageArea import *
from StringUtils import gen_block, gen_line
from VicarSyntaxTests import VicarSyntaxTests

if TYPE_CHECKING:
    from typing import List


class TestImageArea(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            ImageArea(None, None, None)
        with self.assertRaises(Exception):
            ImageArea(None, None, gen_block(0, 25))
        with self.assertRaises(Exception):
            ImageArea(None, None, gen_block(25, 0))
        with self.assertRaises(Exception):
            ImageArea(None, gen_block(2, 2), gen_block(2, 3))
        with self.assertRaises(Exception):
            ImageArea(gen_line(23), None, gen_block(2, 3))
        with self.assertRaises(Exception):
            ImageArea(gen_line(24), gen_block(3, 3), gen_block(2, 3))

    def args_for_test(self):
        return [ImageArea(None, None, gen_block(1, 1)),
                ImageArea(gen_line(10), None, gen_block(5, 23)),
                ImageArea(gen_line(20), gen_block(3, 14), gen_block(7, 14))]

    def test_has_binary_labels(self):
        header = gen_line(2)
        prefixes = gen_block(1, 1)
        image_lines = gen_block(1, 1)

        image_area = ImageArea(None, None, image_lines)
        self.assertFalse(image_area.has_binary_labels())

        image_area = ImageArea(None, prefixes, image_lines)
        self.assertTrue(image_area.has_binary_labels())

        image_area = ImageArea(header, None, image_lines)
        self.assertTrue(image_area.has_binary_labels())

        image_area = ImageArea(header, prefixes, image_lines)
        self.assertTrue(image_area.has_binary_labels())