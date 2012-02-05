from itertools import imap, chain
from entities import Has_Type, ReferenceTo


def xtyp(a, b):
    ret = a.type.match(b.type)
    print "MATCHING", a.type, b.type, "=>", ret
    return ret


class Operation(Has_Type):

    def __new__(cls, op, *operands):
        print "new Operation", op, operands
        typ = reduce(lambda a, b: xtyp(a, b) and a or None, operands)
        return typ is not None and Has_Type.__new__(cls) or None

    def __init__(self, op, *operands):
        typ = reduce(lambda a, b: xtyp(a, b) and a or None, operands)
        print 'operands', operands
        print "found consensus type", typ and typ.type
        Has_Type.__init__(self, typ.type)
        self.operands = operands
        self.operator = op
        print "Operation:", str(self), Operation.__str__(self)

    def __str__(self):
        op = ' ' + self.operator + ' '
        return ('Op(type=' + str(self.type) + ', ' +
                op.join(imap(str, self.operands)) + ')')

    __repr__ = __str__


class Inc(Operation):

    def __str__(self):
        return '++' + str(self.operands[0])


class Dec(Operation):

    def __str__(self):
        return '--' + str(self.operands[0])


class PostInc(Operation):

    def __str__(self):
        return str(self.operands[0]) + '++'


class PostDec(Operation):

    def __str__(self):
        return str(self.operands[0]) + '--'


class Subscript(Operation):

    def __str__(self):
        return str(self.operands[0]) + '[' + str(self.operands[1]) + ']'


class Call(Operation):

    @staticmethod
    def __sig(func, params):
        params = [p.type for p in params]
        i = func.match_signature(params, ('CONST', 'VOLATILE'), True)
        if i is None:
            i = func.match_signature(params, ('CONST',), True)
        if i is None:
            i = func.match_signature(params, ('VOLATILE',), True)
        if i is None:
            i = func.match_signature(params, None, True)
        if i is None:
            print "Couldn't match signature amongst"
            print '  ', '\n   '.join(imap(str, func.signatures))
            print "for", params
            return None
        return func.signatures[i]

    def __new__(cls, func, params):
        sig = Call.__sig(func, params)
        return Operation.__new__(cls, 'call', Has_Type(sig[0]))

    def __init__(self, func, params):
        sig = Call.__sig(func, params)
        Operation.__init__(self, 'call', Has_Type(sig[0]))
        self.operands = tuple(chain([func], params))
        print str(self), Call.__str__(self)

    def __str__(self):
        return ('Call(' + str(self.operands[0]) + ', (' +
                ', '.join(imap(str, self.operands[1:])) + '))')

    __repr__ = __str__


class DotAccess(Operation):
    pass


class ArrowAccess(Operation):
    pass


class TypeId(Operation):
    pass


class Cast(Has_Type):

    def __init__(self, dest_type, expr):
        Has_Type.__init__(self, dest_type)
        self.expr = expr

    def __str__(self):
        return 'Cast(to=' + str(self.type) + ', what=' + str(self.expr) + ')'

    __repr__ = __str__


class AssignSet(Operation):
    pass


class AssignUpdate(Operation):
    pass


class Minus(Operation):

    def __str__(self):
        return '-' + str(self.operands[0])


class Arithmetic(Operation):
    pass


class BitOp(Operation):
    pass


class Comparison(Operation):
    pass
