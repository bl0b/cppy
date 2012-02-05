from base import Scope, Entity, Has_Name, Has_Type
from itertools import izip
from types import EXACT_MATCH, FuncType


class Function(Has_Name, Entity):
    is_function = True

    def __init__(self, name, scope):
        Has_Name.__init__(self, name, scope)
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
        ret_score = ret_type and st.match(ret_type) or 1
        score = ret_score * cv_score * p_score
        return score, p_score == EXACT_MATCH ** len(params)

    def score_signatures(self, ret_type, params, cv):
        exacts = []
        scores = []
        for i, sig in enumerate(self.signatures):
            score, exact = self.__sig_score(sig, ret_type, params, cv)
            print "signature", i, "scored", score
            if exact:
                exacts.append(i)
            if score:
                scores.append((i, score))
        ret = exacts, [i for i, s in sorted(scores, key=lambda x: - x[1])]
        print "signature scores", ret
        return ret

    def create_signature(self, ret_type, params, cv):
        exacts, scores = self.score_signatures(ret_type, params, cv)
        if len(exacts) > 1:
            raise Exception('Ambiguous signature '
                            + str([self.signatures[i] for i in exacts]))
        if len(exacts) == 1:
            return exacts[0]
        if len(exacts) == 0:
            print "No exact match. close matches", scores
            self.signatures.append((ret_type, [p.type for p in params], cv))
            ret = len(self.signatures) - 1
            scope = Scope(None, self.owner)
            self.scopes.append(scope)
            for p in params:
                scope.add(p)
            return ret

    def match_signature(self, params, cv, allow_close_match=False):
        exacts, scores = self.score_signatures(None, params, cv)
        if len(exacts) > 1:
            raise Exception('Ambiguous signature '
                            + str([self.signatures[i] for i in exacts]))
        if len(exacts) == 1:
            i = exacts[0]
            print "Exact signature match", i, self.signatures[i]
            return exacts[0]
        if allow_close_match and len(scores):
            print "Got close match", scores
        print "Couldn't match any signature for", params, cv, "amongst",
        print self.signatures
        return None


class FunctionParam(Has_Name, Has_Type, Entity):
    is_var = True

    def __init__(self, typ, name=None, default=None):
        Has_Name.__init__(self, name, None)
        Has_Type.__init__(self, typ)
        self.default = default

    def __str__(self):
        ret = "FunctionParam(" + str(self.type)
        if self.name:
            ret += ", name=" + repr(self.name)
        if self.default:
            ret += ", default=" + str(self.default)
        return ret + ')'

    __repr__ = __str__
