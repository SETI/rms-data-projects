from typing import TYPE_CHECKING

from Value import StringValue, Value
from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import Optional, Tuple


def parse_label_item(byte_str):
    # type: (str) -> Tuple[str, LabelItem]
    import PlyParser  # to avoid circular imports
    return '', PlyParser.ply_parse_label_item(byte_str)


def parse_general_label_item(byte_str):
    # type: (str) -> Tuple[str, LabelItem]

    # TODO This will fail on a few reserved keywords.  Need to fix
    # this in PlyParser.

    import PlyParser  # to avoid circular imports
    return '', PlyParser.ply_parse_label_item(byte_str)


class LabelItem(VicarSyntax):
    """A key-value pair used for a VICAR label."""

    def __init__(self, initial_space, keyword, equals, value,
                 trailing_space):
        # type: (Optional[str], str, str, Value, Optional[str]) -> None
        VicarSyntax.__init__(self)
        assert keyword is not None
        assert equals is not None
        assert value is not None
        assert isinstance(value, Value)

        self.initial_space = initial_space
        self.keyword = keyword
        self.equals = equals
        self.value = value
        self.trailing_space = trailing_space

    def __repr__(self):
        return 'LabelItem(%r, %r, %r, %s, %r)' % \
               (self.initial_space, self.keyword, self.equals,
                self.value, self.trailing_space)

    def __eq__(self, other):
        return isinstance(other, LabelItem) and \
               self.to_byte_string() == other.to_byte_string()

    def to_byte_string(self):
        return ''.join([maybe_bs(self.initial_space),
                        self.keyword,
                        self.equals,
                        self.value.to_byte_string(),
                        maybe_bs(self.trailing_space)])

    def to_saved_string_value(self):
        # type: () -> StringValue
        """
        Convert the LabelItem to a byte-string, then convert that
        byte-string into a string value.  Useful for saving the
        original contents of a LabelItem, including its whitespace.
        """
        return StringValue.from_raw_string(self.to_byte_string())

    def to_saved_label_item(self, prefix):
        # type: (str) -> LabelItem
        """
        Convert the LabelItem to a byte-string, then convert that
        byte-string into a string value.  Prepend the prefix to the
        original item's keyword, and using that and the string value,
        create a new LabelItem.  Useful for saving the original
        contents of a LabelItem, including its whitespace.
        """
        return LabelItem.create(prefix + self.keyword,
                                self.to_saved_string_value())

    @staticmethod
    def from_saved_string_value(value):
        # type: (Value) -> LabelItem
        from Parsers import parse_all  # avoid circular imports
        assert isinstance(value, StringValue)
        return parse_all(parse_general_label_item, value.to_raw_string())

    @staticmethod
    def from_saved_label_item(label_item):
        # type: (LabelItem) -> LabelItem
        return LabelItem.from_saved_string_value(label_item.value)

    @staticmethod
    def create(keyword, value):
        # type: (str, Value) -> LabelItem
        """
        Synthesize a LabelItem with a single trailing space as
        whitespace.
        """
        return LabelItem(None, keyword, '=', value, ' ')
