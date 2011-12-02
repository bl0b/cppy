__all__ = [
'CppMeta', 'CppStatement', 'IfStatement', 'ElseStatement', 'ForStatement',
'WhileStatement', 'DoWhileStatement', 'SwitchStatement', 'AssignmentStatement',
'VarDeclStatement', 'ClassDeclStatement', 'ReturnStatement', 'DeleteStatement',
'FuncDeclStatement', 'Scope',
]

from parser import compile_expression, match, tokenize
import sys
from itertools import chain, imap, starmap


class CppException(Exception):
    pass


class UnhandledCapture(CppException):

    def __init__(self, name, toks):
        CppException.__init__(self, "Capture <%s> has no handler!" % name)
        self.capture_name = name
        self.capture_tokens = toks


class AmbiguousStatement(CppException):

    def __init__(self, text, scope, classes):
        CppException.__init__(self, "Ambiguous statement: < %s > %s" % (
                                    text, str(classes)))
        self.text = text
        self.scope = scope
        self.classes = classes


class InvalidStatement(CppException):
    pass


class Scope(dict):

    def __init__(self, parent=None):
        dict.__init__(self)
        self.sub = []
        self.parent = parent

    def resolve(self, x):
        if x in self:
            return self[x]
        if self.parent:
            return self.parent.resolve(x)
        return None

    def process_payload(self, gname, gtoks):
        hook = 'hook_' + gname
        if hook in dir(self):
            return getattr(self, hook)(gtoks)
        elif self.parent:
            return self.parent.process_payload(gname, gtoks)
        else:
            raise UnhandledCapture(gname, gtoks)

    def copy(self):
        ret = Scope(self.parent)
        ret.update(self)
        ret.sub = list(self.sub)
        return ret


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
        clsbyname = lambda n: getattr(sys.modules[__name__], n)
        classes = map(clsbyname, ret.iterkeys())
        print "     classes", classes

        if ret and len(ret) > 1:
            # try and disambiguate stuff
            # first, a derived class has priority over the base class.
            print "     more than one possible meaning"

            def test_class(c):
                others = tuple(cl for cl in classes if cl is not c)
                return issubclass(c, others)
            print "     BEFORE disambiguation by derivation", classes
            subclasses = filter(test_class, classes)
            print "     AFTER disambiguation by derivation", subclasses
            if subclasses:
                classes = subclasses

        validate = lambda c: cls.validate(scope, c, text, ret[c.__name__])
        statements = map(validate, classes)
        print "     statements", statements
        if len(statements) == 1:
            return statements[0]
        else:
            raise AmbiguousStatement(text, scope, statements)
        return CppStatement(text, scope, [])

    @classmethod
    def validate(cls, scope, C, text, captures):
        print "     validating", C, text, scope, captures
        try:
            tmp_scope = scope.copy()
            C(text, tmp_scope, captures)
        except InvalidStatement, ista:
            return None
        return C(text, scope, captures)


class CppStatement(Scope):
    __metaclass__ = CppMeta
    recognize = 'semicolon semicolon'  # will never match :)
    tag = 'cpp'
    extra_contents = []
    descriptors = {}
    absorb = tuple()
    absorb_post = tuple()

    def __init__(self, text, parent, payload):
        Scope.__init__(self, parent)
        #print "init cpp statement", type(self), text
        self.text = text
        self.sub = []
        self.scope = parent
        for xc in self.extra_contents:
            setattr(self, xc, [])
        for k, v in self.descriptors.iteritems():
            setattr(self, k, v)
        for discard in starmap(self.process_payload, payload):
            pass

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

    def hook_template_type(self, toks):
        print "| template_type", toks
        pass

    def hook_type(self, toks):
        print "| type", toks
        pass

    def hook_template_param(self, toks):
        print "| template_param", toks
        pass

    def hook_template_param_inst(self, toks):
        print "| template_param inst", toks
        pass

    def hook_CALL(self, toks):
        print "DETECTED A CALL!!", toks

    def hook_UPDATE_TARGET(self, toks):
        print "DETECTED AN UPDATE!!", toks


class TypedefStatement(CppStatement):
    tag = 'typedef'
    recognize = 'kw_typedef ((type_id template_inst?)? #id:type_id semicolon'

    def hook_id(self, toks):
        self.parent[toks] = 'type'


class TypedefAnonStatement(TypedefStatement):
    tag = 'typedef'
    recognize = 'kw_typedef (kw_struct|kw_union) $'
    absorb_post = ('symbol semicolon',)


class ExprStatement(CppStatement):
    tag = 'expr'
    recognize = 'expr (semicolon|close_paren)'
    # close_paren if third statement inside for(;;)


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
    absorb = ('expr', 'expr')


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
    descriptors = {'name': None, 'type': None, 'initialization': None}

    def hook_id(self, toks):
        self.name = ''.join(imap(lambda x: x[1], toks))
        self.scope[toks] = 'var'

    def hook_type(self, toks):
        self.type = toks

    def hook_initialization(self, toks):
        self.initialization = toks


class ClassDeclStatement(CppStatement):
    tag = 'class'
    recognize = """(kw_template template_spec)?
                   type_spec*
                   (kw_class|kw_struct)
                   type_id
                   (colon
                    scope
                    type_id
                    (comma scope type_id)*
                   )?"""


class FuncDeclStatement(CppStatement):
    tag = 'func'
    recognize = '^func_decl'
    descriptors = {'name': None}

    def hook_id(self, toks):
        print "got id capture", toks
        if self.name:
            # must be a param
            self[toks] = 'var'
            print self.name, "has param", toks
        else:
            self.name = ''.join(imap(lambda x: x[1], toks))
            print "function", self.name

    def hook_initialization(self, toks):
        print "got initialization capture", toks

    def hook_param_type(self, toks):
        print "| param_type", toks
        if self.resolve(toks) != 'type':
            print "  param is invalid !"
            raise InvalidStatement()
        print "  param is valid !"

    def hook_param_id(self, toks):
        print "| param_id", toks
        if self.resolve(toks):
            print "  param is invalid !"
            raise InvalidStatement()
        print "  param is valid !"


class ConstructorStatement(FuncDeclStatement):
    tag = 'ctor'
    recognize = 'constructor_decl'


class DestructorStatement(FuncDeclStatement):
    tag = 'dtor'
    recognize = 'destructor_decl'


class UsingStatement(CppStatement):
    tag = 'using'
    recognize = 'kw_using kw_namespace? id'


class ExternLinkage(CppStatement):
    tag = 'extern'
    recognize = 'type_spec string $'
