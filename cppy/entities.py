class Entity(object):
    """Base class for all entities.
    Namespace, local scope, type, template type, variable, function."""
    Null = None
    is_var = False
    is_type = False
    is_const = False
    is_template = False
    is_namespace = False
    is_function = False

    def __init__(self, name, scope):
        self.name = name
        self.owner = scope
        if name and self.owner:
            self.owner.add(self)

    def match_specialization(self, params):
        return Entity.Null

    def resolve(self, sym, local):
        return Entity.Null

    def add(self, what):
        pass

    def __str__(self):
        return type(self).__name__ + '(' + str(self.name) + ')'

    __repr__ = __str__

    @property
    def full_path(self):
        if self.name:
            if self.owner:
                path = self.owner.full_path
            else:
                path = ''
            return path + '::' + self.name
        else:
            return ''


Entity.Null = Entity(None, None)


class Scope(Entity):
    """A C++ scope, namespace or local scope."""
    tag = 'S'

    def __init__(self, name=None, owner=None):
        Entity.__init__(self, name, owner)
        self.contents = {}

    def resolve(self, sym, local):
        if sym in self.contents:
            return self.contents[sym]
        elif self.owner and not local:
            return self.owner.resolve(sym, False)
        return Entity.Null

    def add(self, what):
        self.contents[what.name] = what

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return ''.join((type(self).__name__, '(', repr(self.name), ', ',
                        str(self.contents.values()), ')'))

    __repr__ = __str__


class Namespace(Scope):
    is_namespace = True


class Variable(Entity):
    is_var = True


class Const(Entity):
    is_const = True

    def __init__(self, name, scope, value):
        Entity.__init__(self, name, scope)
        self._v = value

    @property
    def value(self):
        return self._v


class Type(Scope):
    is_type = True

    def __init__(self, name, scope, data):
        Scope.__init__(self, name, scope)
        self.data = data


class Function(Scope):
    is_function = True


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
