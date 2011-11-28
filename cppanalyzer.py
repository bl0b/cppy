#!/usr/bin/env python

import re
import sys, os
from itertools import ifilter, imap, chain

from parser import tokenize, match, find, find_all, named_expression, dump_expression

# xreadlines with stripping of empty lines and single-line comments
def cpp_strip_slc(f):
    reader = hasattr(f, 'xreadlines') and f.xreadlines() or hasattr(f, 'splitlines') and f.splitlines() or f
    for line in reader:
        components = line.strip().split('//')
        if len(components) and len(components[0]) and components[0][0]!='#':
            yield components[0]


multiline_comment = re.compile(r'/[*].*?[*]/')

def cpp_strip_mlc(f):
    big_buffer = ' '.join(cpp_strip_slc(f))
    return ' '.join(multiline_comment.split(big_buffer))


reformat = {
        '{': '\n{\n',
        '}': '\n}\n',
        ';': ';\n',
        r'\ ': ' ',
}

def cpp_read(f):
    no_comment = cpp_strip_mlc(f)
    for match, replace in reformat.iteritems():
        no_comment = replace.join(ifilter(lambda x:x, no_comment.split(match)))
    return filter(lambda s: len(s) and s!=',', imap(str.strip, no_comment.splitlines()))

class CppStatement(object):
    tag = 'cpp'
    extra_contents = []
    def __init__(self, text):
        #print "init cpp statement", type(self), text
        self.text = text
        self.sub = []
        for xc in self.extra_contents:
            setattr(self, xc, [])
    def __str__(self):
        ret = type(self).tag+'('+self.text
        if self.sub:
            ret += ' [%i sub-statements])'%len(self.sub)
        else:
            ret += ')'
        return ret
    __repr__ = __str__
    def tree(self, level, container):
        container.append('%s%s'%('   '*level, self.text))
        map(lambda cts: map(lambda x : x.tree(level+1, container), getattr(self, cts)), chain(('sub',), self.extra_contents))
        return container
    def search_iter(self, predicate):
        if predicate(self):
            yield self
        for statement in chain(self.sub, (s for cts in self.extra_contents for s in getattr(self, cts))):
            for x in statement.search_iter(predicate):
                yield x
        #map(lambda cts: map(lambda x: x.search_iter(predicate), getattr(self, cts)), chain(('sub',), self.extra_contents))

class IfStatement(CppStatement):
    tag = 'if'
    extra_contents = ('elses',)

class ElseStatement(CppStatement):
    tag = 'else'

class ForStatement(CppStatement):
    tag = 'for'

class SwitchStatement(CppStatement):
    tag = 'switch'

class DoWhileStatement(CppStatement):
    tag = 'do'
    extra_contents = ('whilecond',)

class WhileStatement(CppStatement):
    tag = 'while'

class ReturnStatement(CppStatement):
    tag = 'return'

class AssignmentStatement(CppStatement):
    tag = 'assign'
    def __init__(self, text):
        CppStatement.__init__(self, text)
        parts = re.split(Cpp.assignment_op, text)
        self.lvalue = parts[0]
        self.assign_type = re.findall(Cpp.assign_set_op, text) and 'set' or 'update'

class LocalDeclStatement(CppStatement):
    tag = 'local'

class ClassDeclStatement(CppStatement):
    tag = 'class'

class StructDeclStatement(CppStatement):
    tag = 'struct'


