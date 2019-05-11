import random
import unittest

from typing import TYPE_CHECKING

from MigrationInfo import dict_to_label_items, dict_value_to_value, \
    label_items_to_dict, value_to_dict_value

if TYPE_CHECKING:
    from MigrationInfo import DICT, DICT_VALUE


class TestMigrationInfo(unittest.TestCase):
    pass


def generate_dict_value():
    # type: () -> DICT_VALUE
    n = random.randint(0, 1)
    if n:
        return random.randint(1, 100)
    else:
        return 'X%d' % random.randint(1, 100)


def test_dict_value_to_value():
    # type: () -> None
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
