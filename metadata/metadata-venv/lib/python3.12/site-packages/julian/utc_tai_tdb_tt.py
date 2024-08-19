##########################################################################################
# julian/utc_tai_tdb_tt.py
##########################################################################################
"""Conversions between time systems: UTC, TAI, TDB, and TT
"""
##########################################################################################

import numpy as np
from julian              import leap_seconds
from julian.calendar     import day_from_ymd, ymd_from_day
from julian.leap_seconds import delta_t_from_ymd, leapsecs_from_day, leapsecs_from_ym, \
                                seconds_on_day
from julian._utils       import _int, _float, _number

_LEAPSECS_ON_JAN_1_2000 = leapsecs_from_ym(2000,1)
_LEAPSECS_ON_JAN_1_1972 = leapsecs_from_ym(1972,1)
_DAY_OF_JAN_1_1972 = day_from_ymd(1972,1,1)
_LEAPSECS_1972_to_2000 = _LEAPSECS_ON_JAN_1_2000 - _LEAPSECS_ON_JAN_1_1972

##########################################################################################
# Support for old TAI/UTC origin of midnight, not noon
##########################################################################################

_TAI_MIDNIGHT_ORIGIN = False    # Filled in by first call to set_tai_origin()
_SECONDS_PAST_MIDNIGHT = 0
_TAI_OF_JAN_1_2000 = 0          # tai value at UTC midnight
_TAI_OF_JAN_1_1972 = 0
_TT_MINUS_TAI = 0.


def set_tai_origin(origin='NOON'):
    """Set the zeros of the TAI and UTC time system to either noon or midnight on January
    1, 2000. DEPRECATED feature.

    The earlier version of this module measured UTC and TAI from ~ midnight on January 1,
    2000. The preferred origin for the time systems is 12 hours later. Use this function
    to reproduce earlier behavior if you are concerned about the matching values of TAI or
    UTC from an earlier version of the Julian Library.

    Input:
        origin      origin of the TAI and UTC time systems, either "NOON" or "MIDNIGHT".
                    "NOON"      UTC = 0 and TAI = 32 at noon on January 1, 2000 UTC. This
                                is consistent with the definition of TAI within the SPICE
                                toolkit.
                    "MIDNIGHT"  UTC = 0 and TAI = 32 at midnight on January 1, 2000 UTC.

    Note that the TDB and TT time systems have always use the "NOON" origin exclusively.
    """

    global _TAI_MIDNIGHT_ORIGIN, _SECONDS_PAST_MIDNIGHT
    global _TAI_OF_JAN_1_2000, _TAI_OF_JAN_1_1972, _TT_MINUS_TAI
    global _UTC_OF_JAN_1_2000, _UTC_OF_JAN_1_1972

    if origin == 'NOON':
        _TAI_MIDNIGHT_ORIGIN = False
        _SECONDS_PAST_MIDNIGHT = 43200
        _TT_MINUS_TAI = 32.184

    elif origin == 'MIDNIGHT':
        _TAI_MIDNIGHT_ORIGIN = True
        _SECONDS_PAST_MIDNIGHT = 0
        _TT_MINUS_TAI = 32.184 - 43200

    else:
        raise ValueError('invalid origin: ' + repr(origin))     # pragma: no cover

    _TAI_OF_JAN_1_2000 =  _LEAPSECS_ON_JAN_1_2000 - _SECONDS_PAST_MIDNIGHT
    _TAI_OF_JAN_1_1972 = (_LEAPSECS_ON_JAN_1_1972 - _SECONDS_PAST_MIDNIGHT
                          + 86400 * _DAY_OF_JAN_1_1972)


# Intialize globals
set_tai_origin()

########################################
# day/sec-TAI conversions
########################################

