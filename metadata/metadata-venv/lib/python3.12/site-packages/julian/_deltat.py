##########################################################################################
# julian/_deltat.py
##########################################################################################
"""Internal classes for managing offset seconds vs. date.
"""
##########################################################################################

import numpy as np
from julian.calendar import day_from_ymd

# Use the min and max int64 values for unlimited year ranges
# ...but divide by 14 to ensures that 13*year does not overflow.
_MIN_YEAR = np.ma.maximum_fill_value(np.dtype('int64')) // 14     # -658812288346769701
_MAX_YEAR = np.ma.minimum_fill_value(np.dtype('int64')) // 14     #  658812288346769700


class DeltaT(object):
    """Abstract class definition for an object that returns a number of offset seconds as
    a function of date.

    This class is used to manage leap seconds (TAI - UTC) and variations in Earth's
    rotation (TT - UT1).

    Required attributes are:
        first       the first year covered by this object.
        last        the last year (inclusive) to which this object applies. Its value is
                    _MAX_YEAR if the object applies to all future years. This value is only
                    relevant if this object is part of a MergedDeltaT object, in which
                    case a lower-precedence object will be used for later years.
        before      the value of delta-T to return for times before the earliest date.
        after       the value of delta-T to return for times after the latest date.
        is_float    True if this object returns floating-point values; False if it returns
                    integers.

    Note that DeltaT objects always cover a complete range of years, never fractional
    years.
    """

    FLAG = -99999999        # An impossible value of delta-T

    def delta_t_from_ymd(self, y, m, d=1):
        """The cumulative delta-T in seconds for the given day, expressed as a calendar
        year, month, and optional day.

        Integers are returned if the value is integral; otherwise, floats are returned.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        pass        # defined by subclass       # pragma: no cover

    def leapsecs_from_ymd(self, y, m, d=1):
        """The cumulative number of leap seconds on the given date, where the date is
        expressed as a calendar year, month, and optional day.

        This differs from the function delta_t_from_ymd() in that it returns values in
        units of UT "rubber seconds" rather than in units of TAI seconds. Values are
        always integers and have a fixed value if delta-T uses floating-point values.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        # Default behavior is to return zeros
        (y, m, d) = np.broadcast_arrays(y, m, d)
        if y.shape:
            return np.zeros(y.shape, dtype='int')
        else:
            return 0

##########################################################################################
# LeapDeltaT
##########################################################################################

