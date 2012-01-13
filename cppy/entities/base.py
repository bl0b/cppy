from itertools import izip


class Entity(object):
    """Base class for all entities.
    Namespace, local scope, type, template type, variable, function."""
    Null = None
    Void = None
    is_var = False
    is_type = False
    is_const = False
    is_template = False
    is_namespace = False
    is_function = False

    def match_specialization(self, params):
        return Entity.Null

    def resolve(self, sym, local):
        return Entity.Null

    def add(self, what):
        pass

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


Entity.Null = Entity()


class Has_Name(object):

    def __init__(self, name, scope):
        self.name = name
        self.owner = scope
        if name and self.owner:
            self.owner.add(self)

    def __str__(self):
        return type(self).__name__ + '(' + str(self.name) + ')'

    __repr__ = __str__


class Has_Value(object):

    def __init__(self, value):
        self._v = value

    @property
    def value(self):
        return self._v


class Has_Type(object):

    def __init__(self, type):
        self._t = type

    @property
    def type(self):
        return self._t


class Scope(Has_Name, Entity):
    """A C++ scope, namespace or local scope."""
    tag = 'S'

    def __init__(self, name=None, owner=None):
        print "* NEW SCOPE *", "name =", name, "owner =", owner
        Has_Name.__init__(self, name, owner)
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
        owner = self.owner and ', owner=' + repr(self.owner.name) or ''
        contents = self.contents and (', contents=' +
                                      str(self.contents.values())) or ''
        return ''.join((type(self).__name__, '(', repr(self.name), owner,
                        contents, ')'))

    __repr__ = __str__


class Namespace(Scope):
    is_namespace = True


class Variable(Has_Name, Has_Type, Entity):
    is_var = True

    def __init__(self, name, scope, type, static=False, default=None):
        Has_Name.__init__(self, name, scope)
        Has_Type.__init__(self, type)
        self.is_static = static
        self.default = default


class Const(Has_Name, Has_Type, Has_Value, Entity):
    is_const = True

    def __init__(self, name, scope, typ, value):
        Has_Name.__init__(self, name, scope)
        Has_Value.__init__(self, value)
        Has_Type.__init__(self, typ)

    def __str__(self):
        return 'Const(' + str(self.type) + ', ' + str(self.value) + ')'

    __repr__ = __str__
