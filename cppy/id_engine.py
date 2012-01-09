__all__ = ['root', 'current', 'resolve', 'add', 'match_specialization']


from main_grammar import register, validator
from entities import *


__builtins = Namespace('#builtins#')

__root = Namespace('', __builtins)
__current = __root


__cur_stack = []


Type('__builtin_va_list', __builtins)
Function('__builtin_va_start', __builtins)
Function('__builtin_va_end', __builtins)
Function('__builtin_vsnprintf', __builtins)
Function('__builtin_memmove', __builtins)
Function('__builtin_memset', __builtins)
Function('__builtin_memcmp', __builtins)
Function('__builtin_memchr', __builtins)
Function('__builtin_memcpy', __builtins)
Function('__builtin_strlen', __builtins)
Function('__builtin_strcmp', __builtins)
Function('__builtin_expect', __builtins)
Function('__builtin_alloca', __builtins)


def enter(into_what):
    global __current
    __cur_stack.append(__current)
    __current = into_what
    print "ENTER", __cur_stack, __current


def leave():
    global __current
    __current = __cur_stack.pop()
    print "LEAVE", __cur_stack


def current():
    global __current
    return __current


def root():
    global __root
    return __root


def resolve(what, local=True):
    global __current
    return __current.resolve(what, local)


def add(what):
    global __current
    return __current.add(what)


def match_specialization(*a, **kw):
    global __current
    return __current.match_specialization(*a, **kw)


@validator
def _SEARCH_FROM_HERE(ast):
    print "Searching from", __current,
    return __current.resolve(ast[1][1], False)


@validator
def _SEARCH_FROM_ROOT(ast):
    return __root


@validator
def _ASSERT_VAR(ast):
    return ast[1].is_var and ast[1] or None


@validator
def _ASSERT_TYPE(ast):
    return ast[1].is_type and ast[1] or None


@validator
def _ASSERT_CONST(ast):
    return ast[1].is_const and ast[1] or None


@validator
def _ASSERT_TEMPLATE_TYPE(sym):
    return ast[1].is_template and ast[1] or None


@validator
def _ASSERT_FUNC(ast):
    return ast[1].is_function and ast[1] or None


@validator
def path(ast):
    scope = ast[1]
    if len(ast) == 2:
        return scope
    sym = ast[3][1]
    return scope.resolve(sym)


@validator
def any_path(ast):
    scope = ast[1]
    if len(ast) == 2:
        return scope
    sym = ast[2][1]
    return scope.resolve(sym, True)


@validator
def builtin_type(ast):
    if ast[1][0] == 'int_type':
        label = 'int-like'
    else:
        label = ast[-1][1] + '-like'
    ret = Type(label, None, None)
    print ret
    return ret


@validator
def type_id(ast):
    print ast
    if len(ast) == 2:
        return ast[1]  # that is a type object
    else:
        pass


@validator
def type_or_pointer_type(ast):
    return PointerTo(ast[1])


@validator
def ref_to_type(ast):
    return ReferenceTo(ast[1])


@validator
def builtin_Bool(ast):
    return Bool


@validator
def builtin_Wchar_t(ast):
    return Wchar_t


@validator
def builtin_UnsignedChar(ast):
    return UnsignedChar


@validator
def builtin_Char(ast):
    return Char


@validator
def builtin_LongDouble(ast):
    return LongDouble


@validator
def builtin_Double(ast):
    return Double


@validator
def builtin_Float(ast):
    return Float


@validator
def builtin_UnsignedLongLongInt(ast):
    return UnsignedLongLongInt


@validator
def builtin_UnsignedLongInt(ast):
    return UnsignedLongInt


@validator
def builtin_LongLongInt(ast):
    return LongLongInt


@validator
def builtin_LongInt(ast):
    return LongInt


@validator
def builtin_UnsignedShortInt(ast):
    return UnsignedShortInt


@validator
def builtin_ShortInt(ast):
    return ShortInt


@validator
def builtin_Int(ast):
    return Int


register(id_grammar="""
_ASSERT_VAR   = any_path
_ASSERT_TYPE  = any_path
_ASSERT_CONST = any_path
_ASSERT_FUNC  = any_path
_ASSERT_TEMPLATE_TYPE = INF
_SEARCH_FROM_ROOT = SCOPE
_SEARCH_FROM_HERE = symbol

ID             = symbol
OPT_ID         =| symbol
NAMESPACE_NAME = symbol
TEMPLATE_TYPE  = symbol _ASSERT_TEMPLATE_TYPE template_expr_list SUP
TYPE           = symbol

template_expr_list
    = template_expr_list COMMA template_expr
    | template_expr

template_expr
    = any_type
    | expr

-any_type
    = type_or_pointer_type
    | ref_to_type

ref_to_type
    = type_id AMPERSAND

type_or_pointer_type
    = type_or_pointer_type STAR

-type_or_pointer_type
    = type_id
    | builtin_type

container
    = NAMESPACE_NAME
    | TEMPLATE_TYPE
    | TYPE

var_id
    = _ASSERT_VAR

const_id
    = _ASSERT_CONST

type_id
    = _ASSERT_TYPE opt_specialization
    | builtin_type

-builtin_type
    = builtin_Int
    | builtin_ShortInt
    | builtin_UnsignedShortInt
    | builtin_LongInt
    | builtin_LongLongInt
    | builtin_UnsignedLongInt
    | builtin_UnsignedLongLongInt
    | builtin_Float
    | builtin_Double
    | builtin_LongDouble
    | builtin_Char
    | builtin_UnsignedChar
    | builtin_Bool
    | builtin_Wchar_t

builtin_Int
    = INT
    | SIGNED
    | SIGNED INT

builtin_ShortInt
    = SHORT
    | SIGNED SHORT
    | SHORT SIGNED
    | SHORT INT
    | SIGNED SHORT INT
    | SHORT SIGNED INT

builtin_UnsignedShortInt
    = UNSIGNED SHORT
    | UNSIGNED SHORT INT

builtin_LongInt
    = LONG
    | LONG INT
    | SIGNED LONG
    | SIGNED LONG INT

builtin_LongLongInt
    = LONG LONG
    | LONG LONG INT
    | SIGNED LONG LONG
    | SIGNED LONG LONG INT

builtin_UnsignedLongInt
    = UNSIGNED LONG
    | UNSIGNED LONG INT

builtin_UnsignedLongLongInt
    = UNSIGNED LONG LONG
    | UNSIGNED LONG LONG INT

builtin_Float
    = FLOAT

builtin_Double
    = DOUBLE

builtin_LongDouble
    = LONG DOUBLE

builtin_Char
    = CHAR
    | SIGNED CHAR

builtin_UnsignedChar
    = UNSIGNED CHAR

builtin_Wchar_t
    = WCHAR_T

builtin_Bool
    = BOOL

any_path
    = _SEARCH_FROM_ROOT path
    | _SEARCH_FROM_HERE SCOPE path
    | _SEARCH_FROM_HERE

path
    = path SCOPE symbol
    | symbol

""")
