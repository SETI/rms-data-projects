##########################################################################################
# julian/leap_seconds.py
##########################################################################################
"""Functions for managing and tracking leap seconds and "rubber second" offsets.
"""
##########################################################################################

import numpy as np
import pathlib
import os
import re
import sys

from julian.calendar import day_from_ymd, days_in_year, ymd_from_day
from julian._deltat  import FuncDeltaT, LeapDeltaT, MergedDeltaT, SplineDeltaT
from julian._utils   import _int, _number

##########################################################################################
# LEAPS_DELTA_T and SPICE_DELTA_T: baseline models for leap seconds and TAI-UTC.
# Each call to insert_leap_second modifies these globals.
# They are always initialized at startup or by calling _initialize_leap_seconds().
##########################################################################################

_LEAPS_DELTA_T = None
_SPICE_DELTA_T = None

# At load time, this file looks for an environment variable SPICE_LSK_FILEPATH. If found,
# this file is used to initialize the module. Otherwise, the local copy of the latest
# LSK is read.
_LATEST_LSK_NAME = 'naif0012.tls'       # possibly overridden by _default_lsk_path()

# Global variables needed for TAI-UTC conversions, from a SPICE leap seconds kernel
_DELTET_DELTA_T_A = 0.
_DELTET_K  = 0.
_DELTET_EB = 0.
_DELTET_M0 = 0.
_DELTET_M1 = 0.
_DELTET_DELTA_AT = []


def _default_lsk_path():
    """The default LSK path as a Path object."""

    global _LATEST_LSK_NAME

    try:
        lsk_path = os.environ['SPICE_LSK_FILEPATH']

    # If the environment variable is not defined, identify the latest local copy
    except KeyError:
        julian_root_dir = pathlib.Path(sys.modules['julian'].__file__).parent
        julian_docs_dir = julian_root_dir / 'assets'
        lsk_paths = list(julian_docs_dir.glob('naif00*.tls'))
        lsk_paths.sort()
        lsk_path = lsk_paths[-1]
        _LATEST_LSK_NAME = lsk_path.name

    return lsk_path


def _leaps_from_lsk(lsk_path):
    """Return the list of leap seconds from the specified SPICE leap seconds kernel file,
    represented by a string or Path.
    """

    global _DELTET_DELTA_T_A, _DELTET_K, _DELTET_EB, _DELTET_M0, _DELTET_M1, \
           _DELTET_DELTA_AT

    _MONTHNO = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6, 'JUL':7, 'AUG':8,
                'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}

    # This procedure works correctly for naif0012.tls and all previous versions.
    # Unless something changes radically in the future, it should work for future
    # releases as well.

    def get_float(value):
        return float(value.lower().replace('d','e'))

    # Define a regex to match lines like:
    #   "DELTET/DELTA_T_A =   32.184"
    #   "DELTET/K         =    1.657D-3"
    #   "DELTET/EB        =    1.671D-2"
    #   "DELTET/M         = (  6.239996D0   1.99096871D-7 )"
    # DELTET/DELTA_AT     = ( 10,   @1972-JAN-1
    # The first capture is the name after the slash; the second is everything after "=".
    lsk_regex1 = re.compile(r' *DELTET/(\w+) *= *(.*)')

    # Define a regex to match lines like:
    #   "                   11,   @1972-JUL-1     "
    #   "                   12,   @1973-JAN-1     "
    #   "                   37,   @2017-JAN-1 )"
    # The match pattern captures (number of leap seconds, year, month, day)
    lsk_regex2 = re.compile(r' *(\d+), *@(\d\d\d\d)-([A-Z]{3})-(\d+) *\)? *')

    # Read the LSK
    deltet_dict = {}            # a dictionary name -> value from lsk_regex1
    deltet_delta_at = []        # a list of (leap seconds, year, month, day)
    with open(lsk_path, 'r', encoding='latin8') as f:
        for rec in f:           # pragma: no branch
            if rec.startswith('\\begindata'):
                break

        for rec in f:
            if match := lsk_regex1.match(rec):
                name = match.group(1)
                value = match.group(2).rstrip()
                deltet_dict[name] = value
            elif match := lsk_regex2.match(rec):    # groups are (secs, year, mon, day)
                value = match.groups(0)
                deltet_delta_at.append(value)

    # Extract the global values
    _DELTET_DELTA_T_A = get_float(deltet_dict['DELTA_T_A'])
    _DELTET_K         = get_float(deltet_dict['K'])
    _DELTET_EB        = get_float(deltet_dict['EB'])

    # Extract the two DELTET/M values
    parts = deltet_dict['M'].split()                # split by spaces; ignore parentheses
    _DELTET_M0 = get_float(parts[1])
    _DELTET_M1 = get_float(parts[2])

    # Put the first DELTET/DELTA_AT value back at the top of the list
    delta_at = deltet_dict['DELTA_AT'].strip()[1:]  # skip left parenthesis
    _DELTET_DELTA_AT = [lsk_regex2.match(delta_at).groups(0)] + deltet_delta_at

    # Convert the list of DELTET/DELTA_AT values
    leaps = []
    for (count, year, month, day) in _DELTET_DELTA_AT:
        if day != '1':
            raise ValueError('leap second day is not the first '    # pragma: no cover
                             f' of a month: {year}-{month:02d}-{day:02d}')

        leaps.append((int(year), _MONTHNO[month.upper()], int(count)))

    return leaps


