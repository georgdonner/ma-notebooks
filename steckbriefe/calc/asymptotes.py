from sympy import oo, limit, Symbol

def asymptotes(f, x=Symbol('x', real=True)):
    a = set()
    if not f.is_polynomial(x):
        for lim in [oo, -oo]:
            try:
                m = limit(f/x, x, lim)
                if m.is_real:
                    n = limit(f-m*x, x, lim)
                    if n.is_real and n.is_number:
                        a.add(m*x+n)
            except NotImplementedError:
                pass
    return {
        'asymptotes': list(a),
        'asymptotes_count': len(a)
    }
