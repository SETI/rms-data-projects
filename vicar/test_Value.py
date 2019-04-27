import unittest

from Value import *
from VicarSyntaxTests import VicarSyntaxTests


class TestValue(unittest.TestCase, VicarSyntaxTests):
    def test__eq__(self):
        self.assertTrue(IntegerValue('3') == IntegerValue('3'))
        self.assertFalse(IntegerValue('3') == RealValue('3.'))
        self.assertTrue(RealValue('3.') == RealValue('3.'))
        self.assertTrue(
            StringValue("'foo'") == StringValue.from_raw_string('foo'))

    def args_for_test(self):
        return [IntegerValue('3'), StringValue.from_raw_string('foobar'),
                RealValue('3.14159265')]

    def test__str__(self):
        self.assertEqual("IntegerValue('3')", str(IntegerValue('3')))
        self.assertEqual("RealValue('3.')", str(RealValue('3.')))
        self.assertEqual(
            """StringValue("'I don''t like that.'")""",
            str(StringValue.from_raw_string("I don't like that.")))
