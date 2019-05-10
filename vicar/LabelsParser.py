from ply import lex, yacc
from ply.lex import TOKEN
import sys

from LabelItem import LabelItem
from Labels import Labels
from HistoryLabels import HistoryLabels
from PropertyLabels import PropertyLabels
from SystemLabels import SystemLabels
from Value import *


reserved = {
'DAT_TIM' : 'DAT_TIM_KW',
'LBLSIZE' : 'LBLSIZE_KW',
'PROPERTY' : 'PROPERTY_KW',
'TASK' : 'TASK_KW',
'USER' : 'USER_KW',
}

tokens = [
    'EQUALS',
    'INTEGER',
    'INTEGERS',
    'KEYWORD',
    'REAL',
    'REALS',
    'STRING',
    'STRINGS',
    'WHITESPACE'
    ] + list(reserved.values())

# There is a limitation in the Python 2.7 libraries (sre_compile.py)
# in the number of parentheses allowed in a regular expression; the
# error message is "sorry, but this version only supports 100 named
# groups".  I hit this by wrapping *all* the regexps in parentheses,
# then removed some to make it compile, but that also introduced bugs.
# I *think* this version is correct, but if there are bugs in the
# scanning, this might be a good place to look.

################
# CHARACTER SETS
################

_white = r'[ ]'
_digit = r'[0-9]'
_alpha = r'[A-Z]'
_kw_char = r'[A-Z_0-9]'
_sign = r'[-+]'
_sq = "[']"
_not_sq = "[^']"
_left_paren = r'[(]'
_right_paren = r'[)]'
_comma = r'[,]'
_dot = r'[.]'
_exp_char = r'[EeDd]'

################
# REGULAR EXPRESSIONS
################

_digits_re = _digit + r'+'
_opt_sign_re = _sign + r'?'
_integer_re = _opt_sign_re + _digits_re
_opt_digits_re = _digit + r'*'
_opt_white_re = _white + r'*'

_exp_re = _exp_char + _opt_sign_re + _integer_re
_opt_exp_re = r'(' + _exp_re + ')?'

_frac_digits_re = r'(' + _dot + _digits_re + r')'
_frac_opt_digits_re = r'(' + _dot + _opt_digits_re + r')'
_real1_re = r'(' + _integer_re + r'(' + \
    _frac_opt_digits_re + _opt_exp_re + r'|' + \
    _exp_re + \
    r')' + r')'
_real2_re = r'(' + _opt_sign_re + _frac_digits_re + _opt_exp_re + r')'
_real_re = r'(' + _real1_re + r'|' + _real2_re + r')'

# A number of the early Cassini VICAR files contain string values in
# the labels that are not properly escaped.  They include the
# characters " FW'S " whose un-doubled single quote prematurely ends
# the string.  Since most string values are followed by space, we hack
# around this by considering a single quote followed by a capital S
# and a space as legal within a string value.  It isn't legal, but
# this lets the parse continue and doesn't seem to cause other issues.

_cassini_string_char_hack_re = r'(' + _sq + r'[S]' + _white + r')'

_string_char_re = r'(' + \
    _sq + _sq + r'|' + \
    _not_sq + r'|' + \
    _cassini_string_char_hack_re + \
    r')'
_string_re = _sq + r'(' + _string_char_re + r'*)' + _sq

_left_paren_re = r'(' + _left_paren + _opt_white_re + r')'
_right_paren_re = r'(' + _opt_white_re + _right_paren + r')'
_comma_re = r'(' + _opt_white_re + _comma  + _opt_white_re + r')'

################

t_EQUALS = r'(' + _opt_white_re + r'=' + _opt_white_re + r')' 

t_WHITESPACE = r'(' + _white + r'+)'

t_REAL = _real_re

t_INTEGER = _integer_re

t_STRING = _string_re

t_REALS = r'(' + _left_paren_re + _real_re + \
                 r'(' + _comma_re + _real_re + r')*' + \
                 _right_paren_re + r')'

t_INTEGERS = r'(' + _left_paren_re + _integer_re + \
                 r'(' + _comma_re + _integer_re + r')*' + \
                 _right_paren_re + r')'

t_STRINGS = r'(' + _left_paren_re + _string_re + \
                 r'(' + _comma_re + _string_re + r')*' + \
                 _right_paren_re + r')'

def t_KEYWORD(t):
    r'[A-Z_][A-Z_0-9]*'
    t.type = reserved.get(t.value,'KEYWORD')    # Check for reserved words
    return t

# Error handling rule
def t_error(t):
     print "Illegal character '%s'" % t.value[0]
     print "Rest is '%s'" % t.value
     sys.exit(1)


################################

def p_labels(p):
    'labels : systemlabels propertylabels historylabels'
    p[0] = Labels(p[1], p[2], p[3], None)

################

