import cppy
from itertools import ifilter

t = lambda x, e: cppy.match(cppy.tokenize(x), '#capture:(%s)' % e)
c = cppy.Cpp(open('tests/demo.i'))
ass = c.sub[-1].sub[-11]
from cppy.cpp import counter as recog_stats
from cppy.cpp import ambiguities as recog_ambiguities
dump = cppy.dump_expression
recog_failures = dict(ifilter(lambda (k, v): v[0]!=v[1], recog_stats.iteritems()))
print "recog_stats", recog_stats
print "recog_failures", recog_failures
print "recog_ambiguities", recog_ambiguities
lr_cc = cppy.Cpp(open('tests/lr.cc'))
#lr_h = cppy.Cpp(open('tests/lr.cc'))
