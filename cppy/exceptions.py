__all__ = [
    'CppException', 'UnhandledCapture', 'AmbiguousStatement',
    'InvalidStatement',
]


class CppException(Exception):
    pass


class UnhandledCapture(CppException):

    def __init__(self, name, ast):
        CppException.__init__(self, "Capture <%s> has no handler in class %s!"
                                    % (ast.name, name))
        self.capture_name = ast.name
        self.capture_ast = ast
        #toks.dump()


class AmbiguousStatement(CppException):

    def __init__(self, text, scope, classes):
        CppException.__init__(self, "Ambiguous statement: < %s > %s" % (
                                    text, str(classes)))
        self.text = text
        self.scope = scope
        self.classes = classes


class InvalidStatement(CppException):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "Couldn't parse this statement: " + self.text
