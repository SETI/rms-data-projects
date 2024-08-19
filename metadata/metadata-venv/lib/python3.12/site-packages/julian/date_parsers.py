##########################################################################################
# julian/date_parsers.py
##########################################################################################
"""Functions to parse dates given in arbitrary formats
"""
##########################################################################################

import pyparsing
import re

from julian.calendar      import day_from_yd, day_from_ymd
from julian.date_pyparser import date_pyparser
from julian.formatters    import format_day
from julian.mjd_jd        import day_from_mjd
from julian._exceptions   import JulianParseException, JulianValidateFailure

_PRE_FILTER = True      # set False for some performance tests

##########################################################################################
# General date parser
##########################################################################################

def day_from_string(string, order='YMD', *, doy=True, mjd=False, weekdays=False,
                    extended=False, proleptic=False, validate=True):
    """Day number based on the parsing of a free-form string.

    Input:
        string      string to interpret.
        order       One of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        doy         True to recognize dates specified as year and day-of-year.
        mjd         True to recognize Modified Julian Dates.
        weekdays    True to allow dates including weekdays.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        validate    True to raise JulianValidateFailure (a ValueError subclass) for
                    patterns that resemble dates but do not correspond to an actual date
                    on the calendar.
    """

    parser = date_pyparser(order=order, strict=False, doy=doy, mjd=mjd, weekdays=weekdays,
                           extended=extended, padding=True, embedded=False)
    try:
        parse_list = parser.parse_string(string).as_list()
    except pyparsing.ParseException:
        raise JulianParseException(f'unrecognized date format: "{string}"')

    parse_dict = {key:value for key, value in parse_list}
    return _day_from_dict(parse_dict, proleptic=proleptic, validate=validate)

##########################################################################################
# Date scrapers
##########################################################################################

def days_in_strings(strings, order='YMD', *, doy=False, mjd=False, weekdays=False,
                    extended=False, proleptic=False, validate=True, substrings=False,
                    first=False):
    """List of day numbers obtained by searching one or more strings for patterns that
   look like formatted dates.

    Input:
        strings     list/array/tuple of strings to interpret.
        order       One of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        doy         True to recognize dates specified as year and day-of-year.
        mjd         True to recognize Modified Julian Dates.
        weekdays    True to allow dates including weekdays.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        validate    if True, patterns that resembled dates but are not valid for other
                    reasons are ignored.
        substrings  True to also return the substring containing each identified date.
        first       True to return when the first day is found, with None on failure;
                    False to return the full, ordered list of days found.

    Return:         a list containing either day values or tuples (day, substring).
        day         day numbers.
        substring   the substring containing the text that was interpreted to represent
                    this date; included if the input value of substrings is True.

        Note: If the input value of first is True, then the returned quantity is not a
        list, just a single day value or tuple, or else None if no date was identified.
    """

    if isinstance(strings, str):
        strings = [strings]

    parser = date_pyparser(order=order, doy=doy, mjd=mjd, weekdays=weekdays,
                           extended=extended, strict=True, floating=False, iso_only=False,
                           padding=True, embedded=True)

    day_list = []
    for string in strings:

        # Use fast check to skip over strings that are clearly date-less
        if not _date_pattern_filter(string, doy=doy, mjd=mjd):
            continue

        while True:
            parse_dict, substring, string = _search_in_string(string, parser)
            if not parse_dict:
                break

            try:
                day = _day_from_dict(parse_dict, proleptic=proleptic, validate=validate)
            except ValueError:
                continue

            if substrings:
                day_list.append((day, substring))
            else:
                day_list.append(day)

            if first:
                return day_list[0]

    if first:
        return None

    return day_list

##########################################################################################
# Utilities
##########################################################################################

_WORDS = re.compile('([A-Za-z0-9.]+)')

