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
        self.assertEqual(f(t, e), expected, msg="Matching '%s' against %s" %
                         (t, str(e)))

    def test_grouping(self):
        xfoo = [('x', [('symbol', 'foo')])]
        xnewfoo = [('x', [('new', 'new'), ('symbol', 'foo')])]
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

    def runTest(self):
        test_grouping(self)
