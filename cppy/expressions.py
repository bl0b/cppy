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
    'namespace_member? (container namespace_member)* symbol',

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
    'symbol template_inst?',

'type_id':
    """(kw_template template_spec)?
       (kw_class|kw_struct|kw_union)?
       container
       (namespace_member container)*
       template_inst?""",

# TEMPLATES

'template_param_spec':
    """(kw_template|kw_typename|kw_class|kw_struct|kw_union)?
       type_id (assign_set type_id ref_deref*)?""",

'template_spec':
    """open_angle
       (#template_param:template_param_spec
        (comma #template_param:template_param_spec)*
       )?
       close_angle""",

'template_param_inst':
    '#template_param_inst:(type_id ref_deref*|number)',

'template_inst':
    """open_angle
       ( close_angle
       | template_param_inst (comma template_param_inst)* close_angle
       )""",

# TYPECASTING

'typecast':
    'open_paren (ref_deref|type_spec)* type_id ref_deref* close_paren',

# LVALUES

'anon_lvalue_access':
    'open_square expr close_square | call',

'raw_lvalue':
    '#must_be_var:id (access lvalue|anon_lvalue_access)*',

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
       #id:id
       (open_square close_square)?
        #initialization:( call
                        | (open_square expr number? close_square)?
                        (assign_set expr)?
       )""",

'param_decl':
    """type_spec*
       #param_type:type_id
       ref_deref*
       kw_restrict?
       #param_id:id?
       (open_square number? close_square)?
       (open_square number? close_square)*
       #initialization:(assign_set expr)?""",

'param_decl_list':
    'param_decl (comma param_decl)* (comma ellipsis)?',
    # ellipsis is legal only after a regular parameter (see va_list)

'constructor_decl':
    """(kw_template template_spec)?
       type_id
       template_inst?
       open_paren (kw_void|param_decl_list)? close_paren
       (colon
        type_id call
        (comma type_id call)*
       )?""",

'gcc_attribute':
    """kw_gcc_attr
       open_paren open_paren
       symbol (open_paren string close_paren)?
       close_paren close_paren""",

'destructor_decl':
    """type_spec?
       (type_id namespace_member)?
       tilde
       symbol
       open_paren close_paren""",

'func_decl':
    """kw_extension?
       (type_spec string)?
       #template_type:(kw_template template_spec)?
       type_spec*
       #type:type_id
       ref_deref*
       #id:id_or_operator
       template_inst?
       open_paren
       (kw_void|param_decl_list)?
       close_paren
       type_spec?""",  # final const if present

'var_decl':
    """type_spec*
       #must_be_type:type_id
       ref_deref*
       core_decl
       (comma #decl:core_decl)*
       semicolon""",

# EXPRESSIONS

'immed':
    'minus number | number | string | char',

'new_inst':
    """kw_new type_id ref_deref* (open_square expr close_square
                                 |open_paren expr_list close_paren
                                 )?""",

'expr1':
    """immed
     | lvalue
     | incdec #UPDATE_TARGET:lvalue
     | #UPDATE_TARGET:lvalue incdec
     | open_paren expr close_paren (open_square expr close_square)*
     | typecast+ expr1
     | #CREATION:new_inst
     | #CALL:func_call
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
