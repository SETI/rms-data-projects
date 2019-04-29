import random
import unittest

from StringUtils import *

if TYPE_CHECKING:
    from typing import List, Tuple

_TEST_STRINGS = [("foo", "'foo'"),
                 ("don't", "'don''t'")]  # type: List[Tuple[str, str]]

_BAD_STRINGS = ["foo", "'foo", "foo'", "foo''", "'don't'"]  # type: List[str]


class TestStringUtils(unittest.TestCase):
    def test_escape_byte_string(self):
        # type: () -> None
        for (unesc, esc) in _TEST_STRINGS:
            self.assertEqual(escape_byte_string(unesc), esc)

    def test_unescape_byte_string(self):
        # type: () -> None
        for (unesc, esc) in _TEST_STRINGS:
            self.assertEqual(unescape_byte_string(esc), unesc)

        for bad_str in _BAD_STRINGS:
            with self.assertRaises(Exception):
                unescape_byte_string(bad_str)

    def test_gen_line(self):
        n = random.randint(1, 100)
        line = gen_line(n)
        self.assertEqual(n, len(line))

    def test_gen_block(self):
        w = random.randint(1, 25)
        h = random.randint(1, 25)
        block = gen_block(w, h)
        assert len(block) == h
        for line in block:
            assert len(line) == w