def _initialize_leap_seconds(lsk_path=None):
    """Initialize the LEAPS and SPICE models for TAI-UT."""

    global _LEAPS_DELTA_T, _SPICE_DELTA_T

    lsk_path = lsk_path or _default_lsk_path()
    info = _leaps_from_lsk(lsk_path)

    _LEAPS_DELTA_T = LeapDeltaT(info)
    _SPICE_DELTA_T = LeapDeltaT(list(_LEAPS_DELTA_T.info), before=9)


# Initialize at startup
_initialize_leap_seconds()

##########################################################################################
# DELTA_T_1958_1972: UTC "rubber seconds" model, 1958-1972.
# It is initialized at startup or by calling _initialize_utc_1958_1972().
##########################################################################################

# Based on the International Earth Rotation Service (IERS)
# See https://www.ucolick.org/~sla/leapsecs/amsci.html
# Also https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab

_DELTA_T_1958_1972 = None

# Table from https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab
_TAI_MINUS_UTC_1958_1972_TEXT = """\
1961  Jan.  1 - 1961  Aug.  1     1.422 818 0s + (MJD - 37 300) x 0.001 296s
      Aug.  1 - 1962  Jan.  1     1.372 818 0s +        ""
1962  Jan.  1 - 1963  Nov.  1     1.845 858 0s + (MJD - 37 665) x 0.001 123 2s
1963  Nov.  1 - 1964  Jan.  1     1.945 858 0s +        ""
1964  Jan.  1 -       April 1     3.240 130 0s + (MJD - 38 761) x 0.001 296s
      April 1 -       Sept. 1     3.340 130 0s +        ""
      Sept. 1 - 1965  Jan.  1     3.440 130 0s +        ""
1965  Jan.  1 -       March 1     3.540 130 0s +        ""
      March 1 -       Jul.  1     3.640 130 0s +        ""
      Jul.  1 -       Sept. 1     3.740 130 0s +        ""
      Sept. 1 - 1966  Jan.  1     3.840 130 0s +        ""
1966  Jan.  1 - 1968  Feb.  1     4.313 170 0s + (MJD - 39 126) x 0.002 592s
1968  Feb.  1 - 1972  Jan.  1     4.213 170 0s +        ""
1972  Jan.  1 -       Jul.  1    10s
      Jul.  1 - 1973  Jan.  1    11s
...
"""

