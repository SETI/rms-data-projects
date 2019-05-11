from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING

from HistoryLabels import HistoryLabels, Task
from ImageArea import ImageArea
from LabelItem import LabelItem
from Labels import Labels
from Parsers import parse_all
from PropertyLabels import Property, PropertyLabels
from SystemLabels import SystemLabels
from Tail import Tail
from Value import IntegerValue, RealValue, StringValue
from VicarFile import VicarFile

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional
    from Parsers import Parser
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

    def assertEqual(self, _first, _second, _msg=None):
        assert False, 'must be overridden'

    def syntax_parser_for_arg(self, arg):
        # type: (Any) -> Optional[Parser]
        return None

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

    def test_repr(self):
        """
        Verify that evaluating repr(arg) is equal to arg.
        """
        # eval() needs to see all the types in order to build them.
        # Unfortunately, my IDE thinks the imports are unused and deletes them.
        # So I add their names here to fool it.

        _needed_imports = [HistoryLabels, ImageArea, IntegerValue, LabelItem,
                           Labels, Property, PropertyLabels, RealValue,
                           StringValue, SystemLabels, Tail, Task, VicarFile]

        for arg in self.args_for_test():
            self.assertEqual(arg, eval(str(arg)), str(arg))

    def test_parsing(self):
        # type: () -> None
        for arg in self.args_for_test():
            parser = self.syntax_parser_for_arg(arg)
            if parser is not None:
                byte_str = arg.to_byte_string()
                rt_arg = parse_all(parser, byte_str)
                self.assertEqual(arg, rt_arg)
