import unittest

from HistoryLabels import HistoryLabels
from ImageArea import ImageArea
from Labels import Labels
from PropertyLabels import PropertyLabels
from StringUtils import gen_block
from SystemLabels import SystemLabels
from Tail import Tail
from VicarFile import VicarFile
from VicarSyntaxTests import VicarSyntaxTests


class TestVicarFile(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        labels = Labels(SystemLabels([]),
                        PropertyLabels([]),
                        HistoryLabels([]),
                        None)
        image_area = ImageArea(None, None, gen_block(1, 1))
        eol_labels = Labels(SystemLabels([]),
                            PropertyLabels([]),
                            HistoryLabels([]),
                            None)
        tail = Tail(None, None, None)
        # verify that bad inputs raise an exception
        with self.assertRaises(Exception):
            VicarFile(None, image_area, eol_labels, tail)
        with self.assertRaises(Exception):
            VicarFile(labels, None, eol_labels, tail)
        with self.assertRaises(Exception):
            VicarFile(labels, image_area, eol_labels, None)

        # verify that this does not raise
        VicarFile(labels, image_area, None, tail)

    def args_for_test(self):
        labels = Labels(SystemLabels([]),
                        PropertyLabels([]),
                        HistoryLabels([]),
                        None)
        image_area = ImageArea(None, None, gen_block(1, 1))
        tail = Tail(None, None, None)
        return [VicarFile(labels, image_area, None, tail)]
