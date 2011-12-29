from scanner import cpp_scanner
from grammar import grammar, start_symbol
from jupyLR import Automaton, pp_ast
import namespace as ns

counter = 0


def make_anon():
    counter += 1
    return "anon_%i" % counter


class CppParser(Automaton):
    def __init__(self):
        Automaton.__init__(self, start_symbol, grammar, cpp_scanner)
        self.scope_stack = [{}]
        self.root = ns.root()
        self.ns = self.root

    def validate_ast(self, ast):
        #print "validating", ast[0], ast[1:]
        print "========================================================"
        pp_ast(ast)
        print "--------------------------------------------------------"
        try:
            ret = getattr(self, ast[0])(ast)
            key = ast[0]
        except AttributeError, ae:
            ret = self.default(ast)
            key = 'default'
        if not ret:
            print "Failed to validate AST with '%s' handler" % key
            print ast
        return ret

    def default(self, ast):
        #print "Defaulting on", ast[0], ast[1:]
        return True

    def namespace_enter(self, ast):
        print "Entering namespace", ast[2][1]
        self.ns = ns.enter(ast[2][1])
        return True

    def namespace_leave(self, ast):
        ns.leave(self.ns)
        print "Leaving namespace"
        return True

    def struc_decl_enter(self, ast):
        key = ast[1][1]
        if len(ast) == 4:
            tag = ast[2][1]
        else:
            tag = make_anon()
        print "Entering", key, tag
        self.ns = ns.enter(tag, key=key)
        return True

    def struc_decl_leave(self, ast):
        ns.leave(self.ns)
        print "Leaving struct/union/class"
        return True

    def typedef(self, ast):
        qid = ast[-2]
        tid = ast[-3]
        print "TYPEDEF", tid, "AS", qid
        ns.add_type(qid[1:], type=tid)
        print self.root
        return True

    def template_type_decl(self, ast):
        free_params = []
        for a in ast:
            if a[0] == 'template_param':
                free_params.append(a[1:])
            if a[0] == 'struct_type_decl':
                stype = a
        qid = stype[1][2]
        print "got qid", qid
        self.decl_type(qid=qid, tid=stype, params=free_params)
        return True

    def decl_type(self, qid, tid, **md):
        ns.add_type(qid[1:], type=tid)


cppy = CppParser()
cppy.debug = True

from time import time
t0 = time()
c = Automaton('translation_unit', open('grammar.txt').read(),
              cpp_scanner)
dt = time() - t0
print dt
