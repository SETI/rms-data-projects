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
                Tail(None, prefixes, tail),
                Tail(header, None, None),
                Tail(header, None, tail),
                Tail(header, prefixes, None),
                Tail(header, prefixes, tail)]

    def test_has_binary_labels(self):
        header = generate_line(2)
        prefixes = generate_block(1, 1)

        tail = Tail(None, None, None)
        self.assertFalse(tail.has_binary_labels())

        tail = Tail(None, prefixes, None)
        self.assertTrue(tail.has_binary_labels())

        tail = Tail(header, None, None)
        self.assertTrue(tail.has_binary_labels())

        tail = Tail(header, prefixes, None)
        self.assertTrue(tail.has_binary_labels())
