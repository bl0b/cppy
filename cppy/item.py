from parser import Expr, AltExpr
from tokenizer import tokenize_iter
import re
from itertools import ifilter, izip, chain, imap


token_re = re.compile(r"[ \t\n]*(?:(?P<word>\w+)|(?P<sep>=))[ \t\n]*",
                      re.VERBOSE)


def rules(start, grammar, kw):
    words = [start]
    edit_rule = '@'
    kw.add(edit_rule)
    for tokname, tokvalue in tokenize_iter(grammar, token_re):
        if tokname == 'word':
            words.append(tokvalue)
            kw.add(tokvalue)
        elif tokname == 'sep':
            tmp = words.pop()
            yield (edit_rule, tuple(words))
            edit_rule = tmp
            words = []
    yield (edit_rule, tuple(words))


def ruleset(rules):
    ret = {}
    for rulename, elems in rules:
        if rulename not in ret:
            ret[rulename] = []
        ret[rulename].append(elems)
    return ret


def rule_items(rulename, elems):
    return ((elems, i, rulename) for i in xrange(len(elems) + 1))


def items(rules):
    ret = []
    for rulename, elems in rules:
        ret.extend(rule_items(rulename, elems))
    return ret


def first(itemset, ruleset):
    ret = set()
    for ruleelems, i, rulename in itemset:
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if not e in ruleset:
            ret.add(e)
        #else:
        #   ret.update(first(((elems, 0, e) for elems in ruleset[e]), ruleset))
    return ret


def follow(itemset, ruleset):
    ret = dict()
    for ruleelems, i, rulename in itemset:
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if e not in ret:
            ret[e] = set()
        ret[e].update(closure([(ruleelems, i + 1, rulename)], ruleset))
    return ret


def closure(itemset, ruleset):
    C = set(itemset)
    last = -1
    while len(C) != last:
        last = len(C)
        Ctmp = set()
        for item in C:
            elems, i, name = item
            if i == len(elems):
                continue
            if elems[i] in ruleset:
                Ctmp.update((e, 0, elems[i]) for e in ruleset[elems[i]])
        C.update(Ctmp)
    return C


def kernel(itemset, start):
    return set(ifilter(lambda (e, i, n): i != 0 or n == '@', itemset))


def lr_sets(start, grammar):
    kw = set()
    kw.add('$')
    r = list(rules(start, grammar, kw))
    R = ruleset(r)
    I = set(items(r))
    LR0 = set()
    x = closure([(R['@'][0], 0, '@')], R)
    stack = [tuple(sorted(x))]
    while stack:
        x = stack.pop()
        print "set", x
        LR0.add(x)
        F = follow(x, R)
        for t, s in F.iteritems():
            s = tuple(sorted(s))
            if s not in LR0:
                stack.append(s)
    return LR0, R, r, kw


class parser(object):

    def __init__(self, start_sym, grammar):
        LR0, self.R, self.rules, self.kw_set = lr_sets(start_sym, grammar)
        self.I = set(items(self.rules))
        self.initial_items = filter(lambda (e, i, n): i == 0 and n == '@',
                                    self.I)
        print "initial items", self.initial_items
        self.LR0 = list(LR0)
        self.LR0_idx = {}
        for i, s in enumerate(self.LR0):
            self.LR0_idx[s] = i
        self.initial_state = self.index(self.initial_items)
        self.compute_ACTION()

    def closure(self, s):
        return tuple(sorted(closure(s, self.R)))

    def kernel(self, s):
        return kernel(s, self.R)

    def index(self, s):
        return self.LR0_idx[self.closure(s)]

    def compute_GOTO(self):
        self.GOTO = []
        for s in self.LR0:
            f = {}
            for tok, dest in follow(s, self.R).iteritems():
                f[tok] = self.LR0_idx[self.closure(dest)]
            self.GOTO.append(f)

    def init_row(self, init=None):
        if init is None:
            init = []
        ret = {}
        for kw in self.kw_set:
            ret[kw] = [] + init
        return ret

    def follows(self, item):
        items = filter(lambda (e, i, n): e[i - 1] == item[2] and len(e) != i,
                       self.I)
        return first(closure(items, self.R), self.R)

#        def f_iter(thisn):
#            for e, i, n in self.I:
#                if e[i - 1] == thisn:
#                    if i == len(e):
#                        for k in f_iter(n):
#                            yield k
#                    else:
#                        for k in first(closure([(e, i, n)], self.R), self.R):
#                            yield k
#
#        thise, thisi, thisn = item
#        return set(f_iter(thisn))

    def compute_ACTION(self):
        self.compute_GOTO()
        self.ACTION = []
        for s, g in izip(self.LR0, self.GOTO):
            action = self.init_row()
            reductions = filter(lambda (elems, i, name): i == len(elems), s)
            if reductions:
                for k in reductions:
                    if k[2] == '@':
                        action['$'].append(('A',))
                    else:
                        for kw in self.follows(k):
                            action[kw].append(('R', k))
            for tok, dest in g.iteritems():
                action[tok].append(('S', dest))
            self.ACTION.append(action)
        print self.action_to_str()

    def action_to_str(self):

        def ac_str(c):
            if c[0] == 'R':
                return 'R:' + c[1][2]
            return ''.join(imap(str, c))

        def cell(i, kw):
            if i >= 0:
                return ','.join(map(ac_str, self.ACTION[i][kw]))
            if i < 0:
                return str(kw)

        def col_width(kw):
            return reduce(max, chain([type(kw) is str and len(kw) or kw],
                                     (len(cell(i, kw))
                                      for i in xrange(len(self.ACTION)))))

        col_labels = sorted(self.kw_set,
                            key=lambda x: type(x) is int and '|' + str(x)
                                          or x == '$' and '|$'
                                          or x)
        col_widths = [col_width(kw) for kw in col_labels]

        def row(i):
            return ' | '.join(cell(i, kw).center(cw)
                              for kw, cw in izip(col_labels, col_widths))

        header = '    | ' + row(-1) + '\n'
        return header + '\n'.join(('%3i | ' % i) + row(i)
                                  for i in xrange(len(self.ACTION)))

    def recognize(self, tokens):

        class Automaton(object):

            def __init__(self, initial_state):
                self.toki = iter(tokens)
                self.state_stack = [initial_state]
                self.input_stack = []
                self.next_token()

            def next_token(self):
                self.input_stack.append(self.toki.next())

            def shift(self, next_state):
                self.state_stack.append(next_state)
                self.next_token()

            def reduce(self, name, count):
                self.state_stack = self.state_stack[: - count]
                self.input_stack = self.input_stack[: - count]

        A = Automaton(self.initial_state)

        while True:
            ac = self.ACTION[A.state_stack[-1]][A.input_stack[-1]]
            print ac
            if len(ac) == 0:
                print "ERROR", A.state_stack, A.input_stack
                break
            if len(ac) > 1:
                print "CONFLICT!", ac
                break
            ac = ac[0]
            if ac[0] == 'R':
                A.reduce(ac[1][2], ac[1][1])
                goto = self.ACTION[A.state_stack[-1]][ac[1][2]]
                print "goto", goto
                A.state_stack.append(goto[0][1])
            elif ac[0] == 'S':
                A.shift(ac[1])
            elif ac[0] == 'A':
                print "DONE"
                break
            print A.state_stack, A.input_stack
        return A
