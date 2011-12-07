__all__ = [
'CppMeta', 'CppStatement', 'IfStatement', 'ElseStatement', 'ForStatement',
'WhileStatement', 'DoWhileStatement', 'SwitchStatement', 'AssignmentStatement',
'VarDeclStatement', 'ClassDeclStatement', 'ReturnStatement', 'DeleteStatement',
'FuncDeclStatement',  # 'Scope',
]

from parser import compile_expression, match, tokenize, Ast
import sys
from itertools import chain, imap, starmap
#from namespace import Namespace
import namespace
from namespace import Namespace
from exceptions import *

anon_counter = 0


def anon():
    global anon_counter
    anon_counter += 1
    return 'anonymous_' + str(anon_counter)


class Scope(dict):

    def __init__(self, parent=None):
        dict.__init__(self)
        #self.sub = []
        self.parent = parent

    def resolve(self, x):
        return namespace.resolve(x)

    def dump_scope(self):
        #print dict(self)
        self.parent and self.parent.dump_scope()

    def __repr__(self):
        return dict.__repr__(self) + repr(self.parent)

    def __str__(self):
        return dict.__str__(self) + str(self.parent)


class CppMeta(type):
    recognizers = {}
    recog_expr = None
    recog_expr_name = "CppMeta_recognizer"

    def __init__(cls, name, bases, dic):
        if 'recognize' in dic and dic['recognize'] != '':
            CppMeta.recognizers[name] = \
                    dic['recognize']
                    #"#%s:(%s)" % (name, dic['recognize'])
        type.__init__(cls, name, bases, dic)

    @classmethod
    def __recog(cls, tokens):
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
        ret = cls.__recog(tokens)
        clsbyname = lambda n: getattr(sys.modules[__name__], n)
        classes = map(clsbyname, ret.iterkeys())
        #print "     classes", classes

        if ret and len(ret) > 1:
            # try and disambiguate stuff
            # first, a derived class has priority over the base class.
            #print "     more than one possible meaning"

            def test_class(c):
                others = tuple(cl for cl in classes if cl is not c)
                return issubclass(c, others)
            #print "     BEFORE disambiguation by derivation", classes
            subclasses = filter(test_class, classes)
            #print "     AFTER disambiguation by derivation", subclasses
            if subclasses:
                classes = subclasses

        if len(classes) != 1:
            print "ambiguity:", text
            print "     classes", classes

        validate = lambda c: cls.validate(scope, c, text, ret[c.__name__])
        statements = filter(lambda x: x is not None, imap(validate, classes))
        #print "     statements", statements
        if len(statements) == 1:
            return statements[0]
        else:
            raise AmbiguousStatement(text, scope, statements)
        return CppStatement(text, scope, [])

    @classmethod
    def validate(cls, scope, C, text, captures):
        #print "     validating", C, text, scope, captures
        try:
            tmp = namespace.enter(anon())
            C(text, scope, captures)
        except InvalidStatement, ista:
            namespace.delete(tmp)
            return None
        namespace.delete(tmp)
        return C(text, scope, captures)


class CppStatement(object):
    __metaclass__ = CppMeta
    recognize = 'semicolon semicolon'  # will never match :)
    tag = 'cpp'
    extra_contents = []
    descriptors = {}
    absorb = tuple()
    absorb_post = tuple()

    def __init__(self, text, parent, payload):
        #print "init cpp statement", type(self), text
        #print "         payload", payload
        self.parent = parent
        self.text = text
        self.sub = []
        for xc in self.extra_contents:
            setattr(self, xc, [])
        for k, v in self.descriptors.iteritems():
            setattr(self, k, v)
        for discard in imap(self.process_payload, payload):
            pass

    def resolve(self, ast):
        return namespace.resolve(ast.tokens)

    def commit(self):
        """This method is called after all absorb and absorb_post statements
        have been absorbed."""
        pass

    def itemize(self):
        return match(tokenize(self.text), self.recognize)

    def __str__(self):
        ret = self.tag + '(' + self.text
        if self.sub:
            ret += ' [%i sub-statements])' % len(self.sub)
        else:
            ret += ')'
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

    def process_payload(self, ast):
        #print ast
        hook = 'hook_' + ast.name
        #print "DEBUG process_payload", hook, ast
        if hook in dir(self):
            return getattr(self, hook)(ast)
        #elif self.parent:
        #    return self.parent.process_payload(ast)
        else:
            raise UnhandledCapture(ast.name, ast)

    def hook_template_type(self, toks):
        #print "| template_type", toks
        pass

    def hook_type(self, toks):
        #print "| type", toks
        pass

    def hook_template_param(self, toks):
        #print "| template_param", toks
        pass

    def hook_template_param_inst(self, toks):
        #print "| template_param inst", toks
        pass

    def hook_rvalue(self, ast):
        for x in ast.children:
            self.process_payload(x)

    def hook_CALL(self, toks):
        print "DETECTED A CALL!!", toks

    def hook_UPDATE(self, toks):
        print "DETECTED AN UPDATE!!", toks

    def hook_READ(self, ast):
        x = namespace.resolve(ast.tokens)
        if x is None or x[0] != 'var':
            raise InvalidStatement(self.text)

    def hook_WRITE(self, ast):
        x = namespace.resolve(ast.tokens)
        if x is None or x[0] != 'var':
            raise InvalidStatement(self.text)

    def hook_CHECK_EXISTS(self, ast):
        x = namespace.resolve(ast.tokens)
        if x is None:
            #print "COULDN'T RESOLVE", ast.tokens
            raise InvalidStatement(self.text)


