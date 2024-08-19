##########################################################################################
# julian/DEPRECATED.py
##########################################################################################
"""Deprecated function names from Julian Library version 1
"""
##########################################################################################

import numpy as np

from julian._exceptions import JulianValidateFailure
from julian._utils      import _int
from julian._warnings   import _warn

##########################################################################################
# From julian/calendar.py
##########################################################################################

from julian.calendar import day_from_ymd

def month_from_ym(y, m, *, validate=False):
    """Number of elapsed months since January 2000.

    Inputs:
        y           year as a scalar, array, or array-like. Values are truncated to
                    integers if necessary. Note that 1 BCE corresponds to year 0, 2 BCE to
                    -1, etc.
        m           month number, 1-12, as a scalar, array, or array-like. Values are
                    truncated to integers if necessary.
        validate    True to raise JulianValidateFailure (a ValueError subclass) for year,
                    month, and day numbers out of range; default is False.
    """

    _warn('month_from_ym() is deprecated; previously for internal use only')

    m = _int(m)

    if validate:
        if np.any(m < 1) or np.any(m > 12):
            raise JulianValidateFailure('month number must be between 1 and 12')

    return 12*(y - 2000) + (m - 1)

########################################

def ym_from_month(month):
    """Year and month from the number of elapsed months since January 2000.

    Inputs:
        month       month number, as the number of elapsed months since the beginning of
                    January 2000. Can be a scalar, array, or array-like. Values are
                    truncated to integers if necessary.
    """

    _warn('ym_from_month() is deprecated; previously for internal use only')

    month = _int(month)

    y = _int(month // 12)
    m = month - 12 * y
    y += 2000
    m += 1

    return (y, m)

########################################

def days_in_month(month, *, proleptic=False):
    """Number of days in month, given the number of elapsed months since January 2000.

    Note that this is the actual number of days from the first of one month to the first
    of the next. If proleptic is False, this number will be less than the last valid
    calendar day during the month of transition from the Julian to Gregorian calendar.

    Inputs:
        month       month number, as the number of elapsed months since the beginning of
                    January 2000. Can be a scalar, array, or array-like. Values are
                    truncated to integers if necessary.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
                    Regardless of the calendar, all dates BCE are proleptic.
    """

    _warn('days_in_month() is deprecated; use days_in_ym()')

    month = _int(month)

    (y, m) = ym_from_month(month)
    day0 = day_from_ymd(y, m, 1, proleptic=proleptic)

    (y, m) = ym_from_month(month + 1)
    day1 = day_from_ymd(y, m, 1, proleptic=proleptic)

    return day1 - day0

##########################################################################################
# From julian/date_parsers.py
##########################################################################################

from julian.date_parsers import days_in_strings

def day_in_string(string, order='YMD', remainder=False, use_julian=True):
    """Day number derived from the first date that appears in the string.

    Returns None if no date was found.

    DEPRECATED. Use days_in_strings() with first=True.

    Input:
        string      string to interpret.
        order       one of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        remainder   if True and a date was found, return a tuple:
                        (day number, remainder of string).
                    Otherwise, just return the day number.
        use_julian  True to interpret dates prior to the adoption of the Gregorian
                    calendar as dates in the Julian calendar.
    """

    _warn('day_in_string() is deprecated; use days_in_strings() with first=True')

    result = days_in_strings([string], order=order, doy=True, mjd=False,
                             proleptic=(not use_julian), validate=True,
                             substrings=True, first=True)
    if result is None:
        return None

    day, substring = result
    if remainder:
        return (day, string.partition(substring)[2])
    else:
        return day


def days_in_string(string, order='YMD', use_julian=True):
    """List of day numbers found in this string.

    Input:
        string      string to interpret.
        order       one of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        use_julian  True to interpret dates prior to the adoption of the Gregorian
                    calendar as dates in the Julian calendar.
    """

    _warn('days_in_string() is deprecated; use days_in_strings()')

    return days_in_strings([string], order=order, doy=True, mjd=False,
                           proleptic=(not use_julian), validate=True, substrings=False,
                           first=False)

##########################################################################################
# From julian/datetime_parsers.py
##########################################################################################

from julian.datetime_parsers import day_sec_from_string, day_sec_in_strings

def day_sec_type_from_string(string, order="YMD", validate=True, use_julian=True):
    """Day, second, and time system based on the parsing of the string.

    DEPRECATED. Use day_sec_from_string() with timesys=True.

    Input:
        string          String to interpret.
        order           One of 'YMD', 'MDY', or 'DMY'; this defines the default
                        order for date, month, and year in situations where it
                        might be ambiguous.
        validate        True to check the syntax and values more carefully. *IGNORED*
        use_julian      True to interpret dates prior to the adoption of the
                        Gregorian calendar as dates in the Julian calendar.
    """

    _warn('day_sec_type_from_string() is deprecated; '
          'use day_sec_from_string() with timesys=True')

    return day_sec_from_string(string, order=order, timesys=True, timezones=False,
                               mjd=True, floating=True, proleptic=(not use_julian))


def day_sec_type_in_string(string, order='YMD', *, remainder=False, use_julian=True):
    """Day, second, and time system based on the first occurrence of a date within a
    string.

    None if no date was found.

    DEPRECATED. Use day_sec_in_strings() with timesys=True.

    Input:
        string      string to interpret.
        order       One of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        remainder   If True and a date was found, return a 4-element tuple:
                        (day, sec, time system, remainder of string).
                    Otherwise, just return the 3-element tuple:
                        (day, sec, time system).
        use_julian  True to interpret dates prior to the adoption of the Gregorian
                    calendar as dates in the Julian calendar.
    """

    _warn('day_sec_type_in_string() is deprecated; '
          'use day_sec_in_strings() with timesys=True')

    result = day_sec_in_strings([string], order=order, doy=True, mjd=False,
                                proleptic=(not use_julian), treq=False, leapsecs=True,
                                ampm=True, timezones=False, timesys=True, floating=False,
                                validate=True, substrings=True, first=True)
    if result is None:
        return None

    day, sec, tsys, substring = result
    if remainder:
        return (day, sec, tsys, string.partition(substring)[2])
    else:
        return (day, sec, tsys)


def dates_in_string(string, order='YMD', *, use_julian=True):
    """List of the dates found in this string, represented by tuples (day, sec, time
    system).

    DEPRECATED. Use day_sec_in_strings().

    Input:
        string      string to interpret.
        order       One of "YMD", "MDY", or "DMY"; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        use_julian  True to interpret dates prior to the adoption of the Gregorian
                    calendar as dates in the Julian calendar.
    """

    return day_sec_in_strings([string], order=order, doy=True, mjd=True,
                              proleptic=(not use_julian), treq=False, leapsecs=True,
                              ampm=True, timezones=False, floating=True, timesys=True,
                              validate=True, substrings=False, first=False)

##########################################################################################
# From julian/formatters.py
##########################################################################################

from julian.formatters import format_day, format_day_sec, format_sec, format_tai

def ymd_format_from_day(day, *, ydigits=4, dash='-', ddigits=None, proleptic=False,
                        buffer=None, kind="U"):
    """Date in "yyyy-mm-dd" format.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    DEPRECATED name. This function is a variant of format_day() but with a reduced set of
    options.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        ydigits     number of year digits to include, 2 or 4; default 4.
        dash        character(s) to include between fields, if any. Default is "-". Use ""
                    for no separators; any other string can also be used in place of
                    the dashes.
        ddigits     decimal digits to include in day values; use -1 or None to suppress
                    the decimal point; ignored if day values are integers.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_day(day, order='YMD', ydigits=ydigits, dash=dash,  ddigits=ddigits,
                      proleptic=proleptic, buffer=buffer, kind=kind)


def yd_format_from_day(day, *, ydigits=4, dash='-', ddigits=None, proleptic=False,
                       buffer=None, kind="U"):
    """Date in "yyyy-ddd" format. Supports scalars or array-like arguments.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    DEPRECATED name. This function is a variant of format_day() but with a reduced set of
    options.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        ydigits     number of year digits to include, 2 or 4; default 4.
        dash        character(s) to include between fields, if any. Default is "-". Use ""
                    for no separators; any other string can also be used in place of
                    the dashes.
        ddigits     decimal digits to include in day values; use -1 or None to suppress
                    the decimal point; ignored if day values are integers.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_day(day, order='YD', ydigits=ydigits, dash=dash, ddigits=ddigits,
                      proleptic=proleptic, buffer=buffer, kind=kind)


def hms_format_from_sec(sec, digits=None, suffix='', *, colon=':', buffer=None, kind='U'):
    """Time in "hh:mm:ss[.fff][Z]" format.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    DEPRECATED name. This function is a variant of format_sec() with a reduced set of
    options.

    Input:
        sec         the number of seconds into a day, or an arbitrary array thereof;
                    each value should be >= 0 and < 86410.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        suffix      "Z" to include the Zulu time zone indicator.
        colon       character(s) to include between fields, if any. Default is ":". Use
                    "" for no separators; any other string can also be used in place of
                    the colons.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_sec(sec, digits=digits, colon=colon, suffix=suffix, buffer=buffer,
                      kind=kind)


def ymdhms_format_from_day_sec(day, sec, sep='T', digits=None, suffix='',
                               proleptic=False, buffer=None, kind='U'):
    """Date and time in ISO format "yyyy-mm-ddThh:mm:ss....".

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    DEPRECATED name. This function is a variant of format_day_sec() with a reduced set of
    options.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        sec         the number of seconds into a day; should be less than the number of
                    seconds on the associated day. Note that day and sec need not have the
                    same shape, but must be broadcastable to the same shape.
        sep         the character to separate the date from the time. Default is "T" but
                    " " is also allowed.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional byte array into which to write the results.
                    Only used if day/sec are arrays. If the buffer is provided,
                    the elements must have sufficient length.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_day_sec(day, sec, order='YMDT', ydigits=4, dash='-', sep=sep, colon=':',
                          digits=digits, suffix=suffix, proleptic=proleptic,
                          buffer=buffer, kind=kind)


def ydhms_format_from_day_sec(day, sec, *, sep='T', digits=None, suffix='',
                              proleptic=False, buffer=None, kind='U'):
    """Date and time in ISO format "yyyy-dddThh:mm:ss....".

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    DEPRECATED name. This function is a variant of format_day_sec() with a reduced set of
    options.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        sec         the number of seconds into a day; should be less than the number of
                    seconds on the associated day. Note that day and sec need not have the
                    same shape, but must be broadcastable to the same shape.
        sep         the character to separate the date from the time. Default is "T" but
                    " " is also allowed.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional byte array into which to write the results. Only used if
                    day/sec are arrays. If the buffer is provided, the elements must have
                    sufficient length.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_day_sec(day, sec, order='YDT', ydigits=4, dash='-', sep=sep, colon=':',
                          digits=digits, suffix=suffix, proleptic=proleptic,
                          buffer=buffer, kind=kind)


def ymdhms_format_from_tai(tai, *, sep='T', digits=None, suffix='', proleptic=False,
                           buffer=None, kind='U'):
    """Date and time in ISO format "yyyy-mm-ddThh:mm:ss...." given seconds TAI.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype "U") or bytes
    (dtype "S"). If the latter, you can define it as a NumPy memmap and write content
    directly into an ASCII table file.

    DEPRECATED name. This function is a variant of format_tai() but with a reduced set of
    options.

    Input:
        tai         time value in seconds TAI or an array of time values.
        sep         the character to separate the date from the time. Default is "T" but
                    " " is also allowed.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_tai(tai, order='YMDT', ydigits=4, dash='-', sep=sep, colon=':',
                      digits=digits, suffix=suffix, proleptic=proleptic, buffer=buffer,
                      kind=kind)


