__all__ = [
"compile_expression", "match", "find_all", "find", "expressions",
"dump_expression"]

import re
from itertools import ifilter, imap, chain, starmap, izip_longest

from tokenizer import *

ARITY_N = 2 ** 31

arity = {(0, 1): '?', (0, ARITY_N): '*', (1, ARITY_N): '+', (1, 1): ''}

detail_dump_match = False


class Ast(object):

    def __init__(self, name, tokens, children):
        self.name = name
        self.tokens = tokens
        self.children = children

    #def __str__(self):
    #    build = [self.name, ":("]
    #    build.append(', '.join(imap(str, self.children)))
    #    build.append(")")
    #    return ''.join(build)

    def __repr__(self):
        build = [self.name, ":["]
        build.append(' '.join(imap(str, self.tokens)))
        build.append("]:(")
        build.append(', '.join(imap(repr, self.children)))
        build.append(")")
        return ''.join(build)

    __str__ = __repr__

    def dump(self, level=0):
        prefix = "   " * level
        print prefix, "+", self.name
        print prefix, ":", ' '.join(imap(str, self.tokens))
        if self.children:
            print prefix, "`--+"
            for c in self.children:
                c.dump(level + 1)


def str_pub(e):
    return e.publish and '#%s:' % e.publish or ''


def make_tuple(x):
    if type(x) is list:
        return tuple(x)
    elif hasattr(x, '__iter__'):
        return tuple(imap(make_tuple, x))
    else:
        return x


def make_publisher(uniq=False):
    if uniq:
        groups = set()

        def _pub(n, e, s):
            groups.add(Ast(n, e, s))
            #groups.add((n, make_tuple(e), make_tuple(s)))
    else:
        groups = []

        def _pub(n, e, s):
            groups.append(Ast(n, e, s))
            #groups.append((n, make_tuple(e), make_tuple(s)))
    return _pub, groups


class TokenExpr(str):
    "Simply match against the current token type."

    def __new__(self, s, amin=1, amax=1, publish=None):
        """courtesy of http://
bytes.com/topic/python/answers/32098-my-experiences-subclassing-string"""
        return str.__new__(self, s)

    def __init__(self, s, amin=1, amax=1, publish=None):
        self.amin = amin
        self.amax = amax > 0 and amax or (ARITY_N)
        self.publish = publish

    def match(self, l, i, publisher=lambda name, tokens: None):
        i0 = i
        while i < len(l) and (i - i0) < self.amax and self == l[i][0]:
            i += 1
        ok = self.amin <= (i - i0) <= self.amax
        ok and self.publish and publisher(self.publish, l[i0:i], tuple())
        if detail_dump_match:
            print "matched", (i - i0), (self.amin, self.amax), self
        return ok, i

    def copy(self):
        return TokenExpr(self, self.amin, self.amax)

    def __str__(self):
        return str_pub(self) + str.__str__(self) + arity[self.amin, self.amax]

    def __repr__(self):
        return str_pub(self) + str.__repr__(self) + arity[self.amin, self.amax]

    def __eq__(self, s):
        streq = str.__eq__(self, s)
        if isinstance(s, TokenExpr):
            return streq and self.amin == s.amin and self.amax == s.amax
        return str.__eq__(self, s)


class Expr(list):
    "Match a list of sequential sub-expressions"
    sep = ' '
    next_is_published = False
    recursion_watchdog = []

    def __init__(self, l, amin=1, amax=1, publish=None):
        list.__init__(self, l)
        self.amin = amin
        self.amax = amax > 0 and amax or (ARITY_N)
        self.publish = publish

    def match(self, l, i, publisher=lambda name, tokens: None):
        if not self:
            return False, i
        if (self, i) in self.recursion_watchdog:
            print (self, i), self.recursion_watchdog
            return False, i
        i0 = i
        count = 0
        ok = True
        pub, groups = make_publisher()
        self.recursion_watchdog.append((self, int(i)))
        while ok and i < len(l) and count < self.amax:
            i1 = i
            subpub, subgrps = make_publisher()
            for e in self:
                ok, i = e.match(l, i, subpub)
                if not ok:
                    break
            if ok:
                count += 1
                for g in subgrps:
                    pub(g.name, g.tokens, g.children)
                #list(starmap(pub, subgrps))
        self.recursion_watchdog.pop()
        if ok:
            i1 = i
        ok = self.amin <= count <= self.amax
        if ok:
            if self.publish:
                publisher(self.publish, l[i0:i1], groups)
            else:
                for g in groups:
                    publisher(g.name, g.tokens, g.children)
        #ok and self.publish and publisher(self.publish, l[i0:i1], groups)
        #ok and groups and list(starmap(publisher, groups))
        if detail_dump_match:
            print "list", repr(self), "matched", count, (self.amin, self.amax)
        return ok, i1

    def copy(self):
        return type(self)(self, self.amin, self.amax, self.publish)

    def __str__(self):
        a = arity[self.amin, self.amax]
        p = str_pub(self)

        def nice_str(x):
            must_enclose = type(x) in (Expr, AltExpr) and len(x) > 1
            return must_enclose and "(%s)" % str(x) or str(x)

        if a or p:
            return p + '(' + self.sep.join(imap(nice_str, self)) + ')' + a
        return self.sep.join(imap(nice_str, self))

    def __repr__(self):
        a = arity[self.amin, self.amax]
        return 'Seq(' + str_pub(self) + list.__repr__(self) + a + ')'

    def __eq__(self, e):
        return type(self) == type(e) \
               and reduce(lambda a, b: a and b[0] == b[1],
                          izip_longest(self, e), True) \
               and self.amin == e.amin \
               and self.amax == e.amax


