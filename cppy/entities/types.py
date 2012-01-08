__all__ = [
    'Type', 'IntegralType',
    'TemplateType', 'TemplateFreeConst', 'TemplateFreeType',
    'StructuredType',
    'Char', 'Int', 'LongInt', 'LongLongInt',
    'UnsignedChar', 'UnsignedInt', 'UnsignedLongInt', 'UnsignedLongInt',
    'Float', 'Double', 'LongDouble',
    'Bool', 'Wchar_t',
]

from base import Entity, Const

EXACT_MATCH = 2
CLOSE_MATCH = 1
NO_MATCH = 0


class Type(Entity):
    is_type = True

    def __init__(self, name, scope):
        Entity.__init__(self, name, scope)

    def match(self, other):
        return NO_MATCH


CHAR = 0x100
INT = 0x300
FLOAT = 0x700
SIGNED = 0x10
UNSIGNED = 0x20
SHORT = 0x2
LONG = 0x4
LONGLONG = 0x8

MASK = 0xF0F

VOID_STAR = UNSIGNED | LONGLONG | INT


class IntegralType(Type):

    def __init__(self, magic, name):
        Type.__init__(self, None, None)
        self.magic = magic
        self.name = name

    def match(self, other, sign_matters=False):
        if type(other) is PointerTo:
            best = CLOSE_MATCH
        else:
            best = EXACT_MATCH
        mask = sign_matters and 0xFFF or MASK
        a, b = self.magic & mask, other.magic & mask
        if a == b:
            return min(best, EXACT_MATCH)
        if a & b == b:
            return CLOSE_MATCH
        return NO_MATCH

    __str__ = lambda self: self.name
    __repr__ = __str__


class ReferenceTo(Type):

    def __init__(self, ref_type):
        Entity.__init__(self, None, None)
        self.ref_type = ref_type

    def __str__(self):
        return 'ReferenceTo(%s)' % str(self.ref_type)

    __repr__ = __str__

    def match(self, other, sign_matters=False):
        if type(other) is ReferenceTo:
            return self.ref_type.match(other.ref_type)
        return self.ref_type.match(other)


class PointerTo(IntegralType):

    def __init__(self, ref_type):
        IntegralType.__init__(self, VOID_STAR, 'VoidStar')
        self.ref_type = ref_type

    def __str__(self):
        return 'PointerTo(%s)' % str(self.ref_type)

    __repr__ = __str__

    def match(self, other, sign_matters=False):
        if type(other) is ReferenceTo:
            return self.match(other.ref_type)
        if type(other) is PointerTo:
            return self.ref_type.match(other.ref_type)
        if type(other) is IntegralType:
            return min(IntegralType.match(self, other), CLOSE_MATCH)
        return NO_MATCH


class TemplateType(Type):
    is_template = True


class TemplateFreeType(Type):

    def __init__(self, name, scope, kw, default):
        Type.__init__(self, name, scope, kw)
        self.default = default
        self.kw = kw

    class DeferredResolution(Entity):
        pass

    def resolve(self, sym, local):
        return DeferredResolution(self, sym, local)


class TemplateFreeConst(Const):

    def __init__(self, name, scope, kw, default):
        Const.__init__(self, name, scope)
        self.kw = kw
        self.default = default

    class DeferredValue(Entity):
        pass

    @property
    def value(self):
        return DeferredValue(self)


Int = IntegralType(SIGNED | INT, 'Int')
ShortInt = IntegralType(SIGNED | SHORT | INT, 'ShortInt')
UnsignedShortInt = IntegralType(UNSIGNED | SHORT | INT, 'UnsignedShortInt')
LongInt = IntegralType(SIGNED | LONG | INT, 'LongInt')
LongLongInt = IntegralType(SIGNED | LONGLONG | INT, 'LongLongInt')
UnsignedInt = IntegralType(UNSIGNED | INT, 'UnsignedInt')
UnsignedLongInt = IntegralType(UNSIGNED | LONG | INT, 'UnsignedLongInt')
UnsignedLongLongInt = IntegralType(UNSIGNED | LONGLONG | INT,
                                   'UnsignedLongLongInt')
Char = IntegralType(SIGNED | CHAR, 'Char')
UnsignedChar = IntegralType(UNSIGNED | CHAR, 'UnsignedChar')
Float = IntegralType(SIGNED | UNSIGNED | FLOAT, 'Float')
Double = IntegralType(SIGNED | UNSIGNED | LONG | FLOAT, 'Double')
LongDouble = IntegralType(SIGNED | UNSIGNED | LONGLONG | FLOAT, 'LongDouble')
Bool = IntegralType(INT, 'Bool')
Wchar_t = IntegralType(LONG | CHAR, 'Wchar_t')
