__all__ = ['root', 'current', 'resolve', 'add', 'match_specialization']


from main_grammar import register, validator
from entities import *


__root = Namespace('')
__current = __root


__cur_stack = []


Type('__builtin_va_list', __root, [])
Function('__builtin_va_start', __root)
Function('__builtin_va_end', __root)
Function('__builtin_vsnprintf', __root)
Function('__builtin_memmove', __root)
Function('__builtin_memset', __root)
Function('__builtin_memcmp', __root)
Function('__builtin_memchr', __root)
Function('__builtin_memcpy', __root)
Function('__builtin_strlen', __root)
Function('__builtin_strcmp', __root)
Function('__builtin_expect', __root)
Function('__builtin_alloca', __root)


def enter(into_what):
    global __current
    __cur_stack.append(__current)
    __current = into_what


def leave():
    global __current
    __current = __cur_stack.pop()


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
    | type_id AMPERSAND

-type_or_pointer_type
    = type_or_pointer_type STAR
    | type_id

container
    = NAMESPACE_NAME
    | TEMPLATE_TYPE
    | TYPE

var_id
    = _ASSERT_VAR

const_id
    = _ASSERT_CONST

-type_id
    = _ASSERT_TYPE opt_specialization
    | builtin_type

-builtin_type
    = int_type
    | CHAR
    | SIGNED CHAR
    | UNSIGNED CHAR
    | FLOAT
    | DOUBLE
    | LONG DOUBLE
    | BOOL
    | WCHAR_T

any_path
    = _SEARCH_FROM_ROOT path
    | _SEARCH_FROM_HERE SCOPE path
    | _SEARCH_FROM_HERE

path
    = path SCOPE symbol
    | symbol

""",

#int_type="""
#int_type
#    = INT
#    | UNSIGNED INT
#    | SIGNED INT
#    | LONG INT
#    | UNSIGNED LONG INT
#    | LONG UNSIGNED INT
#    | SIGNED LONG INT
#    | LONG SIGNED INT
#    | LONG LONG INT
#    | UNSIGNED LONG LONG INT
#    | LONG LONG UNSIGNED INT
#    | SIGNED LONG LONG INT
#    | LONG LONG SIGNED INT
#    | UNSIGNED
#    | SIGNED
#    | LONG
#    | UNSIGNED LONG
#    | LONG UNSIGNED
#    | SIGNED LONG
#    | LONG SIGNED
#    | LONG LONG
#    | UNSIGNED LONG LONG
#    | LONG LONG UNSIGNED
#    | SIGNED LONG LONG
#    | LONG LONG SIGNED
#"""
int_type="""
int_type
    = int_attr_list

-int_attr_list
    = int_attr_list int_attr
    | int_attr

-int_attr = SIGNED | UNSIGNED | LONG | SHORT | INT
"""
)
