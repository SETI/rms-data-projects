##########################################################################################
# julian/time_of_day.py
##########################################################################################
"""Functions to convert to/from hours, minutes, and seconds
"""
##########################################################################################

import numpy as np
from julian._exceptions import JulianValidateFailure
from julian._utils      import _int, _number


def hms_from_sec(sec):
    """Hour, minute and second from seconds into day.

    Supports scalar or array arguments.

    Input must be between 0 and 86410, where numbers above 86400 are treated as leap
    seconds.

    Data type is preserved.
    """

    sec = _number(sec)

    # Test for valid range
    if np.any(sec < 0):
        raise JulianValidateFailure('seconds < 0')
    if np.any(sec >= 86410):
        raise JulianValidateFailure('seconds >= 86410')

    h = np.minimum(_int(sec//3600), 23)
    t = sec - 3600 * h

    m = np.minimum(_int(t//60), 59)
    t -= 60 * m

    return (h, m, t)


def sec_from_hms(h, m, s, validate=False, leapsecs=True):
    """Seconds into day from hour, minute and second.

    Supports scalar or array arguments.

    If all input values are integers, the returned value is also an integer; otherwise,
    the returned value is floating-point.

    Input:
        h, m, s     Hour, minute, and second values.
        validate    True to check the hour/minute/second and values more carefully;
                    raise JulianValidateFailure (a ValueError subclass) on error.
        leapsecs    True to tolerate leap second values during validation.
    """

    h = _number(h)
    m = _number(m)
    s = _number(s)

    if validate:
        if np.any(h >= 24):
            raise JulianValidateFailure('hour >= 24')
        if np.any(h < 0):
            raise JulianValidateFailure('hour < 0')
        if np.any(m >= 60):
            raise JulianValidateFailure('minute > 60')
        if np.any(m < 0):
            raise JulianValidateFailure('minute < 0')
        if np.any(s < 0):
            raise JulianValidateFailure('seconds < 0')
        if leapsecs:
            if np.any((s >= 60) & (h != 23) & (m != 59)):
                raise JulianValidateFailure('seconds >= 60')
            if np.any(s >= 70):
                raise JulianValidateFailure('seconds >= 70')
        else:
            if np.any(s >= 60):
                raise JulianValidateFailure('seconds >= 60')

    return 3600 * h + 60 * m + s

##########################################################################################
