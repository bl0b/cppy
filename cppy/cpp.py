__all__ = ['Cpp']

import re
import os
import sys
from itertools import ifilter, imap
import expressions
from parser import tokenize, match, find, find_all, compile_expression
from statements import *


inc_path = [
'/usr/include',
'/usr/local/include',
'/usr/include/c++/4.4/',
'/usr/include/c++/4.4/x86_64-linux-gnu/',
'/usr/include/linux/',
'/usr/include/c++/4.4/tr1/',
]

already_included = set()


def include(incname):
    ex = os.path.exists
    inc = filter(ex, (os.path.join(ip, incname) for ip in inc_path))
    if len(inc):
        i = inc[0]
        if i not in already_included:
            print "OPENING INCLUDE FILE", i
            already_included.add(i)
            return open(i)
        return ''
    print "COULDN'T FIND %s" % incname
    return ''


def incname(text):
    l = text.rfind('<')
    if l != -1:
        r = text.rfind('>')
    else:
        l = text.find('"')
        r = text.rfind('"')
    return text[l + 1:r]


def cpp_strip_slc(f):
    # xreadlines with stripping of empty lines and single-line comments
    reader = hasattr(f, 'xreadlines') and f.xreadlines() \
             or hasattr(f, 'splitlines') and f.splitlines() \
             or f
    for line in reader:
        components = line.strip().split('//')
        if len(components) and len(components[0]):
            #if components[0][0] == '#' and 'include' in components[0]:
            #    for inc in cpp_strip_slc(include(incname(components[0]))):
            #        yield inc
            #elif components[0][0] != '#':
            if components[0][0] != '#':
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
    return filter(lambda s: s not in ('', ';', ','), lines)


