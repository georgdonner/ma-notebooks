from sympy import calculus, periodicity as sym_periodicity, I, S, Symbol, solve

def has_inverse_trig(fn_str):
    return 'asin' in fn_str or 'acos' in fn_str

def domain(f, x=Symbol('x', real=True)):
    fn_domain = None
    if not has_inverse_trig(str(f)):
        # sympy returns wrong results for inverse trigonometric functions, see https://github.com/sympy/sympy/issues/21786
        try:
            fn_domain = calculus.util.continuous_domain(f, x, S.Reals)
        except Exception:
            pass
    return {
        'domain': fn_domain
    }

def function_range(f, x=Symbol('x', real=True)):
    fn_range = None
    if not has_inverse_trig(str(f)):
        try:
            fn_range = calculus.util.function_range(f, x, S.Reals)
        except Exception:
            pass
    return {
        'range': fn_range
    }

def fn_types(f, x=Symbol('x', real=True)):
    return {
        'polynomial': bool(f.is_polynomial(x)),
        'rational': bool(f.is_rational_function(x)),
    }

def periodicity(f, x=Symbol('x', real=True)):
    period = None
    try:
        period = sym_periodicity(f, x)
    except Exception:
        pass
    return {
        'periodicity': period,
    }

def y_intercept(f, x=Symbol('x', real=True)):
    y_intercept = None
    try:
        intercept = f.subs(x, 0)
        if intercept.is_real:
            y_intercept = intercept
    except Exception:
        pass
    return {
        'y_intercept': y_intercept,
    }

def inverse(f, x=Symbol('x', real=True)):
    inverse = None
    try:
        y = Symbol('y', real=True)
        inverses = [i.subs(y, x) for i in solve(f-y, x) if not i.has(I)]
        if len(inverses) == 1:
            inverse = inverses[0]
    except Exception:
        pass
    return {
        'inverse': inverse,
    }
    