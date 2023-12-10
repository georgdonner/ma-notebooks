from sympy import S, solve, solveset, Symbol, ConditionSet, ImageSet
from sympy.sets.sets import Intersection, Complement
from math import inf

def zero_count(f, x, zero_set):
    if zero_set == None or isinstance(zero_set, ConditionSet):
        return None
    if zero_set.is_FiniteSet:
        return len(zero_set)
    # Fix unevaluated Intersection/Complement results from solveset
    curr_args = zero_set
    while isinstance(curr_args, Intersection) or isinstance(curr_args, Complement):
        if len(curr_args.args) == 0:
            break
        finite_sets = [arg for arg in curr_args.args if arg.is_FiniteSet]
        if len(finite_sets) > 0:
            if all([f.subs(x, z) == 0 for z in finite_sets[0]]):
                return len(finite_sets[0])
        curr_args = curr_args.args[0]
    if len(zero_set.atoms(ImageSet)):
        return inf
    return None

def zeros(f, x=Symbol('x', real=True), domain=S.Reals, throw=False):
    zeros = None
    zeros_exact = None

    try:
        zeros_exact = solveset(f, x, domain)
        if not zeros_exact.is_FiniteSet:
            if isinstance(zeros_exact, ConditionSet):
                raise NotImplementedError
            zeros = [z for z in solve(f, x) if z.is_real]
        else:
            zeros = list(zeros_exact)
    except Exception:
        if throw:
            raise
    
    return {
        'zeros': zeros,
        'zeros_count': zero_count(f, x, zeros_exact),
        'zeros_exact': zeros_exact,
    }