class LeapDeltaT(DeltaT):
    """A Delta-T subclass that returns integer values (e.g., leap seconds) from a lookup
    table indexed by month.
    """

    is_float = False

    def __init__(self, info, before=None, last=None):
        """Constructor.

        Input:
            info        a list of tuples (year, month, delta_t), where delta_t is the
                        integer number of leap seconds at the beginning of the specified
                        year and month. Dates must be in chronological order.
            before      the value to return for dates before the earliest date; default is
                        to return the same value as for the earliest date in the info
                        list.
            last        the last year (inclusive) to which this object applies. Use None
                        or np.inf for an object that applies for all future dates. This
                        value is only relevant if this object is part of a MergedDeltaT
                        object, in which case a lower-precedence object will be used for
                        later years.
        """

        self.update_count = 0
        self._update(info, before=before, last=last)

    def _update(self, info, before, last):
        """Internal method to insert the list of leap seconds table into this existing
        LeapDeltaT object.
        """

        self.info = info
        self.before = info[0][2] if before is None else int(before)

        years   = np.array([rec[0] for rec in info])
        months  = np.array([rec[1] for rec in info])
        seconds = np.array([rec[2] for rec in info])

        self.first = years[0]
        self.last = _MAX_YEAR if last in (None, np.inf) else max(years[-1], last)
        self.max_year = years[-1] + 1

        indx = 13 * (years - self.first) + months
        if np.any(np.diff(indx) <= 0):
            raise ValueError('leap second dates are not in chronological order')

        # Construct a 1-D array indexed by 13 * (year - first) + month
        self.leaps = np.empty(13 * (self.max_year - self.first + 1), dtype='int')
        self.leaps.fill(DeltaT.FLAG)
        for k in range(len(info)):
            indx = 13 * (years[k] - self.first) + months[k]
            self.leaps[indx] = seconds[k]

        # Flagged values need to be replaced by the next-lower leap second count
        prev_delta_t = self.before
        for indx in range(len(self.leaps)):
            if self.leaps[indx] == DeltaT.FLAG:
                self.leaps[indx] = prev_delta_t
            else:
                prev_delta_t = self.leaps[indx]

        self.update_count += 1          # keep track of updates

    def set_last_year(self, last):
        """Redefine the last year for which this object applies.

        The last year is only used if this is part of a MergedDeltaT object, in which case
        it indicates that a lower-precedence object can be used for later years.
        """

        self._update(self.info, before=self.before, last=last)

    def insert_leap_second(self, y, m, offset=1):
        """Insert a new (positive or negative) leap second into this model.

        Input:
            y, m        insert the leap second(s) just before the beginning of the
                        specified year and month. This must be after any previously
                        defined leap second.
            offset      the change in delta-T. Default is 1; use -1 for a negative leap
                        second.
        """

        latest_leaps = self.leaps[-1]
        leaps_at_ym = self.leapsecs_from_ymd(y, m)
        if leaps_at_ym != latest_leaps:
            raise ValueError('new leap second must occur after %04d-%02d-01'
                             % (self.info[-1][0], self.info[-1][1]))

        info = self.info + [(y, m, latest_leaps + offset)]
        self._update(info, before=self.before, last=self.last)

    def delta_t_from_ymd(self, y, m, d=1):
        """The cumulative delta-T in seconds for the given day, expressed as a calendar
        year, month, and optional day.

        Leap second values are always integers.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        (y, m, d) = np.broadcast_arrays(y, m, d)
        if not y.shape:
            y = y[()]
            m = m[()]
            d = d[()]

        y = np.minimum(y, self.max_year)
        indx = np.maximum(13 * (y - self.first) + m, 0)
        return self.leaps[indx]

    def leapsecs_from_ymd(self, y, m, d=1):
        """The cumulative number of leap seconds on the given date, where the date is
        expressed as a calendar year, month, and optional day.

        This differs from the function delta_t_from_ymd() in that it returns values in
        units of UT "rubber seconds" rather than in units of TAI seconds. Values are
        always integers and have a fixed value if delta-T uses floating-point values.

        For this subclass, leapsecs_from_ymd() and delta_t_from_ymd() are the same.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        return self.delta_t_from_ymd(y, m, d)

##########################################################################################
# SplineDeltaT
##########################################################################################

