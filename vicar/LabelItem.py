from Value import StringValue, Value
from VicarSyntax import VicarSyntax, maybe_bs


class LabelItem(VicarSyntax):
    """A key-value pair used for a VICAR label."""

    def __init__(self, initial_space, keyword, equals, value,
                 trailing_space):
        # type: (str, str, str, Value, str) -> None
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
    def create(keyword, value):
        # type: (str, Value) -> LabelItem
        """
        Synthesize a LabelItem with a single trailing space as
        whitespace.
        """
        return LabelItem(None, keyword, '=', value, ' ')
