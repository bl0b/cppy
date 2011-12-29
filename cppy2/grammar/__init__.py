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


class CppParser(Automaton):

    def __init__(self):
        t0 = time()
        Automaton.__init__(self, 'translation_unit', grammar, cpp_scanner)
        t1 = time()
        self.build_time = t1 - t0
        self.debug = True

    def validate_ast(self, ast):
        if ast[0] in main_grammar.validators:
            print "VALIDATING", ast, "=>",
            ret = main_grammar.validators[ast[0]](ast)
            print ret
            return ret
        else:
            print "AST", ast
            return ast


cpp = CppParser()

print "Built parser in", cpp.build_time, 'seconds'
print "Unused rules :", cpp.unused_rules
print len(cpp.conflicts()), "conflicts."
