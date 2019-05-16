import unittest

from Parsers import *


class TestParsers(unittest.TestCase):
    def test_bytes(self):
        byte_str = 'barfoo'
        with self.assertRaises(Exception):
            bytes(12)(byte_str)

        self.assertEqual(('foo', 'bar'), bytes(3)(byte_str))

    def test_rest_of_input(self):
        byte_str = 'foobar'
        byte_str, _three_bytes = bytes(3)(byte_str)
        self.assertEqual(('', 'bar'), rest_of_input(byte_str))

    def test_parse_all(self):
        byte_str = 'foobar'
        self.assertEqual('foobar', parse_all(bytes(6), byte_str))

        with self.assertRaises(Exception):
            parse_all(bytes(3), byte_str)