class CppExpr(list):
    ANY = 'any'
    SYMBOL = 'symbol'
    KEYWORD = 'keyword'
    OPERATOR = 'operator'
    LIST = 'list'

    def __init__(self, typ, text, contents):
        self.typ = typ
        if text.endswith(';'):
            text = text[:-1]
        self.text = text
        list.__init__(self, contents)
    def __str__(self):
        return self.text

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
    symbol = '(?:%s::)*%s'%(c_symbol, c_symbol)
    assign_update_op = '(?<!=)(?:<<|>>|[+*&|/^~-])=(?!=)'
    assign_set_op = '(?<!=)(?<!<<|>>)(?<![+*&|/^~-])=(?!=)'
    assignment_op = '(?:%s|%s)'%(assign_set_op, assign_update_op)
    assignment_re = re.compile(r'^[*]*('+symbol+')(\[[^]]*\])? *'+assignment_op+'([^;]+);$')
    local_var_decl_re = re.compile('^[_a-zA-Z][a-zA-Z0-9<>,*: ]*?('+c_symbol+')( *=.*)?;$')
    var_spec = '(?:(?:volatile|static|register)*)'

    def __init__(self, f):
        list.__init__(self)
        lines = cpp_read(f)
        start = 0
        while start<len(lines):
            #print "ON LINE", start, start<len(lines) and lines[start] or 'OUT OF BOUNDS'
            statement, start = Cpp._parse(self, lines, start, 0, 0)
            #print start, statement
            self.append(statement)
    @staticmethod
    def _parse(context, lines, start, level, context_in_for):
        def line(l):
            #print "%2i, %s%5i: %s"%(level, '   '*level, l, l<len(lines) and lines[l] or "OUT OF BOUNDS")
            return lines[l]
        if lines[start]=='{':
            # empty statement, probably a sub-structure/array data declaration
            ret = CppStatement('<DATA>')
            start -= 1
        else:
            firstword = lines[start].split(' ')[0]
            if Cpp.keywords.has_key(firstword):
                ret = Cpp.keywords[firstword](lines[start])
            else:
                ret = CppStatement(lines[start])
        if (start+1)<len(lines) and lines[start+1] == '{':
            start += 2
            IN_FOR=0
            while start<len(lines) and line(start)!='}':
                statement, start = Cpp._parse(ret.sub, lines, start, level+1, IN_FOR)
                if not IN_FOR:
                    ret.sub.append(statement)
                    if statement.text.startswith('for'):
                        IN_FOR = 2
                else:
                    ret.sub[-1].text += statement.text
                    IN_FOR -= 1
                    ret.sub[-1].sub.extend(statement.sub)
        return context_in_for==0 and Cpp.postprocess(ret, context) or ret, start+1
    @staticmethod
    def postprocess(statement, context):
        if type(statement) is ElseStatement and type(context[-1]) is IfStatement:
            ret = context.pop()
            ret.elses.append(statement)
            return ret
        if type(statement) is WhileStatement and type(context[-1]) is DoWhileStatement:
            ret = context.pop()
            ret.whilecond.append(statement)
            return ret
        if type(statement) in (ClassDeclStatement, StructDeclStatement):
            scopes = ('public', 'private', 'protected')
            strip_scope = lambda scope, text: text.startswith(scope) and text[len(scope)+1:].strip() or text
            strip3 = lambda text: strip_scope('public', strip_scope('private', strip_scope('protected')))
            def strip_helper(st):
                st.text = strip3(st.text)
            statement.sub = map(strip_helper, statement.sub)
            return statement
        m = Cpp.assignment_re.match(statement.text)
        if m:
            # Detect chained assignments and split them
            parts = filter(bool, re.split(Cpp.assignment_op, statement.text))
            if len(parts)>2:
                #print statement.text
                #print parts
                t = statement.text
                # chained assignment !
                expr = parts[-1]
                exprpos = len(t)-len(expr)
                expr = expr[:-1]  # strip final ;
                exprend = exprpos+len(expr)
                for i in xrange(len(parts)-2, -1, -1):
                    lvaluepos = t.rfind(parts[i], 0, exprpos)
                    tmp_assign = t[lvaluepos:exprend].strip()+';'
                    #print "chained assignment#%i:"%i, tmp_assign
                    context.append(AssignmentStatement(tmp_assign))
                    exprpos = lvaluepos
                    exprend = lvaluepos+len(parts[i])
                return context.pop()  # "much more better" ((C) Jack Sparrow) to keep the code simple
            else:
                ret = AssignmentStatement(statement.text)
                #ret.sub = statement.sub
                #ret.lvalue = m.group(1)
                return ret
        if Cpp.local_var_decl_re.match(statement.text):
            #print "DETECTED LOCAL VAR DECL"
            ok, start, end = match(tokenize(statement.text), 'var_decl')
            print ok and "SUCCESS" or "FAILED", statement.text
            if not ok:
                print tokenize(statement.text)
                #dump_expression('var_decl')

            ret = LocalDeclStatement(statement.text)
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

if __name__=='__main__':
    #
    #cpp = Cpp(open(sys.argv[1]))
    cpp = Cpp(open('calcul/BJS_RHE.cc'))
    #print cpp
    #f = cpp[-1]
    #t = []
    #f.tree(0, t)
    #print t
    #for x in cpp.search_iter(lambda x: type(x) is CppStatement and x.text!='<DATA>'):
    #    print x

    #test = "list(f.search_iter(lambda x: type(x) is AssignmentStatement))"
    #print test
    #eval(test)

