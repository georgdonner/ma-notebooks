from sympy import S, solve, solveset, ConditionSet
from math import inf

def zeros(f, x, domain=S.Reals):
    zeros = None
    zeros_count = None
    zeros_exact = solveset(f, x, domain)

    if not zeros_exact.is_FiniteSet:
        if not isinstance(zeros_exact, ConditionSet):
            zeros_count = inf
    else:
        zeros = list(zeros_exact)
        zeros_count = len(zeros)

    if zeros_count == inf:
        try:
            zeros = [z for z in solve(f, x) if z.is_real]
        except NotImplementedError:
            pass
    
    return {
        'zeros': zeros,
        'zeros_count': zeros_count,
        'zeros_exact': zeros_exact,
    }