class Cpp(Scope):
    "Usable representation of a C++ file. Tries to be as accurate as possible."
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
    }
    c_symbol = '[_a-zA-Z][a-zA-Z0-9:<>,]*'
    symbol = '(?:%s::)*%s' % (c_symbol, c_symbol)
    assign_update_op = '(?<!=)(?:<<|>>|[+*&|/^~-])=(?!=)'
    assign_set_op = '(?<!=)(?<!<<|>>)(?<![+*&|/^~-])=(?!=)'
    assignment_op = '(?:%s|%s)' % (assign_set_op, assign_update_op)
    assignment_re = re.compile(r'^[*]*(' + symbol + ')(\[[^]]*\])? *'
                                + assignment_op + '([^;]+);$')
    #local_var_decl_re = re.compile('^[_a-zA-Z][a-zA-Z0-9<>,*: ]*?('
    #                                + c_symbol + ')( *=.*)?;$')
    var_spec = '(?:(?:volatile|static|register)*)'

    def __init__(self, f):
        Scope.__init__(self)
        lines = cpp_read(f)
        start = 0
        for t in ('int', 'float', 'double', 'char', 'wchar_t'):
            self[tuple(tokenize(t))] = 'type'
        print self
        while start < len(lines):
            statement, start = Cpp.parse(self, lines, start, 0)
            self.sub.append(statement)

    @staticmethod
    def parse(scope, lines, start, level):
        print level, "line #%i" % start, lines[start]
        if lines[start] == '{':
            ret = CppStatement('<DATA>', scope, [])
            start -= 1
        else:
            ret = CppMeta.recognize(lines[start], scope)
            print "      %s" % (' ' * len(str(start))), ret
        if ret is None:
            raise Exception("Couldn't parse < %s >" % lines[start])
        for abs_expr in ret.absorb:
            start += 1
            print level, "ABSORB", abs_expr, "line #%i" % start, lines[start]
            ok, mstart, mend, groups = match(tokenize(lines[start]), abs_expr)
            if not ok:
                raise Exception("parse error")
            print repr(ret.text), repr(lines[start])
            ret.text += lines[start]
            print repr(ret.text)
            for g in groups:
                ret.process_payload(*g)
        if (start + 1) < len(lines) and lines[start + 1] == '{':
            start += 2
            ABSORB = 0
            while start < len(lines) and lines[start] != '}':
                statement, start = Cpp.parse(ret, lines, start,
                                             level + 1)
                print "      %s" % (' ' * len(str(start))), statement
                if not ABSORB:
                    ret.sub.append(statement)
                    if statement.text.startswith('for'):
                        ABSORB = 2
                else:
                    ret.sub[-1].text += statement.text
                    ABSORB -= 1
                    ret.sub[-1].sub.extend(statement.sub)
            for abspo in ret.absorb_post:
                start += 1
                print "ABSORB POST", abspo, "line #%i" % start, lines[start]
                ok, mstart, mend, groups = match(tokenize(lines[start]), abspo)
                if not ok:
                    raise Exception("parse error")
                ret.text += lines[start]
                for g in groups:
                    ret.process_payload(*g)
        ret.commit()
        return ret, start + 1

    @staticmethod
    def _parse(scope, lines, start, level, context_in_for):

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
                        c = lines[start][len(w):]
                        if len(c) == 0 or c != '_' and not c.isalnum():
                            kw = w
                            break
            #firstword = lines[start].split(' ')[0]
            #if firstword in Cpp.keywords:
            if kw:
                #ret = Cpp.keywords[firstword](lines[start])
                ret = Cpp.keywords[kw](lines[start], scope)
            else:
                ret = CppStatement(lines[start], scope)
        if (start + 1) < len(lines) and lines[start + 1] == '{':
            start += 2
            ABSORB = 0
            print "in", ret
            while start < len(lines) and lines[start] != '}':
                statement, start = Cpp._parse(ret, lines, start,
                                              level + 1, ABSORB)
                if not ABSORB:
                    ret.sub.append(statement)
                    if statement.text.startswith('for'):
                        ABSORB = 2
                else:
                    ret.sub[-1].text += statement.text
                    ABSORB -= 1
                    ret.sub[-1].sub.extend(statement.sub)
        # TESTING !
        #print >> sys.stderr, "EXPERIMENTAL RECOGNITION", \
        #                     ret.text, CppMeta.recognize(ret.text)
        # END TESTING !
        if context_in_for == 0:
            pp = Cpp.postprocess(ret, scope)
            return Cpp.test_recog(pp, scope), start + 1
        else:
            return ret, start + 1

    @staticmethod
    def incr(name, matchdict):
        global counter
        ok = bool(name in matchdict or name == 'CppStatement' and matchdict)
        if name in counter:
            counter[name] = (counter[name][0] + int(ok), counter[name][1] + 1)
        else:
            counter[name] = (int(ok), 1)

    @staticmethod
    def test_recog(ret, scope):
        global counter, ambiguities
        recog = CppMeta.recognize(ret.text, scope)
        name = type(ret).__name__
        Cpp.incr(name, recog)
        #grpname = recog[0] and recog[3][0][0] or None
        #if grpname != name:
        if name not in recog:
            if name != 'CppStatement' or not recog:  # grpname is None:
                print "======================================================="
                print "Experimental recognition discrepancy:"
                print "     ", type(ret).__name__, ret.text
                print "     ", type(ret).recognize
                print "     ", tokenize(ret.text)
                #print "     ", grpname, recog
                print "     ", recog
                print "--------------------------------------"
            elif recog:  # grpname is not None:
                #print "Experimental recognition detected a",
                #print recog
                #print grpname, ":", ret.text
                pass
        if len(recog) > 1:
            ambiguities.add(tuple(recog.iterkeys()))
            print "======================================================="
            print "Ambiguity detected !"
            print "Statement <", ret.text, "> is either one of :",
            print ', '.join(recog.iterkeys())
            print recog
            print "--------------------------------------"
        #print counter, ret
        return ret

    @staticmethod
    def postprocess(statement, scope):
        c_type = len(scope.sub) and type(scope.sub[-1]) or None
        if type(statement) is ElseStatement and c_type is IfStatement:
            ret = scope.sub.pop()
            ret.elses.append(statement)
            return ret
        if type(statement) is WhileStatement and c_type is DoWhileStatement:
            ret = scope.sub.pop()
            ret.whilecond.append(statement)
            return ret
        if type(statement) is ClassDeclStatement:
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
                    scope.sub.append(AssignmentStatement(tmp_assign, scope))
                    exprpos = lvaluepos
                    exprend = lvaluepos + len(parts[i])
                return scope.sub.pop()  # "much more better" ((C) Jack Sparrow)
                                      # to keep the code simple
            else:
                ret = AssignmentStatement(statement.text, scope)
                #ret.sub = statement.sub
                #ret.lvalue = m.group(1)
                return ret
        # This is WAY too buggy
        #if Cpp.local_var_decl_re.match(statement.text):
        #    #print "DETECTED LOCAL VAR DECL"
        #    ok, start, end, grps = match(tokenize(statement.text), 'var_decl')
        #    #print ok and "SUCCESS" or "FAILED", statement.text, grps
        #    #    print tokenize(statement.text)
        #    #    #dump_expression('var_decl')
        #
        #    ret = VarDeclStatement(statement.text)
        #    ret.sub = statement.sub
        #    return ret

        # tokenize to differentiate the rest
        #print "TOKENIZING", statement.text
        #for x in tokenize(statement.text):
        #    print x
        return statement

    def tree(self):
        ret = []
        map(lambda x: x.tree(container=ret), self.sub)
        return '\n'.join(ret)

    def search_iter(self, predicate):
        for gen in imap(lambda x: x.search_iter(predicate), self.sub):
            for x in gen:
                yield x

    def __str__(self):
        return dict.__str__(self) + str(self.sub)

    def __repr__(self):
        return dict.__repr__(self) + repr(self.sub)

#DELETEME!
counter = {}
ambiguities = set()
