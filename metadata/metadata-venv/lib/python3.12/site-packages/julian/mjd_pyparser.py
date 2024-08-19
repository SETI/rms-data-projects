##########################################################################################
# julian/mjd_pyparser.py
##########################################################################################
"""Function to generate a PyParsing grammar for strings using MJD/JD notation
"""
##########################################################################################

from julian.time_pyparser import req_timesys

from pyparsing import (
    CaselessLiteral,
    Combine,
    FollowedBy,
    Literal,
    OneOrMore,
    Optional,
    ParserElement,
    StringEnd,
    Suppress,
    White,
    Word,
    ZeroOrMore,
    alphanums,
    nums,
    one_of,
    srange,
)

##########################################################################################
# Begin grammar
##########################################################################################

# All whitespace is handled explicitly
ParserElement.set_default_whitespace_chars('')

# Useful definitions...
white     = Suppress(OneOrMore(White()))
opt_white = Suppress(ZeroOrMore(White()))

def _action(name, value, s, l, t):
    return [(name, value), ('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

def _actions(items, s, l, t):
    item_list = []
    for k in range(0, len(items), 2):
        item_list.append((items[k], items[k+1]))
    return item_list + [('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

##########################################################################################
# Numbers
##########################################################################################

nonzero = srange('[1-9]')
opt_sign = one_of(['-', '+', ''])
digits = Word(nonzero, nums) | Literal('0')

int_value = Combine(opt_sign + digits)
int_value.set_parse_action(lambda s,l,t: _action('DAY', int(t[0]), s,l,t))

float_value = Combine(opt_sign + digits + Literal('.') + Optional(Word(nums)))
float_value.set_parse_action(lambda s,l,t: _action('DAY', float(t[0]), s,l,t))

# Note: float_value must appear before int_value!
number = float_value | int_value

##########################################################################################
# Integer MJD day
##########################################################################################

mjd = CaselessLiteral('MJD')
mjd.set_parse_action(lambda s,l,t: _actions(['YEAR', 'MJD'], s,l,t))

par_mjd = CaselessLiteral('(MJD)')
par_mjd.set_parse_action(lambda s,l,t: _actions(['YEAR', 'MJD'], s,l,t))

mjd_date = (
    mjd + opt_white + int_value |
    int_value + white + mjd |
    int_value + opt_white + par_mjd
)

##########################################################################################
# Numeric date = MJD/JD etc. plus a floating-point number
##########################################################################################

JD_TYPES = {
    'JD' : ('JD' , 'UTC'),
    'MJD': ('MJD', 'UTC'),
}

jd_type = one_of(['JD', 'MJD'], caseless=True)
jd_type.set_parse_action(lambda s,l,t:
        _actions(['YEAR', t[0].upper()], s,l,t))

paren_jd_type = one_of(['(' + k + ')' for k in JD_TYPES.keys()], caseless=True)
paren_jd_type.set_parse_action(lambda s,l,t:
        _actions(['YEAR', t[0][1:-1].upper()], s,l,t))

numeric_date = (
    jd_type + opt_white + number |
    number + white + jd_type |
    number + opt_white + paren_jd_type
)

JXD_TYPES = {
    'JED' : ('JD' , 'TDB'),
    'JTD' : ('JD' , 'TT' ),
    'MJED': ('MJD', 'TDB'),
    'MJTD': ('MJD', 'TT' ),
}

jxd_type = one_of(JXD_TYPES.keys(), caseless=True)
jxd_type.set_parse_action(lambda s,l,t:
        _actions(['YEAR', JXD_TYPES[t[0].upper()][0],
                  'TIMESYS', JXD_TYPES[t[0].upper()][1]], s,l,t))

paren_jxd_type = one_of(['(' + k + ')' for k in JXD_TYPES.keys()], caseless=True)
paren_jxd_type.set_parse_action(lambda s,l,t:
        _actions(['YEAR', JXD_TYPES[t[0][1:-1].upper()][0],
                  'TIMESYS', JXD_TYPES[t[0][1:-1].upper()][1]], s,l,t))

numeric_timesys_date = (
    jxd_type + opt_white + number |
    number + white + jxd_type |
    number + opt_white + paren_jxd_type
)

##########################################################################################

def mjd_pyparser(*, floating=True, timesys=True, padding=True, embedded=False):
    """A date parser using MJD, JD, MJED, or JED.

    The pyparser interprets a string and returns a pyparsing.ParseResults object. Calling
    the as_list() method on this object returns a list containing some but not all of
    these tuples:
        ("YEAR", type)      either "MJD" or "JD", indicating that the day value is not
                            part of an actual year.
        ("TIMESYS", name)   either "UTC" or "TDB".
        ("DAY", day)        day number as either an int or a float.
        ("~", number)       the last occurrence of this tuple in the list contains the
                            number of characters matched.

    Input:
        floating    True to allow fractional days. If false, only an MJD integer date is
                    permitted.
        timesys     True to allow an explicit time system via "MJxD" or "JxD". Ignored if
                    floating is False.
        padding     True to ignore leading or trailing white space.
        embedded    True to allow the time to be followed by additional text.
    """

    if floating:
        if timesys:
            pyparser = numeric_date + req_timesys | numeric_timesys_date | numeric_date
        else:
            pyparser = numeric_date
    else:
        pyparser = mjd_date

    if padding:
        pyparser = opt_white + pyparser

    if embedded:
        pyparser += ~FollowedBy(alphanums)
    elif padding:
        pyparser += opt_white + StringEnd()
    else:
        pyparser += StringEnd()

    return pyparser

##########################################################################################
