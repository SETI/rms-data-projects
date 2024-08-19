##########################################################################################
# julian/_warnings.py
##########################################################################################
"""Definition of class JulianDeprecationWarning
"""
##########################################################################################

import warnings


class JulianDeprecationWarning(DeprecationWarning):
    pass


_WARNING_MESSAGES = set()


def _warn(message):
    """Raise this DeprecationWarning message, but only once."""

    global _WARNING_MESSAGES

    if message in _WARNING_MESSAGES:
        return

    warnings.warn(message, category=JulianDeprecationWarning)
    _WARNING_MESSAGES.add(message)

##########################################################################################
