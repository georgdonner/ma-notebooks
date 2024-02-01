import re, random, time, math, json
from sympy import S, Symbol, sympify, srepr

from steckbriefe.calc.meta import tree_props
from steckbriefe.calc.misc import fn_types, periodicity, y_intercept, domain, function_range, inverse
from steckbriefe.calc.limits import limits, singularities
from steckbriefe.calc.asymptotes import asymptotes
from steckbriefe.calc.zeros import zeros
from steckbriefe.calc.integral import integral
from steckbriefe.calc.derivative import derivative, extrema

def format_list(l):
    if not l:
        return ''
    return ','.join([str(n) for n in l])

def dict_str_values(d):
    return {key: str(val) for key, val in d.items()}

def randomize_function(fn_str, param_range=None, sympy_locals={}):
    regex = r'(?<!\w)[a-hk-w](?!\w)'
    n_constants = len(re.findall(regex, fn_str))
    if not param_range:
        param_range = list(range(2, n_constants + 3))
    elif n_constants > len(param_range):
        param_range = param_range * math.ceil(n_constants / len(param_range))
    def replace_constant(_):
        return str(param_range.pop(random.choice(range(0, len(param_range)))))
    return sympify(re.sub(regex, replace_constant, fn_str), locals=sympy_locals)

def calculate_steckbrief(fn_str):
    x = Symbol('x', real=True)
    f = randomize_function(fn_str, sympy_locals={'x': x})

    start = time.perf_counter()

    steckbrief = {}
    steckbrief['function_example'] = f
    steckbrief['function'] = fn_str

    # Metainformationen
    steckbrief.update(tree_props(f))

    # Funktionstypen
    steckbrief.update(fn_types(f, x))

    # Definitionsbereich
    steckbrief.update(domain(f, x))

    # Wertebereich
    steckbrief.update(function_range(f, x))

    # Unstetigkeitsstellen
    steckbrief.update(singularities(f, x))

    # Grenzwerte
    steckbrief.update(limits(f, x))

    # Asymptoten
    steckbrief.update(asymptotes(f, x))
    steckbrief['asymptotes'] = format_list(steckbrief['asymptotes'])

    # Periodizität
    steckbrief.update(periodicity(f, x))

    # y-Achsenschnitt
    steckbrief.update(y_intercept(f, x))

    # Nullstellen
    steckbrief.update(zeros(f, x, steckbrief['domain'] or S.Reals))
    steckbrief['zeros'] = format_list(steckbrief['zeros'])

    # Ableitung
    steckbrief.update(derivative(f, x))

    # Extrema
    steckbrief.update(extrema(f, x, fd=steckbrief['derivative'], fn_range=steckbrief['range'], domain=steckbrief['domain'] or S.Reals))

    # Integral
    steckbrief.update(integral(f, x))
    steckbrief['integral_rules'] = format_list(steckbrief['integral_rules'])

    # Umkehrfunktion
    steckbrief.update(inverse(f, x))

    # Serialisierung
    sympy_props = ['domain', 'range', 'singularities_exact', 'zeros_exact', 'minima', 'maxima', 'inflections']
    for prop in sympy_props:
        if prop in steckbrief:
            steckbrief[prop] = srepr(steckbrief[prop])
    steckbrief['singularities'] = [dict_str_values(d) for d in steckbrief['singularities']]
    steckbrief['singularities'] = json.dumps(steckbrief['singularities'], ensure_ascii=False)

    steckbrief['computation_seconds'] = round(time.perf_counter() - start, 2)

    return steckbrief
