__all__ = ['cpp', 'pp_ast']

import main_grammar
import entities
import toplevel
import id_engine
import expressions
import statements

grammar = main_grammar.grammar()

from jupyLR import Automaton, pp_ast
from scanner import cpp_scanner
from time import time
import os
import cPickle


CPPYCACHEDIR = os.path.join(os.getenv('HOME'), '.cppycache')
CPPYCACHE_GRAMMAR = os.path.join(CPPYCACHEDIR, 'grammar')
CPPYCACHE_PARSER = os.path.join(CPPYCACHEDIR, 'parser.pkl')

if not os.path.isdir(CPPYCACHEDIR):
    os.makedirs(CPPYCACHEDIR)

if os.path.exists(CPPYCACHE_GRAMMAR):
    cppycached_grammar = open(CPPYCACHE_GRAMMAR).read()
else:
    cppycached_grammar = ''


class CppParser(Automaton):

    def __init__(self, start='translation_unit'):
        t0 = time()
        Automaton.__init__(self, start, grammar, cpp_scanner)
        t1 = time()
        self.build_time = t1 - t0
        self.debug = True

    def validate_ast(self, ast):
        if ast[0] in main_grammar.validators:
            print "VALIDATING", ast, "=>",
            ret = main_grammar.validators[ast[0]](ast)
            print ret
            print 'ROOT', id_engine.root()
            print 'CURPATH', id_engine.current().full_path
            print 'CURRENT', id_engine.current()
            return ret
        else:
            print "AST", ast
            return ast


cache_is_valid = ((cppycached_grammar == grammar)
                  and os.path.isfile(CPPYCACHE_PARSER))

if cache_is_valid:
    cpp = cPickle.load(open(CPPYCACHE_PARSER))
    print "Reusing cached parser"
else:
    open(CPPYCACHE_GRAMMAR, 'w').write(grammar)
    cpp = CppParser()
    print "Built parser in", cpp.build_time, 'seconds'
    print "Unused rules :", cpp.unused_rules
    cpp.resolve_SR_conflicts()
    print len(cpp.conflicts()), "conflicts."
    cPickle.dump(cpp, open(CPPYCACHE_PARSER, 'w'), 2)
