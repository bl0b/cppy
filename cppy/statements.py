__all__ = [
'CppMeta', 'CppStatement', 'IfStatement', 'ElseStatement', 'ForStatement',
'WhileStatement', 'DoWhileStatement', 'SwitchStatement', 'AssignmentStatement',
'VarDeclStatement', 'StructDeclStatement', 'ClassDeclStatement',
'ReturnStatement', 'DeleteStatement', 'FuncDeclStatement']

from parser import compile_expression, match, tokenize
import sys
from itertools import chain, imap


class CppMeta(type):
    recognizers = {}
    recog_expr = None
    recog_expr_name = "CppMeta_recognizer"

    def __init__(cls, name, bases, dic):
        if 'recognize' in dic and dic['recognize'] != '':
            CppMeta.recognizers[name] = \
                '#%s:(%s)' % (name, dic['recognize'])
            #CppMeta.recog_expr = None
        type.__init__(cls, name, bases, dic)

    @classmethod
    def __recog(cls, tokens):
        m = lambda v: match(tokens, v)
        #print cls.recognizers
        tmp = [(g[0][0], g) for ok, start, end, g
                     in imap(m, cls.recognizers.itervalues())
                     if ok and g]
        #print "=>", tmp
        return dict(tmp)

    @classmethod
    def recognize(cls, text):
        tokens = tokenize(text)
        ok, start, end, groups = match(tokens, 'c_label|(scope colon)')
        if ok:
            tokens = tokens[end:]
        #ret = {}
        #while tokens and not ret:
        #    ret = cls.__recog(tokens)
        #    if not ret:
        #        # try to remove leading macros...
        #        ok, start, end, groups = match(tokens, 'macro')
        #        if ok:
        #            tokens = tokens[end:]
        #        else:
        #            break
        ret = cls.__recog(tokens)
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
            #print "AFTER disambiguation by derivation", classes
            if len(classes) == 1:
                c = classes[0].__name__
                return {c: ret[c]}
        return ret




        #if cls.recog_expr is None:
        #    # discard C label declaration if present
        #    recog_str = "(symbol colon)? ("
        #    recog_str += '|'.join("#%s:(%s)" % i
        #                          for i in cls.recognizers.iteritems())
        #    recog_str += ')'
        #    print >> sys.stderr, "Rebuilding statement recognizer:", recog_str
        #    cls.recog_expr = compile_expression(recog_str,
        #                                        name=cls.recog_expr_name)
        #return match(tokenize(text), cls.recog_expr_name)


class CppStatement(object):
    __metaclass__ = CppMeta
    recognize = 'semicolon semicolon'  # will never match :)
    tag = 'cpp'
    extra_contents = []

    def __init__(self, text):
        #print "init cpp statement", type(self), text
        self.text = text
        self.sub = []
        for xc in self.extra_contents:
            setattr(self, xc, [])

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


class AssignmentStatement(ExprStatement):
    tag = 'assign'
    recognize = '^ assignment'

    def __init__(self, text):
        CppStatement.__init__(self, text)
        #parts = re.split(Cpp.assignment_op, text)
        #self.lvalue = parts[0]
        #is_assign_set = re.findall(Cpp.assign_set_op, text)
        #self.assign_type = is_assign_set and 'set' or 'update'
        self.parse()

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


class VarDeclStatement(CppStatement):
    tag = 'var'
    recognize = '^var_decl'


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


class ConstructorStatement(CppStatement):
    tag = 'ctor'
    recognize = 'constructor_decl'


class DestructorStatement(CppStatement):
    tag = 'dtor'
    recognize = 'destructor_decl'


class StructDeclStatement(CppStatement):
    tag = 'struct'
    recognize = 'type_spec* kw_struct'


class FuncDeclStatement(CppStatement):
    tag = 'func'
    recognize = '^func_decl'
