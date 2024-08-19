##########################################################################################
# textkernel/_DATA_GRAMMAR.py
##########################################################################################

import datetime as dt
import julian

from pyparsing import (CharsNotIn,
                       Combine,
                       Literal,
                       nums,
                       oneOf,
                       OneOrMore,
                       Optional,
                       ParseException,
                       ParserElement,
                       StringEnd,
                       Suppress,
                       White,
                       Word,
                       ZeroOrMore)


##########################################################################################
# _DATA_GRAMMAR
#
# _DATA_GRAMMAR.parse_string(text) receives the contents of a "\begindata" section of a
# text kernel and returns a list of tuples (name, op, value), where
#   name    the full name of the variable being defined;
#   op      either "=" or "+=";
#   value   the value an integer, float, string, date, or list of two or more of these.
# The contents of extended strings are merged. Dates are returned as datetime objects.
##########################################################################################

ParserElement.set_default_whitespace_chars(' \t')

NEWLINE = Suppress(OneOrMore(Word('\r\n')))
OPT_NEWLINE = Suppress(ZeroOrMore(Word(('\r\n'))))
OPT_WHITE = Suppress(Optional(White(' \t\r\n')))
OPT_COMMA = OPT_WHITE + Suppress(Optional(Literal(','))) + OPT_WHITE


############################################
# Integer
############################################

SIGN         = oneOf('+ -')
UNSIGNED_INT = Word(nums)
SIGNED_INT   = Combine(Optional(SIGN) + UNSIGNED_INT)
INT          = SIGNED_INT | UNSIGNED_INT
INTEGER      = Combine(Optional(SIGN) + UNSIGNED_INT)
INTEGER.set_name('INTEGER')
INTEGER.set_parse_action(lambda s, loc, toks: int(toks[0]))


############################################
# Floating-point number
############################################

EXPONENT = Suppress(oneOf('e E d D')) + INT
EXPONENT.set_parse_action(lambda s, loc, toks: 'e' + toks[0])

FLOAT_WITH_INT = Combine(INT + '.' + Optional(UNSIGNED_INT) + Optional(EXPONENT))
FLOAT_WO_INT   = Combine(Optional(SIGN) + '.' + UNSIGNED_INT + Optional(EXPONENT))
FLOAT_WO_DOT   = Combine(INT + EXPONENT)
FLOAT          = (FLOAT_WITH_INT | FLOAT_WO_INT | FLOAT_WO_DOT)
FLOAT.set_name('FLOAT')
FLOAT.set_parse_action(lambda s, loc, toks: float(toks[0]))


############################################
# Character string
############################################

# This expression strips away the "'" characters surrounding a string and also changes
# each internal "''" to a single "'".

QUOTEQUOTE = Suppress(Literal("''"))
QUOTEQUOTE.set_parse_action(lambda s, loc, toks: ["'"])

STRING = Combine(Suppress(Literal("'"))
                 + ZeroOrMore(CharsNotIn("'\n\r") | QUOTEQUOTE)
                 + Suppress(Literal("'")))
STRING.set_name('STRING')


############################################
# Date-time (following "@")
############################################

def _parse_datetime(s, loc, tokens):
    """Convert a date expression to a Python datetime object, using the Julian Library's
    string parser.
    """

    try:
        (day, sec) = julian.day_sec_from_string(tokens.as_list()[0])
    except ParseException:
        # Provide a more streamlined error message
        raise ParseException('unrecognized time syntax: ' + tokens[0])  # pragma: no cover

    isec = int(sec)
    micro = int(1e6 * (sec - isec) + 0.5)

    # This will not handle leap seconds correctly, but a leap second is unlikely to
    # appear as a datetime in a SPICE text kenel.
    return dt.datetime(2000, 1, 1) + dt.timedelta(day, isec, micro)


DATE = Combine(Suppress(Literal('@')) + CharsNotIn('@\r\n\t(), '))
DATE.set_name('DATE')
DATE.set_parse_action(_parse_datetime)


############################################
# LIST
############################################

SCALAR = FLOAT | INTEGER | STRING | DATE

LIST = (Suppress(Literal('(')) + OPT_NEWLINE
        + OneOrMore(SCALAR + OPT_COMMA) + OPT_NEWLINE
        + Suppress(Literal(')')))
LIST.set_name('LIST')
LIST.set_parse_action(lambda s, loc, toks: toks[0] if len(toks) == 1 else [list(toks)])

# Anything on the right side of an equal sign
VALUE = SCALAR | LIST


############################################
# Variable names
############################################

EXCLUDED_CHARS = ' ,()=\t\n\r'
NAME_ = Combine(CharsNotIn(EXCLUDED_CHARS))


############################################
# Expressions
############################################

STATEMENT = NAME_ + oneOf('= +=') + OPT_NEWLINE + VALUE + NEWLINE
STATEMENT.set_name('STATEMENT')
STATEMENT.set_parse_action(lambda s, loc, toks: tuple(toks))

_DATA_GRAMMAR = OneOrMore(NEWLINE | STATEMENT) + StringEnd()
_DATA_GRAMMAR.set_name('_DATA_GRAMMAR')

##########################################################################################
