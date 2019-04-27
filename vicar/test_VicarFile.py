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


_ENG = ['FOUR', 'FIVE', 'SIX', 'SEVEN']  # type: List[str]

_SPAN = ['cuatro', 'cinco', 'seis', 'siete']  # type: List[str]

_PORT = ['quatro', 'cinco', 'seis', 'sete']  # type: List[str]


def _mk_label_items_from_lists(keys, value_strs):
    # type: (List[str], List[str]) -> List[LabelItem]
    """
    Make LabelItems from a list of keys and a list of strings to be turned
    into StringValues.
    """
    return [LabelItem.create(k, StringValue.from_raw_string(v))
            for k, v in zip(keys, value_strs)]


def _mk_system_labels_from_lists(keys, value_strs):
    # type: (List[str], List[str]) -> SystemLabels
    """
    Make a SystemLabels whose LabelItems come from a list of keys and a list
    of strings to be turned into StringValues.
    """
    return SystemLabels(_mk_label_items_from_lists(keys, value_strs))


def _mk_sqr_system_labels():
    """
    Make a SystemLabels containing a bunch of LabelItems showing squares of
    integers.
    """

    def generate_label_items():
        for i in range(1, 100):
            yield LabelItem.create('SQR_%d' % i, IntegerValue(str(i * i)))

    return SystemLabels(list(generate_label_items()))


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
                              ]),
                _mk_sqr_system_labels(),
                _mk_system_labels_from_lists(_ENG, _SPAN)]

    def test_select_labels(self):
        sqr_system_labels = _mk_sqr_system_labels()

        keywords = ['SQR_20', 'SQR_3']
        selected = sqr_system_labels.select_labels(keywords)

        expected_1 = LabelItem.create('SQR_3', IntegerValue('9'))
        expected_2 = LabelItem.create('SQR_20', IntegerValue('400'))
        expected = [expected_1, expected_2]

        self.assertEqual(expected, selected)

        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            sqr_system_labels.select_labels(None)

    def test_replace_label_items(self):
        eng_to_span = _mk_system_labels_from_lists(_ENG, _SPAN)
        eng_to_port = _mk_system_labels_from_lists(_ENG, _PORT)

        # by changing a few words, we can turn Spanish into Portuguese
        port_replacements = [
            LabelItem.create('SEVEN', StringValue.from_raw_string('sete')),
            LabelItem.create('FOUR', StringValue.from_raw_string('quatro'))
        ]

        # check that it changed
        self.assertNotEqual(eng_to_span,
                            eng_to_span.replace_label_items(port_replacements))

        # check that it changed to the right thing
        self.assertEqual(eng_to_port,
                         eng_to_span.replace_label_items(port_replacements))

        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            eng_to_span.replace_label_items(None)

    def test_lookup_label_items(self):
        eng_to_span = _mk_system_labels_from_lists(_ENG, _SPAN)
        threes = eng_to_span.lookup_label_items('THREE')
        self.assertEqual([], threes)

        fours = eng_to_span.lookup_label_items('FOUR')
        self.assertEqual(1, len(fours))
        self.assertEqual(
            [LabelItem.create('FOUR', StringValue.from_raw_string('cuatro'))],
            fours)

        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            eng_to_span.lookup_label_items(None)
