import re
from itertools import ifilter, imap, chain



# Code adapted from an answer at stackoverflow.com http://stackoverflow.com/questions/2358890/python-lexical-analysis-and-tokenization
token_pattern = r"""
(?P<number>-?(?:\.[0-9]+|(?:0|[1-9][0-9]*)(?:\.[0-9]*)?)(?:[eE]-?[0-9]+\.?[0-9]*)?)
|(?P<keyword>\b(?:if|else|while|do|for|switch|class|struct|union|return)\b)
|(?P<type_spec>\b(?:typename|template|const|static|register|volatile|extern|long|short|unsigned|signed)\b)
|(?P<symbol>(?!(?P=type_spec))(?!(?P=keyword))\b[a-zA-Z_][a-zA-Z0-9_]*\b)
|(?P<access>(?:\.|->)[*]?)
|(?P<ampersand>[&])
|(?P<comma>[,])
|(?P<semicolon>[;])
|(?P<open_angle>[<])
|(?P<close_angle>[>])
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
|(?P<dot>[.])
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
        #print "at", i, "with", self, 'against', l[i]
        i0 = i
        #print i<len(l), (i-i0)<=self.amax, self==l[i][0]
        while i<len(l) and (i-i0)<self.amax and self==l[i][0]:
            i += 1
            #if i<len(l):
            #    print True, (i-i0)<self.amax, self==l[i][0]
            #else:
            #    print False, (i-i0)<self.amax, self==l[i][0]
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
    def __eq__(self, s):
        return str.__eq__(self, s)


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
compile_expr('simple_typename (namespace_member simple_typename)*', name='qualified_id')
compile_expr('open_paren qualified_id star* close_paren', name='typecast')
compile_expr('star* typecast* qualified_id (access qualified_id)* (open_square expr close_square)*', name='lvalue')
compile_expr('expr (comma expr)*', name='expr_list')
compile_expr('star* qualified_id (assign_set expr)?', name='core_decl')
compile_expr('qualified_id core_decl', name='param_decl')
compile_expr('param_decl (comma param_decl)*', name='param_decl_list')
compile_expr('lvalue open_paren param_decl_list close_paren', name='func_decl')
compile_expr('lvalue open_paren expr_list close_paren', name='func_call')
compile_expr('^param_decl (comma core_decl)*', name='var_decl')
compile_expr('number | string | char', name='immed')
compile_expr('immed | lvalue | expr (binop expr)+ | incdec lvalue | lvalue incdec | expr ternary expr colon expr', name='expr')

