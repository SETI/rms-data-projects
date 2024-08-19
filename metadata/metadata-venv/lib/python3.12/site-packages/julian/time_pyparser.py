##########################################################################################
# julian/time_pyparser.py
##########################################################################################
"""Function to generate a PyParsing grammar for arbitrary time strings
"""
##########################################################################################

import numpy as np
from julian._TIMEZONES import TIMEZONES

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
colon     = Suppress(Literal(':'))
not_colon = ~FollowedBy(Literal(':'))

alpha_end = WordEnd(alphas)
num_end   = WordEnd(nums)
word_end  = WordEnd(alphanums)

nonzero = srange('[1-9]')

def _action(name, value, s, l, t):
    return [(name, value), ('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

def _actions(items, s, l, t):
    item_list = []
    for k in range(0, len(items), 2):
        item_list.append((items[k], items[k+1]))
    return item_list + [('~', s.upper().index(t[0].upper(),l) + len(t[0]))]

##########################################################################################
# Hours 0-23 or 1-12
##########################################################################################

# A number 0-23, zero-padded to two digits
zero_23_2digits = (
    Word('01', nums,  exact=2) |    # 00-19
    Word('2', '0123', exact=2)      # 20-23
)

# A number 0-23, possibly zero-padded or right-justified to two digits
zero_23 = (
    zero_23_2digits |               # 00-23
    Optional(Suppress(Literal(' '))) + Word(nums, exact=1)  # 0-9
)

hour = zero_23.copy()
hour.set_parse_action(lambda s,l,t: _action('HOUR', int(t[0]), s,l,t))

hour_strict = zero_23_2digits.copy()
hour_strict.set_parse_action(lambda s,l,t: _action('HOUR', int(t[0]), s,l,t))

hour_float = Combine(zero_23 + '.' + Optional(Word(nums)))
hour_float.set_parse_action(lambda s,l,t: _action('HOUR', float(t[0]), s,l,t))

hour_float_strict = Combine(zero_23_2digits + '.' + Optional(Word(nums)))
hour_float_strict.set_parse_action(lambda s,l,t: _action('HOUR', float(t[0]), s,l,t))

# A number 1-12, zero-padded to two digits
one_12_2digit = (
    Word('0', nonzero, exact=2) |   # 01-09
    Word('1', '012', exact=2)       # 10-12
)

# A number 1-12, possibly zero-padded or right-justified to two digits
one_12 = (
    one_12_2digit |                 # 01-12
    Optional(Suppress(Literal(' '))) + Word(nonzero, exact=1)   # 1-9
)

hour_am = one_12.copy()
hour_am.set_parse_action(lambda s,l,t: _action('HOUR', int(t[0]) % 12, s,l,t))
# 12 o'clock gets converted to 0, others unchanged

hour_pm = one_12.copy()
hour_pm.set_parse_action(lambda s,l,t: _action('HOUR', 12 + int(t[0]) % 12, s,l,t))
# 12 o'clock gets converted to 12, others to 13-23

hour_am_float = Combine(one_12.copy() + Literal('.') + Word(nums))
hour_am_float.set_parse_action(lambda s,l,t: _action('HOUR', float(t[0])%12, s,l,t))

hour_pm_float = Combine(one_12.copy() + Literal('.') + Word(nums))
hour_pm_float.set_parse_action(lambda s,l,t: _action('HOUR', 12 + float(t[0])%12, s,l,t))

##########################################################################################
# Minutes 0-59 or 0-1439
##########################################################################################

# A number 0-59, zero-padded to two digits
zero_59_2digits = Word('012345', nums, exact=2)

# A number 0-59, two digits but with a possible leading blank instead of zero
zero_59 = zero_59_2digits | Suppress(Literal(' ')) + Word(nums, exact=1)

minute = zero_59.copy()
minute.set_parse_action(lambda s,l,t: _action('MINUTE', int(t[0]), s,l,t))

minute_strict = zero_59_2digits.copy()
minute_strict.set_parse_action(lambda s,l,t: _action('MINUTE', int(t[0]), s,l,t))

# A floating-point number, 0.000-59.999
minute_float = Combine(zero_59 + Literal('.') + Optional(Word(nums)))
minute_float.set_parse_action(lambda s,l,t: _action('MINUTE', float(t[0]), s,l,t))

minute_float_strict = Combine(zero_59_2digits + Literal('.') + Optional(Word(nums)))
minute_float_strict.set_parse_action(lambda s,l,t: _action('MINUTE', float(t[0]), s,l,t))

# A number 0-1439, no leading zeros or white space
zero_1439 = (
    Combine('14' + Word('0123', nums, exact=2)) |   # 1400-1439
    Combine('1'  + Word('0123', nums, exact=3)) |   # 1000-1399
    Word(nonzero, nums, min=1, max=3) |             # 1-999
    Literal('0')                                    # 0
)

minute1439 = zero_1439.copy()
minute1439.set_parse_action(lambda s,l,t: _action('MINUTE', int(t[0]), s,l,t))

minute1439_float = Combine(zero_1439 + Literal('.') + Optional(Word(nums)))
minute1439_float.set_parse_action(lambda s,l,t: _action('MINUTE', float(t[0]), s,l,t))

##########################################################################################
# Seconds 0-59 or 0-86399
##########################################################################################

second = zero_59.copy()
second.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', False], s,l,t))

second_strict = zero_59_2digits.copy()
second_strict.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', False], s,l,t))

# A floating-point number, 0.000-59.999
second_float = Combine(zero_59 + Literal('.') + Optional(Word(nums)))
second_float.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', False], s,l,t))

second_float_strict = Combine(zero_59_2digits + Literal('.') + Optional(Word(nums)))
second_float_strict.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', False], s,l,t))

# A number 0-86399, no leading zeros or white space
zero_86399 = (
    Combine('86' + Word('0123',   nums, exact=3)) | # 86000-86399
    Combine('8'  + Word('012345', nums, exact=4)) | # 80000-85999
    Word('1234567', nums, exact=5)    |             # 10000-79999
    Word(nonzero, nums, min=1, max=4) |             # 1-9999
    Literal('0')                                    # 0
)

second86399 = zero_86399.copy()
second86399.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', False], s,l,t))

second86399_float = Combine(zero_86399 + Literal('.') + Optional(Word(nums)))
second86399_float.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', False], s,l,t))

##########################################################################################
# Leap seconds 0-69 or 0-86409
##########################################################################################

# A number 0-69, zero-padded to two digits
zero_69_2digits = Word('0123456', nums, exact=2)

# A number 0-69, two digits but with a possible leading blank instead of zero
zero_69 = zero_69_2digits | Suppress(Literal(' ')) + Word(nums, exact=1)

leapsec = zero_69.copy()
leapsec.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', int(t[0]) >= 60], s,l,t))

leapsec_strict = zero_69_2digits.copy()
leapsec_strict.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', int(t[0]) >= 60], s,l,t))

# A floating-point number, 0.000-69.999
leapsec_float = Combine(zero_69 + Literal('.') + Optional(Word(nums)))
leapsec_float.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', float(t[0]) >= 60.], s,l,t))

leapsec_float_strict = Combine(zero_69_2digits + Literal('.') + Optional(Word(nums)))
leapsec_float_strict.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', float(t[0]) >= 60.], s,l,t))

# A number 0-86409, no leading zeros or white space
zero_86409 = Combine(Literal('8640') + Word(nums, exact=1)) | zero_86399

leapsec86409 = zero_86409.copy()
leapsec86409.set_parse_action(
    lambda s,l,t: _actions(['SECOND', int(t[0]), 'LEAPSEC', int(t[0]) >= 86400], s,l,t))

leapsec86409_float = Combine(zero_86409 + Literal('.') + Optional(Word(nums)))
leapsec86409_float.set_parse_action(
    lambda s,l,t: _actions(['SECOND', float(t[0]), 'LEAPSEC', float(t[0]) >= 86400],
                           s,l,t))

##########################################################################################
# Time zones
##########################################################################################

# As a numeric offset
z_timezone = opt_white + CaselessLiteral('Z')
z_timezone.set_parse_action(
    lambda s,l,t: _actions(['TZ', 'Z', 'TZMIN', 0, 'TIMESYS', 'UTC'], s,l,t))

z_timezone_strict = Literal('Z')
z_timezone_strict.set_parse_action(
    lambda s,l,t: _actions(['TZ', 'Z', 'TZMIN', 0, 'TIMESYS', 'UTC'], s,l,t))

tz_hours = (Literal('-') | Literal('+')) + (
    Word('0', nums, exact=2) |      # 00-09
    Word('1', '01234', exact=2)     # 10-14
)
tz_minutes = one_of(['00', '15', '30', '45'])

def _tzmin(string):       # convert "-hh", "+hh", "-hh:mm", "+hh:mm" to minutes
    sign = -1 if string[0] == '-' else +1
    h = int(string[1:3])
    m = 0 if len(string) == 3 else int(string[3:].lstrip(':'))
    return sign * (60 * h + m)

hhmm_timezone = Combine(tz_hours + Optional(Optional(Literal(':')) + tz_minutes))
hhmm_timezone.set_parse_action(
    lambda s,l,t: _actions(['TZ', t[0], 'TZMIN', _tzmin(t[0]), 'TIMESYS', 'UTC'], s,l,t))

hhmm_tz = z_timezone | hhmm_timezone
opt_hhmm_tz = Optional(hhmm_tz)

# As an abbreviation
def _tzmin_lookup(string):
    return _tzmin(TIMEZONES[string])

named_tz = opt_white + one_of(TIMEZONES.keys(), caseless=True)
named_tz.set_parse_action(
    lambda s,l,t: _actions(['TZ', t[0].upper(), 'TZMIN', _tzmin_lookup(t[0]),
                            'TIMESYS', 'UTC'], s,l,t))
opt_named_tz = Optional(named_tz)

timezone = hhmm_tz | named_tz
opt_timezone = Optional(timezone)

iso_timezone = z_timezone_strict | hhmm_timezone
opt_iso_timezone = Optional(z_timezone_strict | hhmm_timezone)

##########################################################################################
# Time system suffix, e.g., "UTC", "TAI", "TDB", or "TDT"
##########################################################################################

timesys_et = CaselessLiteral('ET')
timesys_et.setParseAction(lambda s,l,t: _action('TIMESYS', 'TDB', s,l,t))

timesys_tt = CaselessLiteral('TDT')
timesys_tt.setParseAction(lambda s,l,t: _action('TIMESYS', 'TT', s,l,t))

timesys_utc = one_of(['UTC', 'UT1', 'UT'], caseless=True)
timesys_utc.setParseAction(lambda s,l,t: _action('TIMESYS', 'UTC', s,l,t))

timesys_z = CaselessLiteral('Z')    # both a time system and a time zone!
timesys_z.setParseAction(
    lambda s,l,t: _actions(['TIMESYS', 'UTC', 'TZ', 'Z', 'TZMIN', 0], s,l,t))

timesys_other = one_of(['TAI', 'TDB', 'TT'], caseless=True)
timesys_other.setParseAction(lambda s,l,t: _action('TIMESYS', t[0].upper(), s,l,t))

timesys = opt_white + (timesys_other | timesys_utc| timesys_z | timesys_et | timesys_tt)
opt_timesys = Optional(timesys)
req_timesys = timesys       # because variable "timesys" can be used for other purposes

##########################################################################################
# TIME_PYPARSERS
##########################################################################################

am = opt_white + CaselessLiteral('AM')
pm = opt_white + CaselessLiteral('PM')
am.set_parse_action(lambda s,l,t: _actions([], s,l,t))
pm.set_parse_action(lambda s,l,t: _actions([], s,l,t))

H = CaselessLiteral('h')
M = CaselessLiteral('m')
S = CaselessLiteral('s')
H.set_parse_action(lambda s,l,t: _actions([], s,l,t))
M.set_parse_action(lambda s,l,t: _actions([], s,l,t))
S.set_parse_action(lambda s,l,t: _actions([], s,l,t))

# Seconds parser, index is [leapsec]
s_parsers = [second_float | second, leapsec_float | leapsec]

# Parser for h/m/s notation, index is [leapsec]
hm_parser = ( (hour_float       | hour)       + opt_white + H
            | (minute1439_float | minute1439) + opt_white + M)
hms_parsers = [hm_parser | (second86399_float  | second86399)  + opt_white + S,
               hm_parser | (leapsec86409_float | leapsec86409) + opt_white + S]

opt_timezone_timesys = Optional(timezone | timesys)

# Shape is [floating, leapsecs, timesys, timezones, ampm]
TIME_PYPARSERS = np.empty((2,2,2,2,2), dtype='object')

for l in (0,1):
    opt_colon_s = colon + s_parsers[l] | not_colon

    time = hour + colon + minute + opt_colon_s
    time_ampm = ( hour_am + Optional(colon + minute + opt_colon_s) + am
                | hour_pm + Optional(colon + minute + opt_colon_s) + pm)
    ftime = hour + colon + minute_float + not_colon
    ftime_ampm = ( hour_am + colon + minute_float + am | hour_am_float + am
                 | hour_pm + colon + minute_float + pm | hour_pm_float + pm)
    xtime      = ftime      | time
    xtime_ampm = ftime_ampm | time_ampm

    # [floating, ..., am/pm]
    TIME_PYPARSERS[0,l,0,0,0] = time
    TIME_PYPARSERS[0,l,0,0,1] = time_ampm | time

    TIME_PYPARSERS[1,l,0,0,0] = xtime
    TIME_PYPARSERS[1,l,0,0,1] = xtime_ampm | xtime

    # [floating, ..., time zones, am/pm]
    # Only named, not numeric time zones after am/pm.
    TIME_PYPARSERS[0,l,0,1,0] = time       + opt_timezone
    TIME_PYPARSERS[0,l,0,1,1] = time_ampm  + opt_named_tz | TIME_PYPARSERS[0,l,0,1,0]
    TIME_PYPARSERS[1,l,0,1,0] = xtime      + opt_timezone
    TIME_PYPARSERS[1,l,0,1,1] = xtime_ampm + opt_named_tz | TIME_PYPARSERS[1,l,0,1,0]

    # [floating, ..., time system, time zones, am/pm]
    # The time system can only be specified in the absence of a time zone or am/pm.
    TIME_PYPARSERS[0,l,1,0,0] = time + opt_timesys
    TIME_PYPARSERS[0,l,1,1,0] = time + opt_timezone_timesys
    TIME_PYPARSERS[0,l,1,0,1] = time + timesys | TIME_PYPARSERS[0,l,0,0,1]
    TIME_PYPARSERS[0,l,1,1,1] = time + timesys | TIME_PYPARSERS[0,l,0,1,1]

    TIME_PYPARSERS[1,l,1,0,0] = xtime + opt_timesys
    TIME_PYPARSERS[1,l,1,1,0] = xtime + opt_timezone_timesys
    TIME_PYPARSERS[1,l,1,0,1] = xtime + timesys | TIME_PYPARSERS[1,l,0,0,1]
    TIME_PYPARSERS[1,l,1,1,1] = xtime + timesys | TIME_PYPARSERS[1,l,0,1,1]

    # Augment the floating cases with h/m/s notation
    for s in (0,1):
      for z in (0,1):
        for a in (0,1):
            TIME_PYPARSERS[1,l,s,z,a] |= hms_parsers[l]

##########################################################################################
# ISO_TIME_PYPARSER
##########################################################################################

strict_s = second_float_strict | second_strict
colon_strict_s = colon + strict_s
opt_colon_strict_s = not_colon | Optional(colon_strict_s)

# Seconds parser, index is [leapsec]
s_parsers = [second_float_strict | second_strict, leapsec_float_strict | leapsec_strict]

# Index is [floating, leapsecs, timezones]
ISO_TIME_PYPARSERS = np.empty((2,2,2), dtype='object')

for l in (0,1):
    iso_time = hour_strict + ( colon + minute_strict + (colon + s_parsers[l] | not_colon)
                             | minute_strict + Optional(s_parsers[l])
                             | not_colon)
    iso_ftime = ( hour_float_strict
                | hour_strict + Optional(colon) + minute_float_strict) + not_colon

    ISO_TIME_PYPARSERS[0,l,0] = iso_time
    ISO_TIME_PYPARSERS[0,l,1] = iso_time + opt_iso_timezone
    ISO_TIME_PYPARSERS[1,l,0] = iso_ftime | iso_time
    ISO_TIME_PYPARSERS[1,l,1] = ISO_TIME_PYPARSERS[1,l,0] + opt_iso_timezone

##########################################################################################
# PyParser constructor function
##########################################################################################

def time_pyparser(*, leapsecs=False, ampm=False, timezones=False, timesys=False,
                     floating=False, iso_only=False, padding=True, embedded=False):
    """A time pyparser.

    The pyparser interprets a string and returns a pyparsing.ParseResults object. Calling
    the as_list() method on this object returns a list containing some but not all of
    these tuples:
        ("HOUR", hour)      hour if specified, 0-23, an int or possibly a float. Hours
                            am/pm are converted to the range 0-23 automatically.
        ("MINUTE", minute)  minute if specified, integer or float.
        ("SECOND", second)  second if specified, integer or float.
        ("LEAPSEC", True))  present if this is a leap second.
        ("TZ", tz_name)     name of the time zone if specified.
        ("TZMIN", tzmin)    offset of the time zone in minutes.
        ("TIMESYS", name)   time system if specified: "UTC", "TAI", "TDB", or "TDT".
        ("~", number)       the last occurrence of this tuple in the list contains the
                            number of characters matched.

    Input:
        leapsecs    True to allow leap seconds.
        ampm        True to allow "am" and "pm" suffixes.
        timezones   True to allow time zones, e.g, "Z", "PDT", or "+01:00"
        timesys     True to allow a time system, e.g., "UTC", "TAI", "TDB", or "TT".
        floating    True to allow time specified using floating-point hours or minutes.
        iso_only    Require an ISO-compatible time string; ignore ampm and timesys
                    options.
        padding     True to ignore leading or trailing white space.
        embedded    True to allow the time to be followed by additional text.
    """

    if iso_only:
        pyparser = ISO_TIME_PYPARSERS[int(floating), int(leapsecs), int(timezones)]
    else:
        pyparser = TIME_PYPARSERS[int(floating), int(leapsecs), int(timesys),
                                  int(timezones), int(ampm)]

    if padding:
        pyparser = opt_white + pyparser

    if embedded:
        pyparser = pyparser + ~FollowedBy(alphanums)
    elif padding:
        pyparser = pyparser + opt_white + StringEnd()
    else:
        pyparser = pyparser + StringEnd()

    return pyparser

##########################################################################################

