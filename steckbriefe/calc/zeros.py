from sympy import S, solve, solveset, ConditionSet, Intersection, Complement, Symbol
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
                zeros = [z for z in solve(f, x) if z.is_real]
                # Fix unevaluated Intersection/Complement results from solveset
                curr_args = zeros_exact
                while isinstance(curr_args, Intersection) or isinstance(curr_args, Complement):
                    if len(curr_args.args) == 0:
                        break
                    finite_sets = [arg for arg in curr_args.args if arg.is_FiniteSet]
                    if len(finite_sets) > 0:
                        if all([f.subs(x, z) == 0 for z in finite_sets[0]]):
                            zeros_count = len(finite_sets[0])
                        break
                    curr_args = curr_args.args[0]
        else:
            zeros = list(zeros_exact)
            zeros_count = len(zeros)
    except Exception:
        pass
    
    return {
        'zeros': zeros,
        'zeros_count': zeros_count,
        'zeros_exact': zeros_exact,
    }