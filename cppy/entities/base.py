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
        print "* NEW SCOPE *", "name =", name, "owner =", owner
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
        owner = self.owner and ', owner=' + repr(self.owner.name) or ''
        contents = self.contents and (', contents=' +
                                      str(self.contents.values())) or ''
        return ''.join((type(self).__name__, '(', repr(self.name), owner,
                        contents, ')'))

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
