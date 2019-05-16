from typing import TYPE_CHECKING

from LabelItem import LabelItem
from VicarSyntax import VicarSyntax

if TYPE_CHECKING:
    from typing import Tuple


def parse_property_labels(byte_str):
    # type: (str) -> Tuple[str, PropertyLabels]
    """
    Parse the given bytes into PropertyLabels.  Return a 2-tuple of
    any remaining bytes (must be empty, by construction) and the
    PropertyLabels object.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular import
    return '', PlyParser.ply_parse_property_labels(byte_str)


class PropertyLabels(VicarSyntax):
    """Represents the list of properties of an image."""

    def __init__(self, properties):
        # type: (List[Property]) -> None
        VicarSyntax.__init__(self)
        assert properties is not None
        for property in properties:
            assert property is not None
            assert isinstance(property, Property)
        self.properties = properties

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, PropertyLabels) and \
               self.properties == other.properties

    def __repr__(self):
        properties_str = ', '.join([repr(property)
                                    for property in self.properties])
        return 'PropertyLabels([%s])' % properties_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([property.to_byte_length()
                    for property in self.properties])

    def to_byte_string(self):
        return ''.join([property.to_byte_string()
                        for property in self.properties])


def parse_property(byte_str):
    # type: (str) -> Tuple[str, Property]
    """
    Parse the given bytes into a Property.  Return a 2-tuple of
    any remaining bytes (must be empty, by construction) and the
    Property object.

    Parsing labels is context-independent (i.e., does not depend on
    what came earlier in the file), so we pass the parsing off to the
    PlyParser.
    """
    import PlyParser  # to avoid circular import
    return '', PlyParser.ply_parse_property(byte_str)


class Property(VicarSyntax):
    """Represents a property of the image in the image domain."""

    def __init__(self, property_label_items):
        # type: (List[LabelItem]) -> None
        VicarSyntax.__init__(self)
        assert property_label_items is not None
        assert len(property_label_items) > 0
        for label_item in property_label_items:
            assert label_item is not None
            assert isinstance(label_item, LabelItem)
        self.property_label_items = property_label_items

    def __eq__(self, other):
        return other is not None and \
               isinstance(other, Property) and \
               self.property_label_items == other.property_label_items

    def __repr__(self):
        label_items_str = ', '.join([repr(label_item)
                                     for label_item in
                                     self.property_label_items])
        return 'Property([%s])' % label_items_str

    def to_byte_length(self):
        # Summing is slightly more efficient than concatenating a bunch of
        # byte-strings then taking the length.
        return sum([label_item.to_byte_length()
                    for label_item in self.property_label_items])

    def to_byte_string(self):
        return ''.join([label_item.to_byte_string()
                        for label_item in self.property_label_items])
