from main_grammar import register, validator
import id_engine
from entities import Type, Namespace, TemplateType, Entity, Scope
from entities import TemplateFreeConst, TemplateFreeType, Function
from entities import PointerTo, ReferenceTo, FunctionParam, TypeAlias
from entities import Variable


@validator
def typedef(ast):
    sym = ast[-2][1]
    typ = ast[-3]
    ret = TypeAlias(sym, id_engine.current(), typ)
    return ret


@validator
def NAMESPACE_ENTER(ast):
    sym = ast[1][1]
    n = id_engine.resolve(sym, True)
    print "enter namespace ?", n
    if n is Entity.Null:
        n = Namespace(sym, id_engine.current())
        print "new namespace !", n
    id_engine.enter(n)
    return id_engine.current()


@validator
def gcc_attribute(ast):
    return tuple()


@validator
def template_type_decl_prefix(ast):
    free_params = []
    print ast
    #for x in ast[2:]:
    #    if x[0] == 'symbol':
    #        sym = x[1]
    decl = ast[-1]
    sym = decl[-1][1]
    kw = decl[-2][1]
    ret = TemplateType(sym, id_engine.current(), {
        'kw': kw,
        'free_params': ast[1],
        'bound_params': [],
    })
    id_engine.enter(ret)
    return ret


@validator
def template_free_param_list(ast):
    print "T_FPL", ast
    scope = ast[1]
    if len(ast) == 2:
        return scope
    param = ast[-1]
    if param[0] == 'template_free_type':
        cls = TemplateFreeType
    else:
        cls = TemplateFreeConst
    kw = param[1][1]
    sym = param[2][1]
    if len(param) == 4:
        default = param[3]
    else:
        default = None
    cls(sym, scope, kw, default)
    return scope


@validator
def template_param_decl(ast):
    print "template_param_decl", ast
    return ast


@validator
def specialization_decl(ast):
    tt = ast[1]
    print "TODO : match_specialization !"
    return tt


@validator
def _FORWARD_DECL(ast):
    id_engine.leave()
    return tuple()


@validator
def LEAVE_SCOPE(ast):
    id_engine.leave()
    return tuple()


@validator
def using_decl(ast):
    if type(ast[2]) is tuple and ast[2][0] == 'NAMESPACE':
        print "TODO ! import namespace"
    else:
        what = ast[2]
        id_engine.add(what)
        print "Imported", what.full_path, "in", id_engine.current().full_path
    return tuple()


@validator
def enter_template_free_params(ast):
    ret = Scope(None, id_engine.current())
    id_engine.enter(ret)
    return ret


@validator
def template_param_decl(ast):
    print "TODO: declare TemplateParam (TODO: write TemplateParam class)"
    print "TODO: make template parameters scope an ordered list also"
    return ast


@validator
def leave_template_free_params(ast):
    id_engine.leave()
    return ast[-2:]


_anon_counter = 0


def make_anon():
    global _anon_counter
    _anon_counter += 1
    return 'anonymous_' + str(_anon_counter)


@validator
def _ENTER_STRUC(ast):
    if ast[2][0] == 'symbol':
        sym = ast[2][1]
        ret = id_engine.resolve(sym)
    else:
        sym = make_anon()
        ret = Entity.Null
    if ret is Entity.Null:
        ret = Type(sym, id_engine.current(), None)
    id_engine.enter(ret)
    return ret


@validator
def _MARK_STRUC(ast):
    if ast[2][0] == 'symbol':
        sym = ast[2][1]
    else:
        sym = make_anon()
    ret = id_engine.resolve(sym)
    if ret is Entity.Null:
        ret = Type(sym, id_engine.current(), None)
    id_engine.enter(ret)
    return ret


@validator
def func_signature(ast):
    print ast
    params = []
    cv = None
    for x in ast[1:]:
        if x[0] == 'func_type':
            ftype = x[1]
        elif x[0] == 'func_id':
            print "FUNC ID", x[1:]
            if type(x[1]) is Function:
                fid = x[1].name
            else:
                fid = x[1][1]
        elif x[0] == 'func_param':
            params.append(x[1])
        elif x[0] == 'opt_cv_qualifier':
            cv = (a[0] for a in x[1:])
    print "ftype", ftype
    print "fid", fid
    print "fparam", params
    f = id_engine.resolve(fid, True)
    if f is Entity.Null:
        f = Function(fid, id_engine.current())
    sig = f.create_signature(ftype, params, cv)
    id_engine.enter(f.scopes[sig])
    return ('func_signature', fid, sig)


@validator
def func_param(ast):
    print ast
    ptyp = ast[1]
    if len(ast) > 2:
        pname = ast[2][1]
    else:
        pname = None
    if len(ast) == 4:
        pdef = ast[3]
    else:
        pdef = None
    ret = FunctionParam(ptyp, pname, pdef)
    print ret
    return ('func_param', ret)


@validator
def func_type(ast):
    if type(ast[1]) is tuple and ast[1][1] == 'void':
        return ('func_type', Entity.Void)
    else:
        return ast


@validator
def _ASSERT_NEW_SYMBOL(ast):
    if id_engine.resolve(ast[1][1]) is not Entity.Null:
        return None
    return ast[1]


