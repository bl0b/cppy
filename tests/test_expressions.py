from unittest2 import TestCase
import cppy


def match(t, e):
    return cppy.match(cppy.tokenize(t), e)


def find(t, e):
    return cppy.find(cppy.tokenize(t), e)


def find_all(t, e):
    return cppy.find_all(cppy.tokenize(t), e)


class Test_Expressions(TestCase):

    def expect(self, f, t, e, expected):
        print "=========================="
        print f.__name__
        print str(t)
        print repr(cppy.compile_expression(e))
        print "-------------"
        result = f(t, e)
        self.messages.append("%s(%s, %s)" % (
            str(f.__name__), repr(t), repr(e)))
        self.expectations.append(expected)
        self.results.append(result)

    def test_grouping(self):
        self.expectations = []
        self.messages = []
        self.results = []
        xfoo = [('x', (('symbol', 'foo'),))]
        xnewfoo = [('x', (('new', 'new'), ('symbol', 'foo')))]
        exp = (
            (match, 'foo', '#x:symbol',
                (True, 0, 1, xfoo)),
            (match, 'foo', '#x:keyword',
                (False, -1, -1, None)),
            (match, 'new foo', 'new #x:symbol',
                (True, 0, 2, xfoo)),
            (match, 'new foo', '(new #x:symbol|symbol)',
                (True, 0, 2, xfoo)),
            (match, 'new foo', '#x:(new symbol|delete)',
                (True, 0, 2, xnewfoo)),
            (match, 'new foo', '#x:(new symbol|symbol)',
                (True, 0, 2, xnewfoo)),
        )

        for e in exp:
            self.expect(*e)

        self.maxDiff = None
        print dir(self)
        self.assertSequenceEqual(
                zip(self.messages, self.results),
                zip(self.messages, self.expectations))

    def runTest(self):
        test_grouping(self)
