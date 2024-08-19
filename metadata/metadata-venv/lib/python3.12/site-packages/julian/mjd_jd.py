##########################################################################################
# julian/mjd_jd.py
##########################################################################################
"""Functions to convert to/from Julian Date and Modified Julian Date
"""
##########################################################################################

from julian                import utc_tai_tdb_tt
from julian.leap_seconds   import seconds_on_day
from julian.utc_tai_tdb_tt import day_sec_from_tai, day_sec_from_time, day_sec_from_utc, \
                                  tai_from_day_sec, time_from_day_sec, time_from_time, \
                                  utc_from_day_sec
from julian._utils         import _float, _int, _number

# JD and MJD definitions
_MJD_OF_JAN_1_2000 = 51544
_JD_OF_JAN_1_2000 = 2451544.5
_JD_MINUS_MJD = 2400000.5

##########################################################################################
# MJD/JD functions supporting integer days, UTC, and leap seconds.
##########################################################################################

def mjd_from_day(day):
    """Modified Julian Date for a given UTC day number.

    Input:
        day         UTC day number, starting from midnight on January 1, 2000 UTC, as
                    scalar, array, or array-like.

    Return          the Modified Julian Date, as a scalar or array. If the day input is
                    integral, integers are returned.
    """

    return _number(day) + _MJD_OF_JAN_1_2000


def day_from_mjd(mjd):
    """UTC day number for a given UTC Modified Julian Date.

    Input:
        mjd         MJD day number, as a scalar, array, or array-like.

    Return          the associated UTC day, numbered starting from midnight on January 1,
                    2000 UTC. If the mjd input is integral, integers are returned.
    """

    return _number(mjd) - _MJD_OF_JAN_1_2000


def mjd_from_day_sec(day, sec=0):
    """UTC Modified Julian Date for a given UTC day number and seconds.

    Input:
        day         integer UTC day number, starting from January 1, 2000. Can be a
                    scalar, array, or array-like.
        sec         elapsed seconds within that day, allowing for leap seconds. Can be a
                    scalar, array, or array-like.

    Return          the Modified Julian Date, as a scalar or array.

    Note that the MJD time system has day-length "ticks", which means that it interacts in
    a peculiar way with leap seconds. When allowing for leap seconds, some days are longer
    than others. Nevertheless, this time system is defined such that the value of MJD
    always increases by one frome the end of one day to the end of the next. On days that
    contain leap seconds, the fractional rate must therefore be a bit slower.
    """

    day = _int(day)
    return day + _number(sec)/seconds_on_day(day) + _MJD_OF_JAN_1_2000


def day_sec_from_mjd(mjd):
    """UTC day number and seconds for a given UTC Modified Julian Date.

    Input:
        mjd         Julian day value, as a scalar, array, or array-like.

    Return:         (day, sec)
        day         integer UTC day number, starting from midnight on January 1, 2000, as
                    a scalar or array.
        sec         seconds within that day, allowing for leap seconds, as a scalar or
                    array. If mjd values are integral, integers are returned.

    Note that the MJD time system has day-length "ticks", which means that it interacts in
    a peculiar way with leap seconds. When allowing for leap seconds, some days are longer
    than others. Nevertheless, this time system is defined such that the value of MJD
    always increases by one frome the end of one day to the end of the next. On days that
    contain leap seconds, the fractional rate must therefore be a bit slower.
    """

    mjd = _number(mjd)
    int_mjd = _int(mjd)

    day = int_mjd - _MJD_OF_JAN_1_2000
    sec = seconds_on_day(day) * (mjd - int_mjd)
    return (day, sec)


def jd_from_day_sec(day, sec=0):
    """UTC Julian Date for a given UTC day number and seconds.

    Input:
        day         integer UTC day number, starting from January 1, 2000. Can be a
                    scalar, array, or array-like.
        sec         elapsed seconds within that day, allowing for leap seconds. Can be a
                    scalar, array, or array-like.

    Return          the Julian Date, as a scalar or array.

    Note that the JD time system has day-length "ticks", which means that it interacts in
    a peculiar way with leap seconds. When allowing for leap seconds, some days are longer
    than others. Nevertheless, this time system is defined such that the value of JD
    always increases by one frome the end of one day to the end of the next. On days that
    contain leap seconds, the fractional rate must therefore be a bit slower.
    """

    return mjd_from_day_sec(day, sec) + _JD_MINUS_MJD


def day_sec_from_jd(jd):
    """UTC day number and seconds for a given UTC Julian Date.

    Input:
        jd          Julian date, as a scalar, array, or array-like.

    Return:         (day, sec)
        day         integer UTC day number, starting from midnight on January 1, 2000, as
                    a scalar or array.
        sec         seconds within that day, allowing for leap seconds, as a scalar or
                    array. If mjd values are integral, integers are returned.

    Note that the JD time system has day-length "ticks", which means that it interacts in
    a peculiar way with leap seconds. When allowing for leap seconds, some days are longer
    than others. Nevertheless, this time system is defined such that the value of JD
    always increases by one frome the end of one day to the end of the next. On days that
    contain leap seconds, the fractional rate must therefore be a bit slower.
    """

    return day_sec_from_mjd(jd - _JD_MINUS_MJD)

