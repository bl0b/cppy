from parser import compile_expression


expressions = {
'arith':
    'addmoddiv|minus|star',

'binop':
    'arith|boolop|comp|bitop|assign_set|assign_update',

'template_spec':
    """open_angle
       ((#template_param:qualified_id comma)* qualified_id)?
       close_angle""",

'template_inst':
    """open_angle
       ((#template_param:expr comma)* #template_param:expr)?
       close_angle""",

'simple_typename':
    'type_spec* symbol template_spec?',

'qualified_id':
    '(simple_typename namespace_member)* simple_typename',

'typecast':
    'open_paren qualified_id star* close_paren',

'basic_lvalue':
    'qualified_id (call|array)*',

'member':
    'basic_lvalue (access basic_lvalue)*',

'call':
    'open_paren expr_list close_paren',

'array':
    'open_square expr close_square',

'lvalue':
    'star* typecast* member',

'expr_list':
    'expr (comma expr)*',

'core_decl':
    'star* qualified_id (assign_set #initialization:expr)?',

'param_decl':
    'qualified_id core_decl',

'param_decl_list':
    'param_decl (comma param_decl)*',

'func_decl':
    """qualified_id
       lvalue
       open_paren
       param_decl_list
       close_paren""",

'func_call':
    'lvalue call',

'var_decl':
    '^param_decl (comma core_decl)*',

'immed':
    'minus number | number | string | char',

'new_inst':
    """new qualified_id star* (open_square expr close_square
                              |open_paren expr_list close_paren
                              )""",

'expr1':
    """immed
     | lvalue
     | incdec lvalue
     | lvalue incdec
     | open_paren expr close_paren
     | typecast+ expr1
     | new_inst
     | func_call
    """,

'expr2':
    'expr1 (binop expr1)*',

'expr':
    'expr2 (ternary expr colon expr)?',

#'expr':
#    """immed
#     | lvalue
#     | expr (binop expr)+
#     | incdec lvalue
#     | lvalue incdec
#     | func_call
#     | open_paren expr close_paren
#     | expr ternary expr colon expr""",

'assignment':
    """#lvalue:lvalue
       (#set:assign_set|#update:assign_update)
       #rvalue:expr semicolon""",
}

# Predeclare expressions to handle circular dependencies cleanly

for n in expressions:
    compile_expression('', name=n)

# Now that they all exist in the dictionary, do the actual work

for n, e in expressions.iteritems():
    print "compiling", n, ":", ' '.join(map(str.strip, str(e).splitlines()))
    compile_expression(e, name=n)