# (start_day, start_month, offset, dref, factor)
# Between each pair of dates, (TAI-UTC) = offset + (day - dref) * factor
_MJD_OF_JAN_1_2000 = 51544
_TAI_MINUS_UTC_1958_1972_INFO = [
    (1958,  1, 0.      , 0.       , 37300 - _MJD_OF_JAN_1_2000),
    (1961,  1, 1.422818, 0.001296 , 37300 - _MJD_OF_JAN_1_2000),
    (1961,  8, 1.372818, 0.001296 , 37300 - _MJD_OF_JAN_1_2000),
    (1962,  1, 1.845858, 0.0011232, 37665 - _MJD_OF_JAN_1_2000),
    (1963, 11, 1.945858, 0.0011232, 37665 - _MJD_OF_JAN_1_2000),
    (1964,  1, 3.240130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1964,  4, 3.340130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1964,  9, 3.440130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1965,  1, 3.540130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1965,  3, 3.640130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1965,  7, 3.740130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1965,  9, 3.840130, 0.001296 , 38761 - _MJD_OF_JAN_1_2000),
    (1966,  1, 4.313170, 0.002592 , 39126 - _MJD_OF_JAN_1_2000),
    (1968,  2, 4.213170, 0.002592 , 39126 - _MJD_OF_JAN_1_2000),
    (1972,  1, 10      , 0.       , 0                         ),
]


def _initialize_utc_1958_1972():
    """Initialize the TAI-UTC models 1958-1972."""

    global _DELTA_T_1958_1972

    _DELTA_T_1958_1972 = SplineDeltaT(_TAI_MINUS_UTC_1958_1972_INFO, last=1972)


# Initialize at startup
_initialize_utc_1958_1972()

##########################################################################################
# Functional model for -1999 to 3000.
# This is the model used for the Five Millennium Canon of Solar Eclipses: -1999 to +3000.
# See https://eclipse.gsfc.nasa.gov/SEpubs/5MCSE.html.
# The numerical details are here: https://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html.
# DeltaT object is DELTA_T_NEG1999_3000.
# It is initialized at startup or by calling _initialize_ut1_neg1999_3000().
##########################################################################################

def _delta_t_neg0500_0500(y):
    u = y / 100.
    return (10583.6 + u * (-1014.41 + u * (33.78311 + u * (-5.952053 + u * (-0.1798452
            + u * (0.022174192 + u * 0.0090316521))))))

def _delta_t_0500_1600(y):
    u = (y - 1000.) / 100.
    return (1574.2 + u * (-556.01 + u * (71.23472 + u * (0.319781 + u * (-0.8503463
            + u * (-0.005050998 + u * 0.0083572073))))))

def _delta_t_1600_1700(y):
    t = y - 1600
    return 120 + t * (-0.9808 + t * (-0.01532 + t/7129.))

def _delta_t_1700_1800(y):
    t = y - 1700
    return 8.83 + t * (0.1603 + t * (-0.0059285 + t * (0.00013336 - t/1174000.)))

def _delta_t_1800_1860(y):
    t = y - 1800
    return (13.72 + t * (-0.332447 + t * (0.0068612 + t * (0.0041116 + t * (-0.00037436
            + t * (0.0000121272 + t * (-0.0000001699 + t * 0.000000000875)))))))

def _delta_t_1860_1900(y):
    t = y - 1860
    return (7.62 + t * (0.5737 + t * (-0.251754 + t * (0.01680668 + t * (-0.0004473624
            + t/233174.)))))

def _delta_t_1900_1920(y):
    t = y - 1900
    return -2.79 + t * (1.494119 + t * (-0.0598939 + t * (0.0061966 + t * -0.000197)))

def _delta_t_1920_1941(y):
    t = y - 1920
    return 21.20 + t * (0.84493 + t * (-0.076100 + t * 0.0020936))

def _delta_t_1941_1961(y):
    t = y - 1950
    return 29.07 + t * (0.407 + t * (-1./233. + t/2547.))

def _delta_t_1961_1986(y):
    t = y - 1975
    return 45.45 + t * (1.067 + t * (-1./260. - t/718.))

def _delta_t_1986_2005(y):
    t = y - 2000
    return (63.86 + t * (0.3345 + t * (-0.060374 + t * (0.0017275 + t * (0.000651814
            + t * 0.00002373599)))))

def _delta_t_2005_2050(y):
    t = y - 2000
    return 62.92 + t * (0.32217 + 0.005589 * t)

def _delta_t_2050_2150(y):
    return -20 + 32 * ((y - 1820) / 100.)**2 - 0.5628 * (2150 - y)

def _delta_t_long_term(y):
    u = (y - 1820.) / 100.
    return -20 + 32 * u**2

