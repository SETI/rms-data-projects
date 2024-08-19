##########################################################################################
# julian/formatters.py
##########################################################################################
"""Functions to format date/time strings in ISO-standard formats
"""
##########################################################################################

import numpy as np
from julian.calendar       import ymd_from_day, yd_from_day
from julian.leap_seconds   import seconds_on_day
from julian.utc_tai_tdb_tt import day_sec_from_tai
from julian.time_of_day    import hms_from_sec
from julian._utils         import _float, _int, _is_float, _number

_DIGITS1 = np.array(['%d' % i for i in range(10)])
_BDIGITS1 = _DIGITS1.astype('S')

_DIGITS2 = np.array(['%02d' % i for i in range(100)])
_BDIGITS2 = _DIGITS2.astype('S')

_DIGITS3 = np.array(['%03d' % i for i in range(367)])
_BDIGITS3 = _DIGITS3.astype('S')

##########################################################################################
# Date formatting
##########################################################################################

def format_day(day, order='YMD', *, ydigits=4, dash='-', ddigits=None, proleptic=False,
               buffer=None, kind="U"):
    """Format a date or array of dates.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype.kind = "U") or bytes
    (dtype.kind = "S"). If the latter, you can provide a NumPy memmap as input and this
    function will write content directly into an ASCII table file.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        order       the order of the year, optional month, and day fields, one of "YMD",
                    "MDY", "DMY", "YD", or "DY".
        ydigits     number of year digits to include in year, 2 or 4; default 4.
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

    if order not in ('YMD', 'MDY', 'DMY', 'YD', 'DY'):
        raise ValueError('unrecognized date format order: ' + repr(order))

    if ydigits not in (2, 4):
        raise ValueError('ydigits must equal 2 or 4')

    has_dot = _is_float(day) and ddigits is not None and ddigits >= 0
    if has_dot:
        scale = 10**ddigits
        day = ((_float(day) * scale + 0.5)//1 + 0.1)/scale
                # +0.1 to ensure there is no rounding down after division by scale
        int_day = _int(day)
        frac = day - int_day
        day = int_day
    else:
        day = _int(day)
        frac = None

    shape = np.shape(day)

    # Interpret the buffer and kind
    if buffer is None:
        if kind not in ('U', 'S'):
            raise ValueError('invalid kind, must be "U" or "S"')
        su = '=U' if kind == 'U' else '|S'
    else:
        kind = buffer.dtype.kind
        su = buffer.dtype.byteorder + kind
        if kind not in ('U', 'S'):
            raise ValueError('invalid buffer; kind must be "U" or "S"')
        if shape:
            if shape[:-1] != buffer.shape[:-1]:
                raise ValueError('buffer shape does not match that of date array')
            if buffer.shape[-1] < shape[-1]:
                raise ValueError('buffer shape is too small for the date array')

    if kind == 'U':
        w = 4               # output itemsize
        null = ''           # content of an empty cell
        dot = '.'           # representation for a period
        dash_ = dash        # representation for the field separator
        vals1 = _DIGITS1    # representations of numbers 0-9
        vals2 = _DIGITS2    # representations of numbers 0-99
        vals3 = _DIGITS3    # representations of numbers 0-366
    else:
        w = 1
        null = b'\0'
        dot = b'.'
        dash_ = dash.encode('latin8')
        vals1 = _BDIGITS1
        vals2 = _BDIGITS2
        vals3 = _BDIGITS3

    # Translate the days; determine the string format and dtype
    fmt_list = []
    dtype_dict = {}
    lstring = 0
    ldash = len(dash)
    for field, c in enumerate(order):
        if field > 0 and ldash:
            fmt_list.append(dash.replace('{','{{').replace('}','}}'))
            dtype_dict['dash' + str(field)] = (su + str(ldash), lstring * w)
            lstring += ldash

        if c == 'Y':
            fmt_list.append('{y:0' + str(ydigits) + 'd}')

            if ydigits == 4:
                dtype_dict['y12'] = (su + '2', lstring * w)
                lstring += 2

            dtype_dict['y34'] = (su + '2', lstring * w)
            lstring += 2

        elif c == 'M':
            fmt_list.append('{m:02d}')
            dtype_dict['m'] = (su + '2', lstring * w)
            lstring += 2

        else:   # c == 'D'
            dlen = 3 if len(order) == 2 else 2
            fmt_list.append('{d:0' + str(dlen) + 'd}')
            dtype_dict['d'] = (su + str(dlen), lstring * w)
            lstring += dlen

            if has_dot:
                fmt_list.append('.')
                dtype_dict['dot'] = (su + '1', lstring * w)
                lstring += 1

                if ddigits > 0:
                    fmt_list.append('{f:0' + str(ddigits) + 'd}')
                    for i in range(ddigits):
                        dtype_dict['f' + str(i)] = (su + '1', lstring * w)
                        lstring += 1

    fmt = ''.join(fmt_list)

    # Convert to y,m,d
    if len(order) == 3:
        (y,m,d) = ymd_from_day(day, proleptic=proleptic)
    else:
        (y,d) = yd_from_day(day, proleptic=proleptic)
        m = 0   # will be ignored

    # Use string formatting for a scalar return without a buffer
    if not shape and buffer is None:
        if ydigits == 2:
            y = y % 100

        if has_dot and ddigits > 0:
            f = int((frac * 10.**ddigits) // 1)
        else:
            f = 0

        result = fmt.format(y=y, m=m, d=d, f=f)
        if kind == 'U':
            return result
        else:
            return result.encode('latin8')

    # Create a buffer if necessary; otherwise, check dimensions
    if buffer is None:
        buffer = np.empty(shape, dtype='=' + kind + str(lstring))
    else:
        if lstring * w > buffer.dtype.itemsize:
            raise ValueError('buffer itemsize is too small for the date format')
        if lstring * w < buffer.dtype.itemsize:
            extra = buffer.dtype.itemsize//w - lstring
            dtype_dict['extra'] = (su + str(extra), lstring * w)

    # Fill in the fields
    buffer.fill(null)
    view = buffer.view(np.dtype(dtype_dict))
    if shape:
        view = view[..., :shape[-1]]

    if 'y12' in dtype_dict:
        view['y12'] = vals2[y // 100]
    view['y34'] = vals2[y % 100]

    if len(order) == 3:
        view['m'] = vals2[m]
        view['d'] = vals2[d]
    else:
        view['d'] = vals3[d]

    if 'dash1' in dtype_dict:
        view['dash1'] = dash_
    if 'dash2' in dtype_dict:
        view['dash2'] = dash_

    if 'dot' in dtype_dict:
        view['dot'] = dot

    if frac is not None:
        for i in range(ddigits):
            frac *= 10
            f = (frac // 1).astype('int')
            frac -= f
            view['f' + str(i)] = vals1[f]

    return buffer

##########################################################################################
# Time of day formatting
##########################################################################################

def format_sec(sec, digits=None, *, colon=':', suffix='', buffer=None, kind='U'):
    """A time of day in seconds converted to "hh:mm:ss[.fff][Z]" or similar formats.

    This function supports scalar or array-like inputs. If the latter, an array of strings
    or ASCII bytes is returned.

    Note that the optional output buffer can be either strings (dtype.kind = "U") or bytes
    (dtype.kind = "S"). If the latter, you can provide a NumPy memmap as input and this
    function will write content directly into an ASCII table file.

    Input:
        sec         the number of seconds into a day, or an arbitrary array thereof;
                    each value should be >= 0 and < 86410.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        colon       character(s) to include between fields, if any. Default is ":". Use
                    "" for no separators; any other string can also be used in place of
                    the colons.
        suffix      "Z" to include the Zulu time zone indicator.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    # Convert secs to h,m,s
    sec = _number(sec)
    shape = np.shape(sec)
    (h,m,s) = hms_from_sec(sec)

    has_dot = digits is not None and digits >= 0
    if has_dot:
        scale = 10**digits
        sec = ((_float(sec) * scale + 0.5)//1 + 0.1)/scale
                # +0.1 to ensure there is no rounding down after division by scale
        int_sec = _int(sec)
        frac = sec - int_sec
        sec = int_sec
    else:
        s = _int(s)
        frac = None

    # Interpret the buffer and kind
    if buffer is None:
        if kind not in ('U', 'S'):
            raise ValueError('invalid kind, must be "U" or "S"')
        su = '=U' if kind == 'U' else '|S'
    else:
        kind = buffer.dtype.kind
        su = buffer.dtype.byteorder + kind
        if kind not in ('U', 'S'):
            raise ValueError('invalid buffer; kind must be "U" or "S"')
        if shape:
            if shape[:-1] != buffer.shape[:-1]:
                raise ValueError('buffer shape does not match that of time array')
            if buffer.shape[-1] < shape[-1]:
                raise ValueError('buffer shape is too small for the time array')

    if kind == 'U':
        w = 4               # output itemsize
        null = ''           # content of an empty cell
        dot = '.'           # representation of a period
        colon_ = colon      # representation for the field separator
        vals1 = _DIGITS1    # representations of numbers 0-9
        vals2 = _DIGITS2    # representations of numbers 0-99
    else:
        w = 1
        null = b'\0'
        dot = b'.'
        colon_ = colon.encode('latin8')
        vals1 = _BDIGITS1
        vals2 = _BDIGITS2

    # Determine the string format and dtype
    lcolon = len(colon)
    dtype_dict = {
        'h': (su + '2', 0),
        'm': (su + '2', (2 + lcolon) * w),
        's': (su + '2', (4 + 2 * lcolon) * w),
    }

    if lcolon:
        dtype_dict['colon1'] = (su + str(lcolon), 2 * w)
        dtype_dict['colon2'] = (su + str(lcolon), (4 + lcolon) * w)

    lstring = 6 + 2 * lcolon
    fmt = '%02d' + colon + '%02d' + colon + '%02d'

    if has_dot:
        if digits == 0:
            fmt += '.'
            dtype_dict['dot'] = (su + '1', lstring * w)
            lstring += 1
        else:
            fmt += '.%0' + str(digits) + 'd'
            dtype_dict['dot'] = (su + '1', lstring * w)
            lstring += 1
            for i in range(digits):
                dtype_dict['f' + str(i)] = (su + '1', lstring * w)
                lstring += 1

    lsuffix = len(suffix)
    if suffix:
        fmt += suffix
        dtype_dict['z'] = (su + str(lsuffix), lstring * w)
        lstring += lsuffix

    # 0-D return without a buffer is easy
    if not shape and buffer is None:
        if has_dot and digits > 0:
            f = int((frac * 10.**digits) // 1)

        if has_dot and digits > 0:
            result = fmt % (h, m, int(s), f)
        else:
            result = fmt % (h, m, int(s))

        if kind == 'U':
            return result
        else:
            return result.encode('latin8')

    # Create a buffer if necessary; otherwise, check dimensions
    if buffer is None:
        buffer = np.empty(shape, dtype='=' + kind + str(lstring))
    else:
        if lstring * w > buffer.dtype.itemsize:
            raise ValueError('buffer itemsize is too small for the ISO time format')
        if lstring * w < buffer.dtype.itemsize:
            extra = buffer.dtype.itemsize//w - lstring
            dtype_dict['extra'] = (su + str(extra), lstring * w)

    # Fill in the fields
    buffer.fill(null)
    view = buffer.view(np.dtype(dtype_dict))
    if shape:
        view = view[..., :shape[-1]]

    int_s = _int(s)
    view['h'] = vals2[h]
    view['m'] = vals2[m]
    view['s'] = vals2[int_s]
    if lcolon:
        view['colon1'] = colon_
        view['colon2'] = colon_

    if 'dot' in dtype_dict:
        view['dot'] = dot

    if 'z' in dtype_dict:
        view['z'] = suffix

    if frac is not None:
        for i in range(digits):
            frac *= 10
            f = (frac // 1).astype('int')
            frac -= f
            view['f' + str(i)] = vals1[f]

    return buffer

##########################################################################################
# Date/time formatting
##########################################################################################

def format_day_sec(day, sec, order='YMDT', *, ydigits=4, dash='-', sep='T', colon=':',
                   digits=None, suffix='', proleptic=False, buffer=None, kind='U'):
    """Format a date and time.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype "U") or bytes
    (dtype "S"). If the latter, you can define it as a NumPy memmap and write content
    directly into an ASCII table file.

    Input:
        day         integer or arbitrary array of integers defining day numbers relative
                    to January 1, 2000.
        order       the order of the year, optional month, day, and time fields. Can be
                    any of "YMD", "MDY", "DMY", "YD", or "DY". Add "T" at the beginning or
                    end to indicate whether times come before or after the date.
        ydigits     number of year digits to include in year, 2 or 4; default 4.
        dash        character(s) to include between fields, if any. Default is "-". Use ""
                    for no separators; any other string can also be used in place of
                    the dashes.
        sep         character(s) to appear between the date and the time.
        colon       character(s) to include between fields, if any. Default is ":". Use
                    "" for no separators; any other string can also be used in place of
                    the colons.
        digits      decimal digits to include in second values; use -1 or None to suppress
                    the decimal point.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    ymd_order = order.replace('T', '')
    if order[0] != 'T' and order[-1] != 'T':
        raise ValueError('"T" missing from order specification')

    day = _int(day)
    sec = _number(sec)
    day, sec = np.broadcast_arrays(day, sec)
    shape = np.shape(day)

    # Interpret the buffer and kind
    if buffer is None:
        if kind not in ('U', 'S'):
            raise ValueError('invalid kind, must be "U" or "S"')
        su = '=U' if kind == 'U' else '|S'
    else:
        kind = buffer.dtype.kind
        su = buffer.dtype.byteorder + kind
        if kind not in ('U', 'S'):
            raise ValueError('invalid buffer; kind must be "U" or "S"')
        if shape:
            if shape[:-1] != buffer.shape[:-1]:
                raise ValueError('buffer shape does not match that of date array')
            if buffer.shape[-1] < shape[-1]:
                raise ValueError('buffer shape is too small for the date array')

    if kind == 'U':
        w = 4               # output itemsize
        null = ''           # content of an empty cell
        sep_ = sep
    else:
        w = 1
        null = b'\0'
        sep_ = sep.encode('latin8')

    # Handle leap seconds and cases of seconds rounding up to the next day
    digits_ = 0 if digits is None else max(digits, 0)
    scale = 10 ** digits_
    sec = ((sec * scale + 0.5) // 1 + 0.1) / scale
            # +0.1 to ensure there is no rounding down after division by scale

    secs_on_day = seconds_on_day(day)
    crossovers = (sec >= secs_on_day)
    if shape:
        day = day.copy()
        sec = sec.copy()
        day[crossovers] += 1
        sec[crossovers] -= secs_on_day[crossovers]
    elif crossovers:
        day += 1
        sec -= secs_on_day

    ### DETERMINE WHICH DAYS HAVE LEAP SECONDS!

    # Determine the field widths by formatting the first value
    first_index = len(shape) * (0,)
    day0 = day[first_index]
    sec0 = sec[first_index]

    day_formatted = format_day(day0, ymd_order, ydigits=ydigits, dash=dash,
                                     proleptic=proleptic)
    sec_formatted = format_sec(sec0, colon=colon, digits=digits, suffix=suffix)

    if order[0] == 'T':     # if time is first
        result0 = sec_formatted + sep + day_formatted
    else:
        result0 = day_formatted + sep + sec_formatted

    # For a shapeless case with no buffer, we're basically done
    if shape == () and buffer is None:
        if kind == 'U':
            return result0
        else:
            return result0.encode('latin8')

    ltime = len(sec_formatted)
    ldate = len(day_formatted)
    lsep = len(sep)
    lstring = ltime + ldate + lsep

    # Construct the dtype
    dtype_dict = {}
    if order[0] == 'T':
        dtype_dict['time'] = (su + str(ltime), 0)
        if lsep:
            dtype_dict['sep'] = (su + str(lsep), ltime * w)
        dtype_dict['date'] = (su + str(ldate), (ltime + lsep) * w)
    else:
        dtype_dict['date'] = (su + str(ldate), 0)
        if lsep:
            dtype_dict['sep'] = (su + str(lsep), ldate * w)
        dtype_dict['time'] = (su + str(ltime), (ldate + lsep) * w)

    # Create a buffer if necessary; otherwise, check dimensions
    if buffer is None:
        buffer = np.empty(shape, dtype='=' + kind + str(lstring))
    else:
        if lstring * w > buffer.dtype.itemsize:
            raise ValueError('buffer itemsize is too small for the date/time format')
        if lstring * w < buffer.dtype.itemsize:
            extra = buffer.dtype.itemsize//w - lstring
            dtype_dict['extra'] = (su + str(extra), lstring * w)

    # Fill in the date, time, and separator
    buffer.fill(null)
    view = buffer.view(np.dtype(dtype_dict))
    if shape:
        view = view[..., :shape[-1]]
    if lsep:
        view['sep'] = sep_

    _ = format_day(day, ymd_order, ydigits=ydigits, dash=dash, proleptic=proleptic,
                   buffer=view['date'])
    _ = format_sec(sec, colon=colon, digits=digits, suffix=suffix, buffer=view['time'])

    return buffer

##########################################################################################
# Date/time formatting using TAI
##########################################################################################

def format_tai(tai, order='YMDT', *, ydigits=4, dash='-', sep='T', colon=':', digits=None,
               suffix='', proleptic=False, buffer=None, kind='U'):
    """Format a date and time given a time in seconds TAI.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype "U") or bytes
    (dtype "S"). If the latter, you can define it as a NumPy memmap and write content
    directly into an ASCII table file.

    Input:
        tai         time value in seconds TAI or an array of time values.
        order       the order of the year, optional month, day, and time fields. Can be
                    any of "YMD", "MDY", "DMY", "YD", or "DY". Add "T" at the beginning or
                    end to indicate whether times come before or after the date.
        ydigits     number of year digits to include in year, 2 or 4; default 4.
        dash        character(s) to include between fields, if any. Default is "-". Use ""
                    for no separators; any other string can also be used in place of
                    the dashes.
        sep         character(s) to appear between the date and the time.
        colon       character(s) to include between fields, if any. Default is ":". Use
                    "" for no separators; any other string can also be used in place of
                    the colons.
        digits      decimal digits to include in second values; use -1 or None to suppress
                    the decimal point.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    (day, sec) = day_sec_from_tai(tai)
    return format_day_sec(day, sec, order=order, ydigits=ydigits, dash=dash, sep=sep,
                          colon=colon, digits=digits, suffix=suffix, proleptic=proleptic,
                          buffer=buffer, kind=kind)


def iso_from_tai(tai, ymd=True, digits=None, *, suffix='', proleptic=False,
                 buffer=None, kind='U'):
    """Date and time in ISO format given seconds TAI.

    This function supports scalar or array-like inputs. If array-like inputs are provided,
    an array of strings or ASCII byte strings is returned.

    Note that the optional output buffer can be either strings (dtype "U") or bytes
    (dtype "S"). If the latter, you can define it as a NumPy memmap and write content
    directly into an ASCII table file.

    Note that this function is a variant of format_day_sec() but with a reduced set of
    options.

    Input:
        tai         time value in seconds TAI or an array of time values.
        digits      the number of digits to include after the decimal point; use a
                    negative value or None for seconds to be rounded to integer.
        ymd         True for year-month-day format; False for year plus
                    day-of-year format.
        suffix      "Z" to include the Zulu time zone indicator.
        proleptic   True to interpret all dates according to the modern Gregorian
                    calendar, even those that occurred prior to the transition from the
                    Julian calendar. False to use the Julian calendar for earlier dates.
        buffer      an optional array of strings or byte strings into which to write the
                    results. Must have sufficient dimensions.
        kind        "U" to return strings, "S" to return bytes. Ignored if a buffer is
                    provided.
    """

    if ymd:
        return format_tai(tai, order='YMDT', sep='T', digits=digits, suffix=suffix,
                          proleptic=proleptic, buffer=buffer, kind=kind)
    else:
        return format_tai(tai, order='YDT', sep='T', digits=digits, suffix=suffix,
                          proleptic=proleptic, buffer=buffer, kind=kind)

##########################################################################################

