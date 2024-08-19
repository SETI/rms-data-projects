##########################################################################################
# julian/datetime_parsers.py
##########################################################################################
"""Functions to parse date/time strings given in arbitrary formats
"""
##########################################################################################

import numbers
import pyparsing

from julian.date_parsers import _date_pattern_filter, _day_from_dict, _search_in_string
from julian.leap_seconds import seconds_on_day
from julian.mjd_jd       import day_from_mjd, _JD_MINUS_MJD
from julian.time_parsers import _sec_from_dict, _time_pattern_filter
from julian._exceptions  import JulianParseException

from julian.datetime_pyparser import datetime_pyparser

##########################################################################################
# General date/time parser
##########################################################################################

def day_sec_from_string(string, order='YMD', *, doy=True, mjd=True, weekdays=False,
                        extended=False, proleptic=False, treq=False, leapsecs=True,
                        ampm=True, timezones=False, timesys=False, floating=False):
    """Day and second values based on the parsing of a free-form string.

    Input:
        string      string to interpret.
        order       one of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        doy         True to recognize dates specified as year and day-of-year.
        mjd         True to recognize dates expressed as MJD, JD, MJED, JED, etc.
        weekdays    True to allow dates including weekdays.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        treq        True if a time field is required; False to recognize date strings that
                    do not include a time.
        leapsecs    True to recognize leap seconds.
        ampm        True to recognize "am" and "pm" suffixes.
        timezones   True to recognize and interpret time zones. If True, returned values
                    are adjusted to UTC.
        timesys     True to recognize an embedded time system such as "UTC", "TAI", etc.
        floating    True to recognize time specified using floating-point hours or
                    minutes.

    Return:         (day, sec) or (day, sec, tsys)
        day         integer day number, converted to UTC if a time zone was identified.
        sec         seconds into day, converted to UTC if a time zone was identified.
        tsys        name of the time system, included if the input value of timesys is
                    True.
    """

    parser = datetime_pyparser(order=order, treq=treq, strict=False, doy=doy, mjd=mjd,
                      weekdays=weekdays, extended=extended, leapsecs=leapsecs, ampm=ampm,
                      timezones=timezones, floating=floating, timesys=timesys,
                      iso_only=False, padding=True, embedded=False)
    try:
        parse_list = parser.parse_string(string).as_list()
    except pyparsing.ParseException:
        raise JulianParseException(f'unrecognized date/time format: "{string}"')

    parse_dict = {key:value for key, value in parse_list}
    (day, sec, tsys) = _day_sec_timesys_from_dict(parse_dict, proleptic=proleptic,
                                                  leapsecs=leapsecs, validate=True)

    if timesys:
        return (day, sec, tsys)

    return (day, sec)

##########################################################################################
# Date/time scrapers
##########################################################################################

def day_sec_in_strings(strings, order='YMD', *, doy=False, mjd=False, weekdays=False,
                       extended=False, proleptic=False, treq=False, leapsecs=True,
                       ampm=False, timezones=False, timesys=False, floating=False,
                       validate=True, substrings=False, first=False):
    """List of day and second values representing date/time strings found by searching one
    or more strings for patterns that look like formatted dates and times.

    Input:
        strings     list/array/tuple of strings to interpret.
        order       one of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        doy         True to allow dates specified as year and day-of-year.
        mjd         True to allow dates expressed as MJD, JD, MJED, JED, etc.
        weekdays    True to allow dates including weekdays.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        treq        True if a time field is required; False to recognize date strings that
                    do not include a time.
        leapsecs    True to recognize leap seconds.
        ampm        True to recognize "am" and "pm" suffixes.
        timezones   True to recognize and interpret time zones. If True, returned values
                    are adjusted to UTC.
        timesys     True to allow a time system, e.g., "UTC", "TAI", "TDB", or "TT".
        floating    True to recognize time specified using floating-point hours or
                    minutes.
        validate    if True, patterns that resembled date/time strings but are not valid
                    for other reasons are ignored.
        substrings  True to also return the substring containing each identified date and
                    time.
        first       True to return when the first date and time is found, with None on
                    failure; False to return the full, ordered list of dates and times.

    Return:         a list of tuples (day, sec, optional tsys, optional substring).
        day         integer day number, onverted to UTC if a time zone was identified.
        sec         seconds into day, onverted to UTC if a time zone was identified.
        tsys        name of each associated time system, with "UTC" the default; included
                    if the input value of timesys is True.
        substring   the substring containing the text that was interpreted to represent
                    this date and time; included if the input value of substrings is True.

        Note: If the input value of first is True, then a single tuple is returned
        rather than a list of tuples. If no date was identified, None is returned.
    """

    if isinstance(strings, str):
        strings = [strings]

    parser = datetime_pyparser(order=order, treq=treq, strict=True, doy=doy, mjd=mjd,
                               weekdays=weekdays, extended=extended, leapsecs=leapsecs,
                               ampm=ampm, timezones=timezones, timesys=timesys,
                               floating=floating, iso_only=False, padding=True,
                               embedded=True)

    day_sec_list = []
    for string in strings:

        # Use fast check to skip over strings that are clearly time-less
        if not _date_pattern_filter(string, doy=doy, mjd=mjd):
            continue
        if treq and not mjd and not _time_pattern_filter(string):
            continue

        while True:
            parse_dict, substring, string = _search_in_string(string, parser)
            if not parse_dict:
                break

            try:
                (day, sec, tsys) = _day_sec_timesys_from_dict(parse_dict,
                                                              leapsecs=leapsecs,
                                                              proleptic=proleptic,
                                                              validate=validate)
            except ValueError:  # pragma: no cover
                continue

            result = [day, sec]
            if timesys:
                result.append(tsys)
            if substrings:
                result.append(substring)

            day_sec_list.append(tuple(result))

            if first:
                return day_sec_list[0]

    if first:
        return None

    return day_sec_list

##########################################################################################
# Utilities
##########################################################################################

def _day_sec_timesys_from_dict(parse_dict, leapsecs=True, proleptic=False, validate=True):
    """Day, second, and time system values based on the contents of a dictionary."""

    year = parse_dict['YEAR']
    day = parse_dict['DAY']
    timesys = parse_dict.get('TIMESYS', '')
    timesys_or_utc = timesys or 'UTC'

    if isinstance(year, numbers.Integral) and isinstance(day, numbers.Integral):
        day = _day_from_dict(parse_dict, proleptic=proleptic, validate=validate)
        sec, dday, tsys = _sec_from_dict(parse_dict, day, leapsecs=leapsecs,
                                         validate=validate)
        return (day + dday, sec, timesys_or_utc)

    if year == 'MJD' and isinstance(day, numbers.Integral):
        return (day_from_mjd(day), 0, timesys_or_utc)

    # The remaining cases all involve a conversion from fractional day to seconds.
    # The year could be a numeric year, "JD", or "MJD".

    # Convert to day number and fraction
    if year == 'JD':
        day = day - _JD_MINUS_MJD
        year = 'MJD'

    frac = day % 1
    day = int(day // 1.)

    if year == 'MJD':
        day = day_from_mjd(day)
    else:
        day = _day_from_dict(parse_dict, proleptic=proleptic, validate=validate)

    # If a time system is specified, it overrides the leapsecs setting
    if timesys:
        leapsecs = (timesys == 'UTC')

    # Convert fraction of day to seconds
    sec = frac * seconds_on_day(day, leapsecs=leapsecs)

    return (day, sec, timesys_or_utc)

##########################################################################################
