from parser import Expr, AltExpr
from tokenizer import tokenize_iter
import re
from itertools import ifilter


class item(tuple):

    def __new__(self, name, lst, i):
        return (lst, i)

    def __init__(self, name, lst, i):
        self.lst = lst
        self.i = i
        self.name = name


token_re = re.compile(r"[ \t]*(?:(?P<word>\w+)|(?P<sep>=)|(?P<nl>\R))[ \t]*",
                      re.VERBOSE)


def rules(start, grammar):
    words = [start]
    edit_rule = '@'
    for tokname, tokvalue in tokenize_iter(grammar, token_re):
        if tokname == 'word':
            words.append(tokvalue)
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
        else:
            ret.update(first(((elems, 0, e) for elems in ruleset[e]), ruleset))
    return ret


def follow(itemset, ruleset):
    ret = dict()
    for ruleelems, i, rulename in itemset:
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if e not in ret:
            ret[e] = []
        ret[e].append(closure([(ruleelems, i + 1, rulename)], ruleset))
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
                Ctmp.update(closure(
                    ((e, 0, elems[i]) for e in ruleset[elems[i]]), ruleset))
        C.update(Ctmp)
    return C


def kernel(itemset, start):
    return set(ifilter(lambda (e, i, n): i != 0 or n == '@', itemset))


def lr_sets(start, grammar):
    r = list(rules(start, grammar))
    print r
    R = ruleset(r)
    print R
    I = set(items(r))
    print I
    LR0 = set()
    while I:
        x = closure([min(I)], R)
        I.difference_update(x)
        LR0.add(tuple(x))
    return LR0, R
