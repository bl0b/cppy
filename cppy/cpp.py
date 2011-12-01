__all__ = ['Cpp']

import re
import sys
from itertools import ifilter, imap
import expressions
from parser import tokenize, match, find, find_all, compile_expression
from statements import *


def cpp_strip_slc(f):
    # xreadlines with stripping of empty lines and single-line comments
    reader = hasattr(f, 'xreadlines') and f.xreadlines() \
             or hasattr(f, 'splitlines') and f.splitlines() \
             or f
    for line in reader:
        components = line.strip().split('//')
        if len(components) and len(components[0]) and components[0][0] != '#':
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
    nocomment = cpp_strip_mlc(f)
    for match, replace in reformat.iteritems():
        nocomment = replace.join(ifilter(lambda x: x, nocomment.split(match)))
    lines = imap(str.strip, nocomment.splitlines())
    return filter(lambda s: s not in ('', ','), lines)


class Cpp(list):
    keywords = {
            'switch': SwitchStatement,
            'delete': DeleteStatement,
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
            kw = None
            for w in Cpp.keywords:
                if lines[start].startswith(w):
                    if len(lines[start]) >= len(w):
                        c = lines[start][len(w)]
                        if len(c) == 0 or c != '_' and not c.isalnum():
                            kw = w
                            break
            #firstword = lines[start].split(' ')[0]
            #if firstword in Cpp.keywords:
            if kw:
                #ret = Cpp.keywords[firstword](lines[start])
                ret = Cpp.keywords[kw](lines[start])
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
        # TESTING !
        #print >> sys.stderr, "EXPERIMENTAL RECOGNITION", \
        #                     ret.text, CppMeta.recognize(ret.text)
        # END TESTING !
        if context_in_for == 0:
            return Cpp.test_recog(Cpp.postprocess(ret, context)), start + 1
        else:
            return ret, start + 1

    @staticmethod
    def incr(name, ok):
        global counter
        ok = ok and 1 or 0
        if name in counter:
            counter[name] = (counter[name][0] + ok, counter[name][1] + 1)
        else:
            counter[name] = (ok, 1)

    @staticmethod
    def test_recog(ret):
        global counter
        recog = CppMeta.recognize(ret.text)
        name = type(ret).__name__
        Cpp.incr(name, recog[0])
        grpname = recog[0] and recog[3][0][0] or None
        if grpname != name:
            print "Experimental recognition discrepancy:"
            print "     ", type(ret).__name__, ret.text
            print "     ", type(ret).recognize
            print "     ", tokenize(ret.text)
            print "     ", grpname, recog
            print "--------------------------------------"
        print counter, ret
        return ret

    @staticmethod
    def postprocess(statement, context):
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
                return strip('public',
                                   strip('private',
                                               strip('protected', text)))

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
                for i in xrange(len(parts) - 2, -1, -1):
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

#DELETEME!
counter = {}
