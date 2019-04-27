import unittest

from LabelItem import LabelItem
from PropertyLabels import Property, PropertyLabels
from Value import RealValue, StringValue
from VicarSyntaxTests import VicarSyntaxTests


def _mk_map_property():
    # type: () -> Property
    """
    Make a sample property.  Example taken from the VICAR File Format,
    https://www-mipl.jpl.nasa.gov/external/VICAR_file_fmt.pdf
    """
    return Property(
        [LabelItem.create('PROPERTY', StringValue.from_raw_string('MAP')),
         LabelItem.create('PROJECTION',
                          StringValue.from_raw_string('mercator')),
         LabelItem.create('LAT', RealValue('34.2')),
         LabelItem.create('LON', RealValue('177.221'))])


class TestProperty(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            Property(None)
        with self.assertRaises(Exception):
            Property([None])
        with self.assertRaises(Exception):
            Property([1, 2, 3])

        # verify that this does not raise
        _mk_map_property()

    def args_for_test(self):
        return [Property([]),
                _mk_map_property()]


class TestPropertyLabels(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            PropertyLabels(None)
        with self.assertRaises(Exception):
            PropertyLabels([None])
        with self.assertRaises(Exception):
            PropertyLabels([1, 2, 3])

    def args_for_test(self):
        return [PropertyLabels([]),
                PropertyLabels([_mk_map_property()])]
