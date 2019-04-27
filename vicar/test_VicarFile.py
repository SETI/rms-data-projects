import unittest

from VicarFile import *


class TestValue(unittest.TestCase):
    def test__eq__(self):
        self.assertTrue(IntegerValue('3') == IntegerValue('3'))
        self.assertFalse(IntegerValue('3') == RealValue('3.'))
        self.assertTrue(RealValue('3.') == RealValue('3.'))

    def test__str__(self):
        self.assertEqual("IntegerValue('3')", str(IntegerValue('3')))
        self.assertEqual("RealValue('3.')", str(RealValue('3.')))
        self.assertEqual(
            """StringValue("'I don''t like that.'")""",
            str(StringValue.from_raw_string("I don't like that.")))
