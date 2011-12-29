from main_grammar import register
# There is a need to address manually the dangling else problem

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
    | WHILE OPEN_PAR
      SEMICOLON expr_list CLOSE_PAR statement
    | compound_statement

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
