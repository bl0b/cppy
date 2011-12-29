#!/usr/bin/env python

import re
import sys
import os
from itertools import ifilter, imap, chain

from parser import tokenize, match, find, find_all, named_expression
from parser import dump_expression, compile_expression
import expressions

from cpp import cpp_read
from statements import *

class Cpp(list):
    keywords = {
            'switch': SwitchStatement,
            'if': IfStatement,
            'do': DoWhileStatement,
            'else': ElseStatement,
            'for': ForStatement,
            'while': WhileStatement,
            'return': ReturnStatement,
            'class': ClassDeclStatement,
            'struct': StructDeclStatement,
    }
    c_symbol = '[_a-zA-Z][a-zA-Z0-9:<>,]*'
    symbol = '(?:%s::)*%s' % (c_symbol, c_symbol)
    assign_update_op = '(?<!=)(?:<<|>>|[+*&|/^~-])=(?!=)'
    assign_set_op = '(?<!=)(?<!<<|>>)(?<![+*&|/^~-])=(?!=)'
    assignment_op = '(?:%s|%s)' % (assign_set_op, assign_update_op)
    assignment_re = re.compile(r'^[*]*(' + symbol + ')(\[[^]]*\])? *'
                                + assignment_op + '([^;]+);$')
    local_var_decl_re = re.compile('^[_a-zA-Z][a-zA-Z0-9<>,*: ]*?('
                                    + c_symbol + ')( *=.*)?;$')
    var_spec = '(?:(?:volatile|static|register)*)'

    def __init__(self, f):
        list.__init__(self)
        lines = cpp_read(f)
        start = 0
        while start < len(lines):
            statement, start = Cpp._parse(self, lines, start, 0, 0)
            self.append(statement)

    @staticmethod
    def _parse(context, lines, start, level, context_in_for):

        def line(l):
            return lines[l]

        if lines[start] == '{':
            ret = CppStatement('<DATA>')
            start -= 1
        else:
            firstword = lines[start].split(' ')[0]
            if firstword in Cpp.keywords:
                ret = Cpp.keywords[firstword](lines[start])
            else:
                ret = CppStatement(lines[start])
        if (start + 1) < len(lines) and lines[start + 1] == '{':
            start += 2
            IN_FOR = 0
            while start < len(lines) and lines[start] != '}':
                statement, start = Cpp._parse(ret.sub, lines, start,
                                              level + 1, IN_FOR)
                if not IN_FOR:
                    ret.sub.append(statement)
                    if statement.text.startswith('for'):
                        IN_FOR = 2
                else:
                    ret.sub[-1].text += statement.text
                    IN_FOR -= 1
                    ret.sub[-1].sub.extend(statement.sub)
        if context_in_for == 0:
            return Cpp.postprocess(ret, context), start + 1
        else:
            return ret, start + 1

    @staticmethod
    def postprocess(statement, context):
        # TESTING !
        print >> sys.stderr, "EXPERIMENTAL RECOGNITION", \
                             CppMeta.recognize(statement.text)
        # END TESTING !
        c_type = len(context) and type(context[-1]) or None
        if type(statement) is ElseStatement and c_type is IfStatement:
            ret = context.pop()
            ret.elses.append(statement)
            return ret
        if type(statement) is WhileStatement and c_type is DoWhileStatement:
            ret = context.pop()
            ret.whilecond.append(statement)
            return ret
        if type(statement) in (ClassDeclStatement, StructDeclStatement):
            scopes = ('public', 'private', 'protected')

            def strip(scope, text):
                if text.startswith(scope):
                    return text[len(scope) + 1:].strip()
                return text

            def strip3(text):
                return strip_scope('public',
                                   strip_scope('private',
                                               strip_scope('protected', text)))

            def strip_helper(st):
                st.text = strip3(st.text)
            statement.sub = map(strip_helper, statement.sub)
            return statement
        m = Cpp.assignment_re.match(statement.text)
        if m:
            # Detect chained assignments and split them
            parts = filter(bool, re.split(Cpp.assignment_op, statement.text))
            if len(parts) > 2:
                #print statement.text
                #print parts
                t = statement.text
                # chained assignment !
                expr = parts[-1]
                exprpos = len(t) - len(expr)
                expr = expr[:-1]  # strip final ;
                exprend = exprpos + len(expr)
                for i in xrange(len(parts)-2, -1, -1):
                    lvaluepos = t.rfind(parts[i], 0, exprpos)
                    tmp_assign = t[lvaluepos:exprend].strip() + ';'
                    #print "chained assignment#%i:"%i, tmp_assign
                    context.append(AssignmentStatement(tmp_assign))
                    exprpos = lvaluepos
                    exprend = lvaluepos + len(parts[i])
                return context.pop()  # "much more better" ((C) Jack Sparrow)
                                      # to keep the code simple
            else:
                ret = AssignmentStatement(statement.text)
                #ret.sub = statement.sub
                #ret.lvalue = m.group(1)
                return ret
        if Cpp.local_var_decl_re.match(statement.text):
            #print "DETECTED LOCAL VAR DECL"
            ok, start, end, grps = match(tokenize(statement.text), 'var_decl')
            #print ok and "SUCCESS" or "FAILED", statement.text, grps
            #    print tokenize(statement.text)
            #    #dump_expression('var_decl')

            ret = VarDeclStatement(statement.text)
            ret.sub = statement.sub
            return ret
        # tokenize to differentiate the rest
        #print "TOKENIZING", statement.text
        #for x in tokenize(statement.text):
        #    print x
        return statement

    def tree(self):
        ret = []
        map(lambda x: x.tree(container=ret), self)
        return '\n'.join(ret)

    def search_iter(self, predicate):
        for gen in map(lambda x: x.search_iter(predicate), self):
            for x in gen:
                yield x


if __name__ == '__main__':
    #
    #cpp = Cpp(open(sys.argv[1]))
    cpp = Cpp(open('calcul/BJS_RHE.cc'))
    #print cpp
    #f = cpp[-1]
    #t = []
    #f.tree(0, t)
    #print t
    #def test_pred(x):
    #    return type(x) is CppStatement and x.text!='<DATA>'
    #for x in cpp.search_iter(test_pred):
    #    print x

    #test = "list(f.search_iter(lambda x: type(x) is AssignmentStatement))"
    #print test
    #eval(test)
