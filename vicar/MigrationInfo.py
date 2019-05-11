from typing import TYPE_CHECKING

from LabelItem import LabelItem
from Value import IntegerValue, StringValue

if TYPE_CHECKING:
    from typing import Dict, List, Union
    from Value import Value

    DICT_VALUE = Union[str, int]
    DICT = Dict[str, DICT_VALUE]

_MAIN_PREFIX = '_MAIN'  # type: str
_EOL_PREFIX = '_EOL'  # type: str
_PDS3_PREFIX = '_PDS3'  # type: str


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
        # type: (List[LabelItem], List[LabelItem], Dict[str, int]) -> None
        self.label_items = label_items
        self.eol_label_items = eol_label_items
        self.pds3_dict = pds3_dict
