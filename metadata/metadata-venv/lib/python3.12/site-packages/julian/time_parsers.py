##########################################################################################
# julian/time_parsers.py
##########################################################################################
"""Functions to parse time strings given in arbitrary formats
"""
##########################################################################################

import pyparsing
import re

from julian.date_parsers  import _search_in_string
from julian.time_pyparser import time_pyparser
from julian.formatters    import format_day, format_sec
from julian.leap_seconds  import seconds_on_day
from julian._exceptions   import JulianParseException, JulianValidateFailure

_PRE_FILTER = True      # set False for some performance tests

##########################################################################################
# General parser
##########################################################################################

def sec_from_string(string, leapsecs=True, ampm=True, timezones=False, floating=False):
    """Time of day in seconds, based on the parsing of a free-form string.

    Input:
        string      string to interpret.
        leapsecs    True to recognize leap seconds.
        ampm        True to recognize "am" and "pm" suffixes.
        timezones   True to recognize and interpret time zones. If True, returned values
                    are adjusted to UTC.
        floating    True to allow time specified using floating-point hours or minutes.

    Return:         a single count of seconds or a tuple (sec, dday)
        sec         count of seconds.
        dday        the offset in days due to the presence of the time zone, included if
                    the input value of timezones is True.
    """

    parser = time_pyparser(leapsecs=leapsecs, ampm=ampm, timezones=timezones,
                           floating=floating, timesys=False, iso_only=False,
                           padding=True, embedded=False)
    try:
        parse_list = parser.parse_string(string).as_list()
    except pyparsing.ParseException:
        raise JulianParseException(f'unrecognized time format: "{string}"')

    parse_dict = {key:value for key, value in parse_list}
    (sec, dday, _) = _sec_from_dict(parse_dict, leapsecs=leapsecs, validate=True)

    if timezones:
        return (sec, dday)

    return sec

##########################################################################################
# Time scrapers
##########################################################################################

def secs_in_strings(strings, leapsecs=True, ampm=True, timezones=False, floating=False,
                    validate=True, substrings=False, first=False):
    """List of second counts representing times of day, obtained by searching one or more
    strings for patterns that look like formatted times.

    Input:
        strings     list/array/tuple of strings to interpret.
        leapsecs    True to recognize leap seconds.
        ampm        True to recognize "am" and "pm" suffixes.
        timezones   True to recognize and interpret time zones. If True, returned values
                    are adjusted to UTC.
        floating    True to recognize time values specified using floating-point hours or
                    minutes.
        validate    if True, patterns that look like times but are not valid for other
                    reasons are ignored.
        substrings  True to also return the substring containing each identified time.
        first       True to return when the first time is found, with None on failure;
                    False to return the full, ordered list of times found.

    Return:         a list containing either second counts or tuples (sec, optional dday,
                    optional substring).
        sec         number of seconds into day.
        dday        the offset in days due to the presence of the time zone, included if
                    the input value of timezones is True.
        substring   the substring containing the text that was interpreted to represent
                    this time; included if the input value of include_text is True.

        Note: If the input value of first is True, the returned quantity is not a list,
        just a single second count or tuple.
    """

    if isinstance(strings, str):
        strings = [strings]

    parser = time_pyparser(leapsecs=leapsecs, ampm=ampm, timezones=timezones,
                           timesys=False, floating=floating, iso_only=False,
                           padding=True, embedded=True)

    sec_list = []
    for string in strings:

        # Use fast check to skip over strings that are clearly time-less
        if not _time_pattern_filter(string):
            continue

        while True:
            parse_dict, substring, string = _search_in_string(string, parser)
            if not parse_dict:
                break

            try:
                (sec, dday, _) = _sec_from_dict(parse_dict, leapsecs=leapsecs,
                                                validate=validate)
            except ValueError:  # pragma: no cover
                continue

            result = [sec]
            if timezones:
                result.append(dday)
            if substrings:
                result.append(substring)

            sec_list.append(sec if len(result) == 1 else tuple(result))
            if first:
                return sec_list[0]

    if first:
        return None

    return sec_list

##########################################################################################
# Utilities
##########################################################################################

def _sec_from_dict(parse_dict, day=None, leapsecs=True, validate=True):
    """Seconds "delta day", and time system values based on the contents of a dictionary.
    """

    dday = 0
    h = parse_dict.get('HOUR',   0)
    m = parse_dict.get('MINUTE', 0)
    s = parse_dict.get('SECOND', 0)

    timesys = parse_dict.get('TIMESYS', 'UTC')
    tzmin = parse_dict.get('TZMIN', 0)
    is_leap = parse_dict.get('LEAPSEC', False)
    if is_leap and validate:
        if timesys != 'UTC':        # pragma: no cover
            raise JulianValidateFailure('leap seconds are disallowed in time system '
                                        + timesys)
        if not leapsecs:            # pragma: no cover
            raise JulianValidateFailure('leap seconds are disallowed')

    if tzmin:
        if is_leap:
            if s >= 86400:
                leaps = s - 86399   # pragma: no cover
                s = 86399           # pragma: no cover
            else:
                leaps = s - 59
                s = 59

        sec = 3600 * h + 60 * (m - tzmin) + s
        if sec < 0:
            sec += 86400
            dday = -1
        elif sec >= 86400:
            sec -= 86400
            dday = 1

        if is_leap:
            sec += leaps
            if validate:            # pragma: no branch
                if (sec >= 86400 and not leapsecs) or sec < 86400:
                    raise JulianValidateFailure('invalid leap second at '
                                                '%s UTC, time zone %s'
                                                % (format_sec(sec), parse_dict['TZ']))

    else:
        sec = 3600 * h + 60 * m + s

    if is_leap and validate and day is not None and sec >= seconds_on_day(day + dday):
        raise JulianValidateFailure('invalid leap seconds on ' + format_day(day + dday))

    return (sec, dday, timesys)


_HH_COLON_MM = re.compile(r'(?<!\d)[012]?\d:[ 0-5]\d(?!\d)')

def _time_pattern_filter(string):
    """Quick regular expression tests to determine if this string might contain a time."""

    if not _PRE_FILTER:
        return True         # pragma: no cover

    if _HH_COLON_MM.search(string):
        return True

    return False

##########################################################################################