##########################################################################################
# General versions supporting time conversions, selectively handling leap seconds
##########################################################################################

def mjd_from_time(time, timesys='TAI', mjdsys=None):
    """Modified Julian Date for a given time, allowing for time system conversions.

    Input:
        time        time in seconds within the specified time system.
        timesys     name of the current time system, one of "UTC", "TAI", "TDB", or "TT".
        mjdsys      time system for the MJD, one of "UTC", "TAI", "TDB", or "TT". Leap
                    seconds are included if mjdsys="UTC"; otherwise, they are ignored.
                    If not specified, mjdsys equals timesys.

    Return          the Modified Julian Date, as a scalar or array.
    """

    # Ignores leap seconds; provides backward compatibility
    if mjdsys is None:
        if timesys == 'UTC':
            mjdsys = 'UTC'
        else:
            if utc_tai_tdb_tt._TAI_MIDNIGHT_ORIGIN and timesys == 'TAI':
                origin = _MJD_OF_JAN_1_2000
            else:
                origin = _MJD_OF_JAN_1_2000 + 0.5

            return _float(time)/86400. + origin

    time = time_from_time(time, timesys=timesys, newsys=mjdsys)

    if mjdsys == 'UTC':
        return mjd_from_day_sec(*day_sec_from_utc(time))

    day, sec = day_sec_from_time(time, timesys=mjdsys, leapsecs=(mjdsys=='UTC'))
    return day + sec/86400. + _MJD_OF_JAN_1_2000


def time_from_mjd(mjd, timesys='TAI', mjdsys=None):
    """Time in the seconds for a specified MJD, allowing for time system conversions.

    Input:
        mjd         time in seconds within the specified time system.
        timesys     name of the desired time system, one of "UTC", "TAI", "TDB", or "TT".
        mjdsys      time system for the MJD, one of "UTC", "TAI", "TDB", or "TT". Leap
                    seconds are included in the "UTC" MJD time system; ignored otherwise.
                    If not specified, mjdsys equals timesys.

    Return          time in seconds in the specified time system, as a scalar or array.
    """

    # Ignores leap seconds; provides backward compatibility
    if mjdsys is None:
        if timesys == 'UTC':
            mjdsys = 'UTC'
        else:
            if utc_tai_tdb_tt._TAI_MIDNIGHT_ORIGIN and timesys == 'TAI':
                offset = _MJD_OF_JAN_1_2000
            else:
                offset = _MJD_OF_JAN_1_2000 + 0.5

            return (mjd - offset) * 86400.

    if mjdsys == 'UTC':
        time = utc_from_day_sec(*day_sec_from_mjd(mjd))
    else:
        day = _number(mjd) - _MJD_OF_JAN_1_2000
        time = time_from_day_sec(day, 0, timesys=mjdsys, leapsecs=(mjdsys=='UTC'))

    return time_from_time(time, timesys=mjdsys, newsys=timesys)


def jd_from_time(time, timesys='TAI', jdsys=None):
    """Julian Date for a given time, allowing for time system conversions.

    Input:
        time        time in seconds within the specified time system.
        timesys     name of the current time system, one of "UTC", "TAI", "TDB", or "TT".
        jdsys       time system for the JD, one of "UTC", "TAI", "TDB", or "TT". Leap
                    seconds are included if mjdsys="UTC"; otherwise, they are ignored. If
                    not specified, jdsys equals timesys.

    Return          the Julian Date, as a scalar or array.
    """

    return mjd_from_time(time, timesys=timesys, mjdsys=jdsys) + _JD_MINUS_MJD


def time_from_jd(jd, timesys='TAI', jdsys=None):
    """Time in the seconds for a specified JD, allowing for time system conversions.

    Input:
        jd          time in seconds within the specified time system.
        timesys     name of the desired time system, one of "UTC", "TAI", "TDB", or "TT".
        jdsys       time system for the JD, one of "UTC", "TAI", "TDB", or "TT". Leap
                    seconds are included in the "UTC" MJD time system; ignored otherwise.
                    If not specified, jdsys equals timesys.

    Return          time in seconds in the specified time system, as a scalar or array.
    """

    return time_from_mjd(jd - _JD_MINUS_MJD, mjdsys=jdsys, timesys=timesys)

# Shortcuts for TAI

def mjd_from_tai(tai):
    """Modified Julian Date from TAI seconds."""

    return mjd_from_day_sec(*day_sec_from_tai(tai))


def jd_from_tai(tai):
    """Julian Date fram TAI seconds."""

    return jd_from_day_sec(*day_sec_from_tai(tai))


def tai_from_mjd(mjd):
    """TAI seconds from Modified Julian Date."""

    return tai_from_day_sec(*day_sec_from_mjd(mjd))


def tai_from_jd(jd):
    """TAI seconds from Modified Julian Date."""

    return tai_from_day_sec(*day_sec_from_jd(jd))

##########################################################################################
