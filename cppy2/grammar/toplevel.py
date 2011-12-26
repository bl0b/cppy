toplevel = """
_NAMESPACE_ENTER        = symbol
_FUNC_NAME              = symbol
_LEAVE_SCOPE            =

translation_unit
    =| tl_decl_list

tl_decl_list
    = tl_decl_list tl_decl
    | tl_decl

tl_decl
    = namespace_decl
    | func_decl
    | const_decl
    | var_decl
    | type_decl
    | extern_linkage

sub_translation_unit
    = OPEN_CURLY translation_unit CLOSE_CURLY _LEAVE_SCOPE

namespace_decl
    = NAMESPACE _NAMESPACE_ENTER sub_translation_unit

extern_linkage
    = EXTERN string OPEN_CURLY translation_unit LEAVE_SCOPE
    | EXTERN string var_decl
    | EXTERN string func_decl

func_decl
    = func_compile_spec func_signature opt_body
    | func_signature opt_body

func_compile_spec
    = func_compile_spec func_compile_spec1
    | func_compile_spec1

func_compile_spec1 = INLINE | STATIC | EXTERN

func_signature
    = any_type func_id OPEN_PAR func_param_list_opt CLOSE_PAR

func_id
    = _START_BUILD any_path SCOPE ID _ASSERT_FUNC
    | ID

func_param_list_opt
    =| func_param_list

func_param_list
    = func_param_list COMMA func_param
    | func_param

func_param
    = any_type symbol
    | any_type

opt_body
    = semicolon _LEAVE_SCOPE
    | sub_translation_unit
"""
