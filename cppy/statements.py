__all__ = [
'CppMeta', 'CppStatement', 'IfStatement', 'ElseStatement', 'ForStatement',
'WhileStatement', 'DoWhileStatement', 'SwitchStatement', 'AssignmentStatement',
'VarDeclStatement', 'StructDeclStatement', 'ClassDeclStatement',
'ReturnStatement', 'DeleteStatement', 'FuncDeclStatement', 'Scope',
]

from parser import compile_expression, match, tokenize
import sys
from itertools import chain, imap


class Scope(dict):
    def __init__(self, parent=None):
        dict.__init__(self)
        self.sub = []
        self.parent = []

    def resolve(self, x):
        if x in self:
            return self[x]
        if self.parent:
            return self.parent.resolve(x)
        return None

    @property
    def scope(self):
        return self


class CppMeta(type):
    recognizers = {}
    recog_expr = None
    recog_expr_name = "CppMeta_recognizer"

    def __init__(cls, name, bases, dic):
        if 'recognize' in dic and dic['recognize'] != '':
            CppMeta.recognizers[name] = \
                    dic['recognize']
        type.__init__(cls, name, bases, dic)

    @classmethod
    def __recog(cls, tokens, scope):
        m = lambda v: match(tokens, v)
        ret = {}
        for name, rec in cls.recognizers.iteritems():
            ok, start, end, g = m(rec)
            if ok:
                ret[name] = g
        return ret

    @classmethod
    def recognize(cls, text, scope):
        tokens = tokenize(text)
        ok, start, end, groups = match(tokens, 'c_label|(scope colon)')
        if ok:
            tokens = tokens[end:]
        ret = cls.__recog(tokens, scope)
        if ret and len(ret) > 1:
            # try and disambiguate stuff
            # first, a derived class has priority over the base class.
            clsbyname = lambda n: getattr(sys.modules[__name__], n)
            classes = map(clsbyname, ret.iterkeys())
            #print "BEFORE disambiguation by derivation", classes

            def test_class(c):
                others = tuple(cl for cl in classes if cl is not c)
                return issubclass(c, others)
            classes = filter(test_class, classes)
            classes = map(lambda c: (c, c.validate(ret[c.__name__], scope)),
                          classes)
            classes = filter(lambda (cls, (ok, payload)): ok, classes)
            #print "AFTER disambiguation by derivation", classes
            if len(classes) == 1:
                c = classes[0][0].__name__
                return {c: ret[c]}
        return ret


class CppStatement(dict):
    __metaclass__ = CppMeta
    recognize = 'semicolon semicolon'  # will never match :)
    tag = 'cpp'
    extra_contents = []

    def __init__(self, text, parent):
        #print "init cpp statement", type(self), text
        self.text = text
        self._scope = parent
        self.sub = []
        self.scope = parent
        for xc in self.extra_contents:
            setattr(self, xc, [])

    def resolve(self, x):
        if x in self:
            return self[x]
        if self.scope:
            return self.scope.resolve(x)
        return None

    def itemize(self):
        return match(tokenize(self.text), self.recognize)

    def __str__(self):
        ret = self.tag + '(' + self.text
        #if self.sub:
        #    ret += ' [%i sub-statements])' % len(self.sub)
        #else:
        #    ret += ')'
        return ret

    __repr__ = __str__

    def tree(self, level=0, container=None):
        if container is None:
            return '\n'.join(self.tree(level, []))
        container.append('%s%s' % ('   ' * level, self.text))
        map(lambda cts: map(lambda x: x.tree(level + 1, container),
                            getattr(self, cts)),
            chain(('sub',), self.extra_contents))
        return container

    def search_iter(self, predicate):
        if predicate(self):
            yield self
        statements = chain(self.sub, (s for cts in self.extra_contents
                                        for s in getattr(self, cts)))
        for statement in statements:
            if not statement:
                print "No statement!"
                continue
            for x in statement.search_iter(predicate):
                yield x

    @classmethod
    def validate(self, groups, scope):
        return True, None


class TypedefStatement(CppStatement):
    tag = 'typedef'
    recognize = 'kw_typedef type_id type_id'


class ExprStatement(CppStatement):
    tag = 'expr'
    recognize = 'expr semicolon'


class IfStatement(CppStatement):
    tag = 'if'
    recognize = '^kw_if'
    extra_contents = ('elses',)


class ElseStatement(CppStatement):
    tag = 'else'
    recognize = '^kw_else'


class DeleteStatement(CppStatement):
    tag = 'delete'
    recognize = '^kw_delete'


class ForStatement(CppStatement):
    tag = 'for'
    recognize = '^kw_for'


class SwitchStatement(CppStatement):
    tag = 'switch'
    recognize = '^kw_switch'


class DoWhileStatement(CppStatement):
    tag = 'do'
    recognize = '^kw_do'
    extra_contents = ('whilecond',)


class WhileStatement(CppStatement):
    tag = 'while'
    recognize = '^kw_while'


class ReturnStatement(CppStatement):
    tag = 'return'
    recognize = '^kw_return'


class DeleteStatement(CppStatement):
    tag = 'del'
    recognize = '^kw_delete'


class NamespaceStatement(CppStatement):
    tag = 'namespace'
    recognize = '^kw_namespace symbol'


class AssignmentStatement(ExprStatement):
    tag = 'assign'
    recognize = '^ assignment'

    def parse(self):
        ok, start, end, groups = match(tokenize(self.text), 'assignment')
        if groups is None:
            #print >> sys.stderr, "Assignment matching failed !"
            #print >> sys.stderr, " \\_: text", self.text
            return
        l, e, r = groups
        self.lvalue = l[1]  # tokens
        self.rvalue = r[1]  # tokens
        self.effect = e[0]  # group name; will be 'set' or 'update'
        if not ok:
            print "FAILURE", self.text, groups


# a declaration of pointer variable may look like an arithmetic expression
class VarDeclStatement(ExprStatement):
    tag = 'var'
    recognize = 'var_decl'

    @classmethod
    def validate(self, groups, scope):
        vtype = (('symbol', 'int'),)
        vinit = tuple()
        for name, cts in groups:
            print name, "->", cts
            if name == 'type':
                t = scope.resolve(cts)
                #if t is None or t[0] != 'type':
                #    return False, None
                vtype = cts
            elif name == 'id':
                vid = cts
            elif name == 'initialization':
                vinit = cts
        scope[vid] = ('var', vtype, vinit)

        return True, None


class ClassDeclStatement(CppStatement):
    tag = 'class'
    recognize = """type_spec*
                   kw_class
                   type_id
                   (colon
                    scope
                    type_id
                    (comma scope type_id)*
                   )?"""


class FuncDeclStatement(CppStatement):
    tag = 'func'
    recognize = '^func_decl'


class ConstructorStatement(FuncDeclStatement):
    tag = 'ctor'
    recognize = 'constructor_decl'


class DestructorStatement(FuncDeclStatement):
    tag = 'dtor'
    recognize = 'destructor_decl'


class StructDeclStatement(CppStatement):
    tag = 'struct'
    recognize = 'type_spec* kw_struct'


class ExternLinkage(CppStatement):
    tag = 'extern'
    recognize = 'type_spec string $'
