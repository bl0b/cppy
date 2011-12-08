from parser import compile_expression


expressions = {
'macro':
    'symbol call?',

# OPERATORS

'arith':
    'addmoddiv|minus|star',

'binop':
    """arith|boolop|comp|open_angle|close_angle|shift
     | bitop|ampersand|assign_set|assign_update""",

'ref_deref':
    'ampersand|star|type_spec',  # can have interleaved const

# IDENTIFIERS

'id':
    'namespace_member? (container namespace_member)* symbol',

#'id':
#    '(container namespace_member)* symbol',

'operator_id':
    """kw_operator
       ( open_paren close_paren
       | open_square close_square
       | ref_deref
       | binop
       | boolop
       | access
       | incdec
       )""",

'typeof':
    'kw_typeof open_paren expr close_paren',

'container':
    'symbol template_inst?',

'type_id':
    """kw_typename?
       (kw_void star+
       |typeof
       |(kw_template template_spec)?
        (kw_class|kw_struct|kw_union)?
        container
        (namespace_member container)*
        template_inst?)""",

'ptr_to_func':
    """type_spec* (kw_void|type_id) ref_deref*
       open_paren (type_id namespace_member)? star #id:symbol? close_paren
       open_paren (kw_void|param_decl_list)? close_paren""",

'ref_to_array':
    """type_spec* (kw_void ref_deref+|type_id ref_deref*)
       open_paren ampersand #id:symbol? close_paren
       open_square expr close_square""",

# TEMPLATES

'template_param_spec':
    """( (kw_template|kw_typename|kw_class|kw_struct|kw_union)
         #template_tid:type_id
       | (kw_template|kw_typename|kw_class|kw_struct|kw_union)
       | #template_vid:(type_id symbol)
       | #template_tid:symbol
       ) (assign_set type_id ref_deref*)?""",

'template_spec':
    """open_angle
       (template_param_spec
        (comma template_param_spec)*
       )?
       close_angle""",

'template_param_inst':
    """#template_param_inst:(type_spec* ref_deref* type_id ref_deref*
                            |expr
                            |type_spec* kw_void ref_deref* type_spec*
                            |type_spec+)
     | open_paren template_param_inst close_paren
    """,

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
    'open_square expr close_square',

'raw_lvalue':
    'id #ACCESS:(access lvalue|anon_lvalue_access)*',

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
       ( call
       | (open_square expr number? close_square)?
         (assign_set #initialization:expr)?
       )""",

'param_decl':
    """ptr_to_func
     | ref_to_array
     | type_spec*
       #type:type_id
       ref_deref*
       #id:id?
       (open_square number? close_square)?
       (open_square number? close_square)*
       #initialization:(assign_set expr)?
       gcc_attribute*""",

'param_decl_list':
    '#param:param_decl (comma #param:param_decl)* (comma ellipsis)?',
    # ellipsis is legal only after a regular parameter (see va_list)

'constructor_decl':
    """(kw_template template_spec)?
       #id:type_id
       template_inst?
       open_paren (kw_void|param_decl_list)? close_paren
       #CTOR:(colon
              #CHECK_EXISTS:id call
              (comma #CHECK_EXISTS:id call)*
             )?""",

'gcc_attribute':
    """kw_gcc_attr
       open_paren open_paren
       symbol (open_paren string close_paren)?
       close_paren close_paren""",

'destructor_decl':
    """type_spec?
       #id:((type_id namespace_member)? tilde symbol)
       open_paren close_paren""",

'func_decl':
    """(type_spec string)?
       #template_type:(kw_template template_spec)?
       ((type_spec? #type:kw_void
        |type_spec*
         #type:type_id
         ref_deref*
        )
        gcc_attribute*
        #id:(id|operator_id)
       |#id_and_type:(kw_operator symbol)
       )
       template_inst?
       open_paren
       (kw_void|param_decl_list)?
       close_paren
       type_spec?""",  # final const if present

'var_decl':
    """(type_spec string)?
       type_spec*
       (#type:type_id ref_deref* core_decl (comma #decl:core_decl)*
       |ref_to_array
       |ptr_to_func)
       gcc_attribute*
       semicolon""",

# EXPRESSIONS

'immed':
    'minus number | number | string | char',

'new_inst':
    """kw_new type_id ref_deref* (open_square expr close_square
                                 |open_paren expr_list close_paren
                                 )?""",

'expr1':
    """#immed:immed
     | #READ:lvalue
     | incdec #UPDATE:lvalue
     | #UPDATE:lvalue incdec
     | open_paren expr close_paren (open_square expr close_square)*
     | #TYPECAST:(typecast+ expr1)
     | #CREATION:new_inst
     | #CALL:func_call
     | #REF:(ampersand expr1)
     | #DEREF:(star expr1)
     | #SIZEOF:(kw_sizeof open_paren type_spec* type_id close_paren)
     | #NEG:(tilde expr1)
    """,

'expr2':
    '#expr2:(expr1 (#op:binop expr1)*)',

'expr':
    'expr2 (ternary expr colon expr)?',

'c_label':
    'symbol colon',

# STATEMENTS

'assignment':
    """#WRITE:lvalue assign_set #rvalue:expr semicolon
     | #UPDATE:lvalue assign_update #rvalue:expr semicolon
    """,
}

# Predeclare expressions to handle circular dependencies cleanly

for n in expressions:
    compile_expression('', name=n)

# Now that they all exist in the dictionary, do the actual work

for n, e in expressions.iteritems():
    #print "compiling", n, ":", ' '.join(map(str.strip, str(e).splitlines()))
    compile_expression(e, name=n)
