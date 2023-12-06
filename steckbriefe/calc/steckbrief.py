from operator import itemgetter
import re, random, time
from sympy import oo, S, Symbol, sympify, calculus, periodicity, diff

from steckbriefe.calc.meta import tree_props
from steckbriefe.calc.limits import limits, singularities
from steckbriefe.calc.asymptotes import asymptotes
from steckbriefe.calc.zeros import zeros
from steckbriefe.calc.integral import integral

def format_list(l):
    if not l:
        return ''
    return ','.join([str(n) for n in l])

def has_inverse_trig(fn_str):
    return 'asin' in fn_str or 'acos' in fn_str

def calculate_steckbrief(fn_str):
    constants = ['k', 'm']
    x = Symbol('x', real=True)
    f = sympify(re.sub(f"[{''.join(constants)}]", lambda _: str(random.choice([2,3,4])), fn_str), locals={'x': x})

    start = time.perf_counter()

    steckbrief = {}
    steckbrief['function_example'] = str(f)
    steckbrief['function'] = fn_str

    # Metainformationen
    depth, leaves, nodes = tree_props(f)
    steckbrief['depth'] = depth
    steckbrief['leaves'] = leaves
    steckbrief['nodes'] = nodes

    # Funktionstyp
    steckbrief['polynomial'] = bool(f.is_polynomial(x))
    steckbrief['rational'] = bool(f.is_rational_function(x))

    # Definitionsbereich
    domain = None
    if not has_inverse_trig(fn_str):
        # sympy returns wrong results for inverse trigonometric functions, see https://github.com/sympy/sympy/issues/21786
        try:
            domain = calculus.util.continuous_domain(f, x, S.Reals)
        except Exception:
            pass
    steckbrief['domain'] = str(domain) if domain else domain

    # Wertebereich
    f_range = None
    if not has_inverse_trig(fn_str):
        try:
            f_range = calculus.util.function_range(f, x, domain or S.Reals)
        except Exception:
            pass
    steckbrief['range'] = str(f_range) if f_range else f_range

    # Unstetigkeitsstellen
    _singularities, singularities_count = itemgetter('singularities', 'singularities_count')(singularities(f, x))
    steckbrief['singularities'] = format_list(_singularities)
    steckbrief['singularities_count'] = singularities_count

    # Grenzwerte
    _limits = limits(f, x)
    steckbrief['limit_inf'] = _limits[oo]
    steckbrief['limit_ninf'] = _limits[-oo]

    # Asymptoten
    _asymptotes = asymptotes(f, x)
    steckbrief['asymptotes'] = format_list(_asymptotes)
    steckbrief['asymptotes_count'] = len(_asymptotes)

    # Periodizität
    try:
        steckbrief['periodicity'] = periodicity(f, x)
    except Exception:
        pass

    # y-Achsenschnitt
    try:
        y_intercept = f.subs(x, 0)
        steckbrief['y_intercept'] = y_intercept if y_intercept.is_real else None
    except Exception:
        pass

    # Nullstellen
    _zeros, zeros_count, zeros_exact = itemgetter('zeros', 'zeros_count', 'zeros_exact')(zeros(f, x, domain or S.Reals))
    steckbrief['zeros'] = format_list(_zeros)
    steckbrief['zeros_count'] = zeros_count
    steckbrief['zeros_exact'] = str(zeros_exact)

    # Ableitung
    try:
        steckbrief['derivative'] = diff(f, x)
    except Exception:
        pass

    # Integral
    _integral, integral_elementary, integral_rules = itemgetter('integral', 'integral_elementary', 'integral_rules')(integral(f, x))
    steckbrief['integral'] = _integral
    steckbrief['integral_elementary'] = integral_elementary
    steckbrief['integral_rules'] = format_list(integral_rules)

    steckbrief['computation_seconds'] = round(time.perf_counter() - start, 2)

    return steckbrief
