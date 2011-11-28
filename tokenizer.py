__all__ = [ "TokenizerException", "tokenize_iter", "tokenize", "token_pattern" ]

import re



# Code adapted from an answer at stackoverflow.com http://stackoverflow.com/questions/2358890/python-lexical-analysis-and-tokenization
token_pattern = r"""
(?P<number>-?(?:\.[0-9]+|(?:0|[1-9][0-9]*)(?:\.[0-9]*)?)(?:[eE]-?[0-9]+\.?[0-9]*)?)
|(?P<keyword>\b(?:if|else|while|do|for|switch|class|struct|union|return)\b)
|(?P<type_spec>\b(?:typename|template|const|static|register|volatile|extern|long|short|unsigned|signed)\b)
|(?P<new>\bnew\b)
|(?P<delete>\bdelete\b\s*([[][]])?)
|(?P<symbol>(?!(?P=type_spec))(?!(?P=keyword))(?!(?P=new))(?!(?P=delete))\b[a-zA-Z_][a-zA-Z0-9_]*\b)
|(?P<access>(?:\.|->)[*]?)
|(?P<ampersand>[&])
|(?P<comma>[,])
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
|(?P<addsubdiv>[%+/-])
|(?P<star>[*])
|(?P<dot>[.])
|(?P<sharp>[#])
|(?P<dollar>[$])
"""

token_re = re.compile(token_pattern, re.VERBOSE)

class TokenizerException(Exception): pass

def tokenize_iter(text):
    pos = 0
    while True:
        m = token_re.match(text, pos)
        if not m: break
        pos = m.end()
        tokname = m.lastgroup
        tokvalue = m.group(tokname)
        if tokname != 'whitespace':  # don't emit whitespace
            yield tokname, tokvalue
    if pos != len(text):
        raise TokenizerException('tokenizer stopped at pos %r of %r in "%s" at "%s"' % (pos, len(text), text, text[pos:pos+3]))
# End of adapted code

tokenize = lambda t: list(tokenize_iter(t))