def ydhms_format_from_tai(tai, *, sep='T', digits=None, suffix='', proleptic=False,
                          buffer=None, kind='U'):
    """Date and time in ISO format "yyyy-dddThh:mm:ss...." given seconds TAI.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype "U") or bytes
    (dtype "S"). If the latter, you can define it as a NumPy memmap and write content
    directly into an ASCII table file.

    DEPRECATED name. This function is a variant of format_tai() but with a reduced set of
    options.

    Input:
        tai         time value in seconds TAI or an array of time values.
        sep         the character to separate the date from the time. Default is "T" but
                    " " is also allowed.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    return format_tai(tai, order='YDT', ydigits=4, dash='-', sep=sep, colon=':',
                      digits=digits, suffix=suffix, proleptic=proleptic, buffer=buffer,
                      kind=kind)

##########################################################################################
# From julian/mjd_jd.py
##########################################################################################

from julian.mjd_jd import jd_from_time, mjd_from_time, time_from_jd, time_from_mjd

def mjed_from_tdb(tdb):
    """Modified Julian Ephemeris Date from TDB seconds.

    DEPRECATED. Use mjd_from_time() with timesys='TDB', mjdsys='TDB'.
    """

    _warn('mjed_from_tdb() is deprecated; '
          'use mjd_from_time() with timesys="TDB", mjdsys="TDB"')

    return mjd_from_time(tdb, timesys='TDB', mjdsys='TDB')


def jed_from_tdb(tdb):
    """Julian Ephemeris Date from TDB seconds.

    DEPRECATED. Use jd_from_time() with timesys='TDB', jdsys='TDB'.
    """

    _warn('jed_from_tdb() is deprecated; '
          'use jd_from_time() with timesys="TDB", jdsys="TDB"')

    return jd_from_time(tdb, timesys='TDB', jdsys='TDB')


def tdb_from_mjed(mjed):
    """TDB seconds from Modified Julian Ephemeris Date.

    DEPRECATED. Use time_from_mjd() with timesys='TDB', mjdsys='TDB'.
    """

    _warn('tdb_from_mjed() is deprecated; '
          'use jd_from_time() with timesys="TDB", mjdsys="TDB"')

    return time_from_mjd(mjed, timesys='TDB', mjdsys='TDB')


def tdb_from_jed(jed):
    """TDB seconds from Modified Julian Ephemeris Date.

    DEPRECATED. Use time_from_jd() with timesys='TDB', jdsys='TDB'.
    """

    _warn('tdb_from_jed() is deprecated; '
          'use time_from_jd() with timesys="TDB", jdsys="TDB"')

    return time_from_jd(jed, timesys='TDB', jdsys='TDB')


def mjed_from_tai(tai):
    """Modified Julian Ephemeris Date from TAI seconds.

    DEPRECATED. Use mjd_from_time() with timesys='TAI', mjdsys='TDB'.
    """

    _warn('mjed_from_tai() is deprecated; '
          'use mjd_from_time() with timesys="TAI", mjdsys="TDB"')

    return mjd_from_time(tai, timesys='TAI', mjdsys='TDB')


def jed_from_tai(tai):
    """Julian Ephemeris Date from TAI seconds.

    DEPRECATED. Use jd_from_time() with timesys='TAI', jdsys='TDB'.
    """

    _warn('jed_from_tai() is deprecated; '
          'use jd_from_time() with timesys="TAI", jdsys="TDB"')

    return jd_from_time(tai, timesys='TAI', jdsys='TDB')


def tai_from_mjed(mjed):
    """TAI seconds from Modified Julian Ephemeris Date.

    DEPRECATED. Use time_from_mjd() with timesys='TAI', mjdsys='TDB'.
    """

    _warn('tai_from_mjed() is deprecated; '
          'use time_from_mjd() with timesys="TAI", mjdsys="TDB"')

    return time_from_mjd(mjed, timesys='TAI', mjdsys='TDB')


def tai_from_jed(jed):
    """TDB seconds from Modified Julian Ephemeris Date.

    DEPRECATED. Use time_from_jd() with timesys='TAI', jdsys='TDB'.
    """

    _warn('tai_from_jed() is deprecated; '
          'use time_from_jd() with timesys="TAI", jdsys="TDB"')

    return time_from_jd(jed, timesys='TAI', jdsys='TDB')

##########################################################################################
# From julian/time_parsers.py
##########################################################################################

from julian.time_parsers import secs_in_strings

def time_in_string(string, remainder=False):
    """Second value based on the first identified time in a string.

    Returns None if no time was found.

    DEPRECATED. Use secs_in_strings().

    Input:
        string          string to interpret.
        remainder       If True and a date was found, return a tuple:
                            (seconds, remainder of string).
                        Otherwise, just return the day number.
    """

    _warn('time_in_string() is deprecated; use sec_in_strings()')

    result = secs_in_strings([string], leapsecs=True, ampm=True, timezones=False,
                             floating=False, validate=True, substrings=True, first=True)
    if result is None:
        return None

    sec, substring = result
    if remainder:
        return (sec, string.partition(substring)[2])
    else:
        return sec


def times_in_string(string):
    """List of seconds values found in this string.

    DEPRECATED. Use sec_in_strings().
    """

    _warn('times_in_string() is deprecated; use sec_in_strings()')

    return secs_in_strings([string], leapsecs=True, ampm=True, timezones=False,
                           floating=True, validate=True)

##########################################################################################
# From julian/utc_tai_tdb_tt.py
##########################################################################################

from julian.utc_tai_tdb_tt import day_sec_from_time, time_from_day_sec

def utc_from_day_sec_as_type(day, sec, time_type='UTC'):
    """DEPRECATED. Retained for backward compatibility.

    Use day_sec_from_time() with leapsecs=True.
    """

    _warn('utc_from_day_sec_as_type() is deprecated; '
          'use day_sec_from_time() with leapsecs=True')

    time = time_from_day_sec(day, sec, time_type, leapsecs=(time_type == 'UTC'))
    return day_sec_from_time(time, time_type, leapsecs=True)


def day_sec_as_type_from_utc(day, sec, time_type='UTC'):
    """DEPRECATED. Retained for backward compatibility.

    Use day_sec_from_time() with leapsecs = (time_type == 'UTC').
    """

    _warn('day_sec_as_type_from_utc() is deprecated; '
          'use day_sec_from_time() with leapsecs=(time_type == "UTC")')

    time = time_from_day_sec(day, sec, time_type, leapsecs=True)
    return day_sec_from_time(time, time_type, leapsecs=(time_type == 'UTC'))

##########################################################################################