@validator
def _discard_curly(ast):
    return tuple()


__var_type = None


@validator
def var_type(ast):
    global __var_type
    __var_type = ast[1]
    return tuple()


@validator
def single_var(ast):
    global __var_type
    if len(ast) == 3:
        mod = ast[1]
        if mod[0] == 'AMPERSAND':
            typ = ReferenceTo(__var_type)
        else:
            # stars
            typ = __var_type
            for k in mod[1:]:
                typ = PointerTo(__var_type)
    else:
        typ = __var_type
    ret = Variable(ast[-1][1], id_engine.current(), typ)
    return ret


@validator
def single_var_decl(ast):
    var = ast[1]
    if len(ast) == 2:
        return var
    var.default = ast[3]
    return var


@validator
def var_decl(ast):
    return ast[1:-1]


@validator
def static_var_decl(ast):
    for v in ast[2]:
        v.static = True
    return ast

register(
toplevel="""
_ASSERT_NEW_SYMBOL      = symbol
NAMESPACE_ENTER        = symbol
_FUNC_NAME              = symbol
LEAVE_SCOPE            = CLOSE_CURLY
_ENTER_STRUC            = s_c_u symbol OPEN_CURLY
                        | s_c_u OPEN_CURLY
_MARK_STRUC             = s_c_u symbol
                        | s_c_u
_STRUCLEAVE            =
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
    | static_var_decl
    | type_decl
    | extern_linkage
    | using_decl

using_decl
    = USING NAMESPACE any_path SEMICOLON
    | USING any_path SEMICOLON

sub_translation_unit
    = OPEN_CURLY translation_unit LEAVE_SCOPE

namespace_decl
    = NAMESPACE NAMESPACE_ENTER gcc_attribute_opt sub_translation_unit

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
    = func_compile_spec_list

-func_compile_spec_list
    = func_compile_spec func_compile_spec1
    | func_compile_spec1

func_compile_spec1 = INLINE | STATIC | EXTERN

func_signature
    = func_type func_id
      OPEN_PAR func_param_list_opt CLOSE_PAR
      opt_cv_qualifier opt_throw_spec

func_type
    = VOID
    | any_type

opt_cv_qualifier
    =| CONST
     | VOLATILE
     | CONST VOLATILE

opt_throw_spec
    =| THROW OPEN_PAR opt_type_list CLOSE_PAR

opt_type_list
    =| type_list

-type_list
    = type_list COMMA any_type
    | any_type

func_ptr_signature
    = any_type OPEN_PAR opt_type STAR OPT_ID CLOSE_PAR
      OPEN_PAR func_param_list_opt CLOSE_PAR

opt_type
    =| type_id

func_id
    = _ASSERT_FUNC
    | _ASSERT_NEW_SYMBOL

-func_param_list_opt
    =| func_param_list

-func_param_list
    = func_param_list COMMA func_param
    | func_param

func_param
    = any_type symbol opt_default
    | any_type
    | func_ptr_signature

opt_default
    =| expr

-opt_body
    = _FORWARD_DECL
    | _discard_curly opt_statement_list LEAVE_SCOPE

_discard_curly
    = OPEN_CURLY
""",

var_const_decl="""
const_decl
    = CONST type_id symbol EQUAL expr SEMICOLON

static_var_decl
    = STATIC var_decl

var_decl
    = var_type var_decl_list SEMICOLON
    | func_ptr_signature SEMICOLON

var_type
    = type_id

-var_decl_list
    = var_decl_list COMMA single_var_decl
    | single_var_decl

single_var_decl
    = single_var
    | single_var EQUAL var_init

-single_var_base
    = modifier symbol
    | symbol

modifier
    = AMPERSAND
    | stars

single_var
    = single_var subscript
    | single_var_base

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
    = _ENTER_STRUC translation_unit LEAVE_SCOPE
    | _MARK_STRUC

template_type_decl_prefix
    = template_free_param_list leave_template_free_params

template_free_param_list
    = template_free_param_list COMMA template_param_decl
    | enter_template_free_params template_param_decl
    | enter_template_free_params

enter_template_free_params
    = TEMPLATE INF

leave_template_free_params
    = SUP s_c_u symbol

specialization_decl
    = template_type_decl_prefix template_specialization

-template_type_decl_base
    = template_type_decl_prefix
    | specialization_decl

template_type_decl
    = template_type_decl_base _FORWARD_DECL
    | template_type_decl_base OPEN_CURLY translation_unit LEAVE_SCOPE

-opt_template_param_decl_list
    =| template_param_decl_list

-template_param_decl_list
    = template_param_decl_list COMMA template_param_decl
    | template_param_decl

-template_param_decl
    = template_free_type
    | template_free_const

template_free_type
    = TYPENAME symbol opt_tp_default
    | CLASS symbol opt_tp_default
    | STRUCT symbol opt_tp_default
    | UNION symbol opt_tp_default

template_free_const
    = int_type symbol opt_tp_default
    | CHAR symbol opt_tp_default
    | BOOL symbol opt_tp_default

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
    =| OPEN_CURLY translation_unit LEAVE_SCOPE
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
