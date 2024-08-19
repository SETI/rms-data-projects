################################################################################
# interval.py
#
# Deukkwon Yoon & Mark Showalter, PDS Rings Node, SETI Institute, November 2011
################################################################################

import numpy as np

try:
    from ._version import __version__
except ImportError as err:
    __version__ = 'Version unspecified'


class Interval(object):
    """The interval class behaves like a dictionary keyed by ranges of
    floating-point numbers. Each value of the dictionary applies for any key
    value within the numeric range. Later entries into the dictionary can
    partially or completely replace earlier values."""

    def __init__(self, min=-np.inf, max=np.inf, value=None):

        # convert interger to float
        min = float(min)
        max = float(max)

        self.count  = 0             # Latest sequence number added
        self.values = [value]       # Value at each sequence number
        self.counts = {min:0}       # Sequence number at each lower end point
        self.xlist = [min, max]     # List of all numeric endpoints

    def __str__(self):
        """Returns a string representation of the Interval object."""

        strlist = ["Interval{"]
        for i in range(len(self.xlist)-1):
            xlo = self.xlist[i]
            xhi = self.xlist[i+1]

            value = self.values[self.counts[xlo]]

            # Brackets mean the limit is included; parentheses mean it is not
            if self[xlo] == value:
                delim_lo = "["
            else:
                delim_lo = "("

            if self[xhi] == value:
                delim_hi = "]"
            else:
                delim_hi = ")"

            # Erase a trailing zero on integer-valued limits. It looks better
            str_xlo = str(xlo)
            if str_xlo.endswith(".0"):
                str_xlo = str_xlo[:-1]

            str_xhi = str(xhi)
            if str_xhi.endswith(".0"):
                str_xhi = str_xhi[:-1]

            strlist += [delim_lo, str_xlo, ",", str_xhi, delim_hi, ": ",
                        repr(value), ", "]

        strlist[-1] = "}"
        return "".join(strlist)

    def __repr__(self): return str(self)

    def __setitem__(self, xlimits, value):
        """Overlays the given value within the limit s (xlo,xhi)"""

        (xlo, xhi) = xlimits

        # Ignore ranges completely outside the interval
        if xhi <= self.xlist[0]:  return
        if xlo >= self.xlist[-1]: return
        if xhi <= xlo: return

        # Limit each range to the designated interval
        if xlo < self.xlist[0]:  xlo = self.xlist[0]
        if xhi > self.xlist[-1]: xhi = self.xlist[-1]

        # Convert to floating-point if necessary
        xlo = float(xlo)
        xhi = float(xhi)

        # Insert new upper endpoint into the interval
        self.count += 1
        if xhi not in self.xlist:
            self.xlist.append(xhi)
            self.xlist.sort()

            # Assign the value to be that of the point immediately below
            xbelow = self.xlist[self.xlist.index(xhi) - 1]
            self.counts[xhi] = self.counts[xbelow]

        # Insert new lower endpoint and value into the interval
        if xlo not in self.xlist:
            self.xlist.append(xlo)
            self.xlist.sort()

        self.counts[xlo] = self.count
        self.values.append(value)

        # Remove intermediate points, if any (working DOWNWARD!)
        ilo = self.xlist.index(xlo)
        ihi = self.xlist.index(xhi)
        for i in range(ihi-1, ilo, -1):
            del(self.counts[self.xlist[i]])
            ignore = self.xlist.pop(i)

    def _index(self, x, bias=0):
        """Returns the index into self.xlist identifying the lower end of the
        range within which value x falls.

        Input:
            x           an x value.

            bias        defines what to do when x lands on an exact boundary
                        between ranges.
                            bias < 0: choose the lower range
                            bias > 0: choose the upper range
                            bias == 0: choose range defined last.
        """

        if x < self.xlist[0] or x > self.xlist[-1]:
            raise ValueError("value outside range of Interval: " + str(x))

        if x > self.xlist[-2]: return len(self.xlist) - 2

        for i in range(1,len(self.xlist)-1):
            if x > self.xlist[i]: continue
            if x < self.xlist[i]: return i - 1

            # On exact match of boundary, decide which entry takes precedence
            if bias < 0: return i - 1
            if bias > 0: return i

            clo = self.counts[self.xlist[i-1]]
            chi = self.counts[self.xlist[i]]
            if clo > chi:
                return i - 1
            else:
                return i

        # This is where we end up if you ask for the lower limit exactly
        return 0

    def __getitem__(self, x):
        """For a single value, this returns the value of the Interval at the
        requested location. For a tuple (xlo,xhi), this returns the list of
        values found within the range, given in the order they were originally
        inserted into the Interval"""

        # For a single value, one quick lookup will do
        if type(x) != type([]) and type(x) != type(()):
            return self.values[self.counts[self.xlist[self._index(x)]]]

        # Otherwise, make an ordered xlist of counts within the range
        ilo = self._index(x[0], bias=1)
        ihi = self._index(x[1], bias=-1)

        counts = []
        for i in range(ilo, ihi+1):
            count = self.counts[self.xlist[i]]
            if count not in counts: counts.append(count)

        counts.sort()

        # Convert to an ordered list of values
        values = []
        for count in counts:
            value = self.values[count]

            # A duplicate value gets moved to the end of the list
            if value in values:
                ignore = values.pop(values.index(value))

            values.append(value)

        return values
