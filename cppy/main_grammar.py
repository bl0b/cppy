__all__ = ['validators', 'validator', 'register', 'grammar']

__gram_list = []


def register(*parts, **kwparts):
    __gram_list.extend(parts)
    __gram_list.extend(kwparts.values())


def grammar():
    return ''.join(__gram_list)


validators = {}


def validator(f):
    validators[f.__name__] = f
    return f
