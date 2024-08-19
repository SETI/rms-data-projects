##########################################################################################
# julian/_utils.py
##########################################################################################
"""Internal utility functions
"""
##########################################################################################

import numbers
import numpy as np


def _int(arg):
    """Convert to integer type; works for scalar, array, or array-like.

    Floating-point numbers are always rounded downward. Integer arrays are converted to
    signed 64-bit if necessary. Scalars and arrays of shape () are returned as Python
    ints.
    """

    if isinstance(arg, numbers.Integral):
        return int(arg)

    if isinstance(arg, numbers.Real):
        return int(arg // 1.)

    array = np.asarray(arg)                     # if already an array, don't copy

    if array.dtype.kind == 'f':
        array = (array // 1.).astype('int64')

    if not array.shape:
        return int(array[()])

    # If not now int64, re-convert from the original arg
    if array.dtype != np.dtype('int64'):
        array = np.asarray(arg, dtype='int64')

    return array


def _float(arg):
    """Convert to floating-point; works for scalar, array, or array-like."""

    if isinstance(arg, numbers.Real):
        return float(arg)

    if isinstance(arg, np.ndarray) and not arg.shape:
        return float(arg[()])

    return np.asarray(arg, dtype=np.double)


def _number(arg):
    """Convert to array if array-like, but preserve data kind.

    Scalar inputs are always returned as Python ints or floats, never a NumPy data type.

    Ints are converted to signed 64-bit if necessary.
    """

    if isinstance(arg, numbers.Integral):
        return int(arg)

    if isinstance(arg, numbers.Real):
        return float(arg)

    if isinstance(arg, np.ndarray) and not arg.shape:
        return _number(arg[()])

    arg = np.asarray(arg)                       # if already an array, don't copy

    if arg.dtype.kind in 'ui':
        return np.asarray(arg, dtype='int64')   # convert only if necessary; don't copy

    return arg


def _is_int(arg):
    """True if this value or this array-like contains only integers."""

    if isinstance(arg, numbers.Integral):
        return True

    if isinstance(arg, numbers.Real):
        return False

    if not isinstance(arg, np.ndarray):
        arg = np.array(arg)

    return arg.dtype.kind in 'ui'


def _is_float(arg):
    """True if this value or this array-like contains floating-point values."""

    if isinstance(arg, numbers.Integral):
        return False

    if isinstance(arg, numbers.Real):
        return True

    if not isinstance(arg, np.ndarray):
        arg = np.array(arg)

    return arg.dtype.kind == 'f'

##########################################################################################
