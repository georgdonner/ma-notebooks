from sympy import oo, limit

def asymptotes(f, x):
    a = set()
    if f.is_polynomial(x):
        return []
    for lim in [oo, -oo]:
        try:
            m = limit(f/x, x, lim)
            if m.is_real:
                n = limit(f-m*x, x, lim)
                if n.is_real and n.is_number:
                    a.add(m*x+n)
        except NotImplementedError:
            return []
    return list(a)