def day_sec_from_utc(utc):
    """Convert cumulative time in seconds UTC to day number and elapsed seconds.

    The UTC time system is defined to equal zero at noon on January 1, 2000. It differs
    from TAI by a fixed offset of 32 seconds for all dates after the adoption of the leap
    second system in 1972. For earlier dates, when using the "PRE-1972" or "CANON" models,
    UTC uses "rubber seconds", which can expand or shrink as necessary relative to TAI in
    order to ensure that every day before 1972 contained exactly 86,400 seconds.

    Input:
        utc         time in seconds UTC, as a scalar, array, or array-like.

    Return:         (day, sec)
        day         integer UTC day number, starting from January 1, 2000, as a scalar or
                    array.
        sec         seconds within that day, allowing for leap seconds, as a scalar or
                    array. If utc values are given as integers, the returned seconds will
                    also be integers.
    """

    # Reference the time to TAI midnight on January 1, 2000
    tai = _number(utc) + (_SECONDS_PAST_MIDNIGHT + _LEAPSECS_ON_JAN_1_2000)

    # Guess the day. By adding 100 seconds here, this could be one day late but it cannot
    # be early unless the number of leap seconds ever drops below -100, which seems
    # unlikely.
    day = _int((tai + 100) // 86400.)

    # Determine the number of elapsed leap seconds on this day relative to the number on
    # January 1, 2000. Because the number of leap seconds has never gone down (and
    # probably never will if the current leap second system is abandoned as proposed),
    # this is either the correct number or one greater.
    leapsecs = leapsecs_from_day(day)

    # Determine the seconds into the day
    sec = tai - 86400 * day - leapsecs

    # If the day is late or the leap second count is off, the seconds could be negative.
    # If so, decrement the day and increment the time.
    if np.isscalar(sec):
        if sec < 0:
            day -= 1
            sec += seconds_on_day(day)
    else:
        mask = sec < 0
        if np.any(mask):
            day[mask] -= 1
            sec[mask] += seconds_on_day(day[mask])

    return (day, sec)


def utc_from_day_sec(day, sec=0):
    """Convert UTC day number and elapsed seconds to cumulative elapsed UTC seconds.

    The UTC time system is defined to equal zero at noon on January 1, 2000. It differs
    from TAI by a fixed offset of 32 seconds for all dates after the adoption of the leap
    second system in 1972. For earlier dates, when using the "PRE-1972" or "CANON" models,
    UTC uses "rubber seconds", which can expand or shrink as necessary relative to TAI in
    order to ensure that every day before 1972 contained exactly 86,400 seconds.

    Input:
        day         integer UTC day number starting from January 1, 2000, as a scalar,
                    array, or array-like.
        sec         elapsed UTC seconds within that day, allowing for leap seconds. Can be
                    a scalar, array, or array-like. Default is zero.

    Return:         time in seconds UTC, as a scalar or array. If second values are given
                    as integers, the returned values will also be integers.
    """

    day = _number(day)
    (y,m,d) = ymd_from_day(day)
    leapsecs = leapsecs_from_ym(y,m)
    return 86400 * day + leapsecs + (sec - (_SECONDS_PAST_MIDNIGHT
                                            + _LEAPSECS_ON_JAN_1_2000))
        # the groupings inside parentheses eliminate an array op if day is an array but
        # sec is not


def utc_from_day(day, sec=0):
    """Convert UTC day number to cumulative elapsed UTC seconds.

    This is an alternative name for utc_from_day_sec().

    The UTC time system is defined to equal zero at noon on January 1, 2000. It differs
    from TAI by a fixed offset of 32 seconds for all dates after the adoption of the leap
    second system in 1972. For earlier dates, when using the "PRE-1972" or "CANON" models,
    UTC uses "rubber seconds", which can expand or shrink as necessary relative to TAI in
    order to ensure that every day before 1972 contained exactly 86,400 seconds.

    Input:
        day         integer UTC day number starting from January 1, 2000, as a scalar,
                    array, or array-like.
        sec         elapsed UTC seconds within that day, allowing for leap seconds. Can be
                    a scalar, array, or array-like. Default is zero.

    Return:         time in seconds UTC, as a scalar or array. If second values are given
                    as integers, the returned values will also be integers.
    """

    return utc_from_day_sec(day, sec=sec)

########################################
# TAI-UTC conversions
########################################

def tai_from_utc(utc):
    """Convert time in seconds UTC to TAI.

    The UTC time system is defined to equal zero at noon on January 1, 2000. It differs
    from TAI by a fixed offset of 32 seconds for all dates after the adoption of the leap
    second system in 1972. For earlier dates, when using the "PRE-1972" or "CANON" models,
    UTC uses "rubber seconds", which can expand or shrink as necessary relative to TAI in
    order to ensure that every day before 1972 contained exactly 86,400 seconds.

    Input:
        utc         time in seconds UTC as a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array. If utc values are given as
                    integers and UTC "rubber seconds" are not in use, returned values will
                    also be integers.
    """

    utc = _number(utc)
    tai = utc + _LEAPSECS_ON_JAN_1_2000
    if not leap_seconds._RUBBER:
        return tai

    if np.isscalar(tai):
        if tai >= _TAI_OF_JAN_1_1972:
            return tai

        # All days before 1972 contain 86,400 UTC "rubber seconds"
        utc_offset = tai - _TAI_OF_JAN_1_1972
        day_wrt_1972 = utc_offset // 86400
        sec = utc_offset - 86400 * day_wrt_1972
        day = _DAY_OF_JAN_1_1972 + day_wrt_1972
        (y, m, d) = ymd_from_day(day)
        return tai + delta_t_from_ymd(y, m, d + sec/86400.) - 22 + 12

    mask = tai < _TAI_OF_JAN_1_1972
    if not np.any(mask):
        return tai

    tai = np.asarray(tai, dtype=np.double)
    tai1 = tai[mask]
    utc_offset = tai1 - _TAI_OF_JAN_1_1972
    day_wrt_1972 = utc_offset // 86400
    sec = utc_offset - 86400 * day_wrt_1972
    day = _DAY_OF_JAN_1_1972 + day_wrt_1972
    (y, m, d) = ymd_from_day(day)
    tai[mask] = tai1 + delta_t_from_ymd(y, m, d + sec/86400.) - 22 + 12

    return tai


def utc_from_tai(tai):
    """Convert time in seconds TAI to UTC.

    The UTC time system is defined to equal zero at noon on January 1, 2000. It differs
    from TAI by a fixed offset of 32 seconds for all dates after the adoption of the leap
    second system in 1972. For earlier dates, when using the "PRE-1972" or "CANON" models,
    UTC uses "rubber seconds", which can expand or shrink as necessary relative to TAI in
    order to ensure that every day before 1972 contained exactly 86,400 seconds.

    Input:
        tai         time in seconds TAI as a scalar, array, or array-like.

    Return:         time in seconds UTC, as a scalar or array. If tai values are given as
                    integers and UTC "rubber seconds" are not in use, returned values
                    will also be integers.
    """

    tai = _number(tai)
    utc = tai - _LEAPSECS_ON_JAN_1_2000
    if not leap_seconds._RUBBER:
        return utc

    if np.isscalar(tai):
        if tai >= _TAI_OF_JAN_1_1972:
            return utc

        y_prev = 0
        m_prev = -99    # impossible value
        day = int((tai - _SECONDS_PAST_MIDNIGHT) // 86400)   # initial guess
        sec = 0.
        while True:
            (y, m, d) = ymd_from_day(day)
            utc = tai - delta_t_from_ymd(y, m, d+sec/86400.) - _LEAPSECS_1972_to_2000
            if y == y_prev and m == m_prev:
                return utc
            day, sec = day_sec_from_utc(utc)
            y_prev = y
            m_prev = m

    mask = tai < _TAI_OF_JAN_1_1972
    if np.any(mask):
        tai1 = tai[mask]
        y_prev = 0
        m_prev = -99    # impossible value
        day = ((tai1 - _SECONDS_PAST_MIDNIGHT) // 86400).astype('int')
        sec = 0.
        while True:
            (y, m, d) = ymd_from_day(day)
            utc1 = tai1 - delta_t_from_ymd(y, m, d+sec/86400.) - _LEAPSECS_1972_to_2000
            if np.all(y == y_prev) and np.all(m == m_prev):
                utc[mask] = utc1
                break
            day, sec = day_sec_from_utc(utc1)
            y_prev = y
            m_prev = m

    return utc


def day_sec_from_tai(tai):
    """Convert time in seconds TAI to day number and elapsed seconds into that day.

    Input:
        tai         time in seconds TAI, as a scalar, array, or array-like.

    Return:         (day, sec)
        day         integer UTC day number, starting from January 1, 2000, as a scalar or
                    array.
        sec         elapsed seconds into that day, allowing for leap seconds, as a scalar
                    or array.
    """

    return day_sec_from_utc(utc_from_tai(tai))


def tai_from_day_sec(day, sec=0):
    """Convert day number and elapsed seconds to TAI time.

    Input:
        day         integer UTC day number, starting from January 1, 2000. Can be a
                    scalar, array, or array-like.
        sec         optional elapsed seconds into that day, allowing for leap seconds. Can
                    be a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array.
    """

    return tai_from_utc(utc_from_day_sec(day, sec))


def tai_from_day(day, sec=0):
    """Convert day number to TAI seconds.

    This is an alternative name for tai_from_day_sec().

    Input:
        day         integer UTC day number, starting from January 1, 2000. Can be a
                    scalar, array, or array-like.
        sec         optional elapsed seconds into that day, allowing for leap seconds. Can
                    be a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array.
    """

    return tai_from_utc(utc_from_day_sec(day, sec=sec))

##########################################################################################
# TDB conversions
#
# Extracted from naif0009.tls...
#
# [4]       ET - TAI  =  DELTA_T_A  + K sin E
#
# where DELTA_T_A and K are constant, and E is the eccentric anomaly of the
# heliocentric orbit of the Earth-Moon barycenter. Equation [4], which ignores
# small-period fluctuations, is accurate to about 0.000030 seconds.
#
# The eccentric anomaly E is given by
#
# [5]       E = M + EB sin M
#
# where M is the mean anomaly, which in turn is given by
#
# [6]       M = M  +  M t
#                0     1
#
# where t is the number of ephemeris seconds past J2000.
#
# In the end, subtract 12 hours as J2000 starts at noon on 1/1/2000, not midnight.
##########################################################################################

def tdb_from_tai(tai, *, iters=2):
    """Convert time in seconds TAI to TDB.

    Input:
        tai         time in seconds TAI as a scalar, array, or array-like.
        iters       number of iterations to achieve desired precision. A value of 2
                    provides complete floating-point convergence.

    Return:         time in seconds TDB, as a scalar or array.
    """

    # Solve:
    #   tdb = tai + DELTA_T_A + DELTET_K sin(E) = tt + DELTET_K sin(E)
    #   E = M + DELTET_EB sin(M)
    #   M = DELTET_M0 + DELTET_M1 * tdb

    tt = _float(tai) + _TT_MINUS_TAI

    tdb = tt
    for iter in range(iters):
        m = leap_seconds._DELTET_M0 + leap_seconds._DELTET_M1 * tdb
        e = m + leap_seconds._DELTET_EB * np.sin(m)
        tdb = tt + leap_seconds._DELTET_K * np.sin(e)

    return tdb


def tai_from_tdb(tdb):
    """Convert time in seconds TDB to TAI.

    Input:
        tdb         time in seconds TDB as a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array.
    """

    # M = DELTET_M0 + DELTET_M1 * tdb
    # E = M + DELTET_EB sin(M)
    # tt = tdb - DELTET_K sin(E)
    # tai = tdb - DELTA_T_A - DELTET_K sin(E)

    tdb = _float(tdb)
    m = leap_seconds._DELTET_M0 + leap_seconds._DELTET_M1 * tdb
    e = m + leap_seconds._DELTET_EB * np.sin(m)
    tt = tdb - leap_seconds._DELTET_K * np.sin(e)
    tai = tt - _TT_MINUS_TAI
    return tai

########################################
# TAI-TT conversions
########################################

def tt_from_tai(tai):
    """Convert time in seconds TAI to TT.

    Input:
        tai         time in seconds TAI as a scalar, array, or array-like.

    Return:         time in seconds TT, as a scalar or array.
    """

    return _float(tai) + _TT_MINUS_TAI


def tai_from_tt(tt):
    """Convert time in seconds TT to TAI.

    Input:
        tt          time in seconds TT as a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array.
    """

    return _float(tt) - _TT_MINUS_TAI


def tdt_from_tai(tai):
    """DEPRECATED function name; use tt_from_tai.

    Input:
        tai         time in seconds TAI as a scalar, array, or array-like.

    Return:         time in seconds TT, as a scalar or array.
    """

    return _float(tai) + _TT_MINUS_TAI


def tai_from_tdt(tt):
    """"DEPRECATED function name; use tai_from_tt.

    Input:
        tt          time in seconds TT as a scalar, array, or array-like.

    Return:         time in seconds TAI, as a scalar or array.
    """

    return _float(tt) - _TT_MINUS_TAI

##########################################################################################
# General conversions between UTC, TAI, TDB, and TT
##########################################################################################

_TIME_CONVERSION_FUNCS = {
    ('TAI', 'TDB'): tdb_from_tai,
    ('TAI', 'TDT'): tt_from_tai,
    ('TAI', 'TT' ): tt_from_tai,
    ('TAI', 'UTC'): utc_from_tai,
    ('TDB', 'TAI'): tai_from_tdb,
    ('TDT', 'TAI'): tai_from_tt,
    ('TT' , 'TAI'): tai_from_tt,
    ('UTC', 'TAI'): tai_from_utc,
}


def time_from_time(time, timesys, newsys='TAI'):
    """Convert a time from one time system to another.

    Input:
        time        time in seconds as a scalar, array, or array-like.
        timesys     name of the current time system, "UTC", "TAI", "TDB", or "TT".
        newsys      name of the desired time system, "UTC", "TAI", "TDB", or "TT".

    Return:         time in the specified time system, as a scalar or array.
    """

    if timesys == newsys:
        return _number(time)

    key = (timesys, newsys)
    if key in _TIME_CONVERSION_FUNCS:
        return _TIME_CONVERSION_FUNCS[key](time)

    tai = _TIME_CONVERSION_FUNCS[(timesys, 'TAI')](time)
    return _TIME_CONVERSION_FUNCS[('TAI', newsys)](tai)


def day_sec_from_time(time, timesys='TAI', *, leapsecs=True):
    """Convert a time in any time system, to UTC day number and seconds.

    Input:
        time        time in seconds as, a scalar, array, or array-like.
        timesys     name of the current time system, one of "UTC", "TAI", "TDB", or "TT".
        leapsecs    if True, UTC day and second values are returned. Otherwise, the day
                    and seconds are calculated without regard to leap seconds and without
                    any time system conversion. This can be useful for situations where a
                    date is referred to as, for example, an "ephemeris date" rather than
                    as a calendar date.

    Return:         (day, sec)
        day         integer day number, starting from January 1, 2000, as a scalar or
                    array.
        sec         elapsed seconds into that day, as a scalar or array.
    """

    if not leapsecs:
        # Determine whether the zero-value of the time system is midnight or noon on
        # January 1, 2000.
        if _TAI_MIDNIGHT_ORIGIN and timesys in ('TAI', 'UTC'):
            time = _number(time)
        else:
            time = _number(time) + 43200

        day = _int(time // 86400.)
        sec = time - day * 86400
        return (day, sec)

    tai = time_from_time(time, timesys, 'TAI')
    return day_sec_from_tai(tai)


def time_from_day_sec(day, sec, timesys='TAI', *, leapsecs=True):
    """Convert UTC day number and elapsed seconds to time in seconds in the specified time
    system.

    Input:
        day         integer UTC day number, starting from January 1, 2000. Can be a
                    scalar, array, or array-like.
        sec         elapsed seconds into that day, allowing for leap seconds. Can be a
                    scalar, array, or array-like.
        timesys     name of the desired time system, one of "UTC", "TAI", "TDB", or "TT".
        leapsecs    if True, the day and sec values are interpreted as UTC values.
                    Otherwise, the day and seconds are converted to time without regard to
                    leap seconds, and no time system conversion is performed. This can be
                    useful for situations where a date is referred to as, for example, an
                    "ephemeris date" rather than as a calendar date.

    Return:         time in seconds in the specified time system, as a scalar or array.
    """

    if not leapsecs:
        # Determine whether the zero-value of the time system is midnight or noon on
        # January 1, 2000.
        if _TAI_MIDNIGHT_ORIGIN and timesys in ('TAI', 'UTC'):
            time_zero = 0
        else:
            time_zero = 43200

        return _number(day) * 86400 + _number(sec) - time_zero

    tai = tai_from_day_sec(day, sec)
    return time_from_time(tai, 'TAI', timesys)

##########################################################################################