# Set it all up for quick indexing of nonnegative years 0-2149
_DELTA_T_INDEX = np.empty(2150, dtype='int')
_DELTA_T_INDEX[    : 500] =  0
_DELTA_T_INDEX[ 500:1600] =  1
_DELTA_T_INDEX[1600:1700] =  2
_DELTA_T_INDEX[1700:1800] =  3
_DELTA_T_INDEX[1800:1860] =  4
_DELTA_T_INDEX[1860:1900] =  5
_DELTA_T_INDEX[1900:1920] =  6
_DELTA_T_INDEX[1920:1941] =  7
_DELTA_T_INDEX[1941:1961] =  8
_DELTA_T_INDEX[1961:1986] =  9
_DELTA_T_INDEX[1986:2005] = 10
_DELTA_T_INDEX[2005:2050] = 11
_DELTA_T_INDEX[2050:    ] = 12

_DELTA_T_FUNCTIONS = np.empty(13, dtype='object')
_DELTA_T_FUNCTIONS[ 0] = _delta_t_neg0500_0500
_DELTA_T_FUNCTIONS[ 1] = _delta_t_0500_1600
_DELTA_T_FUNCTIONS[ 2] = _delta_t_1600_1700
_DELTA_T_FUNCTIONS[ 3] = _delta_t_1700_1800
_DELTA_T_FUNCTIONS[ 4] = _delta_t_1800_1860
_DELTA_T_FUNCTIONS[ 5] = _delta_t_1860_1900
_DELTA_T_FUNCTIONS[ 6] = _delta_t_1900_1920
_DELTA_T_FUNCTIONS[ 7] = _delta_t_1920_1941
_DELTA_T_FUNCTIONS[ 8] = _delta_t_1941_1961
_DELTA_T_FUNCTIONS[ 9] = _delta_t_1961_1986
_DELTA_T_FUNCTIONS[10] = _delta_t_1986_2005
_DELTA_T_FUNCTIONS[11] = _delta_t_2005_2050
_DELTA_T_FUNCTIONS[12] = _delta_t_2050_2150


def _delta_t_neg1999_3000(y, m, d):

    y_int = _int(y)
    day = day_from_ymd(y_int, m, d)
    y = y_int + (day - day_from_ymd(y_int,1,1)) / days_in_year(y_int)

    # Determine values of TT - UT based on the defined functions
    if np.isscalar(y):
        if y < 0:
            if y < -500:
                tt_minus_ut = _delta_t_long_term(y)
            else:
                tt_minus_ut = _delta_t_neg0500_0500(y)
        elif y < 2150:
            tt_minus_ut = _DELTA_T_FUNCTIONS[_DELTA_T_INDEX[y_int]](y)
        else:
            tt_minus_ut = _delta_t_long_term(y)

    else:
        tt_minus_ut = np.empty(y.shape)
        below_or_above = False

        mask_below_0000 = y < 0
        if np.any(mask_below_0000):
            below_or_above = True
            y_below_0000 = y[mask_below_0000]
            tt_minus_ut_below_0000 = _delta_t_neg0500_0500(y_below_0000)
            mask = y_below_0000 < -500
            tt_minus_ut_below_0000[mask] = _delta_t_long_term(y_below_0000[mask])
            tt_minus_ut[mask_below_0000] = tt_minus_ut_below_0000

        mask_above_2150 = y >= 2150
        if np.any(mask_above_2150):
            below_or_above = True
            tt_minus_ut[mask_above_2150] = _delta_t_long_term(y[mask_above_2150])

        # Create indices, an array with the same shape as y, containing the function index
        # applicable to each value of y. The index is -1 for years < -500 or >= 2150.
        if below_or_above:
            indices = -np.ones(y.shape, dtype='int')
            mask = np.logical_not(mask_below_0000 | mask_above_2150)
            indices[mask] = _DELTA_T_INDEX[y_int[mask]]
        else:
            indices = _DELTA_T_INDEX[y_int]

        # Fill in values for each unique function index
        for indx in set(indices.ravel()):
            if indx < 0:
                continue
            mask = (indx == indices)
            tt_minus_ut[mask] = _DELTA_T_FUNCTIONS[indx](y[mask])

    # Apply the "Canon correction" and the offset to TAI - UT
    # see https://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html
    tai_minus_ut = tt_minus_ut - 0.000012932 * (y - 1955)**2 - 32.184
    return tai_minus_ut


