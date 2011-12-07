__all__ = [
    'resolve',
    'enter', 'leave', 'root', 'delete',
    'enter_scope', 'leave_scope'
]


VAR = 'var'
TYPE = 'type'


class Namespace(object):
    __stack = []

    def __init__(self, name='', parent=None, **metadata):
        self.name = name
        self.parent = parent
        self.scopes = [{}]
        self.namespaces = {}
        if 'key' in metadata:
            self.key = metadata['key']
            del metadata['key']
        else:
            self.key = 'namespace'
        self.metadata = metadata
        print "NEW NAMESPACE"
        print str(self)

    def assign(self, ns):
        self.scopes = ns.scopes
        self.namespaces = ns.namespaces
        self.key = ns.key

    def enter(self):
        self.__stack.append(self)

    def leave(self):
        self.__stack.pop()

    @classmethod
    def current(cls):
        return cls.__stack and cls.__stack[-1] or None

    def enter_subscope(self):
        ret = {}
        self.scopes.append(ret)
        return ret

    def leave_subscope(self):
        self.scopes.pop()

    @property
    def symbols(self):
        return self.scopes[-1]

    def get(self, something):
        if something in self.symbols:
            return self.symbols[something]
        if something in self.namespaces:
            return self.namespaces[something]

    def add_var(self, symbol, **metadata):
        #self.symbols[symbol] = (VAR, metadata)
        self.decl(symbol, VAR, **metadata)

    def add_type(self, symbol, **metadata):
        #self.symbols[symbol] = (TYPE, metadata)
        self.decl(symbol, TYPE, **metadata)

    def add_namespace(self, ns, **metadata):
        self.namespaces[ns.name] = ns

    def interpret_tokens(self, toks):
        name = ''
        ns = []
        for t in toks:
            if t[0] == 'namespace_member':
                ns.append(name)
            if t[0] == 'symbol':
                name = t[1]
        if len(ns) == 0:
            return self, name
        root = self.find_namespace(ns[0])
        container = reduce(lambda cur, name: cur.namespaces[name],
                           ns[1:], root)
        return container, name

    def decl(self, toks, what, **metadata):
        container, name = self.interpret_tokens(toks)
        if name not in container.symbols:
            container.symbols[name] = (what, metadata)

    def find_namespace(self, name):
        print "find_namespace", name, "in", self
        if name in self.namespaces:
            print "in here!"
            return self.namespaces[name]
        if name == self.name:
            print "self"
            return self
        if self.parent is not None:
            print "to parent"
            return self.parent.find_namespace(name)
        print "nothing", self.parent, self.name, self.namespaces
        return None

    def resolve_symbol(self, name):
        for i in xrange(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]
        if self.parent:
            return self.parent.resolve_symbol(name)
        return None

    def resolve(self, toks):
        container, name = self.interpret_tokens(toks)
        return container.resolve_symbol(name)
        #return name in container.symbols and container.symbols[name] or None

    def dump(self, level=0):
        indent = '  ' * level
        build = [indent + self.key + ' ' + self.name + ' {']
        for ns in self.namespaces.itervalues():
            if ns is not self:
                build.append(ns.dump(level + 1))
            else:
                build.append(indent + 'RECURSIVE!!!')
        for sym, stype in self.symbols.iteritems():
            build.append(indent + '  ' + str(sym) + ': ' + str(stype))
        build.append(indent + '}')
        return '\n'.join(build)

    def __str__(self):
        return self.dump()

    __repr__ = __str__


def resolve(tokens):
    return Namespace.current().resolve(tokens)


def enter(name, **metadata):
    pool = current().namespaces
    if name in pool:
        ret = pool[name]
    else:
        ret = Namespace(name, current(), **metadata)
        pool[ret.name] = ret
        #Namespace.current().add_namespace(ret)
    ret.enter()
    return ret


def delete(ns):
    if ns is Namespace.current():
        ns.leave()
    if ns in Namespace.current().namespaces:
        del Namespace.current().namespaces[ns.name]


def leave(ns):
    ns.leave()


def current():
    return Namespace.current()


def root():
    ret = Namespace('', None)
    ret.enter()
    return ret


def enter_scope():
    return Namespace.current().enter_subscope()


def leave_scope():
    Namespace.current().leave_subscope()


def add_type(tokens, **metadata):
    Namespace.current().add_type(tokens, **metadata)


def add_var(tokens, **metadata):
    Namespace.current().add_var(tokens, **metadata)
