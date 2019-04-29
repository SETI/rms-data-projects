import unittest

from SystemLabels import *
from Value import IntegerValue, StringValue
from VicarSyntaxTests import VicarSyntaxTests
from test_LabelItem import mk_sqr_label_items

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
    return SystemLabels.create_with_lblsize(1, _mk_label_items_from_lists(keys,
                                                                          value_strs))


def _mk_sqr_system_labels():
    """
    Make a SystemLabels containing a bunch of LabelItems showing squares of
    integers.
    """
    return SystemLabels.create_with_lblsize(1, mk_sqr_label_items())


def gen_label_items(**kwargs):
    # type: (**int) -> List[LabelItem]
    def make_label_item(k, v):
        # type: (str, int) -> LabelItem
        return LabelItem.create(k, IntegerValue(str(v)))

    # LBLSIZE is always the first keyword.
    return [make_label_item('LBLSIZE', kwargs['LBLSIZE'])] + \
        [make_label_item(k, v)
         for k, v in kwargs.items()
         if k != 'LBLSIZE']


def gen_system_labels(**kwargs):
    # type: (**int) -> SystemLabels
    return SystemLabels(gen_label_items(**kwargs))


class TestSystemLabels(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise exception
        with self.assertRaises(Exception):
            SystemLabels(None)
        with self.assertRaises(Exception):
            SystemLabels([None])
        with self.assertRaises(Exception):
            SystemLabels([1, 2, 3])

        # verify that this does not raise
        SystemLabels([LabelItem.create('LBLSIZE',
                                       IntegerValue('1')),
                      LabelItem.create('ONE',
                                       StringValue.from_raw_string('uno')),
                      LabelItem.create('TWO',
                                       IntegerValue('2')),
                      ])

    def args_for_test(self):
        return [SystemLabels.create_with_lblsize(1, []),
                SystemLabels.create_with_lblsize(1, [LabelItem.create('ONE',
                                                                      StringValue.from_raw_string(
                                                                          'uno')),
                                                     LabelItem.create('TWO',
                                                                      IntegerValue(
                                                                          '2')),
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

    def test_get_int_value(self):
        system_labels = SystemLabels.create_with_lblsize(1, [])
        self.assertEqual(0, system_labels.get_int_value('FOO'))
        self.assertEqual(666, system_labels.get_int_value('FOO', 666))

        system_labels = SystemLabels.create_with_lblsize(1, [
            LabelItem.create('ONE', IntegerValue('1')),
            LabelItem.create('AMBIGUOUS', IntegerValue('123')),
            LabelItem.create('AMBIGUOUS', IntegerValue('456')),
            LabelItem.create('STRING', StringValue.from_raw_string('foobar'))
        ])

        self.assertEqual(0, system_labels.get_int_value('FOO'))
        self.assertEqual(666, system_labels.get_int_value('FOO', 666))
        self.assertEqual(1, system_labels.get_int_value('ONE'))
        self.assertEqual(1, system_labels.get_int_value('ONE', 666))

        with self.assertRaises(Exception):
            # multiple labels match
            system_labels.get_int_value('AMBIGUOUS')

        with self.assertRaises(Exception):
            # a mistyped value: it's string
            system_labels.get_int_value('STRING')
        with self.assertRaises(Exception):
            # a default answer doesn't fix a mistyped value
            system_labels.get_int_value('STRING', 666)