class AltExpr(Expr):
    """Match a list of alternative sub-expressions.
    Only the first longest match is retained."""
    recursion_watchdog = []
    sep = ' | '

    @classmethod
    def matcher(cls, l, i):

        def mk_match(e, (spub, sgrp)):
            if (e, i) in cls.recursion_watchdog:
                return False, i, sgrp
            cls.recursion_watchdog.append((e, int(i)))
            ok, iprime = e.match(l, i, spub)
            cls.recursion_watchdog.pop()
            return ok, iprime, sgrp
        return mk_match

    def match(self, l, i, publisher=lambda name, tokens, sub: None):
        if not self:
            return False, i
        i0 = i
        count = 0
        ok = True
        subpub, groups = make_publisher()
        while ok and i < len(l) and count < self.amax:
            matcher = self.matcher(l, i)
            tmp_groups = zip(self, (make_publisher() for x in self))
            ok, i, g = max(starmap(matcher, tmp_groups),
                           key=lambda (ok, i, g): ok and i or 0)
            if not ok:
                break
            #ok and self.publish and subpub(self.publish, l[i0:i])
            if ok:
                for x in g:
                    subpub(x.name, x.tokens, x.children)
            #ok and g and list(starmap(subpub, g))
            count += 1

        ok = self.amin <= count <= self.amax
        if ok:
            if self.publish:
                publisher(self.publish, l[i0:i], groups)
            else:
                for g in groups:
                    publisher(g.name, g.tokens, g.children)
        #ok and self.publish and publisher(self.publish, l[i0:i])
        #ok and groups and list(starmap(publisher, groups))
        if detail_dump_match:
            print "alt matched", count, (self.amin, self.amax), self
        return ok, i

    def __repr__(self):
        a = arity[self.amin, self.amax]
        return 'Alt(' + str_pub(self) + list.__repr__(self) + a + ')'


class ProxyExpr(TokenExpr):
    "Match a named expression instead of a simple token."

    def __new__(self, l, amin=1, amax=1, publish=None):
        return TokenExpr.__new__(self, l, amin, amax, publish)

    def __init__(self, l, amin=1, amax=1, publish=None):
        TokenExpr.__init__(self, l, amin, amax, publish)
        self.cache = type(l) is ProxyExpr and l.cache or None
        self.e = type(l) is ProxyExpr and l.e or None

    def copy(self):
        return ProxyExpr(self, amin, amax, self.publish)

    def match(self, l, i, publisher=lambda name, tokens: None):
        ne = named_expression[self]
        count = 0
        ok = True
        i0 = i
        pub, g = make_publisher()
        while ok and i < len(l) and count < self.amax:
            ok, i = ne.match(l, i, pub)
            count += int(ok)
        ok = self.amin <= count <= self.amax
        if ok:
            if self.publish:
                publisher(self.publish, l[i0:i], g)
            else:
                for grp in g:
                    publisher(grp.name, grp.tokens, grp.children)
        #ok and self.publish and publisher(self.publish, l[i0:i])
        #ok and g and map(lambda grp: publisher(*grp), g)
        return ok, i

    def __eq__(self, e):
        streq = str.__eq__(self, e)
        if isinstance(e, ProxyExpr):
            return streq and self.amin == e.amin and self.amax == e.amax
        return streq

    def __repr__(self):
        return str_pub(self) + '@' + TokenExpr.__repr__(self)

    __str__ = TokenExpr.__str__


class Anchor(object):
    "Match start or end of token list."

    def __init__(self, atstart):
        self.atstart = atstart
        self.amin = 1
        self.amax = 1
        self.publish = None
        self.cache = None

    def match(self, l, i, publisher=lambda name, tokens: None):
        #print "anchor", self.atstart and "start" or "end", i, len(l)
        if self.cache == (l, i):
            return False, i
        self.cache = (l, i)
        return self.atstart and i == 0 or i == len(l), i

    def copy(self):
        return Anchor(self.atstart)

    def __str__(self):
        return self.atstart and '^' or '$'

    def __eq__(self, e):
        return type(e) is Anchor and self.atstart == e.atstart


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
    "Display human-friendly form of named expression and its dependencies."
    global in_dump
    in_dump = []
    __dump_expr(name)


def select_arity(e, op):
    if op == '?':
        e.amin = 0
        e.amax = 1
    elif op == '*':
        e.amin = 0
        e.amax = ARITY_N
    elif op == '+':
        e.amin = 1
        e.amax = ARITY_N


