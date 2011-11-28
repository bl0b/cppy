#!/usr/bin/env python

import re
import sys, os
from itertools import ifilter, imap, chain

# xreadlines with stripping of empty lines and single-line comments
def cpp_strip_slc(f):
    reader = hasattr(f, 'xreadlines') and f.xreadlines() or hasattr(f, 'splitlines') and f.splitlines() or f
    for line in reader:
        components = line.strip().split('//')
        if len(components) and len(components[0]) and components[0][0]!='#':
            yield components[0]


multiline_comment = re.compile(r'/[*].*?[*]/')

def cpp_strip_mlc(f):
    big_buffer = ' '.join(cpp_strip_slc(f))
    return ' '.join(multiline_comment.split(big_buffer))


reformat = {
        '{': '\n{\n',
        '}': '\n}\n',
        ';': ';\n',
        r'\ ': ' ',
}

def cpp_read(f):
    no_comment = cpp_strip_mlc(f)
    for match, replace in reformat.iteritems():
        no_comment = replace.join(ifilter(lambda x:x, no_comment.split(match)))
    return filter(lambda s: len(s) and s!=',', imap(str.strip, no_comment.splitlines()))

class CppStatement(object):
    tag = 'cpp'
    extra_contents = []
    def __init__(self, text):
        #print "init cpp statement", type(self), text
        self.text = text
        self.sub = []
        for xc in self.extra_contents:
            setattr(self, xc, [])
    def __str__(self):
        ret = type(self).tag+'('+self.text
        if self.sub:
            ret += ' [%i sub-statements])'%len(self.sub)
        else:
            ret += ')'
        return ret
    __repr__ = __str__
    def tree(self, level, container):
        container.append('%s%s'%('   '*level, self.text))
        map(lambda cts: map(lambda x : x.tree(level+1, container), getattr(self, cts)), chain(('sub',), self.extra_contents))
        return container
    def search_iter(self, predicate):
        if predicate(self):
            yield self
        for statement in chain(self.sub, (s for cts in self.extra_contents for s in getattr(self, cts))):
            for x in statement.search_iter(predicate):
                yield x
        #map(lambda cts: map(lambda x: x.search_iter(predicate), getattr(self, cts)), chain(('sub',), self.extra_contents))

class IfStatement(CppStatement):
    tag = 'if'
    extra_contents = ('elses',)

class ElseStatement(CppStatement):
    tag = 'else'

class ForStatement(CppStatement):
    tag = 'for'

class SwitchStatement(CppStatement):
    tag = 'switch'

class DoWhileStatement(CppStatement):
    tag = 'do'
    extra_contents = ('whilecond',)

class WhileStatement(CppStatement):
    tag = 'while'

class ReturnStatement(CppStatement):
    tag = 'return'

class AssignmentStatement(CppStatement):
    tag = 'assign'
    def __init__(self, text):
        CppStatement.__init__(self, text)
        parts = re.split(Cpp.assignment_op, text)
        self.lvalue = parts[0]
        self.assign_type = re.findall(Cpp.assign_set_op, text) and 'set' or 'update'

class LocalDeclStatement(CppStatement):
    tag = 'local'

class ClassDeclStatement(CppStatement):
    tag = 'class'

class StructDeclStatement(CppStatement):
    tag = 'struct'


class CppExpr(list):
    ANY = 'any'
    SYMBOL = 'symbol'
    KEYWORD = 'keyword'
    OPERATOR = 'operator'
    LIST = 'list'

    def __init__(self, typ, text, contents):
        self.typ = typ
        if text.endswith(';'):
            text = text[:-1]
        self.text = text
        list.__init__(self, contents)
    def __str__(self):
        return self.text


