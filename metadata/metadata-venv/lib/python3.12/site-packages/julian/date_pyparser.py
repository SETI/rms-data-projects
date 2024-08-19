##########################################################################################
# julian/date_pyparser.py
##########################################################################################
"""Function to generate a PyParsing grammar for arbitrary date strings
"""
##########################################################################################

import numpy as np
from julian.mjd_pyparser import mjd_pyparser

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
    WordEnd,
    ZeroOrMore,
    alphanums,
    alphas,
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
comma     = Suppress(Literal(',') + ZeroOrMore(White()))
opt_comma = opt_white + Suppress(Literal(',')) + opt_white | white

alpha_end = WordEnd(alphas)
num_end   = WordEnd(nums)
word_end  = WordEnd(alphanums)

nonzero = srange('[1-9]')

def _action(name, value, s, l, t):
    return [(name, value), ('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

def _no_action(s, l, t):
    return [('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

##########################################################################################
# Year
##########################################################################################

year_4digit = Word(nums, exact=4)
year_4digit.set_parse_action(lambda s,l,t: _action('YEAR', int(t[0]), s,l,t))

year_strict = Word('12', nums, exact=4)
year_strict.set_parse_action(lambda s,l,t: _action('YEAR', int(t[0]), s,l,t))

# Year 00-49, assumed 2000 to 2049
year04_2digit = Word('01234', nums, exact=2)
year04_2digit.set_parse_action(lambda s,l,t: _action('YEAR', 2000 + int(t[0]), s,l,t))

# Year 50-99, assumed 1950 to 1999
year59_2digit = Word('56789', nums, exact=2)
year59_2digit.set_parse_action(lambda s,l,t: _action('YEAR', 1900 + int(t[0]), s,l,t))

year_2digit = year04_2digit | year59_2digit

year = year_4digit | year_2digit

##########################################################################################
# General year (negative, CE, BCE, etc.)
##########################################################################################

# Extended year format for the revised ISO 8601 standard
signed_year = Combine(one_of(['-', '+']) + Word(nums, min=4))
signed_year.set_parse_action(lambda s,l,t: _action('YEAR', int(t[0]), s,l,t))

# CE years
unsigned_ce_year = Word(nonzero, nums)
unsigned_ce_year.set_parse_action(lambda s,l,t: _action('YEAR', int(t[0]), s,l,t))

ce_suffix = one_of(['CE', 'AD'],  caseless=True)
ce_suffix.set_parse_action(lambda s,l,t: _no_action(s,l,t))
ce_suffixed_year = unsigned_ce_year + opt_white + ce_suffix

ad_year = Suppress(CaselessLiteral('AD')) + opt_white + unsigned_ce_year
ce_year = ad_year | ce_suffixed_year

# BCE years
unsigned_bce_year = Word(nonzero, nums)
unsigned_bce_year.set_parse_action(lambda s,l,t: _action('YEAR', 1 - int(t[0]), s,l,t))

bce_suffix = one_of(['BCE', 'BC'],  caseless=True)
bce_suffix.set_parse_action(lambda s,l,t: _no_action(s,l,t))
bce_year = unsigned_bce_year + opt_white + bce_suffix

suffixed_year = ce_suffixed_year | bce_year
extended_year = ce_year | bce_year | signed_year

##########################################################################################
# Month
##########################################################################################

# Full month names
FULL_MONTHS = {'JANUARY':1, 'FEBRUARY':2, 'MARCH':3, 'APRIL':4,'MAY':5, 'JUNE':6,
               'JULY':7, 'AUGUST':8, 'SEPTEMBER':9, 'OCTOBER':10, 'NOVEMBER':11,
               'DECEMBER':12}
full_month = one_of(FULL_MONTHS.keys(), caseless=True) + alpha_end
full_month.set_parse_action(lambda s,l,t: _action('MONTH', FULL_MONTHS[t[0].upper()],
                                                  s,l,t))

# Three-letter abbreviations
ABBREV_MONTHS = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4,'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8,
                 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
abbrev_month = one_of(ABBREV_MONTHS.keys(), caseless=True) + alpha_end
abbrev_month.set_parse_action(lambda s,l,t: _action('MONTH', ABBREV_MONTHS[t[0].upper()],
                                                    s,l,t))

# Number 1-12 with zero padding to two digits
one_12_2digit = (
    Word('0', nonzero, exact=2) |   # 01-09
    Word('1', '012',   exact=2)     # 10-12
)

# Number 1-12, optionally zero-padded or right justified to width 2
one_12 = (
    one_12_2digit |                 # 01-12
    Combine(Optional(Literal(' ')) + Word(nonzero, exact=1))    # 1-9
)

month_2digit = one_12_2digit.copy()
month_2digit.set_parse_action(lambda s,l,t: _action('MONTH', int(t[0]), s,l,t))

numeric_month = one_12.copy()
numeric_month.set_parse_action(lambda s,l,t: _action('MONTH', int(t[0]), s,l,t))

# Note: full_month must appear before abbrev_month!
month         = full_month | abbrev_month + Suppress(Optional('.')) | numeric_month
month_strict  = full_month | abbrev_month + Suppress(Optional('.'))
dotless_month = full_month | abbrev_month | numeric_month

##########################################################################################
# Date 1-31 or fractional date 1.000 to 31.999
##########################################################################################

# 01-31
one_31_2digit = (
    Word('0',  nonzero, exact=2) |  # 01-09
    Word('12', nums,    exact=2) |  # 10-29
    Word('3',  '01',    exact=2)    # 30-31
)

# 1-31, optionally zero-padded or right-justified to width two
one_31 = (
    one_31_2digit |                 # 01-31
    Combine(Optional(Suppress(Literal(' '))) + Word(nonzero, exact=1))  # 1-9
)

date = one_31.copy() + num_end
date.set_parse_action(lambda s,l,t: _action('DAY', int(t[0]), s,l,t))

date_2digit = one_31_2digit.copy() + num_end
date_2digit.set_parse_action(lambda s,l,t: _action('DAY', int(t[0]), s,l,t))

date_float = Combine(one_31.copy() + Literal('.') + Optional(Word(nums)))
date_float.set_parse_action(lambda s,l,t: _action('DAY', float(t[0]), s,l,t))

date_2digit_float = Combine(one_31_2digit.copy() + Literal('.') + Optional(Word(nums)))
date_2digit_float.set_parse_action(lambda s,l,t: _action('DAY', float(t[0]), s,l,t))

##########################################################################################
# Day of year 1-366 or fractional day of year 1.000 to 366.999
##########################################################################################

# 001-366
one_366_3digit = (
    # 001-099
    Combine(Literal('0') + (Word('0',nonzero,exact=2) | Word(nonzero,nums,exact=2))) |
    # 100-299
    Word('12', nums, exact=3) |
    # 300-359 or 360-366
    Combine(Literal('3') + (Word('012345',nums,exact=2) | Word('6','0123456',exact=2)))
)

# 1-366, optionally zero-padded or right-justified to width 3
one_366 = (
    one_366_3digit |
    # 10-99 with optional leading blank
    Combine(Optional(Suppress(Literal(' '))) + Word(nonzero, nums, exact=2)) |
    # 1-9, with zero or two leading blanks (must come after the above!)
    Combine(Optional(Suppress(Literal('  '))) + Word(nonzero, exact=1))
)

doy = one_366.copy() + num_end
doy.set_parse_action(lambda s,l,t: _action('DAY', int(t[0]), s,l,t))

doy_3digit = one_366_3digit.copy() + num_end
doy_3digit.set_parse_action(lambda s,l,t: _action('DAY', int(t[0]), s,l,t))

doy_float = Combine(one_366.copy() + Literal('.') + Optional(Word(nums)))
doy_float.set_parse_action(lambda s,l,t: _action('DAY', float(t[0]), s,l,t))

doy_3digit_float = Combine(one_366_3digit.copy() + Literal('.') + Optional(Word(nums)))
doy_3digit_float.set_parse_action(lambda s,l,t: _action('DAY', float(t[0]), s,l,t))

##########################################################################################
# Weekday
##########################################################################################

# Full weekday names
full_weekday = one_of(['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY',
                       'THURSDAY', 'FRIDAY', 'SATURDAY'], caseless=True) + alpha_end
full_weekday.set_parse_action(lambda s,l,t: _action('WEEKDAY', t[0][:3].upper(), s,l,t))

# Three-letter abbreviations
abbrev_weekday = one_of(['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'],
                        caseless=True) + alpha_end
abbrev_weekday.set_parse_action(lambda s,l,t: _action('WEEKDAY', t[0].upper(), s,l,t))

# Note: full_weekday must appear before abbrev_weekday
weekday = full_weekday | abbrev_weekday + Optional(Suppress(Literal('.')))

opt_weekday = Optional(weekday + opt_comma)

##########################################################################################
# Date pyparsers
##########################################################################################

# Index order is [order][extended years, floating, strict]
# floating = 0: no decimal point
# floating = 1: decimal point optional
# floating = 2: decimal point required
ymd_parser = np.empty((2,3,2), dtype='object')
mdy_parser = np.empty((2,3,2), dtype='object')
dmy_parser = np.empty((2,3,2), dtype='object')

dash  = opt_white + Suppress(Literal('-')) + opt_white
slash = opt_white + Suppress(Literal('/')) + opt_white
dot   = opt_white + Suppress(Literal('.')) + opt_white

# [strict, extended years]
y_signed   = [[year       , signed_year   | year       ],
              [year_strict, signed_year   | year_strict]]
y_extended = [[year       , extended_year | year       ],
              [year_strict, extended_year | year_strict]]
y_suffixed = [[year       , suffixed_year | year       ],
              [year_strict, suffixed_year | year_strict]]

# [strict]
m_parsers = [month, month_strict]

# [floating, strict]
d_parsers = [[date             , date_2digit                    ],
             [date_float | date, date_2digit_float | date_2digit],
             [date_float       , date_2digit_float              ]]

# Year-month-day order
for x in range(2):
  for f in range(3):
    for s in range(2):
        dot_md  = dot + dotless_month + dot + date      # no period in month or date
        punc_md = (dash + month + dash | slash + month + slash) + d_parsers[f][0]
        space_ymd = y_signed[0][x] + white + m_parsers[s] + white + d_parsers[f][0]
        ymd_parser[x,f,s] = (y_signed[0][x] + (dot_md | punc_md) | space_ymd)

    # Augment non-strict YMD options with compressed formats
    # Note compressed options must be split, 2-digit year before 4-digit year.
    compressed_ymd = ( year_2digit + month_2digit + d_parsers[f][1]
                     | year_4digit + month_2digit + d_parsers[f][1])
    if x == 1:
        compressed_ymd |= signed_year + month_2digit + d_parsers[f][1]
    ymd_parser[x,f,0] |= compressed_ymd

# Month-day-year order
for x in range(2):
  for f in range(3):
    for s in range(2):
        dot_md  = dotless_month + dot + date + dot  # no period in month or date
        punc_md = month + ( dash  + d_parsers[f][0] + dash
                          | slash + d_parsers[f][0] + slash)
        space_mdy = m_parsers[s] + white + d_parsers[f][0] + opt_comma + y_extended[0][x]
        mdy_parser[x,f,s] = space_mdy | (dot_md | punc_md) + y_suffixed[0][x]

# Day-month-year order
for x in range(2):
  for f in range(3):
    for s in range(2):
        dot_dm  = date + dot + dotless_month + dot  # no period in month or date
        punc_dm = d_parsers[f][0] + (dash + month + dash | slash + month + slash)
        space_dmy = d_parsers[f][0] + white + m_parsers[s] + opt_comma + y_extended[0][x]
        dmy_parser[x,f,s] = space_dmy | (dot_dm | punc_dm) + y_suffixed[0][x]

# Convert required order to preference order; index is [order][extended, floating, strict]
# Also, require num_end
DATE_PYPARSERS = {}
DATE_PYPARSERS['YMD'] = np.empty((2,3,2), dtype='object')
DATE_PYPARSERS['MDY'] = np.empty((2,3,2), dtype='object')
DATE_PYPARSERS['DMY'] = np.empty((2,3,2), dtype='object')

for x in range(2):
  for f in range(3):
    for s in range(2):
        DATE_PYPARSERS['YMD'][x,f,s] = (ymd_parser[x,f,s] | mdy_parser[x,f,s] |
                                        dmy_parser[x,f,s]) + ~FollowedBy(nums)
        DATE_PYPARSERS['MDY'][x,f,s] = (mdy_parser[x,f,s] | ymd_parser[x,f,s] |
                                        dmy_parser[x,f,s]) + ~FollowedBy(nums)
        DATE_PYPARSERS['DMY'][x,f,s] = (dmy_parser[x,f,s] | mdy_parser[x,f,s] |
                                        ymd_parser[x,f,s]) + ~FollowedBy(nums)

##########################################################################################
# Year and day-of-year pyparsers
##########################################################################################

# [floating, strict]
doy_parsers = [[doy            , doy_3digit                   ],
               [doy_float | doy, doy_3digit_float | doy_3digit],
               [doy_float      , doy_3digit_float             ]]

# Index order is [extended years, floating, strict]
YD_PYPARSERS = np.empty((2,3,2), dtype='object')
for x in range(2):
  for f in range(3):
    YD_PYPARSERS[x,f,0] = (( y_signed[0][x] + (dash|slash|white) + doy_parsers[f][0]
                           | y_signed[0][x] + dot                + doy_parsers[0][0]
                           | year_2digit + doy_parsers[f][1]    # compressed options
                           | year_4digit + doy_parsers[f][1])
                          + ~FollowedBy(nums))
    YD_PYPARSERS[x,f,1] = (y_signed[1][x] + (dash|slash) + doy_parsers[f][1]
                          + ~FollowedBy(nums))

##########################################################################################
# ISO date pyparsers
##########################################################################################

dash_ = Suppress(Literal('-'))

# Index order is [extended years, floating, doy]
ISO_DATE_PYPARSERS = np.empty((2,3,2), dtype='object')

for f in range(3):
    ISO_DATE_PYPARSERS[0,f,0] = (   # compressed 2- and 4-digit options must be split
        year + dash_ + month_2digit + dash_ + d_parsers[f][1] |
        year_2digit  + month_2digit +         d_parsers[f][1] |
        year_4digit  + month_2digit +         d_parsers[f][1]
    )

    ISO_DATE_PYPARSERS[0,f,1] = (
        year + dash_ + (doy_parsers[f][1] | month_2digit + dash_ + d_parsers[f][1]) |
        year_2digit  + (doy_parsers[f][1] | month_2digit +         d_parsers[f][1]) |
        year_4digit  + (doy_parsers[f][1] | month_2digit +         d_parsers[f][1])
    )

    ISO_DATE_PYPARSERS[1,f,0] = (
        signed_year + dash_ + month_2digit + dash_ + d_parsers[f][1] |
        ISO_DATE_PYPARSERS[0,f,0]
    )

    ISO_DATE_PYPARSERS[1,f,1] = (
        signed_year + dash_ + (doy_parsers[f][1] |
                               month_2digit + dash_ + d_parsers[f][1]) |
        ISO_DATE_PYPARSERS[0,f,1]
    )

for x in range(2):
  for f in range(3):
    for d in range(2):
        ISO_DATE_PYPARSERS[x,f,d] += ~FollowedBy(nums)

##########################################################################################
# PyParser constructor function
##########################################################################################

def date_pyparser(order='YMD', *, strict=False, doy=False, mjd=False, weekdays=False,
                                  floating=False, floating_only=False, extended=False,
                                  iso_only=False, padding=True, embedded=False):
    """A date parser.

    The pyparser interprets a string and returns a pyparsing.ParseResults object. Calling
    the as_list() method on this object returns a list containing some but not all of
    these tuples:
        ("YEAR", year)      year if specified; two-digit years are converted to 1970-2069.
                            Alternatively, "MJD" or "JD" if the day number is to be
                            interpreted as a Julian or Modified Julian date.
        ("MONTH", month)    month if specified, 1-12.
        ("DAY", day)        day number: 1-31 if a month was specified; 1-366 if a day of
                            year was specified; otherwise, the MJD or JD day value.
        ("WEEKDAY", abbrev) day of the week if provided, as an abbreviated uppercase name:
                            "MON", "TUE", etc.
        ("TIMESYS", name)   "UTC" for an MJD or JD date; "TDB" for an MJED or JED date;
                            "TT" for an MJTD or JTD date.
        ("~", number)       the last occurrence of this tuple in the list contains the
                            number of characters matched.

    Input:
        order       One of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        strict      True for a stricter parser, which is less likely to match strings that
                    might not actually represent dates.
        doy         True to allow dates specified as year and day-of-year.
        mjd         True to allow dates expressed as MJD, JD, MJED, JTD, etc. If floating
                    is False, only "MJD" is allowed.
        weekdays    True to allow a weekday before the date.
        floating    True to allow fractional days. If False, the mjd option only supports
                    integer MJD dates.
        floating_only
                    True to require the date to contain a decimal point.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        iso_only    Require an ISO 8601:1988-compatible date string; ignore order, strict,
                    mjd, and weekdays options.
        padding     True to ignore leading or trailing white space.
        embedded    True to allow the time to be followed by additional text.
    """

    ifloating = 2 if floating_only else 1 if floating else 0

    if iso_only:
        pyparser = ISO_DATE_PYPARSERS[int(extended), ifloating, int(doy)]
    else:
        pyparser = DATE_PYPARSERS[order][int(extended), ifloating, int(strict)]
        if doy:
            pyparser |= YD_PYPARSERS[int(extended), ifloating, int(strict)]
        if weekdays:
            pyparser = opt_weekday + pyparser

        if mjd:
            pyparser = mjd_pyparser(floating=floating, timesys=floating,
                                    padding=False, embedded=True) | pyparser

    if padding:
        pyparser = opt_white + pyparser + opt_white

    if not embedded:
        pyparser = pyparser + StringEnd()

    return pyparser

##########################################################################################
