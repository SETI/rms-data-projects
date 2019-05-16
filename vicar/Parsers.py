"""
Context-sensitive parsing, that is parsing that depends on earlier
parts of the file.

We represent all our context-sensitive parsers as functions that read
a string, and return a 2-tuple containing the unconsumed string and
the result of that parser.  To combine parsers, you parse the
component parts and combine them.

byte_str, part_1 = parse_part_1(byte_str)
byte_str, part_2 = parse_part_2(byte_str)
byte_str, part_3 = parse_part_3(byte_str)
return byte_str, combine_parts(part_1, part_2, part_3)

By having all parsing functions follow this format, we can compose
large parsers hierarchically.

This file contains building blocks to build larger parsers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Tuple

    # A parser is a function that takes a string and returns the
    # unconsumed input and the result of that parser.
    Parser = Callable[[str], Tuple[str, Any]]


def bytes(n):
    # type: (int) -> Parser
    """
    A parser that consumes a fixed number of bytes.
    """

    def bytes_parser(byte_str):
        # type: (str) -> Tuple[str, Any]
        l = len(byte_str)
        if l < n:
            raise Exception('bytes(): not enough bytes available')
        return byte_str[n:], byte_str[:n]

    return bytes_parser


def repeat(n, p):
    # type: (int, Parser) -> Parser
    """
    A parser that runs the given parser n times and returns a list of
    the results.
    """
    assert n >= 0

    def repeating_parser(byte_str):
        # type: (str) -> Tuple[str, List[Any]]
        res = list()
        for i in xrange(n):
            byte_str, item = p(byte_str)
            res.append(item)
        return byte_str, res

    return repeating_parser


def rest_of_input(byte_str):
    # type: (str) -> Tuple[str, Any]
    """
    A parser that consumes and returns the rest of the input.
    """
    return '', byte_str


def parse_all(p, byte_str):
    # type: (Parser, str) -> Any
    """
    Run the parser; raise an exception if it does not consume the
    entire input.
    """
    byte_str, res = p(byte_str)
    if byte_str:
        raise Exception('parse_all() left %d bytes unconsumed' %
                        len(byte_str))
    return res