# Code adapted from an answer at stackoverflow.com http://stackoverflow.com/questions/2358890/python-lexical-analysis-and-tokenization
token_pattern = r"""
(?P<symbol>[a-zA-Z_][a-zA-Z0-9_]*)
|(?P<number>-?(?:\.[0-9]+|(?:0|[1-9][0-9]*)(?:\.[0-9]*)?)(?:[eE]-?[0-9]+\.?[0-9]*)?)
|(?P<type_spec>\b(?:typename|template|const|static|register|volatile|extern|long|short|unsigned|signed)\b)
|(?P<access>(?:\.|->)[*]?)
|(?P<ampersand>[&])
|(?P<comma>,)
|(?P<semicolon>;)
|(?P<open_angle><)
|(?P<close_angle>>)
|(?P<keyword>\b(?:if|else|while|do|for|switch|class|struct|union)\b)
|(?P<open_square>[[])
|(?P<close_square>[]])
|(?P<open_paren>[(])
|(?P<close_paren>[)])
|(?P<namespace_member>::)
|(?P<ternary>[?])
|(?P<colon>(?<!:):(?!:))
|(?P<open_curly>[{])
|(?P<close_curly>[}])
|(?P<whitespace>\s+)
|(?P<assign_set>(?<!=)[=](?!=))
|(?P<assign_update>(?:>>|<<|(?<![<>])[<>]|[&^%*/+-])[=](?!=))
|(?P<incdec>[+][+]|--)
|(?P<string>"(?:\\["bntr]|[^\\])*")
|(?P<char>'(?:\\['bntr]|[^\\])')
|(?P<boolop>[|][|]|[&][&]|!)
|(?P<bitop>(?<!\|)\|(?!\|) | (?<!\&)\&(?!\&) | [~] | (?<!\^)\^(?!\^))
|(?P<comp>==|!=|<=|>=|[><](?!=))
|(?P<addsubdiv>[%+/-])
|(?P<star>[*])
|(?P<dot>\.)
|(?P<dollar>[$])
"""

token_re = re.compile(token_pattern, re.VERBOSE)

class TokenizerException(Exception): pass

def tokenize_iter(text):
    pos = 0
    while True:
        m = token_re.match(text, pos)
        if not m: break
        pos = m.end()
        tokname = m.lastgroup
        tokvalue = m.group(tokname)
        if tokname != 'whitespace':  # don't emit whitespace
            yield tokname, tokvalue
    if pos != len(text):
        raise TokenizerException('tokenizer stopped at pos %r of %r in "%s" at "%s"' % (pos, len(text), text, text[pos:pos+3]))
# End of adapted code

tokenize = lambda t: list(tokenize_iter(t))

arity = { (0, 1): '?', (0, 2**31):'*', (1, 2**31):'+', (1, 1): '' }

class SymbolExpr(str):
    def __init__(self, s, amin=1, amax=1):
        str.__init__(self, s)
        self.amin = amin
        self.amax = amax > 0 and amax or (2**31)
    def match(self, l, i):
        i0 = i
        while i<len(l) and self==l[i][0] and (i-i0)<=self.amax:
            i += 1
        ok = self.amin <= (i-i0) <= self.amax
        #if ok and (i-i0):
        #   print "match", self, i-i0
        return ok, i
    def copy(self):
        return SymbolExpr(self, self.amin, self.amax)
    def __str__(self):
        return str.__str__(self)+arity[self.amin, self.amax]
    def __repr__(self):
        return str.__repr__(self)+arity[self.amin, self.amax]


class Expr(list):
    recursion_watchdog = [None]
    sep = ' '
    def __init__(self, l, amin=1, amax=1):
        list.__init__(self, l)
        self.amin = amin
        self.amax = amax > 0 and amax or (2**31)
    def match(self, l, i):
        #print "seq", str(self)
        #print Expr.recursion_watchdog
        if (self, i) in Expr.recursion_watchdog:
            #raise TokenizerException("Endless recursion detected !")
            return False, i
        Expr.recursion_watchdog.append((self, i))
        i0 = i
        count = 0
        while i<len(l) and count < self.amax:
            i1 = i
            for e in self:
                 ok, i = e.match(l, i)
                 if not ok:
                     Expr.recursion_watchdog.pop()
                     return self.amin <= count <= self.amax, i1
                     #break
            count += 1
        Expr.recursion_watchdog.pop()
        return self.amin <= count <= self.amax, i
    def copy(self):
        return type(self)(self, self.amin, self.amax)
    def __str__(self):
        a = arity[self.amin, self.amax]
        if a:
            return '('+self.sep.join(imap(str, self))+')'+a
        return self.sep.join(imap(str, self))
    def __repr__(self):
        a = arity[self.amin, self.amax]
        return list.__repr__(self)+a
    def __eq__(self, e):
        return list.__eq__(self, e) and self.amin==e.amin and self.amax==e.amax