class SplineDeltaT(DeltaT):
    """A Delta-T subclass that returns floating-point values based on linear spline
    coefficients in a table indexed by month.
    """

    is_float = True

    def __init__(self, info, before=None, last=None):
        """Constructor.

        Input:
            info        a list of tuples with three, four, or five elements
                        (y, m, offset[, slope[, dref]]).
                            y, m    year and month at the start of a spline window;
                            delta_t delta-T at the start of the window;
                            slope   gradient in the window, d(delta-T)/d(day);
                            dref    the day number to which the offset and slope are
                                    referenced.
                        If the slope is not provided, it is inferred from the offset
                        value in the next window. If the reference day number is not
                        provided, it is the day number of the first day in the specified
                        year and month.
            before      the delta-T value to return for dates before the earliest date;
                        default is to return the same value as for the earliest date in
                        the info list.
            last        the last year (inclusive) to which this object applies. Use None
                        or np.inf for an object that applies for all future dates. This
                        value is only relevant if this object is part of a MergedDeltaT
                        object, in which case a lower-precedence object will be used for
                        later years.
        """

        self.info = info

        years   = np.array([rec[0] for rec in info])
        months  = np.array([rec[1] for rec in info])
        offsets = np.array([rec[2] for rec in info])

        self.first = years[0]
        self.last = _MAX_YEAR if last in (None, np.inf) else max(years[-1], last)
        self.max_year = years[-1] + 1

        days = day_from_ymd(years, months, 1)

        if len(info[0]) > 3:
            slopes = np.array([rec[3] for rec in info])
        else:
            slopes = np.zeros(len(info))
            slopes[:-1] = (offsets[1:] - offsets[:-1]) / (days[1:] - days[:-1])

        if len(info[0]) > 4:
            drefs = np.array([rec[4] for rec in info])
        else:
            drefs = days

        self.offsets = offsets
        self.slopes = slopes
        self.drefs = drefs

        # Identify the "before" value
        if before is None:
            self.before = offsets[0] + slopes[0] * (days[0] - drefs[0])
        else:
            self.before = float(before)

        # Construct a 1-D array indexed by 13 * (year - first) + month
        self.params = np.zeros((13 * (self.max_year - self.first + 2), 3))
        self.params.fill(DeltaT.FLAG)

        indx = 13 * (years - self.first) + months
        self.params[indx,0] = self.offsets
        self.params[indx,1] = self.slopes
        self.params[indx,2] = self.drefs

        # Values of zero need to be replaced by the next-lower set of values
        prev_params = np.array([self.before, 0., 0.])
        for indx in range(len(self.params)):
            if self.params[indx,0] == DeltaT.FLAG:
                self.params[indx] = prev_params
            else:
                prev_params = self.params[indx]

    def delta_t_from_ymd(self, y, m, d=1):
        """The cumulative delta-T in seconds for the given day, expressed as a calendar
        year, month, and optional day.

        Returned values are always floating-point.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        (y, m, d) = np.broadcast_arrays(y, m, d)
        if not y.shape:
            y = y[()]
            m = m[()]
            d = d[()]

        y = np.minimum(y, self.max_year)
        indx = np.maximum(13 * (y - self.first) + m, 0)

        if np.isscalar(indx):
            (offset, slope, dref) = self.params[indx]
        else:
            selected = self.params[indx]
            offset = selected[...,0]
            slope  = selected[...,1]
            dref   = selected[...,2]

        day = day_from_ymd(y, m, d)
        return offset + slope * (day - dref)

##########################################################################################
# FuncDeltaT
##########################################################################################

class FuncDeltaT(DeltaT):
    """A Delta-T subclass that returns floating-point values based on a given function of
    year, month, and day.
    """

    is_float = True

    def __init__(self, func, first=None, last=None, before=None, after=None):
        """Constructor.

        Input:
            info        a function of (y,m,d) that returns values of delta-T.
            first       the first year covered by this object. Use None or -np.inf for an
                        object that applies to all earlier dates.
            last        the last year (inclusive) to which this object applies. Use None
                        or np.inf for an object that applies for all future dates. This
                        value is only relevant if this object is part of a MergedDeltaT
                        object, in which case a lower-precedence object will be used for
                        later years.
            before      the value to return for years before first; default is the
                        value at the beginning of the first year.
            after       the value to return for years after last; default is the value at
                        the end of last.
        """

        self.func = func

        # Use the min and max int64 values in place of infinite years
        self.first = _MIN_YEAR if first in (None, -np.inf) else first
        self.last  = _MAX_YEAR if last  in (None,  np.inf) else last

        self.before = func(self.first, 1,1) if before is None else float(before)
        self.after  = func(self.last+1,1,1) if after  is None else float(after)

    def delta_t_from_ymd(self, y, m, d=1):
        """The cumulative delta-T in seconds for the given day, expressed as a calendar
        year, month, and optional day.

        Returned values are always floating-point.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        (y, m, d) = np.broadcast_arrays(y, m, d)
        if not y.shape:
            y = y[()]
            m = m[()]
            d = d[()]

            if y < self.first:
                return self.before
            elif y > self.last:
                return self.after
            else:
                return self.func(y, m, d)

        results = self.func(y, m, d)
        if self.first != _MIN_YEAR:
            results[y < self.first] = self.before

        if self.last != _MAX_YEAR:
            results[y > self.last] = self.after

        return results

##########################################################################################
# MergedDeltaT
##########################################################################################

