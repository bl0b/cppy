from parser import compile_expression


expressions = {
'arith':
    'addmoddiv|minus|star',

'binop':
    """arith|boolop|comp|open_angle|close_angle|shift
     | bitop|assign_set|assign_update""",

'id':
    '(container namespace_member)* symbol',

'id_or_operator':
    '(container namespace_member)* _id_or_operator',

'_id_or_operator':
    """symbol
     | kw_operator
       ( open_paren close_paren
       | open_square close_square
       | arith
       | boolop
       )""",

'container':
    'type_spec* symbol template_inst?',

'type_id':
    """(kw_template template_spec)?
       container
       (namespace_member container)*
       template_spec?""",

'template_spec':
    """open_angle
       ((#template_param:type_id comma)* id)?
       close_angle""",

'template_inst':
    """open_angle
       ((#template_param:expr comma)* #template_param:expr)?
       close_angle""",

'typecast':
    'open_paren type_id (ampersand|star*) close_paren',

'anon_lvalue_access':
    'open_square expr close_square | call',

'raw_lvalue':
    'id (access lvalue|anon_lvalue_access)*',

'call':
    'open_paren expr_list close_paren',

'array':
    'open_square expr close_square',

'lvalue':
    'star* typecast* raw_lvalue',

'expr_list':
    'expr (comma expr)*',

'core_decl':
    'star* id (assign_set #initialization:expr)?',

'param_decl':
    'id core_decl',

'param_decl_list':
    'param_decl (comma param_decl)*',

'func_decl':
    """type_id
       id_or_operator
       template_inst?
       open_paren
       param_decl_list
       close_paren""",

'func_call':
    'lvalue call',

'var_decl':
    '^param_decl (comma core_decl)* semicolon',

'immed':
    'minus number | number | string | char',

'new_inst':
    """kw_new type_id star* (open_square expr close_square
                         |open_paren expr_list close_paren
                         )?""",

'expr1':
    """immed
     | lvalue
     | incdec lvalue
     | lvalue incdec
     | open_paren expr close_paren
     | typecast+ expr1
     | new_inst
     | func_call
     | ampersand expr1
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
    #print "compiling", n, ":", ' '.join(map(str.strip, str(e).splitlines()))
    compile_expression(e, name=n)
