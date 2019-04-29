import unittest

from typing import TYPE_CHECKING

from HistoryLabels import HistoryLabels
from ImageArea import ImageArea
from Labels import Labels
from PropertyLabels import PropertyLabels
from StringUtils import gen_block, gen_line
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
        image_area_h = ImageArea(gen_line(1), None, gen_block(1, 1))
        image_area_p = ImageArea(None, gen_block(1, 1), gen_block(1, 1))
        image_area_hp = ImageArea(gen_line(2),
                                  gen_block(1, 1),
                                  gen_block(1, 1))
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
            VicarFile(gen_labels(), image_area, gen_labels(), tail)
        with self.assertRaises(Exception):
            # missing EOL
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                      image_area, gen_labels(),
                      tail)
        with self.assertRaises(Exception):
            # zero EOL
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0),
                      image_area,
                      gen_labels(),
                      tail)
        with self.assertRaises(Exception):
            # nonzero NBB but no binary prefixes
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NBB=1),
                      image_area,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # zero NBB but with binary prefixes
            VicarFile(gen_labels(RECSIZE=2, LBLSIZE=1, NBB=0),
                      image_area_p,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # nonzero NLB but no binary header
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=1),
                      image_area,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # zero NLB but with binary header
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=0),
                      image_area_h,
                      None,
                      tail)

        with self.assertRaises(Exception):
            # RECSIZE of 1 but ImageArea says 2
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=0),
                      image_area_p,
                      None,
                      tail)

        # verify that these do not raise
        VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                  image_area,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=2, LBLSIZE=1, NBB=1),
                  image_area_p,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=1),
                  image_area_h,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=2, LBLSIZE=1, NBB=1, NLB=1),
                  image_area_hp,
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
