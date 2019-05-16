import unittest

from HistoryLabels import HistoryLabels
from ImageArea import ImageArea
from Labels import Labels
from PropertyLabels import PropertyLabels
from StringUtils import generate_block, generate_line
from Tail import Tail
from VicarFile import VicarFile, parse_vicar_file
from VicarSyntaxTests import VicarSyntaxTests
from test_SystemLabels import gen_system_labels


def gen_labels(**kwargs):
    # type: (**int) -> Labels
    return Labels.create_labels_with_adjusted_lblsize(
        gen_system_labels(**kwargs),
        PropertyLabels([]),
        HistoryLabels([]),
        None)


def gen_eol_labels(recsize, **kwargs):
    # type: (int, **int) -> Labels
    return Labels.create_eol_labels_with_adjusted_lblsize(
        recsize,
        gen_system_labels(**kwargs),
        PropertyLabels([]),
        HistoryLabels([]),
        None)


class TestVicarFile(unittest.TestCase, VicarSyntaxTests):
    def test__init__(self):
        image_area = ImageArea(None, None, generate_block(1, 1))
        image_area_h = ImageArea(generate_line(1), None, generate_block(1, 1))
        image_area_p = ImageArea(None, generate_block(1, 1),
                                 generate_block(1, 1))
        image_area_hp = ImageArea(generate_line(2),
                                  generate_block(1, 1),
                                  generate_block(1, 1))
        tail = Tail(None, None, None)

        # Verify that bad inputs raise an exception.
        # missing sections:
        with self.assertRaises(Exception):
            VicarFile(None, image_area, gen_labels({}), tail)
        with self.assertRaises(Exception):
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, EOL=1), None,
                      gen_labels(1, ), tail)
        with self.assertRaises(Exception):
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, EOL=1),
                      image_area,
                      gen_labels(1),
                      None)

        # inconsistent keywords:
        with self.assertRaises(Exception):
            # missing RECSIZE
            VicarFile(gen_labels(1),
                      image_area,
                      gen_labels(1),
                      tail)
        with self.assertRaises(Exception):
            # missing EOL
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1),
                      image_area,
                      gen_labels(1),
                      tail)
        with self.assertRaises(Exception):
            # zero EOL
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0),
                      image_area,
                      gen_labels(1),
                      tail)
        with self.assertRaises(Exception):
            # nonzero NBB but no binary prefixes
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, NBB=1),
                      image_area,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # zero NBB but with binary prefixes
            VicarFile(gen_labels(2, RECSIZE=2, LBLSIZE=2, NBB=0),
                      image_area_p,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # nonzero NLB but no binary header
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, NLB=1),
                      image_area,
                      None,
                      tail)
        with self.assertRaises(Exception):
            # zero NLB but with binary header
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, NLB=0),
                      image_area_h,
                      None,
                      tail)

        with self.assertRaises(Exception):
            # RECSIZE of 1 but ImageArea says 2
            VicarFile(gen_labels(1, RECSIZE=1, LBLSIZE=1, NLB=0),
                      image_area_p,
                      None,
                      tail)

        # two binary_prefixes
        with self.assertRaises(Exception):
            VicarFile(gen_labels(2, RECSIZE=2, LBLSIZE=2, NBB=1),
                      image_area_p,
                      None,
                      Tail(None, generate_block(2, 2), None))

        # two binary_headers
        with self.assertRaises(Exception):
            VicarFile(gen_labels(2, RECSIZE=1, LBLSIZE=2, NLB=1),
                      image_area_h,
                      None,
                      Tail(generate_line(2), None, None))

        # TODO Create a case with both binary labels and a
        # MigrationTask.

        # verify that these do not raise
        VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1),
                  image_area,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, NBB=1),
                  image_area_p,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=1),
                  image_area_h,
                  None,
                  tail)
        VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, NBB=1, NLB=1),
                  image_area_hp,
                  None,
                  tail)

    def args_for_test(self):
        image_area = ImageArea(None, None, generate_block(1, 1))
        image_area_h = ImageArea(generate_line(1), None, generate_block(1, 1))
        image_area_p = ImageArea(None,
                                 generate_block(1, 1),
                                 generate_block(1, 1))
        image_area_hp = ImageArea(generate_line(2),
                                  generate_block(1, 1),
                                  generate_block(1, 1))
        tail = Tail(None, None, None)
        return [
            VicarFile(
                gen_labels(RECSIZE=1, LBLSIZE=1),
                image_area,
                None,
                tail),
            VicarFile(
                gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0),
                image_area,
                None,
                tail),
            VicarFile(
                gen_labels(RECSIZE=1, LBLSIZE=1, EOL=1),
                image_area,
                gen_eol_labels(1, LBLSIZE=1),
                tail),
            VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, NBB=1),
                      image_area_p,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, EOL=0, NBB=1),
                      image_area_p,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, EOL=1, NBB=1),
                      image_area_p,
                      gen_eol_labels(2, LBLSIZE=2),
                      tail),
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, NLB=1),
                      image_area_h,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=0, NLB=1),
                      image_area_h,
                      None,
                      tail),
            VicarFile(gen_labels(RECSIZE=1, LBLSIZE=1, EOL=1, NLB=1),
                      image_area_h,
                      gen_eol_labels(1, LBLSIZE=1),
                      tail),
            VicarFile(gen_labels(RECSIZE=2, LBLSIZE=2, NBB=1, NLB=1),
                      image_area_hp,
                      None,
                      tail),
            VicarFile(
                gen_labels(RECSIZE=2, LBLSIZE=2, EOL=0, NBB=1, NLB=1),
                image_area_hp,
                None,
                tail),
            VicarFile(
                gen_labels(RECSIZE=2, LBLSIZE=2, EOL=1, NBB=1, NLB=1),
                image_area_hp,
                gen_eol_labels(2, LBLSIZE=2),
                tail),
        ]

    def syntax_parser_for_arg(self, arg):
        if False:
            # TODO To parse the tail, we need access to the info that
            # was stored in the migration task, but that code isn't
            # complete yet.  So punt on these tests.
            return parse_vicar_file
        else:
            return None
