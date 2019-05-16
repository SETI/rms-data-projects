import unittest

from LabelItem import LabelItem, parse_label_item
from Value import *
from VicarSyntaxTests import VicarSyntaxTests


def mk_sqr_label_items():
    """
    Make a bunch of LabelItems showing squares of
    integers.
    """
    return [LabelItem.create('SQR_%d' % i, IntegerValue(str(i * i)))
            for i in range(1, 100)]


class TestLabelItem(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        str_value = StringValue.from_raw_string('foo')
        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            LabelItem(None, None, '=', str_value, None)
        with self.assertRaises(Exception):
            LabelItem(None, 'KEYWORD', None, str_value, None)
        with self.assertRaises(Exception):
            LabelItem(None, 'KEYWORD', '=', None, None)
        with self.assertRaises(Exception):
            LabelItem(None, 'KEYWORD', '=', 'foo', None)

        # verify that this does not raise
        LabelItem(None, 'KEYWORD', ' =  ', str_value, ' ')

    def args_for_test(self):
        exotic_label_item = LabelItem('   ', 'SHERPA_HOME', '     =  ',
                                      StringValue.from_raw_string('Nepal'),
                                      '  ')
        return [LabelItem('    ', 'TRES', '=', IntegerValue('3'), '      '),
                exotic_label_item,
                exotic_label_item.to_saved_label_item('PREFIX_')
                ]

    def syntax_parser_for_arg(self, arg):
        return parse_label_item

    def test_to_saved_string_value(self):
        # works for basic LabelItems
        label_item = LabelItem.create('FIVE_IS_EVEN', IntegerValue('0'))
        self.assertEqual(StringValue("'FIVE_IS_EVEN=0 '"),
                         label_item.to_saved_string_value())

        # works for LabelItems with lots of whitespace
        label_item = LabelItem('   ', 'SHERPA_HOME', '     =  ',
                               StringValue.from_raw_string('Nepal'), '  ')
        self.assertEqual(StringValue(
            "'   SHERPA_HOME     =  ''Nepal''  '"),
            label_item.to_saved_string_value())

        # test roundtripping on all the test values
        for arg in self.args_for_test():
            saved_string_value = arg.to_saved_string_value()
            self.assertEqual(
                arg,
                LabelItem.from_saved_string_value(saved_string_value))

    def test_to_saved_label_item(self):
        label_item = LabelItem.create('FIVE_IS_EVEN', IntegerValue('0'))
        expected = LabelItem.create('MAIN_FIVE_IS_EVEN',
                                    StringValue("'FIVE_IS_EVEN=0 '"))
        self.assertEqual(expected, label_item.to_saved_label_item('MAIN_'))

        # test roundtripping on all the test values
        for arg in self.args_for_test():
            saved_label_item = arg.to_saved_label_item('PREFIX_')

            self.assertTrue(saved_label_item.keyword.startswith('PREFIX_'))
            self.assertEqual(
                arg,
                LabelItem.from_saved_label_item(saved_label_item))