class AltExpr(Expr):
    recursion_watchdog = [None]
    sep = ' | '
    def __init__(self, l, amin=1, amax=1):
        Expr.__init__(self, l, amin, amax)
    def match(self, l, i):
        #print AltExpr.recursion_watchdog
        #print "alt", str(self)
        if (self, i) in AltExpr.recursion_watchdog:
            #raise TokenizerException("Endless recursion detected !")
            return False, i
        AltExpr.recursion_watchdog.append((self, i))
        i0 = i
        count = 0
        while i<len(l) and count < self.amax:
            ok, i = max((e.match(l, i) for e in self), key=lambda (ok, i): ok and i or 0)
            if not ok:
                 AltExpr.recursion_watchdog.pop()
                 return self.amin <= count <= self.amax, i
            count += 1
        AltExpr.recursion_watchdog.pop()
        return self.amin <= count <= self.amax, i
    def __repr__(self):
        a = arity[self.amin, self.amax]
        return 'A'+list.__repr__(self)+a


class ProxyExpr(SymbolExpr):
    def __init__(self, s, amin=1, amax=1):
        SymbolExpr.__init__(self, s, amin, amax)
    def copy(self):
        return ProxyExpr.__init__(self, s, amin, amax)
    def match(self, l, i):
        e = named_expression[self].copy()
        e.amin = self.amin
        e.amax = self.amax
        return e.match(l, i)
    def __repr__(self):
        return '@'+SymbolExpr.__repr__(self)

class Anchor(object):
    def __init__(self, atstart):
        self.atstart = atstart
        self.amin = 1
        self.amax = 1
    def match(self, l, i):
        print "anchor", self.atstart and "start" or "end", i, len(l)
        return self.atstart and i==0 or i==len(l), i
    def copy(self):
        return Anchor(self.atstart)

named_expression = {}

def select_arity(e, op):
    if op == '?':
        e.amin = 0
        e.amax = 1
    elif op == '*':
        e.amin = 0
        e.amax = 2**31
    elif op == '+':
        e.amin = 1
        e.amax = 2**31

def sub_compile_expr(tokens, i, inner=False):
    #print "in sub_compile_expr", tokens[i:], inner
    container = AltExpr([Expr([])])
    while i<len(tokens):
        t = tokens[i]
        if t[1]==')':
            if inner:
                i += 1
                #print 'closing list', i<len(tokens) and tokens[i] or 'AT END'
                if i<len(tokens) and tokens[i][1] in '?+*':
                    #print "has arity", tokens[i][1]
                    select_arity(container, tokens[i][1])
                    i += 1
                return i, container
            else:
                raise TokenizerException("Unexpected '('")
        elif t[1]=='(':
            i, expr = sub_compile_expr(tokens, i+1, True)
            container[-1].append(expr)
        elif t[1]=='^':
            container[-1].append(Anchor(True))
            i += 1
        elif t[1]=='$':
            container[-1].append(Anchor(False))
            i += 1
        elif t[1]=='|':
            container.append(Expr([]))
            i += 1
        elif t[0]=='symbol':
            #print "on sym", t[1]
            i+=1
            if named_expression.has_key(t[1]):
                e = ProxyExpr(t[1])
            elif '<'+t[1]+'>' in token_pattern:
                e = SymbolExpr(t[1])
            else:
                raise TokenizerException('Unknown class '+str(t[1]))
            if i<len(tokens):
                op = tokens[i][1]
                if op in '?+*':
                    i += 1
                    select_arity(e, op)
            container[-1].append(e)
        else:
            raise TokenizerException('Unexpected token '+str(t))
    return i, container


def clean_expr(expr):
    if type(expr) not in (Expr, AltExpr):
        return expr
    if len(expr)!=1:
        for i in xrange(len(expr)):
            expr[i] = clean_expr(expr[i])
        return expr
    ret = clean_expr(expr[0])
    #print "squeeze", repr(expr), "and", ret, "(from", repr(expr[0]), ")"
    ret.amin *= expr.amin
    ret.amax = max(expr.amax, ret.amax)
    return ret

