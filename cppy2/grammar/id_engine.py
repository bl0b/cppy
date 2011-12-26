from entities import *


root_namespace = scope()
current = root


class searcher(object):
    stack = []

    def __init__(self):
        self.cur = current
        self.local = False

    def _from_root(self):
        self.cur = root
        self.local = True

    def _resolve(self, sym):
        self.cur = self.cur.resolve(sym, self.local)
        if self.cur is None:
            return False
        self.local = False
        return True

    def _match_specialization(cls, params):
        self.cur = self.cur.match_specialization(params)

    @classmethod
    def new(cls):
        cls.stack.append(cls())

    @classmethod
    def destroy(cls):
        cls.stack.pop()

    @classmethod
    def from_root(cls):
        cls.stack[-1]._from_root()

    @classmethod
    def resolve(cls):
        cls.stack[-1]._resolve()

    @property
    def is_namespace(cls):
        return cls.stack[-1].cur.is_namespace

    @property
    def is_type(cls):
        t = cls.stack[-1].cur
        return t.is_type and not t.is_template

    @property
    def is_template_type(cls):
        t = cls.stack[-1].cur
        return t.is_type and t.is_template

    @property
    def is_const(cls):
        return cls.stack[-1].cur.is_const

    @property
    def is_var(cls):
        return cls.stack[-1].cur.is_var

    @classmethod
    def assert(cls, what):
        if not getattr(cls, what):
            cls.destroy()
            return False
        return True

    @classmethod
    def match_specialization(cls, params):
        cls.stack[-1]._match_specialization(params)

    assert_var = lambda c: c.assert('is_var')
    assert_type = lambda c: c.assert('is_type')
    assert_const = lambda c: c.assert('is_const')
    assert_namespace = lambda c: c.assert('is_namespace')
    assert_template_type = lambda c: c.assert('is_template_type')


def _START_BUILD():
    searcher.new()


def _BUILD_FROM_ROOT():
    searcher.from_root()


def _ASSERT_VAR():
    return searcher.assert_var()


def _ASSERT_TYPE():
    return searcher.assert_type()


def _ASSERT_CONST():
    return searcher.assert_const()


def ID(sym):
    return searcher.resolve(sym)


def NAMESPACE_NAME(sym):
    if not searcher.resolve(sym):
        return False
    return searcher.assert_namespace()


def TYPE(sym):
    if not searcher.resolve(sym):
        return False
    return searcher.assert_type()


def TEMPLATE_TYPE(sym, params):
    if searcher.resolve(sym) and searcher.assert_template_type():
        searcher.match_specialization(params)
        return True
    return False
#

id_grammar = """
_START_BUILD=
_ASSERT_VAR=
_ASSERT_TYPE=
_ASSERT_CONST=
_BUILD_FROM_ROOT=

ID  = symbol

NAMESPACE_NAME
    = symbol

TEMPLATE_TYPE
    = symbol INF template_expr_list SUP

TYPE
    = symbol

template_expr_list
    = template_expr_list COMMA template_expr
    | template_expr

template_expr
    = any_type
    | expr

any_type
    = type_or_pointer_type
    | type_id AMPERSAND

type_or_pointer_type
    = type_or_pointer_type STAR
    | type_id

container
    = NAMESPACE_NAME
    | TEMPLATE_TYPE
    | TYPE

var_id
    = _START_BUILD any_path SCOPE ID _ASSERT_VAR
    | _START_BUILD ID _ASSERT_VAR

const_id
    = _START_BUILD any_path SCOPE ID _ASSERT_CONST
    | _START_BUILD ID _ASSERT_CONST

type_id
    = _START_BUILD any_path

-any_path
    = SCOPE _BUILD_FROM_ROOT path
    | path

path
    = path SCOPE container
    | container

"""
