##########################################################################################
# julian/datetime_pyparser.py
##########################################################################################
"""Function to generate a PyParsing grammar for arbitrary date/time strings
"""
##########################################################################################

from julian.mjd_pyparser  import mjd_pyparser
from julian.date_pyparser import date_pyparser
from julian.time_pyparser import time_pyparser, opt_timesys

from pyparsing import (
    FollowedBy,
    Literal,
    OneOrMore,
    ParserElement,
    StringEnd,
    Suppress,
    White,
    ZeroOrMore,
    alphanums,
    one_of,
)

# All whitespace is handled explicitly
ParserElement.set_default_whitespace_chars('')

# Useful definitions...
white     = Suppress(OneOrMore(White()))
opt_white = Suppress(ZeroOrMore(White()))

seps = ['-', ',', '//', '/', ':']
NORMAL_SEPS  = Suppress(opt_white + one_of(seps) + opt_white) | white
ISOLIKE_SEPS = Suppress(opt_white + one_of(seps + ['T']) + opt_white) | white
T = Suppress(Literal('T'))


def datetime_pyparser(order='YMD', *, treq=False, strict=False, doy=False, mjd=False,
                      weekdays=False, extended=False, leapsecs=False, ampm=False,
                      timezones=False, timesys=False, floating=False, iso_only=False,
                      padding=True, embedded=False):
    """A date-time pyparser.

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
        ("HOUR", hour)      hour if specified, 0-23, an int or possibly a float. Hours
                            am/pm are converted to the range 0-23 automatically.
        ("MINUTE", minute)  minute if specified, integer or float.
        ("SECOND", second)  second if specified, integer or float.
        ("TZ", tz_name)     name of the time zone if specified.
        ("TZMIN", tzmin)    offset of the time zone in minutes.
        ("TIMESYS", name)   time system if specified: "UTC", "TAI", "TDB", or "TDT".
        ("~", number)       the last occurrence of this tuple in the list contains the
                            number of characters matched.

    Input:
        order       One of 'YMD', 'MDY', or 'DMY'; this defines the default order for
                    date, month, and year in situations where it might be ambiguous.
        treq        True to allow date values with the time component missing.
        strict      True for a stricter date parsing, which is less likely to match
                    strings that might not actually represent dates.
        doy         True to allow dates specified as year and day-of-year.
        mjd         True to allow date-times specified as MJD.
        weekdays    True to allow dates including weekdays.
        extended    True to support extended year values: signed (with at least four
                    digits) and those involving "CE", "BCE", "AD", "BC".
        leapsecs    True to allow leap seconds.
        ampm        True to allow "am" and "pm" suffixes on times.
        timezones   True to allow time zone suffixes on times.
        timesys     True to allow a time system, e.g., "UTC", "TAI", "TDB", or "TT".
        floating    True to allow date-times specified using floating-point days, hours,
                    or minutes.
        iso_only    Require an ISO 8601:1988-compatible date-time string. If True, input
                    options strict, mjd, ampm, and timesys are ignored.
        padding     True to ignore leading or trailing white space.
        embedded    True to allow the time to be followed by additional text.
    """

    # Always include the full ISO 8601:1988 format, including the "T" separator.
    # This is the only allowed use of "T" as a separator.
    iso_idate = date_pyparser(iso_only=True, doy=doy, extended=extended, floating=False,
                              padding=False, embedded=True)
    iso_time = time_pyparser(iso_only=True, leapsecs=leapsecs, timezones=timezones,
                             floating=floating, padding=False, embedded=True)

    if iso_only:
        pyparser = iso_idate + T + iso_time
        if floating:
            iso_fdate = date_pyparser(iso_only=True, doy=doy, extended=extended,
                                      floating=True, floating_only=treq,
                                      padding=False, embedded=True)
            pyparser |= iso_fdate

        elif not treq:
            pyparser |= iso_idate

    # Augment the parser for non-ISO date-times
    else:

        # Define the general parser for date + time or time + date
        # Note that MJD and floating-point dates cannot be combined with a time
        idate = date_pyparser(order=order, strict=strict, doy=doy, mjd=False,
                              weekdays=weekdays, extended=extended, floating=False,
                              padding=False, embedded=True)
        time = time_pyparser(leapsecs=leapsecs, ampm=ampm, timezones=timezones,
                             timesys=timesys, floating=floating,
                             padding=False, embedded=True)

        # Define the parser with or without a time requirement
        pyparser = idate + NORMAL_SEPS + time | time + NORMAL_SEPS + idate

        # Allow for a floating-point date and/or a time system without a date
        if floating:
            fdate = date_pyparser(order=order, strict=strict, doy=doy, mjd=False,
                                  weekdays=weekdays, extended=extended,
                                  floating=True, floating_only=treq,
                                  padding=False, embedded=True)
            if timesys:
                pyparser |= fdate + opt_timesys
            else:
                pyparser |= fdate

        elif not treq:
            if timesys:
                pyparser |= idate + opt_timesys
            else:
                pyparser |= idate

        # Allow for the MJD options
        if mjd:
            mjd_parser = mjd_pyparser(floating=True, timesys=timesys,
                                      padding=False, embedded=True)
            if timesys:
                wo_timesys = mjd_pyparser(floating=True, timesys=False,
                                          padding=False, embedded=True)
                pyparser |= mjd_parser | wo_timesys + opt_timesys
            else:
                pyparser |= mjd_parser

        # Place the standard ISO parser in front
        pyparser = iso_idate + T + iso_time | pyparser

    # Finalize and return
    pyparser = pyparser + ~FollowedBy(alphanums + '.+-' )

    if padding:
        pyparser = opt_white + pyparser + opt_white

    if not embedded:
        pyparser = pyparser + StringEnd()

    return pyparser

##########################################################################################