_DELTA_T_NEG1999_3000 = None

def _initialize_ut1_neg1999_3000():
    """Initialize the TAI-UTC models for years -1999 to 3000 (and beyond)."""

    global _DELTA_T_NEG1999_3000

    _DELTA_T_NEG1999_3000 = FuncDeltaT(_delta_t_neg1999_3000, first=None, last=None)


# Initialize at startup
_initialize_ut1_neg1999_3000()

##########################################################################################
# Model and kernel selectors
##########################################################################################

_SELECTED_DELTA_T = None                     # Filled in below
_SELECTED_UT_MODEL = 'LEAPS'
_SELECTED_FUTURE_YEAR = None
_RUBBER = False

_DELTA_T_DICT = {       # (DeltaT object,
    'LEAPS'   : _LEAPS_DELTA_T,
    'SPICE'   : _SPICE_DELTA_T,
    'PRE-1972': MergedDeltaT(_LEAPS_DELTA_T, _DELTA_T_1958_1972),
    'CANON'   : MergedDeltaT(_LEAPS_DELTA_T, _DELTA_T_1958_1972, _DELTA_T_NEG1999_3000),
}


def set_ut_model(model='LEAPS', future=None):
    """Define how to handle the differences between TAI and UT for years prior to 1972 and
    for years into the future.

    Input:
        model       One of "LEAPS", "SPICE", "PRE-1972", or "CANON". See below.
        future      the future year at which to use the "CANON" model, if it is selected.
                    Use None or np.inf to suppress the CANON model for all future dates.
                    Ignored if the "CANON" model is not in use.

    The following models are supported:
      "LEAPS"
        This is the default model including leap seconds. It assumes that TAI-UTC equals
        10 prior to 1972 and will hold its current fixed value into the future.

      "SPICE"
        Replicate the behavior of the SPICE Toolkit, in which TAI-UTC=9 before 1972. In
        this system, December 31, 1971 incorrectly contained a leap second.

      "PRE-1972"
        In addition to the "LEAPS" model, iclude the full model for UTC widely used during
        the period 1958-1972. In these years, the UTC time system was defined in terms of
        a "rubber second", which could expand or shrink as necessary to ensure that every
        UTC day had exactly 86,400 seconds. In addition, several fractional leap seconds
        were added during the 1960s. See
            https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab

      "CANON"
        In addition to the "PRE-1972" model, include the model for UT1 "rubber seconds"
        based on the Five Millennium Canon of Solar Eclipses for the years -1999 to 3000.
        See
            https://eclipse.gsfc.nasa.gov/SEpubs/5MCSE.html
        When selected, this model will apply for all years before 1958. Use the input
        parameter "future" to specify the future year in which this model overrides the
        UTC leap second model; otherwise, by default, the leap second model will apply to
        all future years.
    """

    global _SELECTED_DELTA_T, _SELECTED_UT_MODEL, _SELECTED_FUTURE_YEAR, _RUBBER
    global _LEAPS_DELTA_T, _SPICE_DELTA_T

    _SELECTED_DELTA_T = _DELTA_T_DICT[model]
    _SELECTED_UT_MODEL = model

    if model != 'CANON':
        future = None

    if future != _SELECTED_FUTURE_YEAR:
        last_year = None if future is None else future - 1
        _LEAPS_DELTA_T.set_last_year(last_year)
        _SPICE_DELTA_T.set_last_year(last_year)
        _SELECTED_FUTURE_YEAR = future

    _RUBBER = model not in ('LEAPS', 'SPICE')


# Initialize...
set_ut_model()


def load_lsk(lsk_path=''):
    """Load the specified SPICE leap seconds kernel, possibly overriding the default
    kernel.

    If lsk_path is blank or None, the default kernel is re-loaded.

    The selected UTC model is preserved. If additional leap seconds were previously
    inserted, they must be inserted again.
    """

    _initialize_leap_seconds(lsk_path)
    _initialize_utc_1958_1972()
    _initialize_ut1_neg1999_3000()
    set_ut_model(_SELECTED_UT_MODEL, future=_SELECTED_FUTURE_YEAR)


