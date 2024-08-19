##########################################################################################
# julian/iso_parsers.py
##########################################################################################
"""Functions to interpret date/time strings in ISO-standard formats
"""
##########################################################################################

import numpy as np
from julian.calendar       import day_from_ymd, day_from_yd
from julian.leap_seconds   import seconds_on_day
from julian.time_of_day    import sec_from_hms
from julian.utc_tai_tdb_tt import tai_from_day_sec, tdb_from_tai, time_from_time
from julian._exceptions    import JulianParseException, JulianValidateFailure


def _count_white(string):
    """(number of leading blanks, number of trailing blanks)"""

    lstring = len(string)
    if not lstring:
        return (0, 0)   # pragma: no cover

    # Count the leading blanks
    for l0 in range(lstring):   # pragma: no branch
        if string[l0] != ' ':
            break

    # Count the trailing blanks
    for l1 in range(lstring):   # pragma: no branch
        if string[~l1] != ' ':          # "~l1" means counting from the end!
            break

    return (l0, l1)

# key = (stripped_length, dash_count); value = (y1, m0, d0, dlen, dash_locs)
_ISO_DATE_FORMAT_INFO = {
    (10,2): (4, 5, 8, 2, (4,7)),        # yyyy-mm-dd
    ( 8,1): (4, 0, 5, 3, (4,) ),        # yyyy-ddd
    ( 8,2): (2, 3, 6, 2, (2,5)),        # yy-mm-dd
    ( 6,1): (2, 0, 3, 3, (2,) ),        # yy-ddd
    ( 8,0): (4, 4, 6, 2, ()   ),        # yyyymmdd
    ( 7,0): (4, 0, 4, 3, ()   ),        # yyyyddd
    ( 6,0): (2, 2, 4, 2, ()   ),        # yymmdd
    ( 5,0): (2, 0, 2, 3, ()   ),        # yyddd
}