class MergedDeltaT(DeltaT):
    """A model that is composed of one or more other models."""

    def __init__(self, *models):
        """Constructor. Input is two or more DeltaT objects in order of decreasing
        precedence.
        """

        self._update(*models)

    def _update(self, *models):
        """Internal method to update the object; needed for when a new leap second is
        inserted into an internal LeapDeltaT object.
        """

        self.models = models
        self.upward = models[::-1]      # models ordered by increasing precedence
        self.first = min(m.first for m in models)
        self.last  = max(m.last  for m in models)
        self.is_float = np.any([m.is_float for m in models])

        # Nested MergedDeltaT is not allowed
        for m in self.models:
            if isinstance(m, MergedDeltaT):
                raise TypeError('MergedDeltaT objects cannot be nested')

        # Identify the earliest model and the "before" value
        self.leap_model_defines_before = False
        for m in self.upward:
            if m.first == self.first:
                self.earliest_model = m
                self.leap_model_defines_before = isinstance(m, LeapDeltaT)
                    # defines whether leap_seconds_from_ymd() returns a nonzero value

        self.before = self.earliest_model.before
        if self.is_float:           # pragma: no branch
            self.before = float(self.before)

        # Identify the internal LeapDeltaT if any
        self.leap_model = None
        self.leap_model_update = 0
        for m in self.upward:
            if isinstance(m, LeapDeltaT):
                if self.leap_model is not None:
                    raise ValueError('Multiple LeapDeltaT objects inside MergedDeltaT')
                self.leap_model = m
                self.leap_model_update = m.update_count

    def delta_t_from_ymd(self, y, m, d=1):
        """The cumulative delta-T in seconds for the given day, expressed as a calendar
        year, month, and optional day.

        Returned values are always floating-point.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        # If the LeapDeltaT was updated, update this
        if self.leap_model and self.leap_model.update_count != self.leap_model_update:
            self._update(*self.models)

        (y, m, d) = np.broadcast_arrays(y, m, d)
        if not y.shape:
            y = y[()]
            m = m[()]
            d = d[()]

            if y < self.first:
                if self.leap_model_defines_before:
                    return int(self.before)
                else:
                    return self.before

            for model in self.models:               # highest to lowest precedence
                if y >= model.first and y <= model.last:
                    return model.delta_t_from_ymd(y, m, d)

            return self.models[0].delta_t_from_ymd(y, m, d)

        # Use this shortcut if only the top model is needed
        if np.all((y >= self.models[0].first) & (y <= self.models[0].last)):
            return self.models[0].delta_t_from_ymd(y, m, d)

        # Track the values and the dtype
        results = np.empty(y.shape)
        undefined = np.ones(y.shape, dtype='bool')
        floats = np.zeros(y.shape, dtype='bool')

        for model in self.upward[:-1]:              # lowest to highest precedence
            mask = (y >= model.first) & (y <= model.last)
            if np.any(mask):
                results[mask] = model.delta_t_from_ymd(y, m, d)[mask]
                undefined[mask] = False
                floats[mask] = model.is_float

        model = self.models[0]
        mask = undefined | ((y >= model.first) & (y <= model.last))
            # use the highest-precedence model wherever the value is still undefined
        results[mask] = model.delta_t_from_ymd(y, m, d)[mask]
        floats[mask] = model.is_float

        if not np.any(floats):
            return results.astype('int')

        return results

    def leapsecs_from_ymd(self, y, m, d=1):
        """The cumulative number of leap seconds on the given date, where the date is
        expressed as a calendar year, month, and optional day.

        This differs from the function delta_t_from_ymd() in that it returns values in
        units of UT "rubber seconds" rather than in units of TAI seconds. Values are
        always integers and have a fixed value if delta-T uses floating-point values.

        Input:
            y       calendar year as an integer scalar, array, or array-like.
            m       calendar month number (1-12) as an integer scalar, array, or
                    array-like.
            d       calendar day number (1-31) as an integer scalar, array, or array-like.

        Note that if any of the input values are arrays or array-like, they need not have
        the same array shape; the the returned array will be have the broadcasted shape
        of the input arrays.
        """

        if not self.leap_model:
            return DeltaT.leapsecs_from_ymd(self, y, m, d)      # return zeros

        # If the LeapDeltaT was updated, update this
        if self.leap_model.update_count != self.leap_model_update:
            self._update(*self.models)

        return self.leap_model.leapsecs_from_ymd(y, m, d)

##########################################################################################

