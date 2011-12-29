class __uninit(object):
    def __str__(self):
        return "Uninitialized"

Uninitialized = __uninit()


class Entity(object):
    def __init__(self, name, writable):
        self.name = name
        self.writable = writable


class Var(Entity):
    def __init__(self, name, type_, init=Uninitialized):
        Entity


class Type(object):
    pass


def IntegralType(Type):
    def __init__(self, name, signed, size):
        pass
