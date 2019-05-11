import random
import unittest

from typing import TYPE_CHECKING

from LabelItem import LabelItem
from MigrationInfo import MigrationInfo, dict_to_label_items, \
    dict_value_to_value, \
    label_items_to_dict, value_to_dict_value
from Value import IntegerValue, StringValue

if TYPE_CHECKING:
    from MigrationInfo import DICT, DICT_VALUE


def generate_dict_value():
    # type: () -> DICT_VALUE
    n = random.randint(0, 1)
    if n:
        return random.randint(1, 100)
    else:
        return 'X%d' % random.randint(1, 100)


def test_dict_value_to_value():
    # type: () -> None

    # Try this odd one
    dv = '/etc/passwd'
    value = dict_value_to_value(dv)
    assert dv == value_to_dict_value(value)

    # Try a bunch of generated ones
    for i in xrange(0, 1000):
        dict_value = generate_dict_value()
        value = dict_value_to_value(dict_value)
        assert dict_value == value_to_dict_value(value)


def test_dict_to_label_items():
    # type: () -> None
    prefix = 'FOOBAR'
    d = {'TAIL_LENGTH': 549, 'FILEPATH': '/etc/passwd'}  # type: DICT
    label_items = dict_to_label_items(prefix, d)
    assert d == label_items_to_dict(prefix, label_items)


def _create_migration_info():
    # type: () -> MigrationInfo
    main_label_items = [
        LabelItem.create('RECSIZE', IntegerValue.from_raw_integer(45)),
        LabelItem.create('LBLSIZE', IntegerValue.from_raw_integer(900)),
        LabelItem.create('HOMER',
                         StringValue.from_raw_string("Lisa's Dad"))
    ]

    eol_label_items = [
        LabelItem.create('LBLSIZE', IntegerValue.from_raw_integer(45))
    ]

    d = {'TAIL_LENGTH': 549, 'FILEPATH': '/etc/passwd'}  # type: DICT

    return MigrationInfo(main_label_items,
                         eol_label_items,
                         d)


class TestMigrationInfo(unittest.TestCase):

    def test_to_label_items(self):
        mi = _create_migration_info()
        label_items = mi.to_label_items()
        rt_mi = MigrationInfo.from_label_items(label_items)
        self.assertEqual(mi, rt_mi)

    def test_to_migration_task(self):
        mi = _create_migration_info()
        migration_task = mi.to_migration_task('<dat_tim>')
        rt_mi = MigrationInfo.from_migration_task(migration_task)
        self.assertEqual(mi, rt_mi)
