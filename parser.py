__all__ = [ "compile_expr", "match", "find_all", "find", "expressions" ]
import re
from itertools import ifilter, imap, chain

from tokenizer import *

arity = { (0, 1): '?', (0, 2**31):'*', (1, 2**31):'+', (1, 1): '' }


class TokenExpr(str):
    def __init__(self, s, amin=1, amax=1, publish=None):
        str.__init__(self, s)
        self.amin = amin
        self.amax = amax > 0 and amax or (2**31)
        self.publish = publish
    def match(self, l, i, publisher=lambda name, tokens: None):
        i0 = i
        while i<len(l) and (i-i0)<self.amax and self==l[i][0]:
            i += 1
        ok = self.amin <= (i-i0) <= self.amax
        ok and self.publish and publisher(self.publish, l[i0:i])
        return ok, i
    def copy(self):
        return TokenExpr(self, self.amin, self.amax)
    def __str__(self):
        return str.__str__(self)+arity[self.amin, self.amax]
    def __repr__(self):
        return str.__repr__(self)+arity[self.amin, self.amax]
    def __eq__(self, s):
        return str.__eq__(self, s)


class Expr(list):
    recursion_watchdog = [None]
    sep = ' '
    next_is_published = False
    def __init__(self, l, amin=1, amax=1, publish=None):
        list.__init__(self, l)
        self.amin = amin
        self.amax = amax > 0 and amax or (2**31)
        self.publish = publish
    def match(self, l, i, publisher=lambda name, tokens: None):
        #print "seq", str(self)
        #print Expr.recursion_watchdog
        if (self, i) in Expr.recursion_watchdog:
            #raise TokenizerException("Endless recursion detected !")
            return False, i
        Expr.recursion_watchdog.append((self, i))
        i0 = i
        count = 0
        ok = True
        groups = []
        while ok and i<len(l) and count < self.amax:
            i1 = i
            g = []
            for e in self:
                 ok, i = e.match(l, i, lambda n, t: g.append((n, t)))
                 if not ok:
                     break
            if ok:
                count += 1
                groups.append(g)
        Expr.recursion_watchdog.pop()
        ok = self.amin <= count <= self.amax
        print ok, groups
        ok and map(lambda gg: map(lambda grp: publisher(*grp), gg), groups)
        ok and self.publish and publisher(self.publish, l[i0:i])
        return ok, i
    def copy(self):
        return type(self)(self, self.amin, self.amax, self.publish)
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
    #def __init__(self, l, amin=1, amax=1, publish=None):
    #    Expr.__init__(self, l, amin, amax, publish)
    def match(self, l, i, publisher=lambda name, tokens: None):
        #print AltExpr.recursion_watchdog
        #print "alt", str(self)
        if (self, i) in AltExpr.recursion_watchdog:
            #raise TokenizerException("Endless recursion detected !")
            return False, i
        AltExpr.recursion_watchdog.append((self, i))
        i0 = i
        count = 0
        ok = True
        tmp_groups = zip(self, ([] for x in self))
        while ok and i<len(l) and count < self.amax:
            (ok, i), g = max(((e.match(l, i, lambda n, t: g.append((n, t))), g) for e, g in tmp_groups), key=lambda ((ok, i), g): ok and i or 0)
            if not ok:
                 AltExpr.recursion_watchdog.pop()
                 break
            count += 1
        AltExpr.recursion_watchdog.pop()
        print tmp_groups
        ok and g and map(lambda grp: publisher(*grp), g)
        ok and self.publish and publisher(self.publisher, l[i0:i])
        return self.amin <= count <= self.amax, i
    def __repr__(self):
        a = arity[self.amin, self.amax]
        return 'A'+list.__repr__(self)+a


class ProxyExpr(TokenExpr):
    def copy(self):
        return ProxyExpr(self, s, amin, amax, self.publish)
    def match(self, l, i, publisher=lambda name, tokens: None):
        g = []
        def pub(n, t):
            g.append((n, t))
        e = named_expression[self].copy()
        e.amin = self.amin
        e.amax = self.amax
        ok, end = e.match(l, i, pub)
        ok and g and map(lambda grp: publisher(*grp), g)
        ok and self.publish and publisher(self.publish, l[i:end])
        return ok, end
    def __repr__(self):
        return '@'+TokenExpr.__repr__(self)

