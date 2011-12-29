class Entity(object):
    """Base class for all entities.
    Namespace, local scope, type, template type, variable, function."""
    is_var = False
    is_type = False
    is_template = False
    is_namespace = False
    is_function = False

    def __init__(self, name, scope):
        self.name = name
        self.owner = scope
        if name and self.owner:
            self.owner.contents[name] = self

    def match_specialization(self, params):
        return None

    def resolve(self, sym, local):
        return None

    def __str__(self):
        return type(self).__name__ + '(' + str(self.name) + ')'

    __repr__ = __str__


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
        return None

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


class Type(Scope):
    is_type = True

    def __init__(self, name, scope, data):
        Scope.__init__(self, name, scope)
        self.data = data


class Function(Scope):
    is_function = True


class TemplateType(Type):
    is_template = True
