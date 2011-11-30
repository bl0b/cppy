__all__ = ["TokenizerException", "tokenize_iter", "tokenize", "token_pattern"]

import re



# Code adapted from an answer at stackoverflow.com
# (url split in 2 to please pep8)
#http://stackoverflow.com/questions/2358890
#/python-lexical-analysis-and-tokenization

num = r"(?:\.[0-9]+|(?:0|[1-9][0-9]*)(?:\.[0-9]*)?)"
expo = r"(?:[eE]-?[0-9]+\.?[0-9]*)?"
number = num + expo

keyword = [
    'switch', 'class', 'while', 'do', 'for',
    'if', 'else', 'struct', 'union', 'return',
]

type_spec = [
    'typename', 'template', 'const', 'static', 'register', 'volatile',
    'extern', 'long', 'short', 'unsigned', 'signed',
]

sym_assert = r"(?!(?P=type_spec))(?!(?P=keyword))(?!(?P=new))(?!(?P=delete))"

token_pattern = r"""
(?P<number>""" + number + r""")
|(?P<kw_switch>\bswitch\b)
|(?P<kw_class>\bclass\b)
|(?P<kw_while>\bwhile\b)
|(?P<kw_do>\bdo\b)
|(?P<kw_for>\bfor\b)
|(?P<kw_if>\bif\b)
|(?P<kw_else>\belse\b)
|(?P<kw_struct>\bstruct\b)
|(?P<kw_union>\bunion\b)
|(?P<kw_return>\breturn\b)
|(?P<keyword>\b(?:""" + '|'.join(keyword) + r""")\b)
|(?P<type_spec>\b(?:""" + '|'.join(type_spec) + r""")\b)
|(?P<new>\bnew\b)
|(?P<delete>\bdelete\b\s*([[][]])?)
|(?P<symbol>""" + sym_assert + r"""\b[a-zA-Z_][a-zA-Z0-9_]*\b)
|(?P<access>(?:\.|->)[*]?)
|(?P<ampersand>[&])
|(?P<comma>[,])
|(?P<minus>[-])
|(?P<semicolon>[;])
|(?P<open_angle>[<])
|(?P<close_angle>[>])
|(?P<open_square>[[])
|(?P<close_square>[]])
|(?P<open_paren>[(])
|(?P<close_paren>[)])
|(?P<namespace_member>::)
|(?P<ternary>[?])
|(?P<colon>(?<!:):(?!:))
|(?P<open_curly>[{])
|(?P<close_curly>[}])
|(?P<whitespace>\s+)
|(?P<assign_set>(?<!=)[=](?!=))
|(?P<assign_update>(?:>>|<<|(?<![<>])[<>]|[&^%*/+-])[=](?!=))
|(?P<incdec>[+][+]|--)
|(?P<string>"(?:\\["bntr]|[^\\])*")
|(?P<char>'(?:\\['bntr]|[^\\])')
|(?P<boolop>[|][|]|[&][&]|!)
|(?P<bitop>(?<!\|)\|(?!\|) | (?<!\&)\&(?!\&) | [~] | (?<!\^)\^(?!\^))
|(?P<comp>==|!=|<=|>=|[><](?!=))
|(?P<addmoddiv>[%+/])
|(?P<star>[*])
|(?P<dot>[.])
|(?P<sharp>[#])
|(?P<dollar>[$])
"""

token_re = re.compile(token_pattern, re.VERBOSE)


class TokenizerException(Exception):
    pass


def tokenize_iter(text):
    pos = 0
    while True:
        m = token_re.match(text, pos)
        if not m:
            break
        pos = m.end()
        tokname = m.lastgroup
        tokvalue = m.group(tokname)
        if tokname != 'whitespace':  # don't emit whitespace
            yield tokname, tokvalue
    if pos != len(text):
        msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
                pos, len(text), text, text[pos:pos + 3])
        raise TokenizerException(msg)
# End of adapted code

tokenize = lambda t: list(tokenize_iter(t))
