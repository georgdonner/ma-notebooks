from sympy import S, solve, solveset, Symbol, ConditionSet, ImageSet
from math import inf

def zero_count(zero_set):
    if zero_set == None or isinstance(zero_set, ConditionSet):
        return None
    if zero_set.is_FiniteSet:
        return len(zero_set)
    if len(zero_set.atoms(ImageSet)):
        return inf
    return None

def zeros(f, x=Symbol('x', real=True), domain=S.Reals, throw=False):
    zeros = None
    zeros_exact = None

    try:
        zeros_exact = solveset(f, x, domain).simplify()
        if not zeros_exact.is_FiniteSet:
            if isinstance(zeros_exact, ConditionSet):
                zeros_exact = None
                raise NotImplementedError
            zeros = [z for z in solve(f, x) if z.is_real]
        else:
            zeros = list(zeros_exact)
    except Exception:
        if throw:
            raise
    
    return {
        'zeros': zeros,
        'zeros_count': zero_count(zeros_exact),
        'zeros_exact': zeros_exact,
    }