class Anchor(object):
    def __init__(self, atstart):
        self.atstart = atstart
        self.amin = 1
        self.amax = 1
        self.publish = None
    def match(self, l, i, publisher=lambda name, tokens: None):
        #print "anchor", self.atstart and "start" or "end", i, len(l)
        return self.atstart and i==0 or i==len(l), i
    def copy(self):
        return Anchor(self.atstart)
    def __str__(self):
        return self.atstart and '^' or '$'

named_expression = {}

in_dump = []


def __dump_expr(name):
    expr = named_expression[name]
    if expr in in_dump:
        return
    print name, '=', str(expr)
    in_dump.append(expr)
    def deep_dump(expr):
        if type(expr) is ProxyExpr:
            dump_expression(expr)
        if type(expr) not in (Expr, AltExpr):
            return
        for e in expr:
            if type(e) is ProxyExpr:
                __dump_expr(e)
            if type(e) in (Expr, AltExpr):
                deep_dump(e)
    deep_dump(expr)

def dump_expression(name):
    global in_dump
    in_dump = []
    __dump_expr(name)

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
    next_publishes = None
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
        elif t[1]=='#':
            i += 1
            if tokens[i][0]=='symbol':
                next_publishes = str(tokens[i][1])
                i += 1
            else:
                raise TokenizerException('Expected symbol after sharp')
            if tokens[i][0]!='colon':
                raise TokenizerException('Expected colon after symbol')
            i += 1
        elif t[1]=='^':
            next_publishes = None
            container[-1].append(Anchor(True))
            i += 1
        elif t[1]=='$':
            next_publishes = None
            container[-1].append(Anchor(None))
            i += 1
        elif t[1]=='|':
            container.append(Expr([], publish=next_publishes))
            next_publishes = None
            i += 1
        elif t[0]=='symbol':
            #print "on sym", t[1]
            i+=1
            if named_expression.has_key(t[1]):
                e = ProxyExpr(t[1])
            elif '<'+t[1]+'>' in token_pattern:
                e = TokenExpr(t[1])
            else:
                raise TokenizerException('Unknown class '+str(t[1]))
            e.publish=next_publishes
            next_publishes = None
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
    ret.publish = ret.publish or expr.publish
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
    groups = []
    def pub(name, toks):
        groups.append((name, toks))
    ok, end = expr.match(toks, 0, pub)
    return ok, not ok and -1 or 0, not ok and -1 or end, ok and groups or None

def find(toks, expr):
    expr = named_expression.has_key(expr) and named_expression[expr].copy() or compile_expr(expr)
    groups = []
    def pub(name, toks):
        groups.append((name, toks))
    for i in xrange(len(toks)):
        ok, end = expr.match(toks, i)
        if ok:
            return True, i, end, ok and groups or None
    return False, -1, -1

def find_all(toks, expr):
    ret = []
    expr = named_expression.has_key(expr) and named_expression[expr].copy() or compile_expr(expr)
    i = 0
    while i<len(toks):
        groups = []
        def pub(name, toks):
            groups.append((name, toks))
        ok, end = expr.match(toks, i, pub)
        if ok:
            ret.append((i, groups))
            i = end
        else:
            i += 1
    return ret

def expressions():
    return named_expression.keys()

compile_expr('', name='expr')
compile_expr('', name='var_decl')
compile_expr('', name='qualified_id')
compile_expr('addsubdiv|star', name='arith')
compile_expr('arith|boolop|comp|bitop|assign_set|assign_update', name='binop')
compile_expr('open_square ((qualified_id comma)* qualified_id)? close_square', 'template_spec')
compile_expr('type_spec* symbol template_spec?', name='simple_typename')
compile_expr('(simple_typename namespace_member)* simple_typename', name='qualified_id')
compile_expr('open_paren qualified_id star* close_paren', name='typecast')
compile_expr('star* typecast* qualified_id (access qualified_id)* (open_square expr close_square)*', name='lvalue')
compile_expr('expr (comma expr)*', name='expr_list')
compile_expr('star* qualified_id (assign_set expr)?', name='core_decl')
compile_expr('qualified_id core_decl', name='param_decl')
compile_expr('param_decl (comma param_decl)*', name='param_decl_list')
compile_expr('qualified_id lvalue open_paren param_decl_list close_paren', name='func_decl')
compile_expr('lvalue open_paren expr_list close_paren', name='func_call')
compile_expr('^param_decl (comma core_decl)*', name='var_decl')
compile_expr('number | string | char', name='immed')
compile_expr('immed | lvalue | expr (binop expr)+ | incdec lvalue | lvalue incdec | expr ternary expr colon expr', name='expr')

