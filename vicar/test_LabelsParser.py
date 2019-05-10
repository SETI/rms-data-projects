import unittest

from LabelsParser import *


class TestLabelsParser(unittest.TestCase):
    def testSanity(self):
        data = "LBLSIZE=62 DEDH=1.5 FOO   = 'bar' NEG_PI= -3.1415926 BAR='foo'"
        lexer = lex.lex()
        parser = yacc.yacc(start='labels')
        self.assertEqual(data, parser.parse(data).to_byte_string())

        with self.assertRaises(Exception):
            # LBLSIZE is wrong
            data = "LBLSIZE=61 " \
                   "DEDH=1.5 FOO   = 'bar' NEG_PI= -3.1415926 BAR='foo'"
            parser.parse(data).to_byte_string()
