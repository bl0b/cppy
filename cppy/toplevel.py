from main_grammar import register, validator
#from id_engine import current
import id_engine
from entities import Type, Namespace, TemplateType


@validator
def typedef(ast):
    sym = ast[-2][1]
    typ = ast[-3]
    ret = Type(sym, id_engine.current, typ)
    print id_engine.current
    return ret


@validator
def int_type(ast):
    return Type('', None, tuple(x[1] for x in ast[1:]))


@validator
def _NAMESPACE_ENTER(ast):
    sym = ast[1][1]
    n = id_engine.current.resolve(sym, True)
    print "enter namespace ?", n
    if n is None:
        n = Namespace(sym, id_engine.current)
        print "new namespace !", n
    id_engine.current = n
    print "root :", id_engine.root_namespace
    return id_engine.current


@validator
def gcc_attribute(ast):
    return tuple()


@validator
def template_type_decl_prefix(ast):
    free_params = []
    for x in ast[1:]:
        if x[0] == 'symbol':
            sym = x[1]
        if x[0] == 'template_param_decl':
            free_params.append(x[1:])
    return TemplateType(sym, id_engine.current, {
        'free_params': free_params,
        'bound_params': []
    })


@validator
def specialization_decl(ast):
    tt = ast[1]
    print "TODO : match_specialization !"
    return tt


@validator
def _FORWARD_DECL(ast):
    id_engine.current = id_engine.current.owner
    return ast


@validator
def _LEAVE_SCOPE(ast):
    id_engine.current = id_engine.current.owner
    return ast


@validator
def using_decl(ast):
    if type(ast[2]) is tuple and ast[2][0] == 'NAMESPACE':
        print "TODO ! import namespace"
    else:
        what = ast[2]
        id_engine.current.contents[what.name] = what
    return tuple()


register(
toplevel="""
_NAMESPACE_ENTER        = symbol
_FUNC_NAME              = symbol
_LEAVE_SCOPE            = CLOSE_CURLY
_MARK_STRUC             = s_c_u OPT_ID
TEMPLATE_TYPE           = _STRUC_ENTER            =
_STRUC_LEAVE            =
-s_c_u                  = CLASS | STRUCT | UNION


translation_unit
    =| tl_decl_list

-tl_decl_list
    = tl_decl_list tl_decl
    | tl_decl

-tl_decl
    = namespace_decl
    | func_decl
    | const_decl
    | var_decl
    | type_decl
    | extern_linkage
    | using_decl

using_decl
    = USING NAMESPACE any_path SEMICOLON
    | USING any_path SEMICOLON

sub_translation_unit
    = OPEN_CURLY translation_unit _LEAVE_SCOPE

namespace_decl
    = NAMESPACE _NAMESPACE_ENTER gcc_attribute_opt sub_translation_unit

gcc_attribute_opt
    =| gcc_attribute

extern_linkage
    = EXTERN string OPEN_CURLY translation_unit LEAVE_SCOPE
    | EXTERN string var_decl
    | EXTERN string func_decl
""",

func_decl="""
func_decl
    = func_compile_spec func_signature opt_body
    | func_signature opt_body

func_compile_spec
    = func_compile_spec func_compile_spec1
    | func_compile_spec1

func_compile_spec1 = INLINE | STATIC | EXTERN

func_signature
    = any_type func_id OPEN_PAR func_param_list_opt CLOSE_PAR

func_ptr_signature
    = any_type OPEN_PAR opt_type STAR OPT_ID CLOSE_PAR
      OPEN_PAR func_param_list_opt CLOSE_PAR

opt_type
    =| type_id

func_id
    = _ASSERT_FUNC
    | ID

func_param_list_opt
    =| func_param_list

func_param_list
    = func_param_list COMMA func_param
    | func_param

func_param
    = any_type symbol
    | any_type
    | func_ptr_signature

opt_body
    = _FORWARD_DECL
    | compound_statement
""",

var_const_decl="""
const_decl
    = CONST type_id symbol EQUAL expr SEMICOLON

var_decl
    = type_id var_decl_list SEMICOLON
    | func_ptr_signature SEMICOLON

-var_decl_list
    = var_decl_list COMMA single_var_decl
    | single_var_decl

single_var_decl
    = single_var opt_var_init

single_var
    = AMPERSAND symbol
    | symbol
    | stars symbol

-opt_init
    =| EQUAL var_init

var_init
    = expr
    | OPEN_CURLY var_init_list CLOSE_CURLY

-var_init_list
    = var_init_list COMMA var_init
    | var_init

-stars
    = stars STAR
    | STAR
""",

type_decl="""
_FORWARD_DECL = SEMICOLON

-type_decl
    = typedef
    | struc_type_decl opt_var_decl_list SEMICOLON
    | template_type_decl

-opt_var_decl_list
    =| var_decl_list

typedef
    = TYPEDEF struc_type_decl symbol SEMICOLON
    | TYPEDEF any_type symbol SEMICOLON

struc_type_decl
    = _MARK_STRUC opt_struc_body

template_type_decl_prefix
    = TEMPLATE INF opt_template_param_decl_list SUP s_c_u symbol

specialization_decl
    = template_type_decl_prefix template_specialization

-template_type_decl_base
    = template_type_decl_prefix
    | specialization_decl

template_type_decl
    = template_type_decl_base _FORWARD_DECL
    | template_type_decl_base OPEN_CURLY translation_unit _LEAVE_SCOPE

-opt_template_param_decl_list
    =| template_param_decl_list

-template_param_decl_list
    = template_param_decl_list COMMA template_param_decl
    | template_param_decl

template_param_decl
    = tp_kw symbol opt_tp_default

-opt_tp_default
    =| EQUAL template_param_inst

-tp_kw = TYPENAME | CLASS | STRUCT | UNION | int_type

-opt_specialization
    =| template_specialization

-template_specialization
    = INF opt_template_param_inst_list SUP

-opt_template_param_inst_list
    =| template_param_inst_list

-template_param_inst_list
    = template_param_inst_list COMMA template_param_inst
    | template_param_inst

template_param_inst
    = expr
    | any_type

-opt_struc_body
    =| OPEN_CURLY translation_unit _LEAVE_SCOPE
""",

gcc_attributes="""
gcc_attribute
    = ATTRIBUTE OPEN_PAR OPEN_PAR
      gcc_attribute_contents CLOSE_PAR CLOSE_PAR

-gcc_attribute_contents
    = symbol
    | symbol OPEN_PAR gcc_attr_param_list CLOSE_PAR

-gcc_attr_param_list
    = gcc_attr_param_list COMMA gcc_attr_param
    | gcc_attr_param

gcc_attr_param
    = string
    | number
""")
