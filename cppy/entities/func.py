from base import Scope, Entity
from itertools import izip
from types import EXACT_MATCH


class Function(Entity):
    is_function = True

    def __init__(self, name, scope):
        Entity.__init__(self, name, scope)
        self.signatures = []
        self.scopes = []

    def __assert_sup_args_are_optional(self, params, op):
        if len(params) > len(op):
            return False
        sup = op[len(params):]
        return reduce(lambda a, b: a and b.default is not None, sup, True)

    def __sig_score(self, sig, ret_type, params, cv):
        st, sp, scv = sig
        cv_score = int(scv == cv)
        if cv_score and self.__assert_sup_args_are_optional(params, sp):
            p_score = reduce(lambda a, (sigp, p): a * sigp.type.match(p.type),
                             izip(sp, params),
                             1)
        else:
            p_score = 0
        ret_score = st.match(ret_type)
        score = ret_score * cv_score * p_score
        return score, p_score == EXACT_MATCH ** len(params)

    def score_signatures(self, ret_type, params, cv):
        exacts = []
        scores = []
        for i, sig in enumerate(self.signatures):
            score, exact = self.__sig_score(sig, ret_type, params, cv)
            if exact:
                exacts.append(i)
            if score:
                scores.append((i, score))
        return exacts, [i for i, s in sorted(scores, key=lambda x: - x[1])]

    def create_signature(self, ret_type, params, cv):
        exacts, scores = self.score_signatures(ret_type, params, cv)
        if len(exacts) > 1:
            raise Exception('Ambiguous signature '
                            + str([self.signatures[i] for i in exacts]))
        if len(exacts) == 1:
            return exacts[0]
        if len(exacts) == 0:
            self.signatures.append((ret_type, params, cv))
            ret = len(self.signatures) - 1
            scope = Scope(None, self)
            self.scopes.append(scope)
            for p in params:
                scope.add(p)
            return ret


class FunctionParam(Entity):
    is_var = True

    def __init__(self, typ, name=None, default=None):
        Entity.__init__(self, None, None)
        self.type = typ
        self.name = name
        self.default = None

    def __str__(self):
        ret = "FunctionParam(" + str(self.type)
        if self.name:
            ret += ", name=" + repr(self.name)
        if self.default:
            ret += ", default=" + str(self.default)
        return ret + ')'

    __repr__ = __str__
