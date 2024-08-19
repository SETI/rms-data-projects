##########################################################################################
# textkernel/_NAME_GRAMMAR.py
##########################################################################################

from pyparsing import (alphanums,
                       CharsNotIn,
                       Combine,
                       Literal,
                       nums,
                       oneOf,
                       OneOrMore,
                       Optional,
                       ParserElement,
                       StringEnd,
                       Suppress,
                       Word,
                       ZeroOrMore)

from textkernel._DATA_GRAMMAR import EXCLUDED_CHARS, INTEGER, UNSIGNED_INT

##########################################################################################
# _NAME_GRAMMAR
#
# _NAME_GRAMMAR.parse_string(name) receives the variable name component of an expression
# and returns:
#   - For nested names, a list the individual names with slashes removed:
#       "DELTET/DELTA_T_A" -> ["DELTET", "DELTA_T_A"]
#   - For indexed names, a three-value tuple (before, index, after):
#       "BODY627_RADII" -> ("BODY", 627, "_RADII")
#       "SCLK_PARTITION_END_32" -> ("SCLK", -32, "_PARTITION_END_")
#   - For "tkframe" names, a three-value tuple (before, middle, after):
#       "TKFRAME_DSS-28_TOPO_AXES" -> ("TKFRAME", "DSS-28_TOPO", "AXES")
#     because sometimes a frame name is embedded here rather than an ID
#   - Otherwise, the name as a single string.
# Note that the order of elements is swapped and the sign of the body ID is changed in the
# case of indexed names beginning with "SCLK".
##########################################################################################

ParserElement.set_default_whitespace_chars('')

GENERAL_NAME = Combine(CharsNotIn(EXCLUDED_CHARS))
GENERAL_NAME.set_name('GENERAL_NAME')

INDEXED_NAME = (oneOf(['BODY', 'OBJECT', 'FRAME', 'TKFRAME', 'INS', 'CK'])
                + Suppress(Optional(Literal('_')))
                + INTEGER
                + Suppress(Optional(Literal('_')))
                + GENERAL_NAME)
INDEXED_NAME.set_name('INDEXED_NAME')
INDEXED_NAME.set_parse_action(lambda s, loc, toks: tuple(toks))

TKFRAME_SUFFIX = oneOf(['ANGLES', 'AXES', 'BORESIGHT', 'MATRIX', 'Q', 'RELATIVE', 'SPEC',
                        'UNITS'])
_TKFRAME_SUFFIX = Suppress(Literal('_')) + TKFRAME_SUFFIX
TKFRAME_NAME = (Literal('TKFRAME')
                + Suppress(Literal('_'))
                + Combine(OneOrMore(~(Literal('_') + TKFRAME_SUFFIX)
                                    + Word(alphanums+'_-', min=1, max=1)))
                + Suppress(Literal('_'))
                + TKFRAME_SUFFIX)
TKFRAME_NAME.set_name('TKFRAME_NAME')
TKFRAME_NAME.set_parse_action(lambda s, loc, toks: tuple(toks))

CK_NAME = (Literal('SCLK')
           + Suppress(Optional(Literal('_')))
           + Combine(ZeroOrMore(~(Literal('_') + Word(nums) + StringEnd())
                                + Word(alphanums+'_-', min=1, max=1)))
           + Suppress(Literal('_')) + UNSIGNED_INT)
CK_NAME.set_name('CK_NAME')
CK_NAME.set_parse_action(lambda s, loc, toks:
                         (toks[0], -int(toks[2]), toks[1]))  # swap, change sign

SECTION_NAME = Combine(CharsNotIn(EXCLUDED_CHARS + '/'))
NESTED_NAME = OneOrMore(SECTION_NAME + Suppress(Literal('/'))) + SECTION_NAME
NESTED_NAME.set_parse_action(lambda s, loc, toks: [list(toks)])

_NAME_GRAMMAR = ((INDEXED_NAME | TKFRAME_NAME | CK_NAME | NESTED_NAME | GENERAL_NAME)
                 + StringEnd())
_NAME_GRAMMAR.set_name('_NAME_GRAMMAR')

##########################################################################################
