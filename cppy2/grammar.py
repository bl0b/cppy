__all__ = ['CppParser']

from jupyLR import Scanner, Automaton
from scanner import cpp_scanner

start_symbol = "CPP"

grammar = """
CPP = cpp_decls

-cpp_decls
    = cpp_decls single_cpp_decl
    | single_cpp_decl

-single_cpp_decl
    = single_decl
    | extern_linkage

extern_linkage
    = kw_extern string single_decl
    | kw_extern string open_curly toplevel_decls close_curly

-toplevel_decls
    = toplevel_decls single_decl
    | single_decl

-single_decl
    = type_decl
    | func_decl
    | var_decl
    | namespace_decl
    | using_decl

var_decl
    = type_spec var_decl_list semicolon

using_decl
    = kw_using qualified_id semicolon
    | kw_using kw_namespace qualified_id semicolon

namespace_decl
    = namespace_enter toplevel_decls namespace_leave
    | namespace_enter namespace_leave

namespace_enter
    = kw_namespace symbol gcc_attribute open_curly
    | kw_namespace symbol open_curly

namespace_leave
    = close_curly

gcc_attribute
    = kw_attribute open_paren open_paren
      gcc_attribute_contents close_paren close_paren

-gcc_attribute_contents
    = symbol
    | symbol open_paren gcc_attr_param_list close_paren

-gcc_attr_param_list
    = gcc_attr_param_list comma gcc_attr_param
    | gcc_attr_param

gcc_attr_param
    = string
    | number

-type_decl
    = typedef
    | complex_type_decl semicolon
    | complex_type_decl var_decl_list semicolon

var_decl_list
    = var_decl_list comma single_var_decl
    | single_var_decl

single_var_decl
    = qualified_id array_spec
    | qualified_id

array_spec
    = array_spec open_square expr close_square
    | open_square expr close_square

expr
    = qualified_id
    | number
    | binexpr
    | minus expr
    | open_paren expr close_paren

-complex_type_decl
    = struct_type_decl
    | template_type_decl

template_type_decl
    = abstract_template struct_type_decl

abstract_template
    = kw_template inf template_param_decl_list sup
    | kw_template inf sup

struct_type_decl
    = struc_decl_enter toplevel_decls struc_decl_leave
    | struc_decl_enter struc_decl_leave
    | struc_ref

struc_ref
    = kw_struc qualified_id
    | kw_union qualified_id
    | kw_class qualified_id

struc_decl_enter
    = kw_struct qualified_id open_curly
    | kw_struct open_curly
    | kw_union qualified_id open_curly
    | kw_union open_curly
    | kw_class qualified_id open_curly
    | kw_class open_curly

struc_decl_leave
    = close_curly

-template_param_decl_list
    = template_param_decl_list comma template_param_decl
    | template_param_decl

-template_param_inst_list
    = template_param_inst_list comma template_param_inst
    | template_param_inst

-template_param_decl
    = template_param assign type_spec
    | template_param

template_param
    = template_param_type symbol assign type_spec
    | template_param_type symbol

-template_param_type
    = kw_typename
    | kw_class
    | kw_struct
    | kw_bool
    | int_type

template_param_inst
    = qualified_id
    | expr
    | type_spec

typedef
    = kw_typedef type_spec qualified_id semicolon

-type_spec
    = type_id ampersand
    | type_id deref
    | complex_type_decl
    | type_id

-deref
    = deref star
    | star

type_id
    = qualified_id
    | qualified_id inf template_param_inst_list sup
    | int_type
    | kw_float
    | kw_char
    | kw_double
    | kw_bool

int_type
    = kw_int
    | kw_unsigned kw_int
    | kw_signed kw_int
    | kw_long kw_int
    | kw_unsigned kw_long kw_int
    | kw_long kw_unsigned kw_int
    | kw_signed kw_long kw_int
    | kw_long kw_signed kw_int
    | kw_long kw_long kw_int
    | kw_unsigned kw_long kw_long kw_int
    | kw_long kw_long kw_unsigned kw_int
    | kw_signed kw_long kw_long kw_int
    | kw_long kw_long kw_signed kw_int
    | kw_unsigned
    | kw_signed
    | kw_long
    | kw_unsigned kw_long
    | kw_long kw_unsigned
    | kw_signed kw_long
    | kw_long kw_signed
    | kw_long kw_long
    | kw_unsigned kw_long kw_long
    | kw_long kw_long kw_unsigned
    | kw_signed kw_long kw_long
    | kw_long kw_long kw_signed

qualified_id
    = namespace_member _qid
    | _qid

-_qid
    = _qid namespace_member id
    | id

-id = symbol template_params
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
    | type_spec

"""