def _search_in_string(string, parser):
    """Parse dictionary derived from the first matching pattern in the string.

    Input:
        string      string to interpret.
        parser      parser to use.

    Return:         (parse_dict, match, remainder)
        parse_dict  dictionary of information about the first matching string. If no match
                    was found, this dictionary is empty.
        match       the text that matched; empty string on failure.
        remainder   the remainder of the string following the match; empty string on
                    failure.
    """

    # To speed things up, only check starting at the beginning of each word
    words = _WORDS.split(string)

    result = None
    for k in range(1, len(words), 2):       # words are at odd locations in this list
        substring = ''.join(words[k:])
        try:
            result = parser.parse_string(substring)
            break
        except pyparsing.ParseException:
            pass

    if result is None:
        return ({}, '', '')

    parse_dict = {key:value for key, value in result.as_list()}

    loc = parse_dict['~']
    match_text = substring[:loc].strip()
    remainder_text = substring[loc:]

    return (parse_dict, match_text, remainder_text)


_WEEKDAYS = {'SAT':0, 'SUN':1, 'MON':2, 'TUE':3, 'WED':4, 'THU':5, 'FRI':6}
_WEEKDAY_NAMES = {'SAT':'Saturday', 'SUN':'Sunday', 'MON':'Monday', 'TUE':'Tuesday',
                  'WED':'Wednesday', 'THU':'Thursday', 'FRI':'Friday'}

def _day_from_dict(parse_dict, proleptic=True, validate=True):
    """Day number based on the contents of a dictionary."""

    y = parse_dict['YEAR']
    d = int(parse_dict['DAY'] // 1.)

    # First check for MJD date
    if y == 'MJD':
        return day_from_mjd(d)

    # Interpret year, month and day
    if 'MONTH' in parse_dict:
        m = parse_dict['MONTH']
        day = day_from_ymd(y, m, d, validate=validate, proleptic=proleptic)
    else:
        day = day_from_yd(y, d, validate=validate, proleptic=proleptic)

    # Check weekday if necessary
    if validate and 'WEEKDAY' in parse_dict:
        if day % 7 != _WEEKDAYS[parse_dict['WEEKDAY']]:
            date = format_day(day, order=('YMD' if 'MONTH' in parse_dict else 'YD'))
            name = _WEEKDAY_NAMES[parse_dict['WEEKDAY']]
            raise JulianValidateFailure(f'Date {date} is not a {name}')

    return day


_DATE_WORDS_REGEX  = re.compile(r'(?<![A-Z])(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|'
                                            'DEC|MON|TUE|WED|THU|FRI|SAT|SUN)', re.I)
_YEAR12_REGEX      = re.compile(r'(?<!\d)[12]\d\d\d(?!\d)')
_FOUR_DIGITS       = re.compile(r'(?<!\d)\d\d\d\d(?!\d)')
_ONE_OR_TWO_DIGITS = re.compile(r'(?<!\d)\d\d?(?!\d)')
_YEAR_DOY_REGEX    = re.compile(r'(?<!\d)(\d\d)?\d\d[^\d]{1,4}[0-3]?\d?\d(?!\d)')
_MJD_REGEX         = re.compile(r'(?<![A-Z])M?J[ET]?D(?![A-Z])', re.I)

def _date_pattern_filter(string, doy=False, mjd=False):
    """True if this string _might_ contain a date.

    This is a quick set of tests using regular expressions; it speeds up the search by not
    spending time attempting to parse strings that clearly do not contain a date.
    """

    if not _PRE_FILTER:
        return True         # pragma: no cover

    # If a month name or weekday name appears, we have a candidate.
    if _DATE_WORDS_REGEX.search(string):
        return True

    # If a 4-digit year starting with 1 or 2 appears, we have a candidate.
    if _YEAR12_REGEX.search(string):
        return True

    # Count the one- or two-digit numbers
    ints = len(_ONE_OR_TWO_DIGITS.findall(string))

    # If three or more appear, we have a candidate.
    if ints >= 3:
        return True

    # A four-digit integer plus two or more integers with one or two digits is also a
    # candidate.
    if _FOUR_DIGITS.search(string) and ints >= 2:
        return True

    # For the day-of-year case, the last remaining option is a two digit number followed
    # closely by a three-digit number < 400
    if doy and _YEAR_DOY_REGEX.search(string):
        return True

    # Check for MJD
    if mjd and _MJD_REGEX.search(string):
        return True

    return False

##########################################################################################