def compile_expr(expr, name=None):
    tokens = list(tokenize(expr))
    i, expr = sub_compile_expr(tokens, 0)
    if i!=len(tokens):
        raise TokenizerException('Failed to compile all tokens (%i/%i)'%(i, len(tokens)))
    #print "have bloaty", repr(expr)
    expr = clean_expr(expr)
    #print "squeezed into", repr(expr)
    if name:
        named_expression[name] = expr
    return expr


def match(toks, expr):
    expr = named_expression.has_key(expr) and named_expression[expr].copy() or compile_expr(expr)
    ok, end = expr.match(toks, 0)
    return ok, not ok and -1 or 0, not ok and -1 or end

def find(toks, expr):
    expr = named_expression.has_key(expr) and named_expression[expr].copy() or compile_expr(expr)
    for i in xrange(len(toks)):
        ok, end = expr.match(toks, i)
        if ok:
            return True, i, end
    return False, -1, -1

def find_all(toks, expr):
    ret = []
    expr = named_expression.has_key(expr) and named_expression[expr].copy() or compile_expr(expr)
    for i in xrange(len(toks)):
        ok, end = expr.match(toks, i)
        if ok:
            ret.append(i, end)
    return ret

compile_expr('', name='expr')
compile_expr('', name='var_decl')
compile_expr('', name='qualified_id')
compile_expr('addsubdiv|star', name='arith')
compile_expr('arith|boolop|comp|bitop|assign_set|assign_update', name='binop')
compile_expr('open_square ((qualified_id comma)* qualified_id)? close_square', 'template_spec')
compile_expr('type_spec* symbol template_spec?', name='simple_typename')
compile_expr('(simple_typename namespace_member)* simple_typename', name='qualified_id')
compile_expr('qualified_id (access qualified_id)* (open_square expr close_square)*', name='lvalue')
compile_expr('expr (comma expr)*', name='expr_list')
compile_expr('star* qualified_id (assign_set expr)?', name='core_decl')
compile_expr('qualified_id core_decl', name='param_decl')
compile_expr('param_decl (comma param_decl)*', name='param_decl_list')
compile_expr('lvalue open_paren param_decl_list close_paren', name='func_decl')
compile_expr('lvalue open_paren expr_list close_paren', name='func_call')
compile_expr('^param_decl (comma core_decl)*', name='var_decl')
compile_expr('number | string | char', name='immed')
compile_expr('immed | lvalue | expr (binop expr)+ | incdec lvalue | lvalue incdec | expr ternary expr colon expr', name='expr')

