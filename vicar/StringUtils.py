'''
Functionality to escape raw strings to their Vicar format and unescape
them back.
'''
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


def escape_byte_string(bs):
    # type: (str) -> str
    '''Escape a raw Python string.'''

    def escape_char(c):
        # type: (str) -> str
        if c == "'":
            return "''"
        else:
            return c

    return "'" + ''.join([escape_char(c) for c in bs]) + "'"


def unescape_byte_string(bs):
    # type: (str) -> str
    '''Unescape a raw Python string.'''
    assert bs[0] == "'" and bs[-1] == "'", 'unescape_byte_string(%r)' % bs
    res = []  # type: List[str]
    saw_quote = False
    for c in bs[1:-1]:
        if saw_quote:
            # We just passed a quote
            assert c == "'", 'unescape_byte_string(%r): double-quotes?' % bs
            res.extend("'")
            saw_quote = False
        elif c == "'":
            # It's a first quote
            saw_quote = True
        else:
            res.extend(c)
            saw_quote = False
    assert not saw_quote, 'unescape_byte_string(%r): EOF quotes?' % bs

    return ''.join(res)
