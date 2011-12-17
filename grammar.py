from jupyLR import Scanner, Automaton

start_symbol = "CPP"

grammar = """
CPP = toplevel_decls

-toplevel_decls
    = toplevel_decls single_decl
    | single_decl

-single_decl
    = type_decl
    | func_decl
    | var_decl
    | namespace_decl

-type_decl
    = typedef
-type_decl
    = struct_decl


typedef
    = kw_typedef type_spec id semicolon

-type_spec
    = type_id ampersand
    | type_id deref
    | type_id

-deref
    = deref star
    | star

type_id
    = qualified_id template_params
    | int_type
    | kw_float
    | kw_char
    | kw_double

-int_type
    = kw_unsigned int_type
    | kw_signed int_type
    | kw_long int_type
    | kw_int
    | kw_unsigned
    | kw_long

qualified_id
    = namespace_member _qid
    | _qid

-_qid
    = _qid namespace_member id
    | id

id  = symbol template_params
    | symbol

template_params
    = inf template_expr_list sup
    | inf sup

-template_expr_list
    = template_expr_list comma template_expr
    | template_expr

template_expr
    = kw_typename symbol
    | kw_class symbol
    | kw_struct symbol
    | kw_union symbol
    | kw_template symbol

"""
