from base import Scope


class Function(Scope):
    is_function = True

    def __init__(self, name, scope):
        Scope.__init__(self, name, scope)
        self.signatures = []

    def __assert_sup_args_are_optional(self, params, op):
        if len(params) > len(op):
            return False
        sup = op[len(params):]
        return reduce(lambda a, b: a and b.default is not None, sup, True)

    def __sig_score(self, sig, ret_type, params, cv):
        st, sp, scv = sig
        cv_score = int(scv == cv)
        if cv_score and self.__assert_sup_args_are_optional(params, sp):
            p_score = reduce(lambda a, (sig_p, p): a * sig_p.match(p),
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
        return exacts, [i for i, s in sorted(scores, key=lambda x: -x[1])]

    def create_signature(self, ret_type, params, cv):
        exacts, scores = self.score_signatures(ret_type, params, cv)
        if len(exacts) > 1:
            raise Exception('Ambiguous signature '
                            + str([self.signatures[i] for i in exacts]))
        if len(exacts) == 1:
            return self.signatures[exacts[0]]
        if len(exacts) == 0:
            self.signatures.append((ret_type, params, cv))
            return self.signatures[-1]


class FunctionParam(object):

    def __init__(self, typ, name=None, default=None):
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
