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
        self.scope = scope
        if name:
            self.scope.contents[name] = self

    def match_specialization(self, params):
        return None

    def resolve(self, sym, local):
        return None


class Scope(Entity, dict):
    """A C++ scope, namespace or local scope."""

    def __init__(self, name=None, parent=None):
        Entity.__init__(self, name, parent)
        self.contents = {}

    def resolve(self, sym, local):
        if sym in self.contents:
            return self.contents[sym]
        elif self.parent and not local:
            return self.parent.resolve(sym, False)
        return None


class Namespace(Scope):
    is_namespace = True


class Variable(Entity):
    is_var = True


class Type(Scope):
    is_type = True


class Function(Scope):
    is_function = True


class TemplateType(Type):
    is_template = True
