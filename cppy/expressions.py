from parser import compile_expression


expressions = {
'macro':
    'symbol call?',

# OPERATORS

'arith':
    'addmoddiv|minus|star',

'binop':
    """arith|boolop|comp|open_angle|close_angle|shift
     | bitop|tilde|ampersand|assign_set|assign_update""",

'ref_deref':
    'ampersand|star',

# IDENTIFIERS

'id':
    '(container namespace_member)* symbol',

'id_or_operator':
    '(container namespace_member)* _id_or_operator',

'_id_or_operator':
    """symbol
     | kw_operator
       ( open_paren close_paren
       | open_square close_square
       | ref_deref
       | binop
       | boolop
       )""",

'container':
    'type_spec* symbol template_inst?',

'type_id':
    """(kw_template template_spec)?
       container
       (namespace_member container)*
       template_inst?
       ref_deref*""",

# TEMPLATES

'template_param_spec':
    '(kw_template|kw_typename|kw_class|kw_struct|kw_union)? type_id',

'template_spec':
    """open_angle
       (#template_param:template_param_spec
        (comma #template_param:template_param_spec)*
       )?
       close_angle""",

'template_inst':
    """open_angle
       ( (#template_param:(type_id|expr) comma)*
         #template_param:(type_id|expr)
       )?
       close_angle""",

# TYPECASTING

'typecast':
    'open_paren type_id close_paren',

# LVALUES

'anon_lvalue_access':
    'open_square expr close_square | call',

'raw_lvalue':
    'id (access lvalue|anon_lvalue_access)*',

'call':
    'open_paren expr_list? close_paren',

'array':
    'open_square expr close_square',

'lvalue':
    'star* typecast* raw_lvalue',

'func_call':
    'lvalue call | type_id call',

# DECLARATIONS

'expr_list':
    'expr (comma expr)*',

'core_decl':
    """ref_deref*
       id
       ( call
       | (open_square expr? close_square)?
         (assign_set #initialization:expr)?
       )""",

'param_decl':
    '#type:type_id #id:id (assign_set #initialization:expr)?',

'param_decl_list':
    '#param:param_decl (comma #param:param_decl)*',

'constructor_decl':
    """(kw_template template_spec)?
       symbol
       template_inst?
       open_paren param_decl_list? close_paren
       (colon
        type_id call
        (comma type_id call)*
       )?""",

'destructor_decl':
    'type_spec? tilde symbol open_paren close_paren',

'func_decl':
    """#template_type:(kw_template template_spec)?
       #type:type_id
       #id:id_or_operator
       template_inst?
       open_paren
       param_decl_list?
       close_paren
       type_spec?""",  # final const if present

'var_decl':
    'param_decl (comma core_decl)* semicolon',

# EXPRESSIONS

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
     | star expr1
    """,

'expr2':
    'expr1 (binop expr2)?',

'expr':
    'expr2 (ternary expr colon expr)?',

'c_label':
    'symbol colon',

# STATEMENTS

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