def sub_compile_expr(tokens, i, inner=False):
    #print "in sub_compile_expr", tokens[i:], inner
    global next_publishes
    container = AltExpr([Expr([])], publish=next_publishes)
    next_publishes = None
    while i < len(tokens):
        t = tokens[i]
        if t[1] == ')':
            if inner:
                i += 1
                #print 'closing list', i<len(tokens) and tokens[i] or 'AT END'
                if i < len(tokens) and tokens[i][1] in '?+*':
                    #print "has arity", tokens[i][1]
                    select_arity(container, tokens[i][1])
                    i += 1
                return i, container
            else:
                raise TokenizerException("Unexpected '('")
        elif t[1] == '(':
            i, expr = sub_compile_expr(tokens, i + 1, True)
            container[-1].append(expr)
        elif t[1] == '#':
            i += 1
            if tokens[i][0] == 'symbol':
                next_publishes = str(tokens[i][1])
                i += 1
            else:
                raise TokenizerException('Expected symbol after sharp '
                                         + str(i) + ' ' + str(tokens))
            if tokens[i][0] != 'colon':
                raise TokenizerException('Expected colon after symbol '
                                         + str(i) + ' ' + str(tokens))
            i += 1
        elif t[1] == '^':
            next_publishes = None
            container[-1].append(Anchor(True))
            i += 1
        elif t[1] == '$':
            next_publishes = None
            container[-1].append(Anchor(None))
            i += 1
        elif t[1] == '|':
            container.append(Expr([], publish=next_publishes))
            next_publishes = None
            i += 1
        elif t[0] in ('symbol'):
            #print "on sym", t[1]
            i += 1
            if t[1] in named_expression:
                e = ProxyExpr(t[1])
            elif '<' + t[1] + '>' in token_pattern:
                e = TokenExpr(t[1])
            else:
                raise TokenizerException('Unknown class ' + str(t[1]))
            e.publish = next_publishes
            next_publishes = None
            if i < len(tokens):
                op = tokens[i][1]
                if op in '?+*':
                    i += 1
                    select_arity(e, op)
            container[-1].append(e)
        else:
            raise TokenizerException('Unexpected token ' + str(t))
    return i, container


def clean_expr(expr):
    if type(expr) not in (Expr, AltExpr):
        return expr
    if len(expr) != 1 or expr.publish is not None:
        for i in xrange(len(expr)):
            expr[i] = clean_expr(expr[i])
        return expr
    ret = clean_expr(expr[0])
    #print "squeeze", repr(expr), "and", ret, "(from", repr(expr[0]), ")"
    ret.amin *= expr.amin
    ret.amax = max(expr.amax, ret.amax)
    ret.publish = ret.publish or expr.publish
    return ret


def compile_expression(expr,
                   name=None):
    "Compile an expression."
    global next_publishes
    next_publishes = None
    tokens = list(tokenize(expr))
    i, expr = sub_compile_expr(tokens, 0)
    if i != len(tokens):
        msg = 'Failed to compile all tokens (%i/%i)' % (i, len(tokens))
        raise TokenizerException(msg)
    #print "have bloaty", repr(expr)
    expr = clean_expr(expr)
    #print "squeezed into", repr(expr)
    if name:
        named_expression[name] = expr
    return expr


def mk_expr(expr):
    if expr in named_expression:
        return named_expression[expr].copy()
    return compile_expression(expr)


def match(toks, expr):
    """Match an expression against a list of tokens (match from start only).
    Returns found:bool, start=0, end:int, groups:list or None
    """
    Expr.recursion_watchdog = []
    AltExpr.recursion_watchdog = []
    expr = mk_expr(expr)
    pub, groups = make_publisher()
    ok, end = expr.match(toks, 0, pub)
    if ok:
        return True, 0, end, sorted(groups)
    else:
        return False, -1, -1, None


def find(toks, expr):
    """Match an expression against a list of tokens (match anywhere).
    Returns found:bool, start=0, end:int, groups:list or None
    """
    Expr.recursion_watchdog = []
    AltExpr.recursion_watchdog = []
    expr = mk_expr(expr)
    for i in xrange(len(toks)):
        pub, groups = make_publisher()
        ok, end = expr.match(toks, i, pub)
        if ok:
            return True, i, end, ok and sorted(groups) or None
    return False, -1, -1


def find_all(toks, expr):
    """Match an expression against a list of tokens (match anywhere).
    Returns list of (found:bool, start=0, end:int, groups:list or None)
    """
    ret = []
    expr = mk_expr(expr)
    i = 0
    while i < len(toks):
        Expr.recursion_watchdog = []
        AltExpr.recursion_watchdog = []
        pub, groups = make_publisher()
        ok, end = expr.match(toks, i, pub)
        if ok:
            ret.append((i, sorted(groups)))
            i = end
        else:
            i += 1
    return ret


def expressions():
    "Returns all defined expression names."
    return named_expression.keys()
