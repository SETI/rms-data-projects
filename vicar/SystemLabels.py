from typing import TYPE_CHECKING

from LabelItem import LabelItem
from Value import IntegerValue
from VicarSyntax import VicarSyntax

if TYPE_CHECKING:
    from typing import List, Tuple


def parse_system_labels(byte_str):
    # type: (str) -> Tuple[str, SystemLabels]
    """
    Parse the given bytes into SystemLabels.  Return a 2-tuple of any
    remaining bytes (must be empty, by construction) and the
    SystemLabels object.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular import
    return '', PlyParser.ply_parse_system_labels(byte_str)


def _lookup_label_items(keyword, label_items):
    # type: (str, List[LabelItem]) -> List[LabelItem]
    """
    Return a list of LabelItems with the given keyword.
    """
    assert keyword is not None
    return [label_item
            for label_item in label_items
            if label_item.keyword == keyword]


class SystemLabels(VicarSyntax):
    """
    An object representing the label items of the VICAR, excluding
    properties and tasks.
    """

    def __init__(self, label_items):
        # type: (List[LabelItem]) -> None
        VicarSyntax.__init__(self)
        assert label_items is not None
        for label_item in label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)

        assert len(_lookup_label_items('LBLSIZE', label_items)) == 1, \
            'must have LBLSIZE'

        self.label_items = label_items

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in self.label_items])
        return 'SystemLabels([%s])' % label_items_str

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, SystemLabels) and \
               self.label_items == other.label_items

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings.
        return sum([label_item.to_byte_length()
                    for label_item in self.label_items])

    def to_byte_string(self):
        return ''.join([label_item.to_byte_string()
                        for label_item in self.label_items])

    def lookup_label_items(self, keyword):
        # type: (str) -> List[LabelItem]
        """
        Return a list of LabelItems with the given keyword.
        """
        return _lookup_label_items(keyword, self.label_items)

    def get_binary_header_size(self):
        # type: () -> int
        """Return the size of any binary header or zero."""
        return self.get_int_value('RECSIZE') * self.get_int_value('NLB')

    def get_binary_prefix_width(self):
        # type: () -> int
        """Return the width of any binary prefix or zero."""
        return self.get_int_value('NBB')

    def get_image_height(self):
        # type: () -> int
        """Return the image height."""
        return self.get_int_value('N2') * self.get_int_value('N3')

    def get_image_width(self):
        # type: () -> int
        """Return the image width."""
        return self.get_int_value('RECSIZE') - self.get_int_value('NBB')

    def get_int_value(self, keyword, default=0):
        # type: (str, int) -> int
        """
        Look up a keyword in the LabelItems and return the
        corresponding integer value as an int.  If there are no matching
        LabelItems, return the default value.  If there are more than
        one, or if the value is not an IntegerValue, raise an exception.
        """
        labels = self.select_labels([keyword])
        len_labels = len(labels)
        assert len_labels <= 1
        if len_labels:
            value = labels[0].value
            assert isinstance(value, IntegerValue)
            return int(value.value_byte_string)
        else:
            return default

    def select_labels(self, keywords):
        # type: (List[str]) -> List[LabelItem]
        """
        Given a list of sought keywords, return all the LabelItems with those
        keywords.
        """
        assert keywords is not None

        return [label_item
                for label_item in self.label_items
                if label_item.keyword in keywords]

    def replace_label_items(self, replacements):
        # type: (List[LabelItem]) -> SystemLabels
        """
        Create a new SystemLabels from this one, but substitute replacement
        LabelItems for any current LabelItem with a matching keyword.
        """
        assert replacements is not None

        def maybe_replace(current_label_item):
            # type: (LabelItem) -> LabelItem
            """
            If there is a replacement LabelItem with the same keyword,
            return it.  Else return the current LabelItem.
            """
            for replacement_label_item in replacements:
                if current_label_item.keyword == \
                        replacement_label_item.keyword:
                    return replacement_label_item
            return current_label_item

        return SystemLabels([maybe_replace(label_item)
                             for label_item in self.label_items])

    @staticmethod
    def create_with_lblsize(lblsize, label_items):
        # type: (int, List[LabelItem]) -> SystemLabels
        """
        Prepend a LBLSIZE LabelItem to the others and create a
        SystemLabels.
        """
        assert not _lookup_label_items('LBLSIZE', label_items)
        return SystemLabels(
            [LabelItem.create('LBLSIZE', IntegerValue(str(lblsize)))] + \
            label_items)
