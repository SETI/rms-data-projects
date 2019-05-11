from typing import TYPE_CHECKING

from LabelItem import LabelItem
from Value import IntegerValue, StringValue

if TYPE_CHECKING:
    from typing import Dict, List, Union
    from Value import Value

    DICT_VALUE = Union[str, int]
    DICT = Dict[str, DICT_VALUE]

_MAIN_PREFIX = 'MAIN_'  # type: str

_EOL_PREFIX = 'EOL_'  # type: str

_PDS3_PREFIX = 'PDS3_'  # type: str


def dict_value_to_value(v):
    # type: (DICT_VALUE) -> Value
    if isinstance(v, int):
        return IntegerValue.from_raw_integer(v)
    elif isinstance(v, str):
        return StringValue.from_raw_string(v)
    else:
        assert False, 'dict_value_to_value: must be integer or string'


def value_to_dict_value(v):
    # type: (Value) -> DICT_VALUE
    if isinstance(v, IntegerValue):
        return v.to_raw_integer()
    elif isinstance(v, StringValue):
        return v.to_raw_string()
    else:
        assert False, 'value_to_dict_value: must be integer or string Value'


def dict_to_label_items(prefix, d):
    # type: (str, DICT) -> List[LabelItem]
    return [LabelItem.create(prefix + k, dict_value_to_value(d[k]))
            for k in sorted(d.keys())]


def label_items_to_dict(prefix, label_items):
    # type: (str, List[LabelItem]) -> (DICT)
    prefix_len = len(prefix)

    def strip_prefix(kw):
        # type: (str) -> str
        assert kw.startswith(prefix)
        return kw[prefix_len:]

    return {strip_prefix(label_item.keyword):
                value_to_dict_value(label_item.value)
            for label_item in label_items}


class MigrationInfo(object):
    def __init__(self, label_items, eol_label_items, pds3_dict):
        # type: (List[LabelItem], List[LabelItem], DICT) -> None
        self.label_items = label_items
        self.eol_label_items = eol_label_items
        self.pds3_dict = pds3_dict

    def __eq__(self, other):
        return other is not None and \
            isinstance(other, MigrationInfo) and \
            (self.label_items, self.eol_label_items, self.pds3_dict) == \
            (other.label_items, other.eol_label_items, other.pds3_dict)

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in self.label_items])
        eol_label_items_str = ', '.join([repr(label_item)
                                     for label_item in self.eol_label_items])
        return 'MigrationInfo([%r], [%r], %r)' % (label_items_str,
                                                  eol_label_items_str,
                                                  self.pds3_dict)

    def to_label_items(self):
        # type: () -> List[LabelItem]
        return [label_item.to_saved_label_item(_MAIN_PREFIX)
                for label_item in self.label_items] + \
                [label_item.to_saved_label_item(_EOL_PREFIX)
                 for label_item in self.eol_label_items] + \
                 dict_to_label_items(_PDS3_PREFIX, self.pds3_dict)

    @staticmethod
    def from_label_items(label_items):
        # type: (List[LabelItem]) -> MigrationInfo
        def filter_by_prefix(prefix, label_items):
            # type: (str, List[LabelItem]) -> List[LabelItem]
            return [label_item
                    for label_item in label_items
                    if label_item.keyword.startswith(prefix)]

        main_label_items = map(LabelItem.from_saved_label_item,
                               filter_by_prefix(_MAIN_PREFIX, label_items))
        eol_label_items = map(LabelItem.from_saved_label_item,
                              filter_by_prefix(_EOL_PREFIX, label_items))
        d = label_items_to_dict(_PDS3_PREFIX,
                                filter_by_prefix(_PDS3_PREFIX, label_items))

        return MigrationInfo(main_label_items,
                             eol_label_items,
                             d)