def day_from_iso(strings, *, validate=True, syntax=False, strip=False, proleptic=False):
    """Day number based on a parsing of a date string in the ISO 8601:1988 format.

    Recognized calendar date formats are "yyyy-mm-dd", "yyyymmdd", "yy-mm-dd", and
    "yymmdd". Supported ordinal date formats are "yyyy-ddd", "yyyyddd", "yy-ddd", and
    "yyddd". A fractional day following a decimal point is also permitted.

    This parser is much faster than the more general date parsing routines. It can also
    process lists or arrays of date strings of arbitrary shape, provided that every
    element uses the exact same format.

    Because it can handle arrays of bytestrings, it is very efficient at processing raw
    data extracted from a column of an ASCII table.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day values more carefully; raise
                    JulianValidateFailure (a ValueError subclass) on error.
        syntax      True to check the string values more closely for conformance to the
                    ISO standard; raise JulianParseException (a ValueError subclass) on
                    error.
        strip       True to skip over leading and trailing blanks.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    # Convert to bytestring if necessary, replace Unicode
    strings = np.array(strings).astype('S')

    first_index = len(strings.shape) * (0,)
    first = strings[first_index].decode('latin8')
    lfirst = len(first)

    # Count characters to strip
    w2 = strings.itemsize - lfirst              # w2 = 0 or 1 trailing null

    # w0 = number of blanks before
    # w1 = number of blanks after
    if strip:
        (w0, w1) = _count_white(first)
    else:
        (w0, w1) = (0, 0)
        test = first.replace('-', '').replace('.','')
        if not test.isdecimal():
            raise JulianParseException(f'unrecognized ISO date format: "{first}"')

    # Check for a dot
    lstripped = lfirst - w0 - w1                # length without padding
    kdot = max(0, first.find('.'))              # 0 means no dot
    kend = w0 + lstripped                       # index of the first char after the date
    kints = kdot if kdot else kend              # index of first char after all integers

    # Identify the format
    ndashes = len(str(first).split('-')) - 1
    try:
        (y1, m0, d0, dlen, dashes) = _ISO_DATE_FORMAT_INFO[(kints - w0, ndashes)]
    except KeyError:
        raise JulianParseException(f'unrecognized ISO date format: "{first}"')

    # Construct the dtype dictionary
    dtype_dict = {}
    dtype_dict['y'] = (f'|S{y1}', w0)
    dtype_dict['d'] = (f'|S{dlen}', w0 + d0)    # d is just the integer part
    if m0:
        dtype_dict['m'] = ('|S2', w0 + m0)

    if w0:
        dtype_dict['white0'] = (f'|S{w0}', 0)
    for i, dash in enumerate(dashes):
        dtype_dict[f'dash{i}'] = ('|S1', w0 + dash)
    if kdot:
        dtype_dict['dot'] = ('|S1', kdot)
        flen = kend - kdot - 1
        if flen:
            dtype_dict['f'] = (f'|S{flen}', kdot + 1)
    if w1:
        dtype_dict['white1'] = (f'|S{w1}', kend)
    if w2:
        dtype_dict['nulls'] = ('|S1', lfirst)

    if syntax:
        dtype_dict['data'] = (f'|S{kend-w0}', w0)

    # Extract year, month, day, and fraction; JulianParseException on failure
    strings = strings.view(np.dtype(dtype_dict))
    try:
        y = strings['y'].astype('int')
        d = strings['d'].astype('int')
        m = strings['m'].astype('int') if 'm' in dtype_dict else 0
        f = strings['f'].astype('int') if 'f' in dtype_dict else 0
    except ValueError as e:
        raise JulianParseException(str(e))

    # Validate syntax if necessary
    if syntax:
        if 'dash0' in dtype_dict and np.any(strings['dash0'] != b'-'):
            raise JulianParseException('inconsistent dashes in ISO date')
        if 'dash1' in dtype_dict and np.any(strings['dash1'] != b'-'):
            raise JulianParseException('inconsistent dashes in ISO date')
        if 'white0' in dtype_dict and np.any(strings['white0'] != w0 * b' '):
            raise JulianParseException('inconsistent white space in ISO date')
        if 'white1' in dtype_dict and np.any(strings['white1'] != w1 * b' '):
            raise JulianParseException('inconsistent white space in ISO date')
        if 'nulls' in dtype_dict and np.any(strings['nulls'] != b'\0'):
            raise JulianParseException('inconsistent null termination in ISO date')

        data = bytearray(strings['data'])
        if b' ' in data:
            raise JulianParseException('invalid blank character in ISO date')

        for key in ('y', 'd', 'm', 'f'):
            if key in dtype_dict:
                if b'-' in bytearray(strings[key]):
                    raise JulianParseException('invalid negative value in ISO date')

    # Convert to day
    if m0:
        day = day_from_ymd(y, m, d, validate=validate, proleptic=proleptic)
    else:
        day = day_from_yd(y, d, validate=validate, proleptic=proleptic)

    # Add fraction if needed
    if kdot:
        day = day + f/10.**(flen)

    return day

########################################

def sec_from_iso(strings, *, validate=True, leapsecs=True, strip=False, syntax=False):
    """Accumulated number of seconds into a day, based on a parsing of a time string in
    ISO 8601:1988 "extended" format (but using a decimal point for fractional seconds
    rather than a comma).

    The format required is "hh:mm:ss[.s...][Z]". This parser is much faster than the more
    general time parsing routines. It can also process lists or arrays of date strings of
    arbitrary shape, provided that every element uses the exact same format.

    Because it can handle arrays of bytestrings, it is very efficient at processing raw
    data extracted from a column of an ASCII table.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day syntax and values more carefully.
        syntax      True to check the string values more closely for conformance to the
                    ISO standard.
        strip       True to skip over leading and trailing blanks.
        leapsecs    True to tolerate leap second values during validation.

    This avoids the very slow julian_isoparser routines and is very fast. It also works
    for lists or arrays of arbitrary shape, provided every item uses the same format.
    """

    # Convert to bytestring if necessary, replace Unicode
    strings = np.array(strings).astype('S')

    first_index = len(strings.shape) * (0,)
    first = strings[first_index].decode('latin8')
    lfirst = len(first)

    # Count characters to strip
    w2 = strings.itemsize - lfirst              # w2 = 0 or 1 trailing null

    # w0 = number of blanks before
    # w1 = number of blanks after
    if strip:
        (w0, w1) = _count_white(first)
    else:
        (w0, w1) = (0, 0)
        test = first.replace(':', '').replace('.','').rstrip('Z')
        if not test.isdecimal():
            raise JulianParseException(f'unrecognized ISO time format: "{first}"')

    # Check for "Z"
    lstripped = lfirst - w0 - w1
    wz = int(first[w0 + lstripped - 1] == 'Z')  # wz = 0 or 1
    lstripped -= wz                             # width of time string without extras
    kend = w0 + lstripped                       # index of the first char after the time

    # Locate colons and dots
    first_array = np.array(list(first))
    kcolons = np.where(first_array == ':')[0]
    if kcolons.size > 2:
        raise JulianParseException('unrecognized ISO time format; too many colons: '
                                   f'"{first}"')

    kdots = np.where(first_array == '.')[0]
    if kdots.size > 1:
        raise JulianParseException('unrecognized ISO time format; too many decimals: '
                                   f'"{first}"')
        kdot = 0
    elif kdots.size == 1:
        kdot = kdots[0]
    else:
        kdot = 0

    kints = kdot if kdot else kend              # index of first char after all integers

    # Identify the h, m, s, and fraction field locations and widths
    if kcolons.size:
        kcolons = [w0-1] + list(kcolons)        # colon locations plus fake one in front
        khms = np.array(kcolons) + 1            # start locations of fields
        khms1 = list(kcolons[1:]) + [kints]     # end locations of all integer fields
        widths = khms1 - khms                   # widths of fields
        if np.any(widths != 2):
            raise JulianParseException(f'invalid field width in ISO time: "{first}"')
    else:
        width = kints - w0
        fields = width // 2
        if fields > 3 or width != fields * 2:
            raise JulianParseException('invalid text width in ISO time format: '
                                       f'"{first}"')
        khms = w0 + 2 * np.arange(fields)       # start locations of fields
        widths = fields * [2]

    # Construct the dtype dictionary
    dtype_dict = {}
    for i, w in enumerate(widths):
        key = 'hms'[i]
        dtype_dict[key] = (f'|S{w}', khms[i])

    if w0:
        dtype_dict['white0'] = (f'|S{w0}', 0)
    for i, kcolon in enumerate(kcolons[1:]):    # skip fake colon in front
        dtype_dict[f'colon{i}'] = ('|S1', kcolon)
    if kdot:
        dtype_dict['dot'] = ('|S1', kdot)
        flen = kend - kdot - 1
        if flen:
            dtype_dict['f'] = (f'|S{flen}', kdot + 1)
    if wz:
        dtype_dict['z'] = ('|S1', kend)
    if w1:
        dtype_dict['white1'] = (f'|S{w1}', kend + wz)
    if w2:
        dtype_dict['nulls'] = ('|S1', lfirst)

    if syntax:
        dtype_dict['data'] = (f'|S{kend-w0}', w0)

    # Extract hours, minutes, seconds; JulianParseException on failure
    strings = strings.view(np.dtype(dtype_dict))
    try:
        h = strings['h'].astype('int')
        m = strings['m'].astype('int') if 'm' in dtype_dict else 0
        s = strings['s'].astype('int') if 's' in dtype_dict else 0
    except ValueError as e:
        raise JulianParseException(str(e))

    if kdot:
        if 'f' in dtype_dict:
            f = strings['f'].astype('int') / 10.**flen
        else:
            f = 0.

        if 's' in dtype_dict:
            s = s + f
        elif 'm' in dtype_dict:
            m = m + f
        else:
            h = h + f

    # Validate if necessary
    if syntax:
        if 'white0' in dtype_dict and np.any(strings['white0'] != w0 * b' '):
            raise JulianParseException('inconsistent white space in ISO time')
        if 'colon0' in dtype_dict and np.any(strings['colon0'] != b':'):
            raise JulianParseException('inconsistent colons in ISO time')
        if 'colon1' in dtype_dict and np.any(strings['colon1'] != b':'):
            raise JulianParseException('inconsistent colons in ISO time')
        if 'dot' in dtype_dict and np.any(strings['dot'] != b'.'):
            raise JulianParseException('inconsistent decimal points in ISO time')
        if 'z' in dtype_dict and np.any(strings['z'] != b'Z'):
            raise JulianParseException('inconsistent "Z" usage in ISO time')
        if 'white1' in dtype_dict and np.any(strings['white1'] != w1 * b' '):
            raise JulianParseException('inconsistent white space in ISO time')
        if 'nulls' in dtype_dict and np.any(strings['nulls'] != b'\0'):
            raise JulianParseException('inconsistent null termination in ISO time')

        data = bytearray(strings['data'])
        if b' ' in data or b'-' in data:
            raise JulianParseException('invalid blank character in ISO time')

    return sec_from_hms(h, m, s, validate=validate, leapsecs=leapsecs)

########################################

def day_sec_from_iso(strings, *, validate=True, syntax=False, strip=False,
                     proleptic=False):
    """Day and second based on a parsing of the string in ISO date-time format.

    This function parses date-time strings in the fixed ISO format, using "yyyy-mm-dd"
    or "yyyy-ddd" for the date, a single space or "T", and a time as "hh:mm:ss[.s...][Z]".
    It is much faster than the more general date parsing routines. It can also process
    lists or arrays of date strings of arbitrary shape, provided that every element uses
    the exact same format.

    Because it can handle arrays of bytestrings, it is very efficient at processing raw
    data extracted from a column of an ASCII table.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day syntax and values more carefully.
        strip       True to skip over leading and trailing blanks.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    # Convert to an array of strings, replace Unicode
    strings = np.array(strings).astype('S')

    first_index = len(strings.shape) * (0,)
    first = strings[first_index].decode('latin8')
    lfirst = len(first)

    # Check for a T or blank separator
    csep = 'T'
    isep = first.find(csep)
    if isep == -1:
        w0, w1 = _count_white(first)
        csep = ' '
        isep = first.find(csep, w0)
        if isep == lfirst - w1:
            isep = -1

    # If no separator is found, it is just a date
    if isep == -1:
        return (day_from_iso(strings, validate=validate, strip=strip), 0)

    # Otherwise, parse the date and time separately
    dtype_dict = {'date': ('|S' + str(isep), 0),
                  'time': ('|S' + str(lfirst - isep - 1), isep + 1),
                  'sep' : ('|S1', isep)}

    strings = strings.view(np.dtype(dtype_dict))
    day = day_from_iso(strings['date'], validate=validate, syntax=syntax, strip=strip,
                                        proleptic=proleptic)
    sec = sec_from_iso(strings['time'], validate=validate, syntax=syntax, strip=strip,
                                        leapsecs=True)

    if syntax:
        if np.any(strings['sep'] != csep.encode('latin8')):
            raise JulianParseException('invalid ISO date-time punctuation')

    if validate:
        if np.any(sec >= seconds_on_day(day)):
            raise JulianValidateFailure('seconds value is outside allowed range')

    return (day, sec)

