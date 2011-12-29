from main_grammar import register
# see http://en.cppreference.com/w/cpp/language/operator_precedence

register(expr_grammar="""
_MARK_UPD=
_MARK_READ=
_MARK_SET=
_MARK_CAST=
_COMMIT_CAST=

typeid = TYPEID OPEN_PAR type_id CLOSE_PAR
cpp_cast = cast_op INF type_id SUP
cast_op = CONST_CAST | DYNAMIC_CAST | STATIC_CAST | REINTERPRET_CAST

-expr_0
    = var_id
    | const_id
    | number
    | string
    | char
    | OPEN_PAR expr_any CLOSE_PAR

-expr_p2 = expr_0
expr_p2
    = expr_p2 INC _MARK_UPD
    | expr_p2 DEC _MARK_UPD
    | expr_p2
    | expr_p2 subscript _MARK_READ
    | expr_p2 DOT _MARK_READ field_id
    | expr_p2 ARROW _MARK_READ field_id
    | typeid
    | cpp_cast _MARK_CAST call _RESOLVE_CAST

-expr_p3 = expr_p2
expr_p3
    = INC expr_p3
    | DEC expr_p3
    | PLUS expr_p3
    | MINUS expr_p3
    | EXCLAMATION expr_p3
    | TILDE expr_p3
    | OPEN_PAR type_id CLOSE_PAR _MARK_CAST expr_p3 _COMMIT_CAST
    | STAR expr_p3
    | AMPERSAND expr_p3
    | SIZEOF OPEN_PAR type_id CLOSE_PAR
    | NEW expr_p3
    | DELETE expr_p3
    | DELETE OPEN_SQ CLOSE_SQ expr_p3

-expr_p4 = expr_p3
expr_p4
    = expr_p4 DOT_STAR field_id
    | expr_p4 ARROW_STAR field_id

-expr_p5 = expr_p4
expr_p5
    = expr_p5 STAR expr_p4
    | expr_p5 SLASH expr_p4
    | expr_p5 PERCENT expr_p4

-expr_p6  expr_p5
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
    = expr_p15 EQUAL _MARK_SET expr_p16
    | expr_p15 ASS_ADD _MARK_UPD expr_p16
    | expr_p15 ASS_SUB _MARK_UPD expr_p16
    | expr_p15 ASS_MUL _MARK_UPD expr_p16
    | expr_p15 ASS_DIV _MARK_UPD expr_p16
    | expr_p15 ASS_MOD _MARK_UPD expr_p16
    | expr_p15 ASS_SHR _MARK_UPD expr_p16
    | expr_p15 ASS_SHL _MARK_UPD expr_p16
    | expr_p15 ASS_AND _MARK_UPD expr_p16
    | expr_p15 ASS_OR  _MARK_UPD expr_p16
    | expr_p15 ASS_XOR _MARK_UPD expr_p16

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

-expr_list
    = expr_list COMMA expr_no_comma
    | expr_no_comma
""")
