import unittest

from typing import TYPE_CHECKING

from HistoryLabels import HistoryLabels
from ImageArea import ImageArea
from Labels import Labels
from PropertyLabels import PropertyLabels
from StringUtils import gen_block
from Tail import Tail
from VicarFile import VicarFile
from VicarSyntaxTests import VicarSyntaxTests
from test_SystemLabels import gen_system_labels

if TYPE_CHECKING:
    pass


def gen_labels(**kwargs):
    # type: (**int) -> Labels
    return Labels(gen_system_labels(**kwargs),
                  PropertyLabels([]),
                  HistoryLabels([]),
                  None)


class TestVicarFile(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        image_area = ImageArea(None, None, gen_block(1, 1))
        tail = Tail(None, None, None)
        # Verify that bad inputs raise an exception.
        # missing sections:
        with self.assertRaises(Exception):
            VicarFile(None, image_area, gen_labels({}), tail)
        with self.assertRaises(Exception):
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=1), None,
                      gen_labels(), tail)
        with self.assertRaises(Exception):
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=1),
                      image_area,
                      gen_labels(),
                      None)

        # inconsistent keywords:
        with self.assertRaises(Exception):
            # missing RECSIZE
            VicarFile(gen_labels(), image_area, gen_labels(), None)
        with self.assertRaises(Exception):
            # missing EOL
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                      image_area, gen_labels(),
                      None)
        with self.assertRaises(Exception):
            # zero EOL
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0),
                      image_area,
                      gen_labels(),
                      None)

        # verify that this does not raise
        VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                  image_area,
                  None,
                  tail)

    def args_for_test(self):
        image_area = ImageArea(None, None, gen_block(1, 1))
        tail = Tail(None, None, None)
        return [
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                      image_area,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0),
                      image_area,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=1),
                      image_area,
                      gen_labels(LBLSIZE=1),
                      tail)
        ]
