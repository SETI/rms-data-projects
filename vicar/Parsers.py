"""
Context-sensitive parsing.

We represent parsers as functions that read a string, and return a
tuple containing the unconsumed string and the result of that parser.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Tuple

    # A parser is a function that takes a string and returns the
    # unconsumed input and the result of that parser.
    Parser = Callable[[str], Tuple[str, Any]]


def pure(res):
    # type: (Any) -> Parser
    """
    This creates a "dummy" parser: it just returns the result without
    consuming any input.  This is useful at the end of a chain of
    binds.
    """

    def pure_parser(byte_str):
        # type: (str) -> Tuple[str, Any]
        """Return the result without consuming any input."""
        return byte_str, res

    return pure_parser


def bind(p, f):
    # type: (Parser, Callable[[Any], Parser]) -> Parser
    """
    Combine a parser that depends on context with a previous parser.
    This is how context-sensitivity is implemented.

    The first argument is the earlier parser.  The later parser is
    created by the second argument, a function that takes the first
    parser's result and returns a parser.

    You generally want to bind to the right.
    """

    def bound_parser(byte_str):
        # type: (str) -> Tuple[str, Any]
        """
        Run the first parser.  Give the result to the function to get
        the second parser.  Run it on the remaining input.
        """
        byte_str, res = p(byte_str)
        return f(res)(byte_str)

    return bound_parser


def pmap(f, p):
    # type: (Callable[[Any], Any], Parser) -> Parser
    """
    Mapping over a parser's result.  Convert a parser returning res
    into a parser returning f(res).
    """

    def mapped_parser(byte_str):
        # type: (str) -> Tuple[str, Any]
        byte_str, res = p(byte_str)
        return byte_str, f(res)

    return mapped_parser


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


def eof(str):
    # type: (str) -> Tuple[str, Any]
    """
    A parser for the end of file.  Returns None if at the end of file;
    raises an exception if not.
    """
    if not len(str):
        return '', None
    else:
        raise Exception('eof parser failed')