class TypedefStatement(CppStatement):
    tag = 'typedef'
    descriptors = {'tid': None, 'key': None}
    recognize = """kw_typedef
                   type_spec*
                   (kw_struct|kw_union|kw_class)?
                   (#tid:type_id ref_deref* #id:type_id
                   |ref_deref* #id:type_id)
                   semicolon"""

    def hook_tid(self, ast):
        self.tid = ast.tokens

    def hook_key(self, ast):
        self.key = ast.tokens[0][1]

    def hook_id(self, ast):
        #print "REGISTERING TYPE", ast
        self.name = ast.tokens

    def commit(self):
        if self.tid is None:
            self.tid = (('symbol', 'int'),)
        if self.key is not None:
            namespace.add_type(self.name, type=self.tid, key=self.key)
        else:
            namespace.add_type(self.name, type=self.tid)


class TypedefStructStatement(TypedefStatement):
    tag = 'typedef'
    recognize = """kw_typedef
                   #key:(kw_struct|kw_union|kw_class)
                   #tid:type_id?
                   $"""
    absorb_post = ('ref_deref* #id:symbol ($|semicolon)',)
    descriptors = {'name': None, 'tid': None, 'id': None}

    def hook_tid(self, ast):
        self.tid = ast.tokens
        #print "DEBUG TypedefStructStatement", ast.tokens
        if not self.tid:
            self.tid_name = anon()
            self.container = namespace.current()
        else:
            c = namespace.current()
            self.container, self.tid_name = c.interpret_tokens(self.tid)
        self.tid = (('symbol', self.tid_name),)
        #print "DBG TypedefStructStatement", self.tid, self.tid_name, self.tid

    def pre_sub(self):
        #print "PRE SUB TypedefStructStatement", self.key, self.tid_name,
        #print self.tid
        self.ns = namespace.enter(self.tid_name, key=self.key)
        #Namespace.current().add_namespace(self.ns)
        #self.ns.enter()
        self.container.add_type(self.tid,
                                key=self.key, ns=self.tid)
        self.ns.add_type(self.tid, key=self.key, ns=self.tid)

    def post_sub(self):
        #print "POST SUB TypedefStructStatement"
        #self.ns.leave()
        namespace.leave(self.ns)
        #namespace.add_type((('symbol', self.ns_name),))

    def commit(self):
        #print "tid", self.tid
        #print "name", self.name
        #print "key", self.key
        namespace.add_type(self.name, key=self.key, ns=self.tid)


class ExprStatement(CppStatement):
    tag = 'expr'
    recognize = 'expr (semicolon|close_paren)'
    # close_paren if third statement inside for(;;)


class IfStatement(CppStatement):
    tag = 'if'
    recognize = '^kw_if'
    extra_contents = ('elses',)

    def __init__(self, text, parent, payload):
        CppStatement.__init__(self, text, parent, payload)
        self.scope = namespace.enter_scope()

    def commit(self):
        namespace.leave_scope()

    def pre_sub(self):
        pass

    def post_sub(self):
        pass


class ElseStatement(CppStatement):
    tag = 'else'
    recognize = '^kw_else'


class DeleteStatement(CppStatement):
    tag = 'delete'
    recognize = '^kw_delete'


class ForStatement(CppStatement):
    tag = 'for'
    recognize = '^kw_for'
    absorb = ('expr_list', 'expr_list')

    def __init__(self, text, parent, payload):
        CppStatement.__init__(self, text, parent, payload)
        self.scope = namespace.enter_scope()

    def commit(self):
        namespace.leave_scope()

    def pre_sub(self):
        pass

    def post_sub(self):
        pass


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
    recognize = '^kw_namespace #id:symbol'

    def hook_id(self, ast):
        #self.ns = Namespace(ast.tokens[0][1], Namespace.current())
        self.name = ast.tokens[0][1]

    def pre_sub(self):
        self.ns = namespace.enter(self.name)

    def post_sub(self):
        namespace.leave(self.ns)
        #print "=============================================================="
        #print namespace.current()
        #print "=============================================================="


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


class ClassDeclStatement(TypedefStructStatement):
    tag = 'class'
    recognize = """(kw_template template_spec)?
                   type_spec*
                   #key:(kw_class|kw_struct)
                   #id:type_id
                   (colon
                    scope
                    type_id
                    (comma scope type_id)*
                   )?"""

    def hook_id(self, ast):
        TypedefStructStatement.hook_id(self, ast)
        TypedefStructStatement.hook_tid(self, ast)

    def pre_sub(self):
        this = [Ast('type', self.tid, []),
                Ast('id', (('symbol', 'this'),), []),
                Ast('initialization', tuple(), [])]
        VarDeclStatement("<this>", self, this).commit()
        TypedefStructStatement.pre_sub(self)

