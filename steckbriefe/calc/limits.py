from sympy import S, limit, Limit, oo, FiniteSet, AccumBounds, calculus, Symbol
from math import inf

invalid_limit_types = [AccumBounds, Limit]

def limits(f, x=Symbol('x', real=True)):
    limits = {}
    for p in FiniteSet(-oo, oo):
        key = 'limit_inf' if p == oo else 'limit_ninf'
        try:
            l = limit(f, x, p)
            limits[key] = float(l)
        except (TypeError, ValueError, NotImplementedError):
            limits[key] = None
    return limits

def singularities(f, x=Symbol('x', real=True)):
    f_singularities = None
    singularities_count = None
    try:
        all_singularities = calculus.singularities(f, x, S.Reals)
        if all_singularities.is_FiniteSet:
            f_singularities = []
            for s in all_singularities:
                s_type = None
                left_limit = limit(f, x, s, '-')
                right_limit = limit(f, x, s, '+')
                if left_limit.is_real and left_limit == right_limit:
                    s_type = 'Hebbare Lücke'
                elif left_limit.is_real and right_limit.is_real and left_limit != right_limit:
                    s_type = 'Sprungstelle'
                elif any([not l for l in [left_limit, right_limit]]):
                    s_type = 'Wesentliche Singularität'
                elif all([l.is_number and not l.as_real_imag()[1] for l in [left_limit, right_limit]]):
                    s_type = 'Polstelle'
                if s_type:
                    f_singularities.append((s, s_type, (left_limit, right_limit)))
            singularities_count = len(f_singularities)
        else:
            singularities_count = inf
            f_singularities = None
    except NotImplementedError:
        pass
    
    return {
        'singularities': f_singularities,
        'singularities_count': singularities_count
    }