class Cpp(list):
    keywords = {
            'switch': SwitchStatement,
            'if': IfStatement,
            'do': DoWhileStatement,
            'else': ElseStatement,
            'for': ForStatement,
            'while': WhileStatement,
            'return': ReturnStatement,
            'class': ClassDeclStatement,
            'struct': StructDeclStatement,
    }
    c_symbol = '[_a-zA-Z][a-zA-Z0-9:<>,]*'
    symbol = '(?:%s::)*%s'%(c_symbol, c_symbol)
    assign_update_op = '(?<!=)(?:<<|>>|[+*&|/^~-])=(?!=)'
    assign_set_op = '(?<!=)(?<!<<|>>)(?<![+*&|/^~-])=(?!=)'
    assignment_op = '(?:%s|%s)'%(assign_set_op, assign_update_op)
    assignment_re = re.compile(r'^[*]*('+symbol+')(\[[^]]*\])? *'+assignment_op+'([^;]+);$')
    local_var_decl_re = re.compile('^[_a-zA-Z][a-zA-Z0-9<>,*: ]*?('+c_symbol+')( *=.*)?;$')
    var_spec = '(?:(?:volatile|static|register)*)'

    def __init__(self, f):
        list.__init__(self)
        lines = cpp_read(f)
        start = 0
        while start<len(lines):
            #print "ON LINE", start, start<len(lines) and lines[start] or 'OUT OF BOUNDS'
            statement, start = Cpp._parse(self, lines, start, 0, 0)
            #print start, statement
            self.append(statement)
    @staticmethod
    def _parse(context, lines, start, level, context_in_for):
        def line(l):
            #print "%2i, %s%5i: %s"%(level, '   '*level, l, l<len(lines) and lines[l] or "OUT OF BOUNDS")
            return lines[l]
        if lines[start]=='{':
            # empty statement, probably a sub-structure/array data declaration
            ret = CppStatement('<DATA>')
            start -= 1
        else:
            firstword = lines[start].split(' ')[0]
            if Cpp.keywords.has_key(firstword):
                ret = Cpp.keywords[firstword](lines[start])
            else:
                ret = CppStatement(lines[start])
        if (start+1)<len(lines) and lines[start+1] == '{':
            start += 2
            IN_FOR=0
            while start<len(lines) and line(start)!='}':
                statement, start = Cpp._parse(ret.sub, lines, start, level+1, IN_FOR)
                if not IN_FOR:
                    ret.sub.append(statement)
                    if statement.text.startswith('for'):
                        IN_FOR = 2
                else:
                    ret.sub[-1].text += statement.text
                    IN_FOR -= 1
                    ret.sub[-1].sub.extend(statement.sub)
        return context_in_for==0 and Cpp.postprocess(ret, context) or ret, start+1
    @staticmethod
    def postprocess(statement, context):
        if type(statement) is ElseStatement and type(context[-1]) is IfStatement:
            ret = context.pop()
            ret.elses.append(statement)
            return ret
        if type(statement) is WhileStatement and type(context[-1]) is DoWhileStatement:
            ret = context.pop()
            ret.whilecond.append(statement)
            return ret
        if type(statement) in (ClassDeclStatement, StructDeclStatement):
            scopes = ('public', 'private', 'protected')
            strip_scope = lambda scope, text: text.startswith(scope) and text[len(scope)+1:].strip() or text
            strip3 = lambda text: strip_scope('public', strip_scope('private', strip_scope('protected')))
            def strip_helper(st):
                st.text = strip3(st.text)
            statement.sub = map(strip_helper, statement.sub)
            return statement
        m = Cpp.assignment_re.match(statement.text)
        if m:
            # Detect chained assignments and split them
            parts = filter(bool, re.split(Cpp.assignment_op, statement.text))
            if len(parts)>2:
                #print statement.text
                #print parts
                t = statement.text
                # chained assignment !
                expr = parts[-1]
                exprpos = len(t)-len(expr)
                expr = expr[:-1]  # strip final ;
                exprend = exprpos+len(expr)
                for i in xrange(len(parts)-2, -1, -1):
                    lvaluepos = t.rfind(parts[i], 0, exprpos)
                    tmp_assign = t[lvaluepos:exprend].strip()+';'
                    #print "chained assignment#%i:"%i, tmp_assign
                    context.append(AssignmentStatement(tmp_assign))
                    exprpos = lvaluepos
                    exprend = lvaluepos+len(parts[i])
                return context.pop()  # "much more better" ((C) Jack Sparrow) to keep the code simple
            else:
                ret = AssignmentStatement(statement.text)
                #ret.sub = statement.sub
                #ret.lvalue = m.group(1)
                return ret
        if Cpp.local_var_decl_re.match(statement.text):
            #print "DETECTED LOCAL VAR DECL"
            ok, start, end = match(tokenize(statement.text), 'var_decl')
            print ok and "SUCCESS" or "FAILED", statement.text

            ret = LocalDeclStatement(statement.text)
            ret.sub = statement.sub
            return ret
        # tokenize to differentiate the rest
        #print "TOKENIZING", statement.text
        #for x in tokenize(statement.text):
        #    print x
        return statement
    def tree(self):
        ret = []
        map(lambda x: x.tree(container=ret), self)
        return '\n'.join(ret)
    def search_iter(self, predicate):
        for gen in map(lambda x: x.search_iter(predicate), self):
            for x in gen:
                yield x

if __name__=='__main__':
    #
    #cpp = Cpp(open(sys.argv[1]))
    cpp = Cpp(open('calcul/BJS_RHE.cc'))
    #print cpp
    #f = cpp[-1]
    #t = []
    #f.tree(0, t)
    #print t
    #for x in cpp.search_iter(lambda x: type(x) is CppStatement and x.text!='<DATA>'):
    #    print x

    #test = "list(f.search_iter(lambda x: type(x) is AssignmentStatement))"
    #print test
    #eval(test)

