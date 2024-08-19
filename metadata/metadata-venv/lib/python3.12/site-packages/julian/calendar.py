##########################################################################################
# julian/calendar.py
##########################################################################################
"""Calendar functions

Algorithms are from http://alcor.concordia.ca/~gpkatch/gdate-algorithm.html

day     = number of days elapsed since January 1, 2000
month   = number of months elapsed since January 2000
(y,m,d) = year, month (1-12), day (1-31)
(y,d)   = year and day-of-year (1-366)
(y,m)   = year and month number (1-12)

All function operate on either scalars or arrays. If given scalars, they return Python
ints or floats; if given anything array-like, they return NumPy arrays.
"""
##########################################################################################

import numpy as np

from julian._exceptions import JulianValidateFailure
from julian._utils      import _int, _is_float, _number


def day_from_ymd(y, m, d, *, validate=False, proleptic=False):
    """Number of elapsed days after January 1, 2000, given a year, month, and day.

    Inputs:
        y           year as a scalar, array, or array-like. Values are truncated to
                    integers if necessary. Note that 1 BCE corresponds to year 0, 2 BCE to
                    -1, etc.
        m           month number, 1-12, as a scalar, array, or array-like. Values are
                    truncated to integers if necessary.
        d           day number, 1-31, as a scalar, array, or array-like. Values can be
                    integers or floats; if the latter, floating-point values are returned.
        validate    True to raise JulianValidateFailure (a ValueError subclass) for year,
                    month, or day numbers out of range; default is False.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    y = _int(y)
    m = _int(m)
    d = _number(d)

    is_float = _is_float(d)
    if is_float:
        frac = d % 1
        d = _int(d)
    else:
        frac = 0

    if validate:
        if np.any(m < 1) or np.any(m > 12):
            raise JulianValidateFailure('month must be between 1 and 12')
        if np.any(d < 1):
            raise JulianValidateFailure('day number must be at least 1')
        if np.any(d >= days_in_ym(y, m, proleptic=True) + 1):  # 31.99 is OK, but not 32
            raise JulianValidateFailure('day number cannot exceed days in month')

    mm = (m + 9) % 12   # This makes March the first month and February the last
    yy = y - mm//10     # This subtracts one from the year if the month is January or
                        # February.

    # Random notes:
    #
    # 306 is the number of days in March-December
    #
    # The formula (mm*306 + 5)//10 yields the number of days from the end of February to
    # the end of the given the month, using mm==1 for March, 2 for April, ... 10 for
    # December, 11 for January.
    #
    # The formula 365*yy + yy//4 - yy//100 + yy//400 is the number of elapsed days from
    # the end of February in 1 BCE to the end of February in year yy. (Note that 1 BCE is
    # yy==0.)

    day = ((365*yy + yy//4 - yy//100 + yy//400) + (mm * 306 + 5) // 10 + d
           + _FEB29_1BCE_GREGORIAN)

    if proleptic:
        return day + frac

    # Handle the Julian-Gregorian calendar transition if necessary
    if np.isscalar(day):
        if day >= _GREGORIAN_DAY1:
            return day + frac
        else:
            alt_day = ((365 * yy + yy//4) + (mm * 306 + 5) // 10 + d
                       + _FEB29_1BCE_JULIAN)
            if validate:
                alt_ymd = ymd_from_day(alt_day, proleptic=False)
                if alt_ymd != (y,m,d):
                    isodate = '%04d-%02d-%02d' % (y, m, d)
                    raise JulianValidateFailure(isodate + ' falls between the Julian and '
                                                          'Gregorian calendars')
            return alt_day + frac

    mask = (day < _GREGORIAN_DAY1)
    if np.any(mask):
        alt_day = (365 * yy + yy//4) + (mm * 306 + 5) // 10 + d + _FEB29_1BCE_JULIAN
        day[mask] = alt_day[mask]

        if validate:
            alt_d = ymd_from_day(alt_day[mask], proleptic=False)[2]
            dd = np.broadcast_to(d, alt_day.shape)
            if np.any(alt_d != dd[mask]):
                raise JulianValidateFailure('one or more dates fall between the Julian '
                                            'and Gregorian calendars')

    if is_float:
        return day + frac

    return day

########################################

def ymd_from_day(day, *, proleptic=False):
    """Year, month and day from day number.

    Inputs:
        day         number of elapsed days after January 1, 2000 as a scalar, array, or
                    or array-like. Values can be integers or floats; if the latter,
                    returned day values are also floats.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    day = _number(day)
    is_float = _is_float(day)
    if is_float:
        frac = day % 1
        day = _int(day)
    else:
        frac = 0

    # Execute the magic algorithm for the proleptic Gregorian calendar
    # Note that 64-bit integers are required for the math operations below
    g = day + 730425                    # Elapsed days after March 1, 1 BCE, Gregorian
    y = (10000*g + 14780)//3652425      # Year, assumed starting on March 1
    doy = g - (365*y + y//4 - y//100 + y//400)
                                        # Day number starting from March 1 of given year

    # In leap years before year 200, doy = -1 on March 1.
    if np.any(doy < 0):
        if np.shape(day):
            y[doy < 0] -= 1
        else:
            y -= 1
        doy = g - (365*y + y//4 - y//100 + y//400)

    if not proleptic:
        # https://www.quora.com/What-were-the-leap-years-from-45-BC-to-0-BC
        # https://scienceworld.wolfram.com/astronomy/LeapYear.html
        # https://www.wwu.edu/astro101/a101_leapyear.shtml

        # Prior to year 1, we extrapolate the Julian calendar backward. In reality, there
        # were no leap days prior to 46 BCE, and there is no clear consensus on which
        # years were leap years in Rome prior to 8 CE.

        mask = (day < _GREGORIAN_DAY1)
        if np.any(mask):
            alt_g = day + 730427
            alt_y = (100 * alt_g + 75) // 36525
            alt_doy = alt_g - (365 * alt_y + alt_y//4)

            if np.isscalar(day):
                y = alt_y
                doy = alt_doy
            else:
                y[mask] = alt_y[mask]
                doy[mask] = alt_doy[mask]

    m0 = (100 * doy + 52)//3060         # mm = month, with m0==0 for March
    m = (m0 + 2) % 12 + 1
    y += (m0 + 2) // 12
    d = doy - (m0 * 306 + 5)//10 + 1

    if is_float:
        return (y, m, d + frac)
    return (y, m, d)

########################################

def yd_from_day(day, *, proleptic=False):
    """Year and day-of-year from day number.

    Inputs:
        day         number of elapsed days after January 1, 2000 as a scalar, array, or
                    array-like. Values can be integers or floats; if the latter, returned
                    day values are also floats.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    (y,m,d) = ymd_from_day(day, proleptic=proleptic)
    return (y, _number(day) - day_from_ymd(y, 1, 1, proleptic=proleptic) + 1)

########################################

def day_from_yd(y, d, *, validate=False, proleptic=False):
    """Day number from year and day-of-year.

    Inputs:
        y           year as a scalar, array, or array-like. Values are truncated to
                    integers if necessary. Note that 1 BCE corresponds to year 0, 2 BCE to
                    -1, etc.
        d           day of year, 1-366, as a scalar, array, or array-like. Values can be
                    integers or floats; if the latter, floating-point values are returned.
        validate    True to raise JulianValidateFailure (a ValueError subclass) for day
                    numbers out of range; default is False.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    if validate:    # pragma: no branch
        if np.any(_int(d) < 1) or np.any(_int(d) > days_in_year(y, proleptic=proleptic)):
            raise JulianValidateFailure('day number cannot exceed the number of days in '
                                        'the year')

    return day_from_ymd(y, 1, 1, proleptic=proleptic) + _number(d) - 1

########################################

_DAYS_IN_MONTH = np.array([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

def days_in_ym(y, m, *, validate=False, proleptic=False):
    """Number of days in month.

    Note that this is the actual number of days from the first of one month to the first
    of the next. If proleptic is False, this number will be less than the last valid
    calendar day during the month of transition from the Julian to Gregorian calendar.

    Inputs:
        y           year as a scalar, array, or array-like. Values are truncated to
                    integers if necessary. Note that 1 BCE corresponds to year 0, 2 BCE to
                    -1, etc.
        m           month number, 1-12, as a scalar, array, or array-like. Values are
                    truncated to integers if necessary.
        validate    True to raise JulianValidateFailure (a ValueError subclass) for month
                    numbers out of range; default is False.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    y = _int(y)
    m = _int(m)

    outside = np.any(m < 1) or np.any(m > 12)
    if validate and outside:
        raise JulianValidateFailure('month must be between 1 and 12')

    # Maybe a bit quicker...
    if proleptic and not outside:
        days = _DAYS_IN_MONTH[m]
        leap_month_mask = (m == 2) & (days_in_year(y) == 366)

        if np.isscalar(leap_month_mask):
            return 29 if leap_month_mask else int(days)

        if leap_month_mask.shape != np.shape(days):
            days = np.broadcast_to(days, leap_month_mask.shape).copy()

        days[leap_month_mask] = 29
        return days

    # Turn off validation because m+1 might be 13
    return (day_from_ymd(y, m+1, 1, proleptic=proleptic, validate=False) -
            day_from_ymd(y, m  , 1, proleptic=proleptic, validate=False))

########################################

def days_in_year(year, *, proleptic=False):
    """Number of days in year.

    Note that this is the actual number of days from the first of one year to the first
    of the next. If proleptic is False, this number will be less than 365 during the year
    of transition from the Julian to Gregorian calendar.

    Inputs:
        y           year as a scalar, array, or array-like. Values are truncated to
                    integers if necessary. Note that 1 BCE corresponds to year 0, 2 BCE to
                    -1, etc.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    year = _int(year)

    # This is quicker if there's no calendar transition
    if proleptic:
        answer = np.empty(np.shape(year), dtype='int64')
        answer.fill(365)
        answer[(year % 4) == 0] = 366
        answer[(year % 100) == 0] = 365
        answer[(year % 400) == 0] = 366
        if np.isscalar(year):
            return int(answer[()])
        return answer

    return (day_from_ymd(year+1, 1, 1, proleptic=proleptic) -
            day_from_ymd(year,   1, 1, proleptic=proleptic))

########################################

def set_gregorian_start(y=1582, m=10, d=15):
    """Set the first day of the Gregorian calendar as a year, month, and day.

    Note that is a global setting for the entire Julian library.

    Use set_gregorian_start(None) to ignore the Julian calendar, using the modern
    Gregorian calendar exclusively, even where proleptic=False.
    """

    global _GREGORIAN_DAY1, _GREGORIAN_DAY1_YMD, _GREGORIAN_DAY0_YMD

    if y is None:       # prevents any Julian calendar date from being used
        _GREGORIAN_DAY1 = -1.e30
        return

    _GREGORIAN_DAY1 = day_from_ymd(y, m, d, proleptic=True)
    _GREGORIAN_DAY1_YMD = (y, m, d)
    _GREGORIAN_DAY0_YMD = ymd_from_day(_GREGORIAN_DAY1-1, proleptic=False)

# Fill in some constants used by day_from_ymd

# Day number of February 29 1 BCE (year 0) in the Gregorian and Julian
# calendars, relative to January 1, 2000 in the Gregorian calendar.
# Should be...
# _FEB29_1BCE_GREGORIAN = -730426
# _FEB29_1BCE_JULIAN    = -730428

# Day number of the first day of the Gregorian calendar, October 15, 1582.
# Should be...
# _GREGORIAN_DAY1 = -152384
# _GREGORIAN_DAY1_YMD = (1582, 10, 15)
# _GREGORIAN_DAY0_YMD = (1582, 10,  4)

# Deriving from first principles...
_FEB29_1BCE_GREGORIAN = 0
_FEB29_1BCE_GREGORIAN = (day_from_ymd(0, 2, 29, proleptic=True) -
                         day_from_ymd(2000, 1, 1, proleptic=True))

_GREGORIAN_DAY1_YMD = (1582, 10, 15)
_GREGORIAN_DAY1 = day_from_ymd(*_GREGORIAN_DAY1_YMD, proleptic=True)

_FEB29_1BCE_JULIAN = 0
_FEB29_1BCE_JULIAN = (day_from_ymd(0, 2, 29, proleptic=False)
                      - day_from_ymd(1582, 10, 5, proleptic=False)
                      + _GREGORIAN_DAY1)

_GREGORIAN_DAY0_YMD = ymd_from_day(_GREGORIAN_DAY1-1, proleptic=False)

##########################################################################################
