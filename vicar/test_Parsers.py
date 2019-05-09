import unittest

from Parsers import *


class TestParsers(unittest.TestCase):
    def testPure(self):
        byte_str = 'foobar'
        self.assertEqual(('foobar', 666), pure(666)('foobar'))

    def test_bind(self):
        def read_digit_as_int(byte_str):
            byte_str, res = bytes(1)(byte_str)
            return byte_str, int(res)

        # The first argument, a parser, reads a digit; the second
        # argument is a function that returns a parser that reads that
        # many bytes.
        context_sensitive_parser = bind(read_digit_as_int, bytes)

        # read four bytes since the input starts with 4
        self.assertEqual(('56789', '1234'),
                         context_sensitive_parser('4123456789'))
        # read zero bytes since the input starts with 0
        self.assertEqual(('123456789', ''),
                         context_sensitive_parser('0123456789'))
        # read nine bytes since the input starts with 9
        self.assertEqual(('', '123456789'),
                         context_sensitive_parser('9123456789'))

    def test_pmap(self):
        p = pure(3)
        f = lambda x: x * x
        byte_str = 'foobar'
        self.assertEqual(('foobar', 9), pmap(f, p)(byte_str))

    def test_bytes(self):
        byte_str = 'barfoo'
        with self.assertRaises(Exception):
            bytes(12)(byte_str)

        self.assertEqual(('foo', 'bar'), bytes(3)(byte_str))

    def test_rest_of_input(self):
        byte_str = 'foobar'
        byte_str, rst = bytes(3)(byte_str)
        self.assertEqual(('', 'bar'), rest_of_input(byte_str))

    def test_parse_all(self):
        byte_str = 'foobar'
        self.assertEqual('foobar', parse_all(bytes(6), byte_str))

        with self.assertRaises(Exception):
            parse_all(bytes(3), byte_str)

    def test_eof(self):
        # test at EOF
        byte_str = 'foobar'
        byte_str, res = bytes(6)(byte_str)
        byte_str, res = eof(byte_str)
        self.assertEqual((byte_str, res), ('', None))

        # test not at EOF
        byte_str = 'foobar'
        byte_str, res = bytes(3)(byte_str)
        with self.assertRaises(Exception):
            byte_str, res = eof(byte_str)
