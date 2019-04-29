import unittest

from ImageArea import *
from VicarSyntaxTests import VicarSyntaxTests

if TYPE_CHECKING:
    from typing import List


def _gen_line(width):
    # type: (int) -> str
    return width * '\0'


def _gen_bytes(width, height):
    # type: (int, int) -> List[str]
    return [_gen_line(width) for i in xrange(height)]


class TestImageArea(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            ImageArea(None, None, None)
        with self.assertRaises(Exception):
            ImageArea(None, None, _gen_bytes(0, 25))
        with self.assertRaises(Exception):
            ImageArea(None, None, _gen_bytes(25, 0))
        with self.assertRaises(Exception):
            ImageArea(None, _gen_bytes(2, 2), _gen_bytes(2, 3))
        with self.assertRaises(Exception):
            ImageArea(_gen_line(23), None, _gen_bytes(2, 3))
        with self.assertRaises(Exception):
            ImageArea(_gen_line(24), _gen_bytes(3, 3), _gen_bytes(2, 3))

    def args_for_test(self):
        return [ImageArea(None, None, _gen_bytes(1, 1)),
                ImageArea(_gen_line(10), None, _gen_bytes(5, 23)),
                ImageArea(_gen_line(20), _gen_bytes(3, 14), _gen_bytes(7, 14))]
