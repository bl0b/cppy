__all__ = ['cpp_scanner']
from jupyLR import Scanner
from itertools import imap


num = r"(?:\.[0-9]+|(?:[0-9]+)(?:\.[0-9]*)?)"
expo = r"(?:[eE]-?[0-9]+\.?[0-9]*)?[uUlLdf]*"
number = num + expo

hexnum = "0x[0-9a-fA-F]+[lLuU]*"

keywords = [
    'switch', 'class', 'while', 'do', 'for', 'typedef', 'if', 'else', 'struct',
    'union', 'return', 'namespace', 'new', 'delete', 'operator', 'typename',
    'template', 'throw', 'using', '__restrict', '__extension', '__attribute__',
    'void', 'inline', 'sizeof', 'enum', '__typeof', '__typeof__', 'typename',
    'const', '__const', 'static', 'register', 'volatile', 'virtual', 'extern',
    'long', 'short', 'signed', 'unsigned', 'friend', 'public', 'private',
    'protected', 'int', 'float', 'double', 'char', 'bool', 'this', 'wchar_t',
]


def kw_to_dic(kw):
    raw_kw = kw
    if kw.startswith('__'):
        kw = kw[2:]
    if kw.endswith('__'):
        kw = kw[:-2]
    return kw.upper(), raw_kw

kw_dic = {}

for kw in keywords:
    name, value = kw_to_dic(kw)
    if name in kw_dic:
        kw_dic[name] += '|'
    else:
        kw_dic[name] = ''
    kw_dic[name] += value

for k, v in kw_dic.iteritems():
    kw_dic[k] = r'\b(?:%s)\b' % v


misc = dict(PLUS='+', MINUS='-', STAR='*', SLASH='/',
            INF='<', SUP='>',
            AMPERSAND='&', PIPE='|', TILDE='~', CIRCONFLEX='^',
            EXCLAMATION='!',
            SHL='<<', SHR='>>',
            ASS_ADD='+=', ASS_SUB='-=', ASS_MUL='*=', ASS_DIV='/=',
            ASS_MOD='%=',
            LE='<=', GE='>=', EQ='==', NE='!=',
            LOG_AND="&&", LOG_OR="||",
            ASS_SHL='<<=', ASS_SHR='>>=',
            COMMA=',',
            EQUAL='=',
            COLON=':',
            SCOPE='::',
            SEMICOLON=';',
            OPEN_PAR='(',
            CLOSE_PAR=')',
            OPEN_CURLY='{',
            CLOSE_CURLY='}',
            PERCENT='%',
            OPEN_SQ='[',
            CLOSE_SQ=']',
            ELLIPSIS='...',
            DOT='.',
            ARROW='->',
            ARROW_STAR='->*',
            DOT_STAR='.*',
            QUESTION='?',
           )

one_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 1)
two_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 2)
three_char = dict((k, v) for k, v in misc.iteritems() if len(v) == 3)


def escape(c):
    return c == '^' and r'\^' or c


for k, op in one_char.iteritems():
    #asserts = filter_asserts(op, two_char)
    #asserts += filter_asserts(op, three_char)
    #tokens[k] = mk_op_re(op, asserts)
    one_char[k] = '[%s]' % ']['.join(imap(escape, op))

for k, op in two_char.iteritems():
    #tokens[k] = mk_op_re(op, filter_asserts(op, three_char))
    two_char[k] = '[%s]' % ']['.join(imap(escape, op))

for k, op in three_char.iteritems():
    #tokens[k] = mk_op_re(op, filter_asserts(op, three_char))
    three_char[k] = '[%s]' % ']['.join(imap(escape, op))

#tokens.update(three_char)

#tokens['number'] = number
#tokens['symbol'] = symbol_assert + r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'

discard_them_all = ['RESTRICT', 'CONST']

cpp_scanner = Scanner(**kw_dic).add(**three_char) \
                .add(**two_char).add(**one_char) \
                .add(symbol=r'\b[a-zA-Z_][a-zA-Z0-9_]*\b') \
                .add(hex=hexnum).add(number=number) \
                .add(string=r'"(?:\\["bntr]|[^\\"])*"') \
                .add(char=r"'(?:\\['bntr\\]|[^\\'])'") \
                .add(ws='[ \t\n]+', discard_names=('ws',)) \
                .add(discard_names=discard_them_all)