# a declaration of pointer variable may look like an arithmetic expression
# a decl may also look like a class decl without {}


class VarDeclStatement(ExprStatement, ClassDeclStatement):
    tag = 'var'
    recognize = 'var_decl'
    descriptors = {'name': None, 'type': None, 'initialization': None}

    def hook_id(self, ast):
        self.name = ast.tokens
        #self.parent[ast.tokens] = 'var'

    def hook_type(self, toks):
        self.type = toks

    def hook_initialization(self, toks):
        self.initialization = toks

    def commit(self):
        namespace.add_var(self.name, type=self.type,
                          initialization=self.initialization)
        #Namespace.current().add_var(self.name,
        #                            type=self.type,
        #                            initialization=self.initialization)


class VarDeclAnonStrucStatement(VarDeclStatement):
    tag = 'var'
    recognize = '#key:(kw_struct|kw_union)$'
    absorb_post = ("""ref_deref*
                      #id:symbol
                      (comma ref_deref* #id:symbol)*
                      semicolon""",)

    def pre_sub(self):
        #print "PRE SUB VarDeclAnonStrucStatement"
        self.ns_name = anon()
        #self.ns = Namespace(self.ns_name, Namespace.current())
        self.ns = namespace.enter(self.ns_name, key=self.ns_key)
        self.type = (('symbol', self.ns_name),)
        #Namespace.current().add_type(self.type, ns=self.ns_name)
        #Namespace.current().add_namespace(self.ns)
        #self.ns.enter()

    def hook_key(self, ast):
        self.ns_key = ast.tokens[0][1]

    def hook_id(self, ast):
        self.name = ast.tokens

    def post_sub(self):
        #print "POST SUB VarDeclAnonStrucStatement"
        #self.ns.leave()
        namespace.leave(self.ns)

    def commit(self):
        self.ns.key = self.ns_key
        VarDeclStatement.commit(self)
        #Namespace.current().add_var(self.name, type=self.ns_name)
        namespace.add_type(self.type, ns=self.ns_name)
        namespace.add_var(self.name, type=self.type)


class FuncDeclStatement(CppStatement):
    tag = 'func'
    recognize = '^func_decl'
    descriptors = {'name': '', 'params': []}

    def hook_param(self, ast):
        self.params.append(ast)
        #print "DECLARE PARAMETER", ast

    def hook_id(self, ast):
        #print "got id capture", ast
        self.name = ast.tokens
        self.ns_name = ast.tokens[-1][1]

    def hook_id_and_type(self, ast):
        #print "got operator id capture", ast
        self.name = ast.tokens
        self.ns_name = ast.tokens[-1][1]

    def hook_initialization(self, ast):
        #print "got initialization capture", ast
        pass

    def pre_sub(self):
        #print "PRE SUB FuncDeclStatement"
        self.ns = namespace.enter(self.ns_name, key='function')
        for p in self.params:
            VarDeclStatement('', self, p.children).commit()
        namespace.add_func((('symbol', self.ns_name),), self.params, self)

    def post_sub(self):
        #print "POST SUB FuncDeclStatement"
        namespace.leave(self.ns)

    def commit(self):
        namespace.add_func((('symbol', self.ns_name),), self.params, self)


class ConstructorStatement(FuncDeclStatement):
    tag = 'ctor'
    recognize = 'constructor_decl'
    descriptors = {'name': '', 'params': [], 'ctor': []}

    def hook_CTOR(self, ast):
        self.ctor = ast.children

    def commit(self):
        FuncDeclStatement.commit(self)
        self.ns.enter()
        for c in self.ctor:
            self.process_payload(c)
        self.ns.leave()


class DestructorStatement(FuncDeclStatement):
    tag = 'dtor'
    recognize = 'destructor_decl'


class UsingStatement(CppStatement):
    tag = 'using'
    recognize = 'kw_using #ns:kw_namespace? #id:id'

    def hook_ns(self, ast):
        self.mode = len(ast.tokens) and 'ns' or 'sym'

    def hook_id(self, ast):
        self.sym = ast.tokens

    def commit(self):
        if self.mode == 'ns':
            ns = namespace.current.find_namespace(self.sym)
            namespace.current().namespaces.update(ns.namespaces)
            namespace.current().symbols.update(ns.symbols)
        else:
            x = namespace.resolve(self.sym)
            if x is None:
                print "COULDN'T RESOLVE", self.sym
                raise InvalidStatement(self.text)
            #print self.sym
            name = self.sym[-1][1]
            if x[0] == namespace.VAR:
                namespace.current().add_var(name, **x[1])
            elif x[0] == namespace.TYPE:
                namespace.current().add_type(name, **x[1])


class ExternLinkage(CppStatement):
    tag = 'extern'
    recognize = 'type_spec string $'

    def pre_sub(self):
        pass

    def post_sub(self):
        pass
