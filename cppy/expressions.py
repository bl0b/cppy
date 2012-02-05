from main_grammar import register, validator
# see http://en.cppreference.com/w/cpp/language/operator_precedence
import id_engine

from entities import Int, UnsignedInt, LongInt, UnsignedLongInt, LongLongInt

from entities import UnsignedLongLongInt, Const
from operations import *


@validator
def int_const(ast):
    enc, val, ofs = ast[1]
    val = val.upper()
    if val.endswith('U'):
        cls = UnsignedInt
        sfx = -1
    elif val.endswith('UL'):
        cls = UnsignedLongInt
        sfx = -2
    elif val.endswith('ULL'):
        cls = UnsignedLongLongInt
        sfx = -3
    elif val.endswith('LL'):
        cls = LongLongInt
        sfx = -2
    elif val.endswith('L'):
        cls = LongInt
        sfx = -1
    else:
        cls = Int
        sfx = len(val)
    if enc == 'int_hex':
        base = 16
    elif enc == 'int_oct':
        base = 8
    elif enc == 'int_dec':
        base = 10
    return Const(None, None, cls, int(val[:sfx], base))


@validator
def expr_list(ast):
    if len(ast) == 2:
        return (ast[1],)
    return ast[1] + (ast[3],)


@validator
def call(ast):
    if len(ast) == 4:
        return ('call', ast[2])
    return ('call', tuple())


@validator
def typeid(ast):
    return Entity.Null


@validator
def cpp_cast(ast):
    return Entity.Null


def binop(cls, ast):
    return cls(ast[2][1], ast[1], ast[3])


@validator
def expr_0(ast):
    # always the sub-expression grouping.
    return ast[2]


@validator
def expr_p1(ast):
    id = ast[-1]
    spec = len(id) == 3 and id[-1] or None
    print
    print "EXPR_P1", len(ast), ast, id[1][1]
    if len(ast) == 2:
        what = id_engine.resolve(id[1][1], False)
    elif len(ast) == 3:
        what = id_engine.root().resolve(id[1][1], False)
    else:
        what = ast[1].resolve(id[1][1], True)
    if spec:
        return what.match_specialization(spec)
    else:
        return what


def unop(cls, ast):
    return cls(ast[1][1], ast[2])


@validator
def expr_p2(ast):
    if len(ast) == 2:
        return ast[1]
    if ast[-1][0] == 'INC':
        return unop(Inc, ast)
    elif ast[-1][0] == 'DEC':
        return unop(PostDec, ast)
    elif ast[-1][0] == 'subscript':
        return Subscript(ast[1], ast[2][1])
    elif ast[-1][0] == 'call':
        return Call(ast[1], ast[2][1])
    if ast[-2][0] == 'DOT':
        return DotAccess(ast[1], ast[3])
    elif ast[-2][0] == 'ARROW':
        return ArrowAccess(ast[1], ast[3])


@validator
def expr_p3(ast):
    k = ast[1][0]
    if k == 'INC':
        return unop(Inc, ast)
    elif k == 'DEC':
        return unop(Dec, ast)
    elif k == 'PLUS':
        return ast[2]
    elif k == 'MINUS':
        return unop(Minus, ast)
    elif k == 'EXCLAMATION':
        return unop(BitOp, ast)
    elif k == 'OPEN_PAR':
        return Cast(ast[2], ast[4])


@validator
def expr_p4(ast):
    # TODO!
    raise Exception("Unhandled arrow/dot -star operator")
    return binop(Arithmetic, ast)


@validator
def expr_p5(ast):
    return binop(Arithmetic, ast)


@validator
def expr_p6(ast):
    return binop(Arithmetic, ast)


@validator
def expr_p7(ast):
    return binop(Arithmetic, ast)


@validator
def expr_p8(ast):
    return binop(Comparison, ast)


@validator
def expr_p9(ast):
    return binop(Comparison, ast)


@validator
def expr_p10(ast):
    return binop(BitOp, ast)


@validator
def expr_p11(ast):
    return binop(BitOp, ast)


@validator
def expr_p12(ast):
    return binop(BitOp, ast)


@validator
def expr_p13(ast):
    return binop(BitOp, ast)


@validator
def expr_p14(ast):
    return binop(BitOp, ast)


