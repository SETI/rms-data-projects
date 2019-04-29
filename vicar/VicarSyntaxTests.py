import random
from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

from HistoryLabels import HistoryLabels, Task
from ImageArea import ImageArea
from LabelItem import LabelItem
from Labels import Labels
from PropertyLabels import Property, PropertyLabels
from SystemLabels import SystemLabels
from Tail import Tail
from Value import IntegerValue, RealValue, StringValue
from VicarFile import VicarFile

if TYPE_CHECKING:
    from typing import Iterable
    from VicarSyntax import VicarSyntax


class VicarSyntaxTests(object):
    """
    An abstract base class providing tests for common functionality of
    VicarSyntax elements.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def args_for_test(self):
        # type: () -> Iterable[VicarSyntax]
        """
        Some interesting (or not) values for testing.
        """
        pass

    def assertEqual(self, first, second, msg=None):
        assert False, 'must be overridden'

    def test_equal(self):
        # type: () -> None
        """
        Verify that equality is reflexive on the given values.
        """
        for arg in self.args_for_test():
            self.assertEqual(arg, arg)

    def test_to_byte_length(self):
        # type: () -> None
        """
        Verify that to_byte_length() yields the same as (the possibly less
        efficient) length of the result of to_byte_string().
        """
        for arg in self.args_for_test():
            self.assertEqual(len(arg.to_byte_string()), arg.to_byte_length())

    def test_to_padded_byte_string(self):
        # type: () -> None
        """
        Verify that to_padded_byte_string(recsize) yields a string of
        a length that's a multiple of recsize.
        """
        for arg in self.args_for_test():
            byte_str = arg.to_byte_string()
            byte_len = arg.to_byte_length()

            if byte_len:
                # check that it won't pad at all if not necessary
                padded_byte_str = arg.to_padded_byte_string(byte_len)
                self.assertEqual(byte_str, padded_byte_str)

            # check that it pads properly in other cases:
            recsize = random.randint(256, 2048)
            padded_byte_str = arg.to_padded_byte_string(recsize)
            # that the length is a multiple
            self.assertEqual(0, len(padded_byte_str) % recsize)
            # and that the initial part of the string is untouched
            self.assertEqual(byte_str, padded_byte_str[:byte_len])

    def test_repr(self):
        """
        Verify that evaluating repr(arg) is equal to arg.
        """
        # eval() needs to see all the types in order to build them.
        # Unfortunately, my IDE thinks the imports are unused and deletes them.
        # So I add their names here to fool it.

        needed_imports = [HistoryLabels, ImageArea, IntegerValue, LabelItem,
                          Labels, Property, PropertyLabels, RealValue,
                          StringValue, SystemLabels, Tail, Task, VicarFile]

        for arg in self.args_for_test():
            self.assertEqual(arg, eval(str(arg)), str(arg))
