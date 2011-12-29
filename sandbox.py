#!/usr/bin/ipython -i
from parser import cppy

sys.exit(0)




import cppy
from itertools import ifilter, imap, izip, chain
from cppy import namespace as ns

from cppy import item
import re


def make_tokenizer(**tokens):
    if 'discard_names' in tokens:
        discard_names = tokens['discard_names']
        del tokens['discard_names']
    else:
        discard_names = []
    if 'discard_values' in tokens:
        discard_values = tokens['discard_values']
        del tokens['discard_values']
    else:
        discard_values = []
    big_re = re.compile('|'.join('(?P<%s>%s)' % (k, v)
                      for k, v in tokens.iteritems()), re.VERBOSE)

    def _t(text):
        return cppy.tokenizer.tokenize_iter(text, big_re,
                                            discard_names, discard_values)
    return _t


if True:
    lr = item.parser('S', 'S = a S b S  S = a')
    tokenizer = make_tokenizer(a='a', b='b')

    def parse(text):
        return lr.recognize(chain(tokenizer(text), [('$', '$')]))

if False:
    mb = ('namespace_member', '::')
    s = lambda x: ('symbol', x)

    grammar = """
    start = decl
    decl = type var_list semicolon
    type = symbol
    ref_deref = ref_deref star
    var = symbol
    var = ref_deref symbol
    var_list = var
    var_list = var_list comma var
    ref_deref = star
    """

    lr = item.parser('start', grammar)

    T = cppy.tokenize('int foobar, * pouet;')

if False:
    test = open('tests/demo.i')

recognize = cppy.statements.CppMeta.recognize

st = """template<typename _StateT>
inline bool operator==
(const fpos<_StateT>& __lhs, const fpos<_StateT>& __rhs)"""

if False:
    test = """
    typedef int pouet;
    typedef struct { pouet plop; } coin;
    namespace hop {
        typedef struct foobar
        {
            pouet a;
            plop b;
        } alias;
    };
    //typedef hop::alias blabla;
    void toto(int pouet, char* plop) {
        if(pouet) {
            printf("%s hop", plop);
        }
        return pouet*2;
    }
    """

if False:
    t = lambda x, e: cppy.match(cppy.tokenize(x), '#capture:(%s)' % e)
    c = cppy.Cpp(test)
    #c = cppy.Cpp(open('tests/hello.c'))
    ass = c.sub[-1].sub[-11]
    from cppy.cpp import counter as recog_stats
    from cppy.cpp import ambiguities as recog_ambiguities
    dump = cppy.dump_expression
    recog_failures = dict(ifilter(lambda (k, v): v[0] != v[1],
                                  recog_stats.iteritems()))
    print "recog_stats", recog_stats
    print "recog_failures", recog_failures
    print "recog_ambiguities", recog_ambiguities
    lr_cc = cppy.Cpp(open('tests/lr.cc'))
    #lr_h = cppy.Cpp(open('tests/lr.cc'))

if False:
    r = ns.root()
    a = ns.enter('a')
    print a.interpret_tokens((mb, s('toto')))