@validator
def expr_p16(ast):
    if ast[2][0] == 'ASS_OP':
        return binop(AssignUpdate, ast)
    return binop(AssignSet, ast)


register(expr_grammar="""
typeid = TYPEID OPEN_PAR type_id CLOSE_PAR
cpp_cast = cast_op INF type_id SUP
cast_op = CONST_CAST | DYNAMIC_CAST | STATIC_CAST | REINTERPRET_CAST

int_const = int_dec | int_oct | int_hex
float_const = number

-expr_0
    = int_const
    | float_const
    | string
    | char
    | expr_p1
expr_0
    = OPEN_PAR expr_any CLOSE_PAR

expr_p1
    = expr_p1 SCOPE id
    | id
    | SCOPE id

id  = symbol opt_specialization

-expr_p2 = expr_0
expr_p2
    = expr_p2 INC
    | expr_p2 DEC
    | expr_p2 subscript
    | expr_p2 call
    | field_resolution
    | typeid
    | cpp_cast call

field_resolution
    = dot_arrow expr_p1

dot_arrow
    = expr_p2 DOT
    | expr_p2 ARROW

subscript
    = OPEN_SQ expr CLOSE_SQ
    | OPEN_SQ CLOSE_SQ

call
    = OPEN_PAR expr_list CLOSE_PAR
    | OPEN_PAR CLOSE_PAR

-expr_p3 = expr_p2
expr_p3
    = INC expr_p3
    | DEC expr_p3
    | PLUS expr_p3
    | MINUS expr_p3
    | EXCLAMATION expr_p3
    | TILDE expr_p3
    | OPEN_PAR type_id CLOSE_PAR expr_p3
    | STAR expr_p3
    | AMPERSAND expr_p3
    | SIZEOF OPEN_PAR any_type CLOSE_PAR
    | NEW expr_p3
    | DELETE expr_p3
    | DELETE OPEN_SQ CLOSE_SQ expr_p3

-expr_p4 = expr_p3
expr_p4
    = expr_p4 DOT_STAR id
    | expr_p4 ARROW_STAR id

-expr_p5 = expr_p4
expr_p5
    = expr_p5 STAR expr_p4
    | expr_p5 SLASH expr_p4
    | expr_p5 PERCENT expr_p4

-expr_p6 = expr_p5
expr_p6
    = expr_p6 PLUS expr_p5
    | expr_p6 MINUS expr_p5

-expr_p7 = expr_p6
expr_p7
    = expr_p7 SHR expr_p6
    | expr_p7 SHL expr_p6

-expr_p8 = expr_p7
expr_p8
    = expr_p8 INF expr_p7
    | expr_p8 LE expr_p7
    | expr_p8 SUP expr_p7
    | expr_p8 GE expr_p7

-expr_p9 = expr_p8
expr_p9
    = expr_p9 EQ expr_p8
    | expr_p9 NE expr_p8

-expr_p10 = expr_p9
expr_p10 = expr_p10 AMPERSAND expr_p9

-expr_p11 = expr_p10
expr_p11 = expr_p11 CIRCONFLEX expr_p10

-expr_p12 = expr_p11
expr_p12 = expr_p12 PIPE expr_p11

-expr_p13 = expr_p12
expr_p13 = expr_p13 LOG_AND expr_p12

-expr_p14 = expr_p13
expr_p14 = expr_p14 LOG_OR expr_p13

-expr_p15 = expr_p14
expr_p15 = expr_p14 QUESTION expr_p15 COLON expr_p15
expr_p15 = expr_p14 QUESTION expr_p17 COLON expr_p15
expr_p15 = expr_p14 QUESTION expr_p15 COLON expr_p17

-expr_p16 = expr_p15
expr_p16
    = expr_p15 EQUAL expr_p16
    | expr_p15 ASS_OP expr_p16

-expr_p17 = expr_p16
expr_p17 = THROW expr_p16

-expr_p18 = expr_p17
-expr_p18 = expr_p16
expr_p18 = expr_p18 COMMA expr_p17

-expr_no_comma = expr_p17
-expr_any = expr_p18
-expr = expr_p16

-expr_list_opt
    = expr_list
    |

expr_list
    = expr_list COMMA expr_no_comma
    | expr_no_comma
""")