def insert_leap_second(y, m, offset=1):
    """Insert a new (positive or negative) leap second.

    Input:
        y, m        insert the leap second(s) just before the beginning of the specified
                    year and month. This must be after any previously defined leap second.
        offset      the change in TAI - UT. Default is 1; use -1 for a negative leap
                    second.
    """

    global _LEAPS_DELTA_T, _SPICE_DELTA_T

    _LEAPS_DELTA_T.insert_leap_second(y, m, offset)
    _SPICE_DELTA_T.insert_leap_second(y, m, offset)

    _DELTA_T_DICT['LEAPS'] = _LEAPS_DELTA_T     # otherwise dict values would be stale
    _DELTA_T_DICT['SPICE'] = _SPICE_DELTA_T
    set_ut_model(_SELECTED_UT_MODEL, future=_SELECTED_FUTURE_YEAR)

##########################################################################################
# Standard API
##########################################################################################

def delta_t_from_ymd(y, m, d=1):
    """The difference between TAI seconds and UT seconds for the given date, expressed as
    a calendar year, month, and optional day.

    Integers are returned if the difference is exclusively defined by leap seconds; floats
    are returned if the difference involves UT "rubber seconds".
    """

    return _SELECTED_DELTA_T.delta_t_from_ymd(y, m, d)


def delta_t_from_day(day):
    """The difference between TAI seconds and UT seconds for the given day number.

    Integers are returned if the difference is exclusively defined by leap seconds; floats
    are returned if the difference involves UT "rubber seconds".
    """

    day = _number(day)
    (y, m, d) = ymd_from_day(day)
    return _SELECTED_DELTA_T.delta_t_from_ymd(y, m, d)


def leapsecs_from_ymd(y, m, d=1):
    """The number of leap seconds on the given date, where the date is expressed as a
    calendar year, month, and optional day.

    This differs from the function tai_minus_utc_from_ymd() in that it ignores UT "rubber
    seconds" and therefore always returns integers, typically 86400 or 86401.
    """

    return _SELECTED_DELTA_T.leapsecs_from_ymd(y, m, d)


def leapsecs_from_ym(y, m, d=1):
    """The number of leap seconds on the given date, where the date is expressed as a
    calendar year, month, and optional day.

    Alternative name for leapsecs_from_ymd().
    """

    return _SELECTED_DELTA_T.leapsecs_from_ymd(y, m, d)


def leapsecs_on_day(day):
    """The cumulative difference between TAI and UT for the given day number.

    This differs from the function tai_minus_utc_from_day() in that it ignores UT "rubber
    seconds" and therefore always returns integers, typically 86400 or 86401.
    """

    day = _number(day)
    (y, m, d) = ymd_from_day(day)
    return _SELECTED_DELTA_T.leapsecs_from_ymd(y, m, d)


def leapsecs_from_day(day):
    """The cumulative difference between TAI and UT for the given day number.

    This differs from the function tai_minus_utc_from_day() in that it ignores UT "rubber
    seconds" and therefore always returns integers, typically 86400 or 86401.

    Alternative name for leapsecs_on_day().
    """

    return leapsecs_on_day(day)


def seconds_on_day(day, leapsecs=True, timesys='UTC'):
    """Number of seconds on a given day number.

    If leapsecs is True, values of 86400 are returned regardless of the input.

    If timesys equals "UTC" (the default), the values returned are in units of UTC "rubber
    seconds", which are adjusted relative to TAI seconds in order to ensure that every day
    prior to 1972 contains exactly 86400 seconds.

    if timesys equals "TAI", then the values returned are in fixed units of TAI seconds,
    meaning that days prior to 1972 may not have integral durations.
    """

    day = _int(day)
    if not leapsecs:
        if np.isscalar(day):
            return 86400
        result = np.empty(day.shape, dtype='int')
        result.fill(86400)
        return result

    if timesys == 'UTC':
        return 86400 + leapsecs_on_day(day+1) - leapsecs_on_day(day)

    if timesys == 'TAI':
        return 86400 + delta_t_from_day(day+1) - delta_t_from_day(day)

    raise ValueError('timesys must be either "UTC" or "TAI"')   # pragma: no cover

##########################################################################################
