from sympy import S, limit, Limit, oo, FiniteSet, AccumBounds, calculus
from math import inf
from utils import convert_inf

invalid_limit_types = [AccumBounds, Limit]

def limits(f, x):
    limits = {}
    for p in FiniteSet(-oo, oo):
        try:
            l = limit(f, x, p)
            if type(l) not in invalid_limit_types and not l.as_real_imag()[1]:
                limits[p] = convert_inf(l)
            else:
                limits[p] = None
        except (ValueError, NotImplementedError):
            limits[p] = None
    return limits

def singularities(f, x):
    f_singularities = None
    singularities_count = None
    try:
        all_singularities = calculus.singularities(f, x, S.Reals)
        if all_singularities.is_FiniteSet:
            f_singularities = []
            singularities_count = len(all_singularities)
            for s in all_singularities:
                left_limit = limit(f, x, s, '-')
                right_limit = limit(f, x, s, '+')
                s_type = 'Polstelle'
                if left_limit.is_real and left_limit == right_limit:
                    s_type = 'Hebbare Lücke'
                elif left_limit.is_real and right_limit.is_real and left_limit != right_limit:
                    s_type = 'Sprungstelle'
                elif any([not l for l in [left_limit, right_limit]]):
                    s_type = 'Wesentliche Singularität'
                f_singularities.append((s, s_type, (left_limit, right_limit)))
        else:
            singularities_count = inf
            f_singularities = None
    except NotImplementedError:
        pass
    
    return {
        'singularities': f_singularities,
        'singularities_count': singularities_count
    }
