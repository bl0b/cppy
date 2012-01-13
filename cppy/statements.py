from main_grammar import register, validator
from entities import Scope
import id_engine
# There is a need to address manually the dangling else problem


class Statement(object):
    pass


class CondStatement(Statement):
    pass


class LoopStatement(Statement):
    pass


class JumpStatement(Statement):
    pass


class ExprStatement(Statement):
    pass


@validator
def _ENTER_LOCAL_SCOPE(ast):
    ret = Scope(None, id_engine.current())
    id_engine.enter(ret)
    return tuple()


def _LEAVE_LOCAL_SCOPE(ast):
    id_engine.leave()
    return tuple()


register(statements="""
_ENTER_LOCAL_SCOPE = OPEN_CURLY
_LEAVE_LOCAL_SCOPE = CLOSE_CURLY

condition
    = OPEN_PAR expr CLOSE_PAR

statement
    = SEMICOLON
    | BREAK SEMICOLON
    | CONTINUE SEMICOLON
    | FOR OPEN_PAR expr_list SEMICOLON expr_list
    | IF condition statement
    | IF condition statement ELSE statement
    | SWITCH OPEN_PAR expr CLOSE_PAR compound_statement SEMICOLON
    | label
    | RETURN expr SEMICOLON
    | WHILE OPEN_PAR
      SEMICOLON expr_list CLOSE_PAR statement
    | compound_statement
    | var_decl
    | static_var_decl
    | _ASSERT_FUNC call SEMICOLON

label
    = symbol COLON

compound_statement
    = _ENTER_LOCAL_SCOPE opt_statement_list _LEAVE_LOCAL_SCOPE

opt_statement_list
    =| statement_list

statement_list
    = statement_list statement
    | statement
""")