def p_systemlabels(p):
    'systemlabels : lblsizeitem labelitems'
    p[0] = SystemLabels([p[1]] + p[2])

################

def p_lblsizeitem(p):
    'lblsizeitem : optwhitespace LBLSIZE_KW EQUALS INTEGER optwhitespace'
    p[0] = LabelItem(p[1], p[2], p[3], IntegerValue(p[4]), p[5])

################

def p_labelitems_some(p):
    'labelitems : labelitems labelitem'
    p[1].append(p[2])
    p[0] = p[1]

def p_labelitems_none(p):
    'labelitems : '
    p[0] = list()

################

def p_generallabelitem_lblsize(p):
    'generallabelitem : optwhitespace LBLSIZE_KW EQUALS INTEGER optwhitespace'
    p[0] = LabelItem(p[1], p[2], p[3], IntegerValue(p[4]), p[5])

def p_generallabelitem_other(p):
    'generallabelitem : labelitem'
    p[0] = p[1]

################

def p_labelitem(p):
    'labelitem : KEYWORD EQUALS value optwhitespace'
    p[0] = LabelItem(None, p[1], p[2], p[3], p[4])

################

def p_value_integer(p):
    'value : INTEGER'
    p[0] = IntegerValue(p[1])

def p_value_integers(p):
    'value : INTEGERS'
    p[0] = IntegersValue(p[1])

def p_value_real(p):
    'value : REAL'
    p[0] = RealValue(p[1])

def p_value_reals(p):
    'value : REALS'
    p[0] = RealsValue(p[1])

def p_value_string(p):
    'value : STRING'
    p[0] = StringValue(p[1])

def p_value_strings(p):
    'value : STRINGS'
    p[0] = StringsValue(p[1])

################

def p_optwhitespace_some(p):
    'optwhitespace : WHITESPACE'
    p[0] = p[1]

def p_optwhitespace_none(p):
    'optwhitespace :'
    p[0] = None

################

def p_propertylabels(p):
    'propertylabels : properties'
    p[0] = PropertyLabels(p[1])

################

def p_properties_some(p):
    'properties : properties property'
    p[1].append(p[2])
    p[0] = p[1]

def p_properties_none(p):
    'properties :'
    p[0] = list()

################

def p_property(p):
    'property : propertyitem labelitems'
    p[0] = Property([p[1]] + p[2])

################

def p_propertyitem(p):
    'propertyitem : PROPERTY_KW EQUALS STRING optwhitespace'
    p[0] = LabelItem(None, p[1], p[2], StringValue(p[3]), p[4])

################

def p_historylabels(p):
    'historylabels : tasks'
    p[0] = HistoryLabels(p[1])

################

def p_tasks_some(p):
    'tasks : tasks task'
    p[1].append(p[2])
    p[0] = p[1]

def p_tasks_none(p):
    'tasks :'
    p[0] = list()

################

def p_task(p):
    'task : taskitem useritem dattimitem labelitems'
    p[0] = Task([p[1], p[2], p[3]] + p[4])

################

def p_taskitem(p):
    'taskitem : TASK_KW EQUALS STRING optwhitespace'
    p[0] = LabelItem(None, p[1], p[2], StringValue(p[3]), p[4])

################

def p_useritem(p):
    'useritem : USER_KW EQUALS STRING optwhitespace'
    p[0] = LabelItem(None, p[1], p[2], StringValue(p[3]), p[4])

################

def p_dattimitem(p):
    'dattimitem : DAT_TIM_KW EQUALS STRING optwhitespace'
    p[0] = LabelItem(None, p[1], p[2], StringValue(p[3]), p[4])

################

def p_error(p):
    print 'Syntax error at %s: %s' % (p.type, p)
    sys.exit(1)

################################

def parse_labels(src):
    # type: (str) -> Labels
    lexer = lex.lex()
    parser = yacc.yacc(start='labels')
    return parser.parse(src)

##############################

def parse_label_item(src):
    # type: (str) -> LabelItem
    lexer = lex.lex()
    # TODO Is this right?  Or am I excluding certain keywords?
    parser = yacc.yacc(start='generallabelitem')
    return parser.parse(src)

################################

def parse_lblsize(src):
    # type: (str) -> int
    lexer = lex.lex()
    lexer.input(src)
    tok = lexer.token()
    if tok.type == 'WHITESPACE':
        tok = lexer.token()
    assert tok.type == 'LBLSIZE_KW'
    tok = lexer.token()
    assert tok.type == 'EQUALS'
    tok = lexer.token()
    return int(tok.value)

################################

if __name__ == '__main__':
    # print _real_re
    lexer = lex.lex()
    data = "LBLSIZE=62 DEDH=1.5 FOO   = 'bar' NEG_PI= -3.1415926 BAR='foo'"
    
    if False:
        lexer.input(data)
        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok)
    else:
        parser = yacc.yacc(start='labels')
        print parser.parse(data).to_byte_string()
