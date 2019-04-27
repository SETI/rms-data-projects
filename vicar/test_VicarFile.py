import unittest

from VicarFile import *
from VicarFile import _VicarBase

if TYPE_CHECKING:
    from typing import Iterable


class VicarBaseTest(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def args_for_test_to_byte_length(self):
        # type: () -> Iterable[_VicarBase]
        pass

    def assertEqual(self, first, second, msg=None):
        assert False, 'should be overridden'

    def test_to_byte_length(self):
        # type: () -> None
        for arg in self.args_for_test_to_byte_length():
            self.assertEqual(len(arg.to_byte_string()), arg.to_byte_length())


class TestValue(unittest.TestCase, VicarBaseTest):
    def test__eq__(self):
        self.assertTrue(IntegerValue('3') == IntegerValue('3'))
        self.assertFalse(IntegerValue('3') == RealValue('3.'))
        self.assertTrue(RealValue('3.') == RealValue('3.'))
        self.assertTrue(
            StringValue("'foo'") == StringValue.from_raw_string('foo'))

    def args_for_test_to_byte_length(self):
        return [IntegerValue('3'), StringValue.from_raw_string('foobar'),
                RealValue('3.14159265')]

    def test__str__(self):
        self.assertEqual("IntegerValue('3')", str(IntegerValue('3')))
        self.assertEqual("RealValue('3.')", str(RealValue('3.')))
        self.assertEqual(
            """StringValue("'I don''t like that.'")""",
            str(StringValue.from_raw_string("I don't like that.")))


class TestLabelItem(unittest.TestCase, VicarBaseTest):
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

    def args_for_test_to_byte_length(self):
        exotic_label_item = LabelItem('   ', 'SHERPA_HOME', ' \t   =\n\n',
                                      StringValue.from_raw_string('Nepal'),
                                      '  ')
        return [LabelItem('    ', 'TRES', '=', IntegerValue('3'), '      '),
                exotic_label_item,
                exotic_label_item.to_saved_label_item('PREFIX_')
                ]

    def test_to_saved_string_value(self):
        # works for basic LabelItems
        label_item = LabelItem.create('FIVE_IS_EVEN', IntegerValue('0'))
        self.assertEqual(StringValue("'FIVE_IS_EVEN=0 '"),
                         label_item.to_saved_string_value())

        # works for LabelItems with crazy whitespace
        label_item = LabelItem('   ', 'SHERPA_HOME', ' \t   =\n\n',
                               StringValue.from_raw_string('Nepal'), '  ')
        self.assertEqual(StringValue(
            "'   SHERPA_HOME \t   =\n\n''Nepal''  '"),
            label_item.to_saved_string_value())

    def test_to_saved_label_item(self):
        label_item = LabelItem.create('FIVE_IS_EVEN', IntegerValue('0'))
        expected = LabelItem.create('MAIN_FIVE_IS_EVEN',
                                    StringValue("'FIVE_IS_EVEN=0 '"))
        self.assertEqual(expected, label_item.to_saved_label_item('MAIN_'))


class TestSystemLabels(unittest.TestCase, VicarBaseTest):
    def test__init__(self):
        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            SystemLabels(None)
        with self.assertRaises(Exception):
            SystemLabels([None])
        with self.assertRaises(Exception):
            SystemLabels([1, 2, 3])

        # verify that this does not raise
        SystemLabels([LabelItem.create('ONE',
                                       StringValue.from_raw_string('uno')),
                      LabelItem.create('TWO',
                                       IntegerValue('2')),
                      ])

    def args_for_test_to_byte_length(self):
        return [SystemLabels([LabelItem.create('ONE',
                                               StringValue.from_raw_string(
                                                   'uno')),
                              LabelItem.create('TWO',
                                               IntegerValue('2')),
                              ])]

    def test_select_labels(self):
        def generate_label_items():
            for i in range(3, 25):
                yield LabelItem.create('SQR_%d' % i, IntegerValue(str(i * i)))

        system_labels = SystemLabels(list(generate_label_items()))
        keywords = ['SQR_20', 'SQR_3']
        selected = system_labels.select_labels(keywords)

        expected_1 = LabelItem.create('SQR_3', IntegerValue('9'))
        expected_2 = LabelItem.create('SQR_20', IntegerValue('400'))
        expected = [expected_1, expected_2]

        self.assertEqual(expected, selected)
