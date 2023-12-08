from sympy import S, solve, solveset, ConditionSet, Symbol
from math import inf

def zeros(f, x=Symbol('x', real=True), domain=S.Reals):
    zeros = None
    zeros_count = None
    zeros_exact = None

    try:
        zeros_exact = solveset(f, x, domain)
        if not zeros_exact.is_FiniteSet:
            if not isinstance(zeros_exact, ConditionSet):
                zeros_count = inf
        else:
            zeros = list(zeros_exact)
            zeros_count = len(zeros)

        if zeros_count == inf:
            zeros = [z for z in solve(f, x) if z.is_real]
    except Exception:
        pass
    
    return {
        'zeros': zeros,
        'zeros_count': zeros_count,
        'zeros_exact': zeros_exact,
    }