########################################

def tai_from_iso(strings, *, validate=True, strip=False, proleptic=False):
    """TAI time given an ISO date or date-time string.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day syntax and values more carefully.
        strip       True to skip over leading and trailing blanks.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    (day, sec) = day_sec_from_iso(strings, validate=validate, strip=strip,
                                  proleptic=proleptic)
    return tai_from_day_sec(day, sec)


def tdb_from_iso(strings, *, validate=True, strip=False, proleptic=False):
    """TDB time given an ISO date or date-time string.

    This is a shortcut for time_from_iso() with timesys='TDB'.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day syntax and values more carefully.
        strip       True to skip over leading and trailing blanks.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    (day, sec) = day_sec_from_iso(strings, validate=validate, strip=strip,
                                  proleptic=proleptic)
    return tdb_from_tai(tai_from_day_sec(day, sec))


def time_from_iso(strings, timesys='TAI', *, validate=True, strip=False, proleptic=False):
    """Time in a specified time system given an ISO date or date-time string.

    Input:
        strings     One or more strings or bytestrings to interpret.
        validate    True to check the year/month/day syntax and values more carefully.
        strip       True to skip over leading and trailing blanks.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
    """

    tai = tai_from_iso(strings, validate=validate, strip=strip, proleptic=proleptic)
    return time_from_time(tai, 'TAI', newsys=timesys)

##########################################################################################
