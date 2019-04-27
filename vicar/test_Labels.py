import unittest

from HistoryLabels import HistoryLabels
from Labels import *
from PropertyLabels import PropertyLabels
from SystemLabels import SystemLabels
from VicarSyntaxTests import VicarSyntaxTests

if TYPE_CHECKING:
    from VicarSyntax import VicarSyntax


class TestLabels(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        system_labels = SystemLabels([])
        property_labels = PropertyLabels([])
        history_labels = HistoryLabels([])
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            Labels(None, property_labels, history_labels, None)
        with self.assertRaises(Exception):
            Labels(system_labels, None, history_labels, None)
        with self.assertRaises(Exception):
            Labels(system_labels, property_labels, None, None)

        # verify that this does not raise
        Labels(system_labels, property_labels, history_labels, None)

    def args_for_test(self):
        system_labels = SystemLabels([])
        property_labels = PropertyLabels([])
        history_labels = HistoryLabels([])

        return [Labels(system_labels, property_labels, history_labels, None)]
