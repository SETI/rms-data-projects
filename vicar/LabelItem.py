from typing import TYPE_CHECKING

from Value import IntegerValue, StringValue, Value
from VicarSyntax import VicarSyntax, maybe_bs

if TYPE_CHECKING:
    from typing import Optional, Tuple


def parse_label_item(byte_str):
    # type: (str) -> Tuple[str, LabelItem]
    """
    Parse the given bytes into LabelItem.  Return a 2-tuple of any
    remaining bytes (must be empty, by construction) and the LabelItem
    object.

    This parses LabelItems that are part of the body and excludes
    special keywords that act as landmarks for specific locations in
    the file such as LBLSIZE, DAT_TIM, PROPERTY, TASK.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular imports
    return '', PlyParser.ply_parse_label_item(byte_str)


def parse_general_label_item(byte_str):
    # type: (str) -> Tuple[str, LabelItem]
    """
    Parse the given bytes into LabelItem.  Return a 2-tuple of any
    remaining bytes (must be empty, by construction) and the LabelItem
    object.

    This parses LabelItems with any keyword.  This is needed to
    restore any LabelItems saved into the migration task, which might
    include landmark LabelItems.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular imports
    return '', PlyParser.ply_parse_general_label_item(byte_str)


class LabelItem(VicarSyntax):
    """
    A key-value pair used for a VICAR label.  Because migration and
    back-migration need to maintain byte-for-byte equality, we make
    the extra effort to store all whitespace.
    """

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
        """
        Convert a string value back into a LabelItem.
        """
        from Parsers import parse_all  # avoid circular imports
        assert isinstance(value, StringValue)
        return parse_all(parse_general_label_item, value.to_raw_string())

    @staticmethod
    def from_saved_label_item(label_item):
        # type: (LabelItem) -> LabelItem
        """
        Convert a saved LabelItem back into the original LabelItem.
        """
        return LabelItem.from_saved_string_value(label_item.value)

    @staticmethod
    def create(keyword, value):
        # type: (str, Value) -> LabelItem
        """
        Synthesize a LabelItem with a single trailing space as
        whitespace.  A convenience function.
        """
        return LabelItem(None, keyword, '=', value, ' ')

    @staticmethod
    def create_int_item(keyword, value):
        # type: (str, int) -> LabelItem
        """
        Create a LabelItem from a keyword and an int.  A convenience
        function.
        """
        return LabelItem.create(keyword, IntegerValue.from_raw_integer(value))

    @staticmethod
    def create_lblsize_item(n=0):
        # type: (int) -> LabelItem
        """
        Create a LBLSIZE LabelItem from an integer.  Since the size of
        the labels depends on the size of the LBLSIZE LabelItem, its
        size is fixed; this breaks the logical circularity.

        We typically add a LBLSIZE item with a wrong value, calculate
        the actual size, then go back and patch it.
        """
        int_str = '%-10d' % n
        return LabelItem.create('LBLSIZE', IntegerValue(int_str))
